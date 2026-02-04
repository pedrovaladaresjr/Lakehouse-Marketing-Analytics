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

|   Fields    |   Type    |   Required   |            Rule            |
| :-----------|:--------- |:------------:|:--------------------------:| 
| user_id     | string    |      yes     |    Unique user identifier  |
| email       | string    |      no      |      Lowercase + trim      |
| country     | string    |      no      |   Normalized to ISO-2      |
| signup_date | date      |      no      | Conversion with null fallback |
| created_at  | timestamp |      yes     |   Basis for deduplication  |
| source_file | string    |      yes     |       Traceability         |


#### Transformation Rules

**Typing**

* `signup_date` &rarr; **`date`**
* `created_at` &rarr; **`timestamp`**

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

Represent the valid campaigns in time and channel

#### Canonical Schema

|    Fields     |   Type    |   Required   |            Rule            |
| :-------------|:--------- |:------------:|:--------------------------:| 
| campaign_id   | string    |      yes     | Unique campaigns identifier|
| campaign_name | string    |      no      |            Trim            |
| channel       | string    |      yes     |         Normalized         |
| start_date    | date      |      yes     |        <= end_date         |
| end_date      | date      |      yes     |        >= start_date       |
| source_file   | string    |      yes     |       Traceability         |


#### Transformation Rules

**Typing**

* `start_date`, `end_date` &rarr; **`date`**

**Normalization**

* Channels:

    * e-mail &rarr; **`EMAIL`**
    * social &rarr; **`SOCIAL`**
    * others &rarr; **`OTHER`**

**Validation**

* Remove campaigns with `start_date > end_date`
* Remove nulls `campaign_id`

**Deduplication**

* Role: keep the most recent register per `campaing_id`
* Criterion: higher `ingestion_timestamp`


---

## ENTITY: EVENTS

Behavioral events of users.


#### Canonical Schema

|    Fields     |   Type    |   Required   |            Rule            |
| :-------------|:--------- |:------------:|:--------------------------:| 
| event_id      | string    |      yes     |   Unique events identifier |
| user_id       | string    |      yes     |            should exist    |
| event_type    | string    |      yes     |        Enum controlled     |
|event_timestamp| timestamp |      yes     |        valid Timestamp     |
| source_file   | string    |      yes     |         Traceability       |



#### Transformation Rules

**Typing**

* `event_timestamp` &rarr; **`timestamp`**

**Normalization**

* `event_type` allowed:

    * **VIEW**
    * **CLICK**
    * **PURCHASE**

**Validation**

* Remove events without `user_id`
* Remove events outside of enum

**Deduplication**

* Not applicable (event is atomic)


---

## ENTITY: CONVERSIONS

### Purpose

Financial conversion applied of users

#### Canonical Schema

|    Fields     |   Type    |   Required   |            Rule            |
| :-------------|:--------- |:------------:|:--------------------------:| 
| conversion_id | string    |      yes     |            Identifier      |
| user_id       | string    |      yes     |            should exist    |
| revenue       | decimal(10,2)|   yes     |              >= 0          |
|conversion_date| date      |      yes     |        valid date          |
| source_file   | string    |      yes     |         Traceability       |



#### Transformation Rules


**Typing**

* `conversion_date` &rarr; **`date`**
* `revenue` &rarr; **`decimal(10, 2)`**


**Validation**

* Remove `revenue < 0`
* Remove nulls `user_id`

**Deduplication**

* Rule: Keep the most recent register per `conversion_id`


---

## GOVERNANCE

* Any amendment in this documents require:

    * Separeted commit
    * Corresponding adjustment in the code
    
