Here is the content, with backticks replaced by '`', in a code block:

```markdown
# Recharge Shift Tool

## Overview

**Recharge Shift** is a Python script designed to process and reschedule customer subscription data. It cross-matches data from reference and current CSV files, applies filters, and reschedules charges based on specified criteria.

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Command-Line Arguments](#command-line-arguments)
- [Functionality](#functionality)
- [Output](#output)
- [Example](#example)
- [Logging](#logging)
- [License](#license)
- [Contributing](#contributing)

## Requirements

To run the script, ensure you have **Python 3.x** installed along with the following packages:

- `pandas`
- `openpyxl`

## Installation

Install the required Python packages using `pip`:

`bash
pip install pandas openpyxl
`

## Usage

Run the script using the following command:

`bash
python recharge_shift.py \
  --reference-file <path_to_reference_file> \
  --current-file <path_to_current_file> \
  --output-folder <path_to_output_folder> \
  --base-name <output_base_name> \
  --reschedule-date <new_date> \
  [--product-title <product_title>]
`

## Command-Line Arguments

- `--reference-file`: *(Optional)* Path to the reference CSV file containing subscription data.
- `--current-file`: *(Required)* Path to the current CSV file with charge data to be processed.
- `--output-folder`: *(Required)* Path to the folder where output files will be saved.
- `--base-name`: *(Required)* Base name for the output files.
- `--reschedule-date`: *(Required)* The date to reschedule charges to, in `YYYY-MM-DD` format (e.g., `"2023-05-01"`).
- `--product-title`: *(Optional)* The product title to filter on.

## Functionality

The script performs the following steps:

1. **Data Loading**:
   - Reads and processes the reference file (if provided).
   - Reads the current file.

2. **Filtering**:
   - Applies filters based on subscription status.
   - Filters by product title if specified.

3. **Rescheduling**:
   - Reschedules charges for matching records to the specified date.

4. **Output Generation**:
   - Generates output files including:
     - A CSV file with rescheduled candidates.
     - An Excel workbook with multiple sheets containing detailed information.

## Output

The script generates the following output files in the specified output folder:

1. `<base_name>_candidates.csv`:  
   CSV file containing the rescheduled candidates.

2. `<base_name>_workbook.xlsx`:  
   Excel workbook with multiple sheets:
   
   - **Candidates**: Trimmed list of rescheduled candidates.
   - **Rejected**: Trimmed list of rejected candidates.
   - **Hits Raw**: Raw data of matching records.
   - **Misses Raw**: Raw data of non-matching records.
   - **Reference**: Reference data (if provided).
   - **Current Unpatched**: Original current data.
   - **Current Patched**: Processed current data.

## Example

Here's an example command to run the script:

`bash
python recharge_shift.py \
  --reference-file data/reference.csv \
  --current-file data/current.csv \
  --output-folder output \
  --base-name may_reschedule \
  --reschedule-date 2023-05-15 \
  --product-title "Monthly Box"
`

**Description**:  
This command processes the `reference.csv` and `current.csv` files, reschedules charges for the "Monthly Box" product to May 15, 2023, and outputs the results to the `output` folder with the base name `may_reschedule`.

## Logging

The script utilizes Python's `logging` module to provide detailed information about its progress and any issues encountered during execution. Logs include:

- Start and completion of major steps.
- Number of records processed, matched, and rescheduled.
- Any errors or warnings during processing.

## License

This project is licensed under the [MIT License](LICENSE). See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

2. **Create a Feature Branch**

   `bash
   git checkout -b feature/YourFeature
   `

3. **Commit Your Changes**

   `bash
   git commit -m "Add some feature"
   `

4. **Push to the Branch**

   `bash
   git push origin feature/YourFeature
   `

5. **Open a Pull Request**

Please open an issue or submit a pull request for any improvements or bug fixes.

---

*Thank you for using the Recharge Shift Tool!*
```