# DataCleanse-Py: Automated Raw Data & Log Ingestion Engine

**DataCleanse-Py** is a modular, zero-dependency Python ETL (Extract, Transform, Load) utility designed to ingest raw, unstructured, or corrupted CSV sales records, isolate malformed rows into an auditable quarantine log, standardize valid records, and generate an automated execution summary report.

Built with **defensive programming** principles, type hinting, and Python standard library modules (`csv`, `pathlib`, `datetime`), this project demonstrates production-ready data validation and error-handling practices without relying on heavy external frameworks.

---

## Key Features

- **Defensive Ingestion & Error Isolation:** Gracefully handles missing files (`FileNotFoundError`), type mismatches (`ValueError`, `TypeError`), missing mandatory fields, negative values, and malformed dates/emails without crashing the pipeline.
- **Auditable Quarantine Logging:** Every rejected record is logged to `logs/error_logs.txt` with an exact timestamp, original CSV row number, failure reason, and raw payload for debugging.
- **Data Standardization & Enrichment:**
  - Trims whitespace and normalizes text casing (`Title Case` for products/categories, `lowercase` for emails).
  - Standardizes date separators (`YYYY/MM/DD` to `YYYY-MM-DD`) and validates calendar integrity.
  - Deduplicates records in $O(1)$ lookup time using hash sets (`set`) based on `transaction_id`.
  - Computes derived analytical fields (`total_amount = quantity * unit_price`).
- **Automated Executive Reporting:** Outputs real-time data quality metrics (total rows processed, clean record ratio, quarantined row count, and total valid revenue) to both the console and `logs/execution_report.txt`.

---

## Project Architecture

    datacleanse-py/
    ├── data/
    │   ├── raw_sales_data.csv        # Input: Raw dataset containing intentional anomalies
    │   └── cleaned_sales_data.csv    # Output: Standardized & enriched valid dataset
    ├── logs/
    │   ├── error_logs.txt            # Output: Timestamped quarantine log for rejected rows
    │   └── execution_report.txt      # Output: Summary metrics and data quality report
    ├── src/
    │   └── main.py                   # Core modular ETL & validation engine
    ├── .gitignore                    # Excludes cache and environment files
    └── README.md                     # Project documentation

---

## Quick Start

### Prerequisites
- Python **3.10+** (Uses only Python Standard Library—no `pip install` required)

### Running the Pipeline
Navigate to the project root directory and run:

    python src/main.py

---

## Sample Output (`execution_report.txt`)

    ==================================================
           DATACLEANSE-PY EXECUTION REPORT            
    ==================================================
    Çalışma Zamanı       : 2026-11-14 12:02:00
    Toplam Okunan Satır  : 11
    Temizlenen Satır     : 4
    Karantinaya Alınan   : 7
    Veri Kalite Oranı    : %36.36
    Toplam Geçerli Ciro  : $3,350.79
    ==================================================

---

## Author
**Nevzat Eren Koyuncu**  
Computer Engineering Undergraduate — Bursa Technical University