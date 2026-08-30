# Databricks notebook source
# MAGIC %md
# MAGIC # Generate Campaigns
# MAGIC ---
# MAGIC O objetivo deste notebook é criar a base de campanhas, os dados intencionalmente serão gerados com inconsistências.
# MAGIC
# MAGIC
# MAGIC * Canal: `email`, `EMAIL`, 
# MAGIC * Datas invertidas
# MAGIC * Campanhas duplicadas
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC Campos da tabela **campaigns**:
# MAGIC
# MAGIC * **campaign_id:** *Representa o id da campanha*
# MAGIC * **campaign_name:** *Nome da campanha*
# MAGIC * **channel:** *Canal de origem ("E-mail", "Social")*
# MAGIC * **start_date:** *Inicio da campanha*
# MAGIC * **end_date:** *Fim da campanha*

# COMMAND ----------

# MAGIC %pip install faker

# COMMAND ----------

from faker import Faker
import random 

# COMMAND ----------

# Setup
random.seed(42)
fake = Faker()
fake.seed_instance(42)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Geração dos Dados

# COMMAND ----------

channels = ["email", "EMAIL", "e-mail", "social", "SOCIAL"]

campaigns = []

for i in range(30):

    start = fake.date_between("-6m", "today")
    end = fake.date_between("-6m", "today")

    campaigns.append({
        "campaign_id" : fake.uuid4(),
        "campaign_name" : f"Campaign_{i}",
        "channel" : random.choice(channels),
        "start_date" : start.strftime("%Y-%m-%d"),
        "end_date" : end.strftime("%Y-%m-%d")
    })

df_campaigns = spark.createDataFrame(campaigns)
display(df_campaigns.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC #### Escrita na RAW

# COMMAND ----------

BASE_PATH = "/Volumes/main/lakehouse_marketing/raw"

df_campaigns.write\
    .mode("overwrite")\
    .option("header", "true")\
    .csv(f"{BASE_PATH}/campaigns")

# COMMAND ----------

# MAGIC %md
# MAGIC * Validação

# COMMAND ----------

dbutils.fs.ls(f"{BASE_PATH}")
