# **SILVER LAYER - Data Contract & Transformation Rules**

---

## Document Purpose

This document defines the **canonical rules for the SILVER layer.**

It serves as:

* Data contract
* Single implementation guide for code with column typing
* Basis for auditing and maintenance

---

## SILVER Principles

* **Semantically typed** data
* **Explicit and justifiable** rules
* Standardized normalization
* Deterministic deduplication
* No aggregation

---

## ENTITY: USERS

#### Purpose

To represent unique, consistent, and reliable users.

#### Canonical Schema

|   Fields    |   Type    | Required  |            Rule            |
| :-----------|:--------- |:------------:|:--------------------------:| 
| user_id     | string    |      yes     |    Unique user identifier  |
| email       | string    |      no      |      Lowercase + trim      |
| country     | string    |      no      |   Normalized to ISO-2      |
| signup_date | date      |      no      | Conversion with null fallback |
| created_at  | timestamp |      yes     |   Basis for deduplication  |
| source_file | string    |      yes     |       Traceability         |


#### Transformation Rules

**Typing**

* `signup_date` &rarr; `date`
* `created_at` &rarr; `timestamp`

**Normalization**

* Countries:
    * BR, BRAZIL, BRA &rarr; **BR**
    * US, USA &rarr; **US**
    * Others &rarr; **UNKNOWN**

**Validation**

* Remove records with null `user_id`

**Deduplication**

* **Rule:** keep the most recent record per user_id
* **Criterion:** highest `created_at`

---

## ENTITY: CAMPAIGNS

...