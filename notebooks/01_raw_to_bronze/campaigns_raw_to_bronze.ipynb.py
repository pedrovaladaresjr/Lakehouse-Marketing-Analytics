# Databricks notebook source
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql.window import Window

# COMMAND ----------

BASE_PATH = "/Volumes/main/lakehouse_marketing"
RAW_PATH = f"{BASE_PATH}/raw"
BRONZE_PATH = f"{BASE_PATH}/bronze"

# COMMAND ----------

campaign_schema = StructType([
    StructField("campaign_id", StringType(), True),
    StructField("campaign_name", StringType(), True),
    StructField("channel", StringType(), True),
    StructField("start_date", StringType(), True),
    StructField("end_date", StringType(), True)
])

df_campaigns_raw = spark.read\
                    .schema(campaign_schema)\
                    .option("header", "true")\
                    .csv(f"{RAW_PATH}/campaigns")

# COMMAND ----------

df_campaigns_bronze = df_campaigns_raw\
                        .withColumn("ingestion_timestamp", F.current_timestamp())\
                        .withColumn("source_file", F.col("_metadata.file_path"))

# COMMAND ----------

# MAGIC %md
# MAGIC * Escrita na Bronze

# COMMAND ----------

f"{BRONZE_PATH}/campaigns"

# COMMAND ----------

BRONZE_CAMPAIGNS_PATH = f"{BRONZE_PATH}/campaigns"

df_campaigns_bronze.write\
    .format('delta')\
    .mode('overwrite')\
    .save(BRONZE_CAMPAIGNS_PATH)

# COMMAND ----------

# MAGIC %md
# MAGIC * Validação

# COMMAND ----------

spark.read\
    .format('delta')\
    .load("/Volumes/main/lakehouse_marketing/bronze/campaigns/")\
    .count()


# COMMAND ----------

# display(spark.read\
#     .format("delta")\
#     .load("/Volumes/main/lakehouse_marketing/bronze/campaigns/"))
