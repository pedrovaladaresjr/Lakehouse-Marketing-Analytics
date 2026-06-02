# Databricks notebook source
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql.window import Window

# COMMAND ----------

BASE_PATH = "/Volumes/main/lakehouse_marketing"
RAW_PATH = f"{BASE_PATH}/raw"
BRONZE_PATH = f"{BASE_PATH}/bronze"

# COMMAND ----------

# MAGIC %md
# MAGIC %md
# MAGIC * Definindo Schema e lendo o csv da Raw

# COMMAND ----------

# DBTITLE 1,Cell 4
events_schema = StructType([
    StructField("campaign_id", StringType(), True),
    StructField("event_id", StringType(), True),
    StructField("event_timestamp", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("user_id", StringType(), True)
])


df_events_raw = spark.read\
                    .schema(events_schema)\
                    .option("header", "true")\
                    .csv(f"{RAW_PATH}/events")

# COMMAND ----------

df_events_bronze = df_events_raw\
                        .withColumn("ingestion_timestamp", F.current_timestamp())\
                        .withColumn("source_file", F.col("_metadata.file_path"))


# COMMAND ----------

display(df_events_bronze.limit(5))

# COMMAND ----------

BRONZE_EVENTS_PATH = f"{BRONZE_PATH}/events"

df_events_bronze.write\
    .format('delta')\
    .mode('overwrite')\
    .save(BRONZE_EVENTS_PATH)

# COMMAND ----------

dbutils.fs.ls(BRONZE_EVENTS_PATH)

# COMMAND ----------

display(spark.read\
    .format("delta")\
    .option("header", "true")\
    .load(f"{BRONZE_EVENTS_PATH}"))

# COMMAND ----------

spark.read\
    .format("delta")\
    .load(f"{BRONZE_EVENTS_PATH}")\
    .count()
