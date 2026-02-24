# Padrão de Qualidade de Dados (Data Quality)

| Item | Detalhes |
| :--- | :--- |
| **Projeto** | Lakehouse Marketing Analytics |
| **Camada** | Monitoring (Monitoramento) |


## Objetivo
Definir o framework oficial de Qualidade de Dados (DQ) e as regras de governança para o projeto Lakehouse Marketing.

**A camada de DQ é responsável por:**
* Monitoramento contínuo dos datasets da camada Silver.
* Auditabilidade e rastreabilidade.
* Acompanhamento do histórico de qualidade.
* Suporte a dashboards analíticos e executivos.

---

## Princípios de Arquitetura

### 1️⃣ Separação de Responsabilidades

| Camada | Responsabilidade |
| :--- | :--- |
| **RAW** | Ingestão bruta (sem transformações) |
| **BRONZE** | Metadados técnicos e rastreabilidade |
| **SILVER** | Regras de negócio e limpeza |
| **DQ** | Monitoramento de qualidade e pontuação (scoring) |
| **GOLD** | Consumo analítico |


> **O DQ não substitui a validação da Silver.** O DQ monitora as saídas (outputs) da Silver.

### Esquema de Dados (Schema)
Todos os artefatos de DQ devem ser armazenados em: `main.monitoring`

**Estrutura:**
* `main.monitoring.<entidade>_dq`
* `main.monitoring.<entidade>_dq_metrics`

---

## Framework de Classificação de Regras
Todas as regras de DQ devem ser categorizadas em um dos seguintes tipos:

| Tipo de Regra | Descrição |
| :--- | :--- |
| **COMPLETENESS** | Valores nulos ou ausentes (Completude) |
| **VALIDITY** | Formatos ou valores inválidos (Validade) |
| **UNIQUENESS** | Registros duplicados (Unicidade) |
| **CONSISTENCY** | Consistência lógica entre colunas |
| **REFERENTIAL** | Validação de integridade entre tabelas |

---

## Modelo de Execução
Para cada entidade, o processo de DQ deve gerar um dataset enriquecido com flags e um dataset de métricas agregadas, ambos com o timestamp `dq_execution_date`.

### Datasets de Saída

#### 1. Dataset Enriquecido (`main.monitoring.<entidade>_dq`)
* Colunas originais
* `dq_<nome_da_regra>`: flags (booleano)
* `dq_error_count`: total de erros no registro (inteiro)
* `dq_status`: (VALID / INVALID)
* `dq_execution_date`: (timestamp)

#### 2. Dataset de Métricas (`main.monitoring.<entidade>_dq_metrics`)
| Coluna | Descrição |
| :--- | :--- |
| `execution_date` | Timestamp da execução |
| `total_records` | Total de registros processados |
| `valid_records` | Registros com 0 erros |
| `invalid_records` | Registros com ≥1 erro |
| `error_rate` | Taxa de erro (Inválidos / Total) |
| `rule_name` | Nome da regra avaliada |
| `failed_count` | Quantidade de falhas por regra |

### Definição do Score de Qualidade
O score deve ser calculado por entidade a cada execução:

$$DQ\ Score\ (\%) = \left( \frac{valid\_records}{total\_records} \right) \times 100$$

---

## Regras Específicas por Entidade

### USERS (Usuários)
* **COMPLETENESS:** `user_id`, `email`, `signup_date` (Não nulos).
* **VALIDITY:** `country` (BR, US, UNKNOWN), `email` (Formato válido).
* **UNIQUENESS:** `user_id` deve ser único.

### CAMPAIGNS (Campanhas)
* **COMPLETENESS:** `campaign_id`, `start_date`, `end_date`, `channel` (Não nulos).
* **VALIDITY:** `channel` (Valores aceitos: EMAIL, SOCIAL).
* **CONSISTENCY:** `start_date` $\le$ `end_date`.
* **UNIQUENESS:** `campaign_id` deve ser único.

### EVENTS (Eventos)
* **COMPLETENESS:** `event_id`, `user_id`, `event_timestamp`, `event_type` (Não nulos).
* **VALIDITY:** `event_type` (VIEW, CLICK, PURCHASE).
* **REFERENTIAL:** `user_id` deve existir na tabela `silver.users`.
* **UNIQUENESS:** `event_id` deve ser único.

### CONVERSIONS (Conversões)
* **COMPLETENESS:** `conversion_id`, `user_id`, `campaign_id`, `conversion_timestamp`, `revenue` (Não nulos).
* **VALIDITY:** `revenue` $\ge 0$, `conversion_timestamp` (Timestamp válido).
* **REFERENTIAL:** `user_id` (silver.users), `campaign_id` (silver.campaigns).
* **CONSISTENCY:** `campaign.start_date` $\le$ `conversion_timestamp` $\le$ `campaign.end_date`.
* **UNIQUENESS:** `conversion_id` deve ser único.

---

## Regras de Governança
1.  **Imutabilidade:** O DQ nunca deve deletar registros; apenas classificar e medir.
2.  **Histórico:** Todas as execuções de DQ devem ser armazenadas historicamente.
3.  **Documentação:** Todas as regras devem ser documentadas antes da implementação.
4.  **Integridade:** Validações referenciais devem ser reavaliadas sempre que as entidades relacionadas mudarem.

---

## Roadmap de Evolução
* **Fase 1:** Implementação de regras estáticas (PySpark).
* **Fase 2:** Framework de DQ reutilizável.
* **Fase 3:** Engine de regras baseada em metadados.
* **Fase 4:** Dashboard de monitoramento automático (Camada Gold).

---
**Definição Final:** Qualidade de Dados neste projeto é um framework mensurável, auditável e evolutivo para garantir a confiabilidade analítica em todo o lakehouse.