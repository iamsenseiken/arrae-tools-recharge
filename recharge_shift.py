import pandas as pd
import argparse
import os
import time
import logging
from libraries import utilities

# Setup the important fields
reference_forcetext_cols = ['customer_email', 'product_title', 'product_variant_title']
current_forcetext_cols = ['email', 'line_item_title', 'line_item_variant_title', 'scheduled_at']
current_carry_cols = current_forcetext_cols + ['customer_id']
current_carry_deps = { 'line_item_variant_title': 'line_item_title'}
candidate_keep_cols = ['charge_id', 'next_charge_date']
audit_keep_cols = ['charge_id', 'scheduled_at', 'email', 'customer_id', 'line_item_title', 'line_item_variant_title','address_id']
product_title_col = 'line_item_title'
current_dtypes={'email': str, 'line_item_title': str, 'line_item_variant_title': str, 'scheduled_at': str }
reference_dtypes={'email': str, 'product_title': str, 'product_variant_title': str, 'subscription_status': str}
product_title_col = 'line_item_title'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def match_row(needle, haystack):
    email = needle['email']
    line_item_title = needle['line_item_title']
    line_item_variant_title = needle['line_item_variant_title']

    for _, ref_row in haystack.iterrows():
        ref_email = ref_row['customer_email']
        ref_item_title = ref_row['product_title']
        ref_item_variant_title = ref_row['product_variant_title']

        if (
            ref_email == email and
            ref_item_title == line_item_title and
            ref_item_variant_title == line_item_variant_title
        ):
            return True
    return False

def cross_match(current_df, reference_df):
    filter_results = utilities.cross_match(current_df, reference_df)
    return filter_results

def transform_audit(data):
    transformed_data = utilities.transform_audit(data)
    return transformed_data

def slice_results(data, columns_to_keep):
    sliced_data = utilities.slice_results(data, columns_to_keep)
    return sliced_data

def dedup_results(data):
    deduped_data = utilities.dedup_results(data)
    return deduped_data

def log_hr():
    logging.info("----------------------------------------")

