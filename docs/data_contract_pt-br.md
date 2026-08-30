# **CAMADA SILVER - Contrato de Dados & Regras de Transformação**

---

## Objetivo do Documento

Este documento define as **regras canônicas da camada SILVER.**

Ele serve como:

* Contrato de dados (data contract)
* Guia único para implementação em código com tipagens de colunas
* Base de auditoria e manutenção

---

## Princípios da SILVER

* Dados **tipados semanticamente**
* Regras **explícitas e justificáveis**
* Normalização padronizada
* Deduplicação determinística
* Sem agregação

---

## ENTIDADE: USERS

#### Finalidade

Representar usuários únicos, consistentes e confiáveis.

#### Esquema Canônico

|   Campos    |   Tipo    | Obrigatório  |            Regra           |
| :-----------|:--------- |:------------:|:--------------------------:| 
| user_id     | string    |      sim     | Indicador único do usuário |
| email       | string    |      não     |      Lowercase + trim      |
| country     | string    |      não     |  Normalizado para ISO-2    |
| signup_date | date      |      não     | Conversão com fallback null|
| created_at  | timestamp |      sim     |    Base para deduplicação  |
| source_file | string    |      sim     |      Rastreabilidade       |


#### Regras de Transformação

**Tipagem**

* `signup_date` &rarr; `date`
* `created_at` &rarr; `timestamp`

**Normalização**

* Países:
    * BR, BRAZIL, BRA &rarr; **BR**
    * US, USA &rarr; **US**
    * Outros &rarr; **UNKNOWN**

**Validação**

* Remover registros com `user_id` nulo

**Deduplicação**

* **Regra:** Manter o registro mais recente por `user_id`
* **Critério:** Maior `created_at` 

---

## ENTIDADE: CAMPAIGNS

#### Finalidade

Representar campanhas válidas no tempo e canal.

#### Esquema Canônico

|    Campo      |   Tipo    |  Obrigatório |            Regra           |
| :-------------|:--------- |:------------:|:--------------------------:| 
| campaign_id   | string    |      sim     |      Identificador         |
| campaign_name | string    |      não     |            Trim            |
| channel       | string    |      sim     |         Normalizado        |
| start_date    | date      |      sim     |        <= end_date         |
| end_date      | date      |      sim     |        >= start_date       |
| source_file   | string    |      sim     |       Rastreabilidade      |


#### Regras de Transformação

**Tipagem**

* `start_date`, `end_date` &rarr; **`date`**

**Normalização**

* Canais:
    * e-mail &rarr; **`EMAIL`**
    * social &rarr; **`SOCIAL`**
    * others &rarr; **`OTHER`**

**Validação**

* Remover campanhas com `start_date > end_date`
* Remover `campaign_id` nulos

**Deduplicação**

* **Regra:** Manter o registro mais recente por `campaign_id`
* **Critério:** Maior `ingestion_timestamp`

---

## ENTIDADE: EVENTS

#### Finalidade

Eventos comportamentais de usuários.

#### Esquema Canônico

|    Fields           |   Type    |   Required   |            Rule            |
| :-------------------|:--------- |:------------:|:--------------------------:| 
| event_id            | string    |      yes     |   Unique events identifier |
| user_id             | string    |      yes     |            should exist    |
| campaign_id         | string    |    optional  |            should exist    |
| event_type          | string    |      yes     |        Enum controlled     |
| event_timestamp     | timestamp |      yes     |        valid Timestamp     |
| source_file         | string    |      yes     |         Traceability       |
| ingestion_timestamp | timestamp |      yes     |         valid Timestamp    |

#### Regras de Transformação

**Tipagem**

* `event_timestamp` &rarr; **`timestamp`**

**Normalização**

* Tipos de `event_type` permitidos (Upper + Trim):
    * **VIEW**
    * **CLICK**
    * **PURCHASE**

**Validação**

* Remover eventos sem `user_id`
* Remover eventos fora do enum

**Deduplicação**

* Não aplicável (evento é atômico)

---

## ENTIDADE: CONVERSIONS

#### Finalidade

Conversões financeiras aplicadas de usuários.

#### Esquema Canônico

|    Campos     |   Tipo    |   Obrigatório|            Regra           |
| :-------------|:--------- |:------------:|:--------------------------:| 
| conversion_id | string    |      sim     |        Identificador       |
| user_id       | string    |      sim     |        Deve existir        |
| revenue       | decimal(10,2)|   sim     |            >= 0            |
|conversion_date| date      |      sim     |        Data válida         |
| source_file   | string    |      sim     |       Rastreabilidade      |

#### Regras de Transformação

**Tipagem**

* `conversion_date` &rarr; **`date`**
* `revenue` &rarr; **`decimal(10, 2)`**

**Validação**

* Remover `revenue < 0`
* Remover `user_id` nulos

**Deduplicação**

* **Regra:** Manter o registro mais recente por `conversion_id`

---

## GOVERNANÇA

* Qualquer alteração nestes documentos requer:

    * Commit separado
    * Ajuste correspondente no código