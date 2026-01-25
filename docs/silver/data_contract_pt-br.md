# **SILVER LAYER - Contrato de Dados & Regras de Transformações**

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

* **Regra:** manter o registro mais recente por user_id
* **Critério:** maior `created_at` 

---

## ENTIDADE: CAMPAIGNS

...