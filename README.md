

# Recharge Cross-Match Filter

## Overview

The Recharge Cross-Match Filter is a Python script designed to cross-match and filter customer data from two CSV files: a reference file and a current file. The script processes the data, filters it based on specific criteria, and outputs the results to various CSV files.

## Requirements

To run the script, you need to have the following Python packages installed:

- pandas
- chardet
- argparse

You can install the required packages using the following command:


pip install pandas chardet argparse


## Usage

To use the script, run the following command:


python recharge/cross_match_filter.py --reference-file <path_to_reference_file> --current-file <path_to_current_file> --audit-passed-file <path_to_audit_passed_file> --candidate-file <path_to_candidate_file> --candidate-sparse-file <path_to_candidate_sparse_file> --audit-failed-file <path_to_audit_failed_file>


### Command-Line Arguments

- `--reference-file`: Path to the reference CSV file.
- `--current-file`: Path to the current CSV file.
- `--audit-passed-file`: Path to the audit CSV file for passed records.
- `--candidate-file`: Path to the candidate CSV file.
- `--candidate-sparse-file`: Path to the candidate sparse CSV file.
- `--audit-failed-file`: Path to the audit CSV file for failed records.

## Functionality

The script performs the following steps:

1. **Encoding Detection**: Detects the encoding of the reference and current CSV files.
2. **Reading Files**: Reads the reference and current CSV files into pandas DataFrames.
3. **Patching Data**: Cleans and patches the data to ensure consistency.
4. **Filtering Data**: Filters the reference data for paused subscriptions and matches the current data against the reference data.
5. **Slicing Results**: Retains only specific columns in the results.
6. **Transforming Results**: Transforms the results by adding new columns and modifying existing ones.
7. **Deduplicating Results**: Removes consecutive duplicate records from the results.
8. **Outputting Results**: Writes the results to various CSV files.

## Logging

The script uses the `logging` module to log information, warnings, and errors during execution. The log messages provide insights into the processing steps and any issues encountered.

## Example

Here is an example command to run the script:


python recharge/cross_match_filter.py --reference-file data/reference.csv --current-file data/current.csv --audit-passed-file output/audit_passed.csv --candidate-file output/candidate.csv --candidate-sparse-file output/candidate_sparse.csv --audit-failed-file output/audit_failed.csv


This command will process the `reference.csv` and `current.csv` files, and output the results to the specified CSV files in the `output` directory.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Contact

For any questions or inquiries, please contact [your_email@example.com].


