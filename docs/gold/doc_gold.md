# Modelagem da Camada Gold 

## Visão Geral do Projeto

A camada gold representa a camada orientada a negócios do Projeto Lakehouse Marketing.

Seu objetivo é fornecer conjuntos de dados dimensionais selecionados e otimizados para:

- Inteligência de Negócio (BI)
- Dashboarding
- Monitoramento de KPI
- Self-Service Analítica
- Análise Ad-hoc SQL

A camada gold segue a abordagem da modelagem dimensional metodológica Star Schema.

---

# Objetivos de Negócios

A camada gold deve permitir que as partes interessadas respondam a perguntas estratégicas de negócios sobre:

## Aquisição de Usuários

- Quantos novos usuários captamos ao longo do tempo?
- Quais países geram mais usuários?
- Como se dá o crescimento mensal dos usuários?

## Performance de Campanhas

- Quais campanhas geram mais conversões?
- Quais campanhas obtivemos maior receita?
- Quais canais performam melhor?

## Engajamento dos Usuários

- Quantas visualizações, cliques, e compras são geradas?
- Como os usuários estão interagindo com as campanhas?

## Funil de Marketing

- Quantos VISUALIZAÇÕES se tornam eventos de CLICK?
- Quantos CLIQUES se tornam em uma COMPRA?
- Qual é a taxa de conversão do funil?

## Análse de Receita

- Receita por campanhas
- Receita por canal
- Receita por país
- Tendência da Receita ao longo do tempo

---

# Gold Architecture

A Camada Gold está organizada usando o Schema Estrela (Star Schema).

#### `Tabelas Dimensão`

###### dim_user

-  *Entidade de Negócios representando usuários.*

    - **Granularidade:** 1 linhas = 1 usuários
    - **Fonte:** silver_marketing.users
    - **Atributos:**

        |   Colunas   |
        |-------------|
        | user_sk     |
        | user_id     |
        | country     |
        | signup_date |


###### dim_campaign

- *Representa as campanhas de Marketing*

    - **Granularidade:** 1 linhas = 1 campanha
    - **Fonte:** silver_marketing.campaigns
    - **Atributos:**

        |   Colunas     |
        |---------------|
        | campaign_sk   |
        | campaign_id   |
        | campaign_name |
        | channel       |
        | start_date    |
        | end_date      |



###### dim_date

- *Calendários dimensional usado para análise temporal*

    - **Granularidade:** 1 linhas = 1 dia 
    - **Gerado Internamente**
    - **Atributos:**

        |   Colunas    |
        |------------  |
        | date_sk      |
        | date         |
        | year         |
        | quarter      |
        | month        |
        | month_name   |
        | week_of_year |
        | weekday      |

---

#### `Tabelas Fato`

###### fact_events

- *Armazena eventos comportamentais do usuário.*

    - **Granularidade:** 1 linhas = 1 evento 
    - **Fonte:** silver_marketing.events
    - **Chaves Estrangeiras:**

        | Colunas      |
        |--------------|
        | user_sk      |
        | campaign_sk  |
        | date_sk      |

    - **Medidas**

        | Medidas  | Descrição        |
        |----------|------------------|
        | contagem eventos | sempre 1 |

    - **Ojetivo de Negócio**

        Permite análise de engajamento e funil de marketing.


###### fact_conversions

- Armazena os eventos de conversão.

    - **Granularidade:** 1 linha = 1 conversão
    - **Origem:** silver_marketing.conversions
    - **Chaves Estrangeiras:**

        | Coluna |
        |---------|
        | user_sk |
        | campaign_sk |
        | date_sk |

    - **Medidas:**

        | Métrica  | Descrição |
        |----------|----------|
        | revenue  | Valor da conversão |
        | conversion_count | Sempre igual a 1 |

    - **Objetivo de Negócio:**

        Permitir análises de receita e conversão.

---

# Diagrama Star Schema


                                                dim_user
                                                    |
                                                    |
                                                    |
                                                    |
                            dim_date ------ fact_events ------ dim_campaign

                            dim_date --- fact_conversions --- dim_campaign
                                                    |
                                                    |
                                                dim_user

---

# Indicadores de Negócio (KPIs)

Os seguintes KPIs poderão ser calculados a partir da camada Gold.

## Aquisição

- Novos Usuários
- Usuários por País
- Crescimento Mensal de Usuários

## Engajamento

- Total de Visualizações (VIEW)
- Total de Cliques (CLICK)
- Total de Compras (PURCHASE)

## Conversão

- Quantidade de Conversões
- Taxa de Conversão
- Taxa de Conversão por Campanha

## Receita

- Receita Total
- Receita por Campanha
- Receita por Canal
- Receita por País

---

# Estrutura Física Planejada

Catalog:

- main

Schemas:

- silver_marketing
- governance_marketing
- gold_marketing

Tabelas previstas na camada Gold:

- dim_user
- dim_campaign
- dim_date
- fact_events
- fact_conversions

---

# Evoluções Futuras

Possíveis melhorias futuras para o projeto:

- Slowly Changing Dimensions (SCD Type 2)
- Attribution Modeling
- Customer Lifetime Value (CLV)
- Cohort Analysis
- Tabela agregada de performance de campanhas
- Integração de indicadores de Data Quality na camada Gold
- Dashboard executivo de governança de dados