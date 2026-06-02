# Databricks notebook source
# MAGIC %md
# MAGIC # Generate Users
# MAGIC ---
# MAGIC O objetivo deste notebook é criar a base de usuários, usaremos a biblioteca `Faker` para simular os dados.
# MAGIC
# MAGIC Definimos também a `seed = 42`, a fim de obtermos a mesma reprodutibilidade na geração dos dados.
# MAGIC
# MAGIC Campos da tabela **users**:
# MAGIC
# MAGIC * **user_id:** *Representa o id do usuário*
# MAGIC * **email:** *Email do usuários*
# MAGIC * **country:** *País associado ao usuário*
# MAGIC * **signup_date:** *data de cadastro*
# MAGIC * **created_at:** *data de criação*

# COMMAND ----------

# MAGIC %pip install faker

# COMMAND ----------

from faker import Faker
import random 

# COMMAND ----------

# MAGIC %md
# MAGIC #### Geração dos Dados

# COMMAND ----------

# Setup
random.seed(42)
fake = Faker()
fake.seed_instance(42)

# Geração de dados (com erro proposital)
users = []

for _ in range(5000):

    users.append({
        "user_id" : fake.uuid4() if random.random() > 0.05 else None,
        "email" : fake.email(),
        "country" : random.choice(["BR", "br", "Brazil", "US", "usa", None]),
        "signup_date" : fake.date_between("-2y", "today").strftime("%Y-%m-%d"),
        "created_at" : fake.iso8601()
    })

df_users = spark.createDataFrame(users)
display(df_users.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC #### Escrita na RAW 
# MAGIC
# MAGIC * Criação dos Volumes

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE CATALOG IF NOT EXISTS main;
# MAGIC CREATE SCHEMA IF NOT EXISTS main.lakehouse_marketing;
# MAGIC
# MAGIC CREATE VOLUME IF NOT EXISTS main.lakehouse_marketing.raw;

# COMMAND ----------

# MAGIC %md
# MAGIC * Escrita na RAW

# COMMAND ----------

BASE_PATH = "/Volumes/main/lakehouse_marketing/raw"

df_users.write\
    .mode("overwrite")\
    .option("header", "true")\
    .csv(f"{BASE_PATH}/users")

# COMMAND ----------

# MAGIC %md
# MAGIC * Validação

# COMMAND ----------


dbutils.fs.ls("/Volumes/main/lakehouse_marketing/raw")
