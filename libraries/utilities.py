import pandas as pd
import os
import chardet
import logging
from openpyxl import load_workbook, Workbook

# Function to detect file encoding
def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        return result['encoding']

# Function to read the current file
def load_csv_file(current_file_path, encoding, dtypes=None):
    if os.path.exists(current_file_path):
        current_df = pd.read_csv(current_file_path, encoding=encoding, low_memory=False, dtype=dtypes)
        return current_df
    else:
        logging.error("Error: The file %s does not exist.", current_file_path)
        raise FileNotFoundError(f"The file {current_file_path} does not exist.")

# Function to clean data
def force_cols_to_text(data, cols_list):
    data = data.copy()

    # Ensure the specified columns are treated as text fields    
    for column in cols_list :
        data[column] = data[column].astype(str).replace('nan', '')
        logging.info("Forcing astype string on %s.", column)
    
    for i in range(1, len(data)):
        for column in cols_list :
            if pd.isna(data.at[i, column]):
                data.at[i, column] = ''
            else:
                data.at[i, column] = data.at[i, column].strip()

    return data

# Function to patch the current data
def patch_data(data, carry_cols, carry_deps):
    data = data.copy()
    
    for i in range(1, len(data)):
        deps_hit = {}
        if data.at[i, 'multiple_rows'] == True:
            for column in carry_cols :
                if pd.isna(data.at[i, column]) or data.at[i, column] == '':
                    deps_hit[column] = True
                    if column in carry_deps:
                        if carry_deps[column] in deps_hit:
                            data.at[i, column] = data.at[i-1, column]
                    else:
                            data.at[i, column] = data.at[i-1, column]

    return data

# Funnction to slice and de-duplicate in one operation
def slice_and_dedup(data, columns_to_keep):
    working = data.copy()
    working = slice_results(working, columns_to_keep)
    working = dedup_results(working)    
    return working

# Function to slice the results to retain only specific columns
def slice_results(data, columns_to_keep):
    working = data.copy()
    return working[columns_to_keep]

# Function to kill consecutive duplicates
def dedup_results(data):
    working = data.copy()
    consecutive_duplicates = working.duplicated(keep='first')
    df_unique = working[~consecutive_duplicates]
    return df_unique

# Function to output the results to a CSV file
def output_to_csv(data, output_file_path, encoding):
    data.to_csv(output_file_path, index=False, encoding=encoding)
    logging.info("Results have been written to %s", output_file_path)
    
# Function to filter the reference file for paused subscriptions
def filter_by_column(haystack_df, filter_column, filter_value, exact_match=True, case_sensitive=True):
    if not case_sensitive:
        haystack_df[filter_column] = haystack_df[filter_column].str.lower()
        filter_value = filter_value.lower()

    if exact_match:
        mask = haystack_df[filter_column] == filter_value
    else:
        mask = haystack_df[filter_column].str.contains(filter_value, na=False)

    hits_df = haystack_df[mask]
    misses_df = haystack_df[~mask]

    return {
        'hits': hits_df,
        'misses': misses_df
    }

# Enhanced reschedule_charges function
def reschedule_charges(data, reschedule_date):
    data = data.copy()
    data['scheduled_at'] = pd.to_datetime(data['scheduled_at'])
    data['next_charge_date'] = pd.Timestamp(reschedule_date)
    return data

import os

def write_df_to_excel(df, file_path, sheet_name):
    file_exists = os.path.exists(file_path)
    
    if file_exists:
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    logging.info("DataFrame has been written to %s in sheet %s", file_path, sheet_name)