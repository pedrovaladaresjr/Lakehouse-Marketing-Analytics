# Databricks notebook source
# MAGIC %md
# MAGIC # Users Silver
# MAGIC ---
# MAGIC
# MAGIC * Cada usuário aparece **uma única vez**
# MAGIC * Tipos devem seguir o documento de padronização da Silver
# MAGIC * Datas devem seguir os tipos especificados no documento
# MAGIC * Dados ruins são tratados, não ignorados
# MAGIC
# MAGIC ---
# MAGIC **Bibliotecas**
# MAGIC
# MAGIC * `functions (F)` &rarr; transformações declarativas (Spark SQL style)
# MAGIC * `Window` &rarr; deduplicação correta
# MAGIC
# MAGIC ---
# MAGIC **Leitura da Bronze**
# MAGIC
# MAGIC * Estamos confiando que a Bronze:
# MAGIC   * já tem schema
# MAGIC   * já tem metadados
# MAGIC   * já é rastreável
# MAGIC
# MAGIC ---
# MAGIC **Seleção de colunas**
# MAGIC
# MAGIC Esse é um processo simples, mas `arquiteturalmente crítico`
# MAGIC
# MAGIC * Não aplicar `select("*")`:
# MAGIC   * Campos inesperados quebram os contratos
# MAGIC   * Evolução de schema fica caótica
# MAGIC   * Times downstream perdem confiança
# MAGIC
# MAGIC > *Aqui será definido tudo de forma explícita.*
# MAGIC
# MAGIC ---
# MAGIC **Aplicação da Tipagem nas colunas**
# MAGIC
# MAGIC * Aplicar as regras que estão no **data contract**
# MAGIC   * Não é necessário definir a tipagem a ser aplicada depois para todas as colunas, apenas para as colunas que precisam dos ajustes necessários
# MAGIC
# MAGIC ---
# MAGIC **Normalização**
# MAGIC
# MAGIC Aqui será aplicado as regras definidas no documento para a normalização das nomenclaturas dos países.
# MAGIC
# MAGIC * Segue a nomenclatura com 2 dígitos
# MAGIC * Aplicação de `upper()` 
# MAGIC
# MAGIC ---
# MAGIC **Validações Mínimas de Qualidade**
# MAGIC
# MAGIC Remover registros nullos da coluna `user_id`
# MAGIC
# MAGIC ---
# MAGIC **Deduplicação**
# MAGIC
# MAGIC > *Para cada `user_id`, manter o registro com `created_at` mais recente.*
# MAGIC
# MAGIC Aqui é onde escolhemos a "verdadeira" versão de um mesmo registro quando ele aparece mais de uma vez.
# MAGIC
# MAGIC **Não usar `dropDuplicates()` aqui, pois não resolve a regra.**
# MAGIC

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.window import Window

# COMMAND ----------

# MAGIC %md
# MAGIC * **Leitura do dados na bronze**

# COMMAND ----------

users_bronze = "/Volumes/main/lakehouse_marketing/bronze/users/"

df_bronze = spark.read\
                .format("delta")\
                .load(users_bronze)

display(df_bronze.limit(5))
display(df_bronze.printSchema())

# COMMAND ----------

# MAGIC %md
# MAGIC * **Aqui faremos:**
# MAGIC
# MAGIC   * *Seleção das Colunas*
# MAGIC   * *Definição da Tipagem*
# MAGIC   * *Normalização para Country*
# MAGIC   * *Validações Mínimas de qualidade*
# MAGIC

# COMMAND ----------

#########################################################
#  Seleção explícita das colunas que serão usadas
#########################################################
df = df_bronze.select(
    "user_id",
    "email",
    "country",
    "signup_date",
    "created_at",
    "ingestion_timestamp",
    "source_file"
)

#############################################################
# Isso é apenas uma forma declarativa para se aplicar depois
#############################################################
df_typed = df\
            .withColumn("email", F.lower("email"))\
            .withColumn("country", F.upper("country"))\
            .withColumn("signup_date", F.to_date("signup_date"))

#####################################
#Nomalização para a coluna country
#####################################
df_normalized = df_typed.withColumn(
    "country",
    F.when(F.col("country").isin("BRA", "BRAZIL"), "BR")
     .when(F.col("country").isin("USA", "US", "UNITED STATES"), "US")
     .otherwise("UNKNOWN")
)
display(df_normalized.groupBy("country").count())
display(df_normalized.sample(0.001))


# COMMAND ----------

# MAGIC %md
# MAGIC * Cria coluna para Validação
# MAGIC ---
# MAGIC *Criaremos uma coluna com as regras para então depois filtrarmos*

# COMMAND ----------

####################################
# Validações mínimas de qualidade
####################################
# df_valid = df_normalized.filter(F.col("user_id").isNotNull())
# display(df_valid.sample(0.001))

df_with_rules = df_normalized.withColumn(
                    "rejection_reason",
                    F.when(F.col("user_id").isNull(), "NULL_USER_ID")
                     .when(F.col("email").isNull(), "NULL_EMAIL")
                     .when(~F.col("email").rlike("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$"), "INVALID_EMAIL")
                     .otherwise(None)
)

display(df_with_rules.sample(0.01))

# COMMAND ----------

# MAGIC %md
# MAGIC * Deduplicação
# MAGIC ---
# MAGIC
# MAGIC A regra: *Aplicar deduplicação em `user_id` com `created_at` mais recente*.

# COMMAND ----------

# Primeiro particionamos por user_id e ordenamos por signup_date
window = Window.partitionBy("user_id").orderBy(F.col("signup_date").desc())

# Após definimos a janela, o row_number define um rank para cada registro
# como ordenamos de forma decrescente, o maior "signup_date" de cada "user_id"
# terá o rank 1, com isso, conseguimos filtrar apenas o que for igual a  1.
df_dedup = (
    df_with_rules
    .withColumn("row_number", F.row_number().over(window))
    .filter(F.col("row_number") == 1)
    .drop("row_number")
)

print(f"Sem deduplicação: {df_with_rules.count()}")
print(f"Deduplicação tratada: {df_dedup.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Escrita na SILVER

# COMMAND ----------

# MAGIC %md
# MAGIC * Usando dados completos

# COMMAND ----------

df_valid = df_dedup.filter(F.col("rejection_reason").isNull())
df_rejected = df_dedup.filter(F.col("rejection_reason").isNotNull())

# COMMAND ----------

# MAGIC %md
# MAGIC #### Definição do Schema

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS main.silver_marketing;
# MAGIC CREATE SCHEMA IF NOT EXISTS main.governance_marketing;

# COMMAND ----------

# Resultados válidos
df_valid.write\
        .format("delta")\
        .mode("overwrite")\
        .saveAsTable("main.silver_marketing.users")


# Resultados Rejeitados
df_rejected.write\
        .format("delta")\
        .mode("overwrite")\
        .saveAsTable("main.governance_marketing.users_rejected")

# COMMAND ----------

# MAGIC %md
# MAGIC * Validação

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN main.silver_marketing;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     COUNT(*)
# MAGIC FROM main.silver_marketing.users
# MAGIC
