# Databricks notebook source
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql.window import Window

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE VOLUME IF NOT EXISTS main.lakehouse_marketing.bronze;

# COMMAND ----------

BASE_PATH = "/Volumes/main/lakehouse_marketing"
RAW_PATH = f"{BASE_PATH}/raw"
BRONZE_PATH = f"{BASE_PATH}/bronze"

# COMMAND ----------

# MAGIC %md
# MAGIC * Definição do Schema e letura da RAW

# COMMAND ----------

users_schema = StructType([
    StructField("country", StringType(), True),
    StructField("created_at", StringType(), True),
    StructField("email", StringType(), True),
    StructField("signup_date", StringType(), True),
    StructField("user_id", StringType(), True)
])

df_users_raw = spark.read\
                .schema(users_schema)\
                .option("header", "true")\
                .csv(f"{RAW_PATH}/users")

# COMMAND ----------

# DBTITLE 1,Cell 7
display(df_users_raw.sample(0.001))

# COMMAND ----------

# MAGIC %md
# MAGIC * **Metadados para bronze (ingestion + source_file)**
# MAGIC
# MAGIC     * Garantir auditoria
# MAGIC     * Debug
# MAGIC     * Reprocesso

# COMMAND ----------

# DBTITLE 1,Cell 6
df_users_bronze = df_users_raw\
                    .withColumn("ingestion_timestamp", F.current_timestamp())\
                    .withColumn("source_file", F.col('_metadata.file_path'))


# COMMAND ----------

# MAGIC %md
# MAGIC * **Escrita**
# MAGIC
# MAGIC     * Delta Lake
# MAGIC     * Versionamento
# MAGIC     * ACID
# MAGIC     * Time Travel

# COMMAND ----------

BRONZE_USERS_PATH = f"{BRONZE_PATH}/users"

df_users_bronze.write\
    .format("delta")\
    .mode("overwrite")\
    .save(BRONZE_USERS_PATH)

# COMMAND ----------

# MAGIC %md
# MAGIC * **Validação**

# COMMAND ----------

# Deve bater com as 5000 linhas
spark.read\
    .format("delta")\
    .load("/Volumes/main/lakehouse_marketing/bronze/users/")\
    .count()

# COMMAND ----------

display(spark.read\
    .format("delta")\
    .load("/Volumes/main/lakehouse_marketing/bronze/users/"))
