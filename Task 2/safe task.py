import pandas as pd
import os
import matplotlib.pyplot as plt


# ==============================
# Setup
# ==============================

os.makedirs('output', exist_ok=True)

# Reading the input csv
input_csv='contract_events.csv'
df_raw = pd.read_csv(input_csv)

# Quick normalization
df_raw['block_timestamp']=pd.to_datetime(df_raw['block_timestamp'])
df_raw['event_id'] = df_raw['event_id'].astype(str)
df_raw['previous_event_id'] = df_raw['previous_event_id'].astype(str).replace({'nan': None})

# Keep only events that are final and part of the canonical chain
df = df_raw[df_raw.status == 'Confirmed'].copy()

# ==============================
# Task 1: Orphan Event Detection
# ==============================

def task1_solution(df): 
    # Task 1 solution log
    print('\nTask 1 Answer: Orphan Event Detection') 
    cols = ['event_id','previous_event_id','contract_address','event_type','block_number']

    # previous_event_id not empty
    df_prev_present = df[df['previous_event_id'].notna()]
    # previous_event_id not present in existing event_id
    orphan = df_prev_present[~df_prev_present['previous_event_id'].isin(df['event_id'])]
    orphan_result = orphan[cols]
    print('Orphan Events: ',len(orphan_result))
    orphan_result.to_csv('output/task1_result.csv', index=False)

# ==============================
# Task 2: Time Delta Per Contract
# ==============================

def task2_solution(df):
    # Task 2 solution log
    print('\nTask 2 Answer: Time Delta Per Contract') 
    cols = ['event_id','contract_address','event_type','block_timestamp','seconds_since_last_event']

    df = df.sort_values(['contract_address', 'block_timestamp'])
    df['seconds_since_last_event'] = df.groupby('contract_address')['block_timestamp'].diff().dt.total_seconds()
    time_delta = df[df['seconds_since_last_event'].notna()]
    time_delta_results = time_delta[cols]
    print('Total Events: ',len(time_delta_results))
    time_delta_results.to_csv('output/task2_time_delta_result.csv', index=False)

    # Averge time delta per contract
    average_result = (
    df.groupby('contract_address')
      .agg(
          event_count=('event_id', 'count'),
          avg_seconds_between_events=('seconds_since_last_event', 'mean'),
          median_seconds_between_events=('seconds_since_last_event', 'median'))
      .reset_index()
    )
    print(average_result)
    average_result.to_csv('output/task2_contracts_average_time_delta.csv', index=False)

# ==============================
# Task 3: Sender Activity Mapping
# ==============================

def task3_solution(df):
    # Task 3 solution log
    print('\nTask 3 Answer: Sender Mapping') 
    
    block_counts = df.groupby('block_number').size().reset_index(name='event_count')
    print('Highest # of Events In a Block? :', block_counts['event_count'].max()) # =1
    # Each block contains only one event, so block-level sender mapping is not meaningful
    # Instead, analyze sender activity at the contract level

    activity = df.groupby(['sender', 'contract_address']).size().reset_index(name='event_count')
    activity['rank_in_sender_activity'] = activity.groupby('contract_address')['event_count'].rank(method='dense', ascending=False)
    activity = activity.sort_values(['contract_address', 'rank_in_sender_activity'],ascending=[True, True])
    print(activity)
    activity.to_csv('output/task3_sender_mapping_in_contracts.csv', index=False)


# ==============================
# Bonus 1: Data Quality Checks
# ==============================

def bonus1(df, df_raw):
    # Bonus 1 solution log
    print('\nBonus 1: Data Quality and Inconsistencies') 

    #1. tx_hash 
    tx_hash = df.groupby(['tx_hash']).size().reset_index(name='tx_count')
    tx_hash.to_csv('output/bonus1_tx_hash_reuse.csv', index=False)
    print('Average Useage Count of tx_hash: ', round(tx_hash['tx_count'].mean(),2))

    #2. previous_event_id belongs to non-confirmed event
    cols = ['event_id','previous_event_id','contract_address','event_type','block_number']
    
    # previous_event_id not empty
    df_prev_present = df[df['previous_event_id'].notna()]
    # previous_event_id not present in existing event_id
    df_not_confirmed = df_raw[df_raw.status != 'Confirmed']
    orphan_unconfirmed = df_prev_present[~df_prev_present['previous_event_id'].isin(df['event_id']) & df_prev_present['previous_event_id'].isin(df_not_confirmed['event_id'])]
    orphan_unconfirmed_result = orphan_unconfirmed[cols]
    print('Events With Unconfirmed Previous Events: ',len(orphan_unconfirmed_result))
    orphan_unconfirmed_result.to_csv('output/bonus1_previous_event_unconfirmed.csv', index=False)

# ==============================
# Bonus 2: Suspicious / Bot-like Behavior
# ==============================

def bonus2(df_raw):
    # Bonus 2 solution log
    print('\nBonus 2: Possible Bot-like Behavior') 
    df_raw = df_raw.sort_values('block_timestamp')
    df_raw['seconds_since_last_block'] = df_raw['block_timestamp'].diff().dt.total_seconds()
    df_result = df_raw.groupby('seconds_since_last_block').size().reset_index(name='count')
    print('Time Difference Between Blocks: \n',df_result)

# ==============================
# Bonus 3: Visualization
# ==============================

def plot_simple_chart(x,y,xlabel,ylabel,title,file_name):
    plt.figure()
    plt.bar(x, y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig('output/'+file_name, bbox_inches='tight')
    plt.close()

def plot_bar_chart(pivot,xlabel,ylabel,title,legend_title,legend_loc,file_name):
    pivot.plot(kind='bar')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(title=legend_title, loc=legend_loc)
    plt.savefig('output/'+file_name, bbox_inches='tight')
    plt.close()

def bonus3(df, df_raw):
    # Bonus 3 solution log
    print('\nBonus 3: Visualize Interesting Patterns') 

    # Events type frequency chart (Confirmed events)
    df_result = df.groupby('event_type').size().reset_index(name='event_count').sort_values('event_count', ascending=False)
    plot_simple_chart(df_result['event_type'], df_result['event_count'],'Event Type','Event Count','Event Count by Type','1.event_type_counts.png')

    # Contracts event frequency chart (Confirmed events)
    df_result = df.groupby('contract_address').size().reset_index(name='event_count').sort_values('event_count', ascending=False)
    plot_simple_chart(df_result['contract_address'], df_result['event_count'],'Contract Name','Event Count','Event Count by Contract','2.contracts_event_counts.png')

    # Contracts event frequency by status chart
    df_result = df_raw.groupby(['contract_address','status']).size().reset_index(name='event_count').sort_values('event_count', ascending=False)
    pivot = df_result.pivot(
        index='contract_address',
        columns='status',
        values='event_count'
    )
    plot_bar_chart(pivot,'Contract Address','Event Count','Event Count by Contract and Status','Status','lower center','3.contract_status_counts.png')

    # Contracts event frequency by sender chart (Confirmed events)
    df_result = df.groupby(['contract_address','sender']).size().reset_index(name='event_count').sort_values('event_count', ascending=False)
    pivot = df_result.pivot(
        index='contract_address',
        columns='sender',
        values='event_count'
    )
    plot_bar_chart(pivot,'Contract Address','Event Count','Event Count by Contract and Sender','Sender','lower center','4.contract_sender_counts.png')



# ==============================
# Main Execution
# ==============================

def main():
    task1_solution(df)
    task2_solution(df)
    task3_solution(df)
    bonus1(df, df_raw)
    bonus2(df_raw)
    bonus3(df, df_raw)

if __name__ == "__main__":
    main()
