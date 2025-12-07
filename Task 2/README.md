# Task 2 Answer: Python Data Wrangling Challenge

#### This document explains my approach, design decisions, and implementation details for the Wrangle-Me data engineering challenge.
---

## 📁 Project Structure
```
.
├── contract_events.csv
├── requirements.txt
├── safe task.py
└── output/
    ├── task1_result.csv
    ├── task2_time_delta_result.csv
    ├── task2_contracts_average_time_delta.csv
    ├── task3_sender_mapping_in_contracts.csv
    ├── bonus1_tx_hash_reuse.csv
    ├── bonus1_previous_event_unconfirmed.csv
    └── *.png (visualizations)
```
## ⚙️ How to Run

__Prerequisites__:
- Python 3.x
- Pandas (Data manipulation)
- Matplotlib (Visualization)

__Installation__:
```
pip install -r requirements.txt
```
__Running the Script__:

Ensure _contract_events.csv_ is in the root directory and run:
```
python safe task.py
```
This will generate all results inside the output/ folder.

## ✅ Assumptions
- Only events with `status == "Confirmed"` are treated as canonical chain data and used for task 1 to 3 analysis. We used `Pending` and `Reorged` events for certain parts of bonus analysis.
- The results presented here are based on the analyzed dataset available at [this link](https://github.com/safehjc/wrangle-me/blob/main/contract_events.csv).

---
# 🧠 Task 1 – Orphan Event Detection

__Goal__:
Finding events where _previous_event_id_ references a non-existent event.

__Approach__:
To identify Orphan events, we examined confirmed events where the _previous_event_id_ field contains a valid value and does not exist in the _event_id_ list.

__Output__:
There are 1822 Orphan events in the dataset, and all of them are accessible [here](./output/task1_result.csv).

| event_id | previous_event_id | contract_address | event_type | block_number |
|----------|----------|-----------|----------|-----------|
|evt_00029	| evt_00026	| 0xOmega	| Glint	| 1036 |
|evt_00061	| evt_00039	| 0xBeta	| Zync	| 1076 |
|evt_00068	| evt_00019	| 0xAlpha	| Withdr-O	| 1085 |
|evt_00073	| evt_00072	| 0xOmega	| Zync	| 1091 |
|...	| ...	| ...	| ...	| ... |

# ⏱️ Task 2 – Time Delta Per Contract

__Goal__:
Calculating the time differences between consecutive events per contract.

__Approach__:
To calculate the time differences between consecutive events for each contract, we sorted each contract’s events separately by time and measured the time difference between each consecutive event.

__Output__:
These are 6628 confirmed events, and all of them are accessible by their time delta [here](./output/task2_time_delta_result.csv). The [table below](./output/task2_contracts_average_time_delta.csv) shows the average and median time delta between consecutive events for each contract, along with their total number of events.

| contract_address | event_count | avg_seconds_between_events | median_seconds_between_events |
|----------|----------|-----------|----------|
|0xAlpha|	1356|	221.3579335793358|	165.0|
|0xBeta|	1345|	223.15848214285714|	150.0|
|0xDelta|	1328|	225.55388093443858|	150.0|
|0xGamma|	1276|	234.75294117647059|	165.0|
|0xOmega|	1328|	225.85908063300678|	165.0|

# 🧑‍💻 Task 3 – Sender Mapping

__Goal__:
Understand sender activity per block and contract.

__Approach__:
In this task’s dataset, each block contains only one event, making it irrelevant to determine the block with the most events emitted by senders. Since each block has only one event emitted by one sender, we focused on analyzing contracts and ranking their senders based on the frequency of events they emitted.

__Output__:
There are five contracts and six senders in the dataset. We can see the ranking of each sender on each contract in terms of emitted events in the file [here](./output/task3_sender_mapping_in_contracts.csv).

|sender|contract_address|event_count|rank_in_sender_activity|
|----------|----------|-----------|----------|
|0xAlice|0xAlpha|290|1.0|
|0xDave |0xAlpha|280|2.0|
|0xCarol|0xAlpha|275|3.0|
|0xBob|0xAlpha|257|4.0|
|0xEve|0xAlpha|254|5.0|
|...	| ...	| ...	| ...	|

---
## 🧪 Bonus 1 – Data Quality & Inconsistencies
### 1.Reused tx_hash
In standard blockchain systems, a `tx_hash` is expected to uniquely identify a transaction. However, in this dataset, the same `tx_hash` appears across multiple blocks, at different timestamps, and even under different block statuses. This behavior breaks the uniqueness assumption and reduces the reliability of `tx_hash` as an identifier, indicating a clear data quality issue in the dataset.

A detailed view of the duplicated `tx_hash` usage in confirmed events is available [here](./output/bonus1_tx_hash_reuse.csv).

### 2. References to Unconfirmed Events
Similar to the orphan event detection task, the focus here was to identify confirmed events whose `previous_event_id` references an event that exists only in `Pending` or `Reorged` status. 

A total of 1,690 events were found to reference unconfirmed previous events. You can view the complete list of these cases [here](./output/bonus1_previous_event_unconfirmed.csv).

## 🤖 Bonus 2 – Bot-like Behavior Analysis
In this step, we investigated suspicious temporal patterns that could indicate automated behavior. As a simple example, we analyzed the time difference between consecutive blocks. The results showed that, with the exception of 9 blocks, all other 19,993 blocks — independent of their status — had an exact 15-second time gap from both the preceding and following blocks.

|seconds_since_last_block|count|
|----------|----------|
|0|6|
|15 |19993|
|30 |3|

This pattern may indicate automatically generated blocks or synthetic block data, as the time intervals between blocks appear to be artificially consistent.

## 📊 Bonus 3 – Visualizations
In this section, we visualized several interesting patterns observed in the dataset.

1. Event Types Confirmed Event Frequency:
<figure>
  <img src="./output/1.event_type_counts.png" alt="My Image Title" width="500">
</figure>

2. Contracts Confirmed Events Frequency:
<figure>
  <img src="./output/2.contracts_event_counts.png" alt="My Image Title" width="500">
</figure>

3. Contracts Events Frequency By Status:
<figure>
  <img src="./output/3.contract_status_counts.png" alt="My Image Title" width="500">
</figure>

4. Contracts Confirmed Events Frequency By Senders:
<figure>
  <img src="./output/4.contract_sender_counts.png" alt="My Image Title" width="500">
</figure>
