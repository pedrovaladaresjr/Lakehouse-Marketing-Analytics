# Databricks notebook source
# MAGIC %pip install faker

# COMMAND ----------

from faker import Faker 
import random

# COMMAND ----------

# Setup
random.seed(42)
fake = Faker()
fake.seed_instance(42)

conversions = []

for _ in range(3000):

    conversions.append({
        "conversion_id" : fake.uuid4(),
        "user_id" :  fake.uuid4(),
        "campaign_id" : fake.uuid4(),
        "conversion_date" : fake.date_between("-3m", "today").strftime("%d-%m-%Y"),
        "revenue" : str(round(random.uniform(10, 500), 2))
    }
    )

df_conversions = spark.createDataFrame(conversions)
display(df_conversions.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC * Escrita na RAW

# COMMAND ----------

BASE_PATH = "/Volumes/main/lakehouse_marketing/raw"

df_conversions.write\
    .mode("overwrite")\
    .option("header", "true")\
    .csv(f"{BASE_PATH}/conversions")

# COMMAND ----------

# MAGIC %md
# MAGIC * Validação

# COMMAND ----------

dbutils.fs.ls(BASE_PATH)