# Main function to perform cross-matching and filtering
def process_reschedule(reference_file, current_file, output_folder, base_name, reschedule_date, product_title):
    total_start_time = time.time()

    have_reference = reference_file is not None
    have_product_title = product_title is not None

    #######################################
    # REFERENCE FILE INGEST
    #######################################
    if have_reference:
        log_hr()
        logging.info("INGEST REFERENCE FILE")
        log_hr()

        logging.info("Encoding detection... ")
        reference_encoding = utilities.detect_encoding(reference_file)
        logging.info(" %s", reference_encoding)

        logging.info("Reading file %s...", reference_file)
        try:
            raw_reference_df = utilities.load_csv_file(reference_file, reference_encoding, reference_dtypes)
        except Exception as e:
            logging.error("Error reading reference file: %s", e)
            exit(1)
        logging.info("- %d records.", len(working_reference_df))

        logging.info("Forcing...")
        working_reference_df = utilities.force_cols_to_text(raw_reference_df, reference_forcetext_cols)
        logging.info("- %d records", len(working_reference_df))
    else:
        working_reference_df = None

    #######################################
    # CURRENT FILE INGEST
    #######################################
    log_hr()
    logging.info("INGEST CURRENT FILE")
    log_hr()
    
    logging.info("Encoding detection... ")
    current_encoding = utilities.detect_encoding(current_file)
    logging.info("- %s", current_encoding)

    logging.info("Reading file %s...", current_file)
    try:
        raw_current_df = utilities.load_csv_file(current_file, current_encoding, current_dtypes)
    except Exception as e:
        logging.error("Error reading current file: %s", e)
        exit(1)
    logging.info("- %d records", len(raw_current_df))
    
    logging.info("Forcing...")
    working_current_df = utilities.force_cols_to_text(raw_current_df, current_forcetext_cols)
    logging.info("- %d records", len(working_current_df))
    
    logging.info("Patching...")    
    patched_current_df = utilities.patch_data(working_current_df, current_carry_cols, current_carry_deps)
    logging.info("- %d records", len(patched_current_df))

    # put a copy in cooked, but save the patched version
    candidates_df = patched_current_df
    rejected_candidates_df = pd.DataFrame(columns=candidates_df.columns)

    #######################################
    # PROCESSING
    #######################################
    log_hr()
    logging.info("PROCESSING")
    log_hr()

    if working_reference_df is not None:
        logging.info("Filtering reference for 'PAUSED' subscriptions...")
        filter_results = utilities.filter_by_column(working_reference_df, 'subscription_status', 'PAUSED')
        filter_hits_reference_df = filter_results['hits']
        filter_misses_reference_df = filter_results['misses']
        logging.info("- hits: %d", len(filter_hits_reference_df))
        logging.info("- misses %d", len(filter_misses_reference_df))
        
    if have_reference:
        logging.info("Cross match...")
        filter_results = cross_match(candidates_df, filter_hits_reference_df)
        filter_hits_reference_df = filter_results['hits']
        filter_misses_reference_df = filter_results['misses']
        logging.info("- hits: %d", len(filter_hits_reference_df))
        logging.info("- misses %d", len(filter_misses_reference_df))
        candidates_df = filter_hits_reference_df

    if have_product_title:
        logging.info("Filtering current for product '%s'...", product_title)
        filter_results = utilities.filter_by_column(candidates_df, product_title_col, product_title)
        filter_hits_current_df = filter_results['hits']
        filter_misses_current_df = filter_results['misses']
        logging.info("- hits: %d", len(filter_hits_current_df))
        logging.info("- misses %d", len(filter_misses_current_df))
        candidates_df = filter_hits_current_df

    logging.info("Trimming passed candidates...")
    rejected_candidates_trimmed_df = utilities.slice_and_dedup(filter_misses_current_df, audit_keep_cols)
    logging.info("- %d records", len(rejected_candidates_trimmed_df))

    logging.info("Trimming rejected candidates...")
    rejected_candidates_trimmed_df = utilities.slice_and_dedup(filter_misses_current_df, audit_keep_cols)
    logging.info("- %d records", len(rejected_candidates_trimmed_df))

    logging.info("Rescheduling candidates...")
    candidates_rescheduled_df = utilities.reschedule_charges(candidates_df, reschedule_date)
    logging.info("- %d records", len(candidates_rescheduled_df))

    logging.info("Sparsing rescheduled candidates...")
    candidates_trimmed_df = utilities.slice_and_dedup(candidates_rescheduled_df, candidate_keep_cols)
    logging.info("- %d records", len(candidates_trimmed_df))

    #######################################
    # OUTPUT
    #######################################
    log_hr()
    logging.info("OUTPUT RESULTS")
    log_hr()
    
    candidates_csv_path = os.path.join(output_folder, f"{base_name}_candidates.csv")
    logging.info("Output path: '%s'", output_folder)
    
    logging.info("Exporting candidates CSV...")
    utilities.output_to_csv(candidates_trimmed_df, os.path.join(output_folder, f"{base_name}_candidates.csv"), current_encoding)
    logging.info("- %d records", len(candidates_trimmed_df))

    workbook_path = os.path.join(output_folder, f"{base_name}_workbook.xlsx")

    logging.info("Exporting trimmed candidates...")
    utilities.write_df_to_excel(candidates_trimmed_df, workbook_path, "Candidates")
    logging.info("- %d records", len(candidates_trimmed_df))

    logging.info("Exporting trimmed rejected candidates...")
    utilities.write_df_to_excel(rejected_candidates_trimmed_df, workbook_path, "Rejected")
    logging.info("- %d records", len(rejected_candidates_trimmed_df))

    logging.info("Exporting raw hits...")
    utilities.write_df_to_excel(filter_hits_current_df, workbook_path, "Hits Raw")
    logging.info("- %d records", len(candidates_rescheduled_df))

    logging.info("Exporting raw rejected candidates...")
    utilities.write_df_to_excel(filter_misses_current_df, workbook_path, "Misses Raw")
    logging.info("- %d records", len(rejected_candidates_df))

    if have_reference:
        logging.info("Exporting reference...")
        utilities.write_df_to_excel(working_reference_df, workbook_path, "Reference")
        logging.info("- %d records", len(working_reference_df))

    logging.info("Exporting current...")
    utilities.write_df_to_excel(working_current_df, workbook_path, "Current Unpatched")
    logging.info("- %d records", len(working_current_df))
    
    logging.info("Exporting patched current...")
    utilities.write_df_to_excel(patched_current_df, workbook_path, "Current Patched")
    logging.info("- %d records", len(patched_current_df))

    total_elapsed_time = time.time() - total_start_time
    logging.info("Total processing time: %.2f seconds.", total_elapsed_time)

# Command-line argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cross-match and filter customer data.')
    parser.add_argument('--reference-file', type=str, required=False, help='Path to the reference CSV file')
    parser.add_argument('--current-file', type=str, required=True, help='Path to the current CSV file')
    parser.add_argument('--output-folder', type=str, required=True, help='Path to the output folder')
    parser.add_argument('--base-name', type=str, required=True, help='Base name for the output files')
    parser.add_argument('--reschedule-date', type=str, required=True, help='The date to reschedule to, in text format')
    parser.add_argument('--product-title', type=str, required=False, help='The product title to filter on')
    args = parser.parse_args()

    process_reschedule(args.reference_file, args.current_file, args.output_folder, args.base_name, args.reschedule_date, args.product_title)
