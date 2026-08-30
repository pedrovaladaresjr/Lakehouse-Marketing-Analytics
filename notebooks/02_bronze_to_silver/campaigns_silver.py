# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# COMMAND ----------

campaigns_bronze = '/Volumes/main/lakehouse_marketing/bronze/campaigns/'


df_campaigns = spark.read\
                    .format("delta")\
                    .option("header", "true")\
                    .load(campaigns_bronze)

display(df_campaigns)
display(df_campaigns.printSchema())

# COMMAND ----------

#########################################################
#  Seleção explícita das colunas que serão usadas
#########################################################
df = df_campaigns.select(
    'campaign_id',
    'campaign_name',
    'channel',
    'start_date',
    'end_date',
    'ingestion_timestamp',
    'source_file'
)

#############################################################
# Isso é apenas uma forma declarativa para se aplicar depois
#############################################################
df_typed = df\
            .withColumn('campaign_name', F.trim(F.col('campaign_name')))\
            .withColumn('start_date', F.to_date('start_date'))\
            .withColumn('end_date', F.to_date('end_date'))

#####################################
#Nomalização para o canal (EMAIL | SOCIAL)
#####################################
df_normalized = df_typed.withColumn(
    "channel",
    F.when(F.lower(F.regexp_replace("channel", "-", "")) == "email", "EMAIL")
    .when(F.lower(F.col("channel")).isin("social"), "SOCIAL")
    .otherwise("OTHER")
)

df_normalized.printSchema()
display(df_normalized)

# COMMAND ----------

# MAGIC %md
# MAGIC * Cria coluna para Validação
# MAGIC ---
# MAGIC *Será dividido os dados tratados em uma tabela e os que contém nulos em outra*

# COMMAND ----------

df_with_rules = df_normalized.withColumn(
    "rejection_reason",
    F.when(F.col("campaign_id").isNull(), "NULL_CAMPAIGN_ID")
     .when(F.col("campaign_name").isNull(), "NULL_CAMPAIGN_NAME")
     .when(F.col("channel").isNull(), "NULL_CHANNEL")
     .otherwise(None)     
)

display(df_with_rules)

# COMMAND ----------

# MAGIC %md
# MAGIC * Deduplicação
# MAGIC ---
# MAGIC *Aplica a deduplicação em `campaign_id`*

# COMMAND ----------

window = Window.partitionBy("campaign_id").orderBy(F.col("ingestion_timestamp").desc())

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
# MAGIC
# MAGIC --- 
# MAGIC A criação do **schema** da tabela está sendo feita no notebook `users_bronze_to_silver`, logo, não há a necessidade de replicar o código aqui.
# MAGIC

# COMMAND ----------

df_valid = df_dedup.filter(F.col("rejection_reason").isNull())
df_rejected = df_dedup.filter(F.col("rejection_reason").isNotNull())

# COMMAND ----------

# Resultados válidos
df_valid.write\
    .format("delta")\
    .mode("overwrite")\
    .saveAsTable("main.lakehouse_marketing_silver.campaigns")

# Resultados Rejeitados
df_rejected.write\
    .format("delta")\
    .mode("overwrite")\
    .saveAsTable("main.governance_marketing.campaigns_rejected")

# COMMAND ----------

# MAGIC %md
# MAGIC * Validação

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN main.lakehouse_marketing_silver;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     COUNT(*) AS total_registros
# MAGIC FROM main.lakehouse_marketing_silver.campaigns
