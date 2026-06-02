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
# MAGIC * Definindo Schema e lendo o csv da Raw

# COMMAND ----------

conversions_schema = StructType([
    StructField("conversion_id", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("campaign_id", StringType(), True),
    StructField("conversion_date", StringType(), True),
    StructField("revenue", StringType(), True)
])

df_conversions_raw = spark.read\
                        .schema(conversions_schema)\
                        .option("header", "true")\
                        .csv(f"{RAW_PATH}/conversions")

# COMMAND ----------

df_conversions_bronze = df_conversions_raw\
                        .withColumn("ingestion_timestamp", F.current_timestamp())\
                        .withColumn("source_file", F.col("_metadata.file_path"))

# COMMAND ----------

# MAGIC %md
# MAGIC * Escrita na Bronze

# COMMAND ----------

BRONZE_CONVERSIONS_PATH = f"{BRONZE_PATH}/conversions"

df_conversions_bronze.write\
    .format('delta')\
    .mode('overwrite')\
    .save(BRONZE_CONVERSIONS_PATH)

# COMMAND ----------

dbutils.fs.ls(BRONZE_CONVERSIONS_PATH)

# COMMAND ----------

display(spark.read\
    .format("delta")\
    .load(f"{BRONZE_CONVERSIONS_PATH}"))
