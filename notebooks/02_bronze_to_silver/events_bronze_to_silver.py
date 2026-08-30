# Databricks notebook source
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# COMMAND ----------

events_bronze = "/Volumes/main/lakehouse_marketing/bronze/events/"

df_events_bronze = spark.read\
                    .format("delta")\
                    .option("header", "true")\
                    .load(events_bronze)

display(df_events_bronze.limit(5))
display(df_events_bronze.printSchema())

# COMMAND ----------

# MAGIC %md
# MAGIC * Selecionando as colunas

# COMMAND ----------

df = df_events_bronze.select(
                        "event_id",    
                        "user_id",
                        "campaign_id",
                        "event_type",
                        "event_timestamp",
                        "source_file",
                        "ingestion_timestamp"
)

##########################################################
# Aplicação / Reforço da Tipagem para (event_timestamp)
#########################################################
df_typed = df\
            .withColumn("event_timestamp", F.to_timestamp("event_timestamp"))


##########################################################################
#Nomalização para a coluna event_type (Precisa aplicar upper + trim)
##########################################################################
df_normalized = df_typed.withColumn("event_type", F.upper(F.trim(F.col("event_type"))))


display(df_normalized.select("event_type").distinct())
display(df_normalized.count())


# COMMAND ----------

# MAGIC %md
# MAGIC #### Regras de Transformação

# COMMAND ----------

# MAGIC %md
# MAGIC * Check de nulos

# COMMAND ----------

# Verificando a quantidade de nulos na base
df_normalized.groupBy(F.col("user_id").isNull().alias("is_null")).count().show()

# COMMAND ----------

# DBTITLE 1,OLD-REMOVE-NULLS
# # # REGRA 1: Remover eventos sem `user_id`
# df_valid = df_normalized.filter(F.col("user_id").isNotNull())

# # REGRA 2: Trazer apenas o conjunto de eventos permitidos
# allowed_events = ['VIEW', 'PURCHASE', 'CLICK']
 
# df_valid = df_valid.filter(F.upper(F.col("event_type")).isin(allowed_events))

# # REGRA 3: Trazer apenas `event_timestamp` validos
# df_valid = df_valid.filter(F.col("event_timestamp").isNotNull())
# display(df_valid)

# COMMAND ----------

# MAGIC %md
# MAGIC Vamos aplicar 3 regras:
# MAGIC * REGRA 1: Remover eventos sem `user_id`
# MAGIC * REGRA 2: Trazer apenas o conjunto de eventos permitidos
# MAGIC * REGRA 3: Trazer apenas `event_timestamp` validos
# MAGIC
# MAGIC

# COMMAND ----------

# Define os eventos permitos, conforme a documentação
allowed_events = ['VIEW', 'PURCHASE', 'CLICK']


df_with_rules = df_normalized.withColumn(
    "rejection_reason",
    F.when(F.col("user_id").isNull(), "NULL_USER_ID")
     .when(~F.col("event_type").isin(allowed_events), "INVALID_EVENT_TYPE")
     .when(F.col("event_timestamp").isNull(), "NULL_EVENT_TIMESTAMP")
     .otherwise(None)
)

display(df_with_rules.sample(0.001))

# COMMAND ----------

# MAGIC %md
# MAGIC * Separar válidos e rejeitados

# COMMAND ----------

df_valid = df_with_rules.filter(F.col("rejection_reason").isNull())
df_rejected = df_with_rules.filter(F.col("rejection_reason").isNotNull())

display(df_valid.sample(0.001))
display(df_rejected.sample(0.001))

# COMMAND ----------

# MAGIC %md
# MAGIC #### Escrita na Silver

# COMMAND ----------

EVENTS_SILVER_PATH = "/Volumes/main/lakehouse_marketing/silver"

# Resultados válidos
df_valid.write\
        .format("delta")\
        .mode("overwrite")\
        .save(f"{EVENTS_SILVER_PATH}/events")



# Registros rejeitados
df_rejected.write\
        .format("delta")\
        .mode("overwrite")\
        .save(f"{EVENTS_SILVER_PATH}/events_rejected")


# COMMAND ----------

# MAGIC %md
# MAGIC #### Validação Dados Silver - Events
# MAGIC

# COMMAND ----------

df_events_valid = spark.read\
                    .format("delta")\
                    .option("header", "true")\
                    .option("inferSchema", "true")\
                    .load(f"{EVENTS_SILVER_PATH}/events")

display(df_events_valid)
    

# COMMAND ----------

df_events_valid.count()
