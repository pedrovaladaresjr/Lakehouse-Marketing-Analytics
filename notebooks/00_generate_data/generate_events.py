# Databricks notebook source
# MAGIC %md
# MAGIC # Generate Events
# MAGIC ---
# MAGIC O objetivo deste notebook é criar a base de eventos dos cliente, os dados intencionalmente serão gerados com inconsistências, que simula **tracking quebrado**.
# MAGIC
# MAGIC
# MAGIC * Problemas intencionais:
# MAGIC   * Usuários inexistente
# MAGIC   * Evento duplicado
# MAGIC   * Timestamp inválido
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC Campos da tabela **campaigns**:
# MAGIC
# MAGIC * **event_id:** *event_id do usuários*
# MAGIC * **user_id:** *Representa o id do usuário*
# MAGIC * **campaign_id:** *id da campanha associada*
# MAGIC * **event_type:** *Tipo de evento ("view", "click")*
# MAGIC * **event_timestamp:** *data do evento*

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

events = []

for _ in range(100_000):

    events.append({
        "event_id" : fake.uuid4(),
        "user_id" : fake.uuid4() if random.random() > 0.1 else None,
        "campaign_id" : fake.uuid4(),
        "event_type" : random.choice(["view", "click", "purchase"]),
        "event_timestamp" : fake.iso8601()
    })

df_events = spark.createDataFrame(events)
display(df_events.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC * Escrita na RAW

# COMMAND ----------

BASE_PATH = "/Volumes/main/lakehouse_marketing/raw"

df_events.write\
    .mode("overwrite")\
    .option("header", "true")\
    .csv(f"{BASE_PATH}/events")

# COMMAND ----------

# MAGIC %md
# MAGIC * Validação

# COMMAND ----------

dbutils.fs.ls("/Volumes/main/lakehouse_marketing/raw")
