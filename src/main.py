import csv
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw_sales_data.csv"
CLEAN_DATA_PATH = BASE_DIR / "data" / "cleaned_sales_data.csv"
ERROR_LOG_PATH = BASE_DIR / "logs" / "error_logs.txt"
REPORT_PATH = BASE_DIR / "logs" / "execution_report.txt"


def setup_directories() -> None:
  
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    ERROR_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def read_raw_data(file_path: Path) -> list[dict[str, Any]]:
   
    if not file_path.exists():
        raise FileNotFoundError(f"Kritik Hata: Kaynak dosya bulunamadı -> {file_path}")

    with open(file_path, mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def log_error(row_number: int, row_data: dict[str, Any], reason: str) -> None:
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] SATIR {row_number} | SEBEP: {reason} | VERİ: {row_data}\n"

    with open(ERROR_LOG_PATH, mode="a", encoding="utf-8") as log_file:
        log_file.write(log_entry)
def validate_and_clean(raw_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
   
    cleaned_rows: list[dict[str, Any]] = []
    seen_transactions: set[str] = set()
    error_count = 0

    for idx, row in enumerate(raw_rows, start=2): 
        try:
            
            txn_id = (row.get("transaction_id") or "").strip()
            product = (row.get("product_name") or "").strip()
            category = (row.get("category") or "").strip()
            raw_date = (row.get("date") or "").strip()
            raw_qty = (row.get("quantity") or "").strip()
            raw_price = (row.get("unit_price") or "").strip()
            email = (row.get("customer_email") or "").strip()

            if not all([txn_id, product, raw_date, raw_qty, raw_price]):
                raise ValueError("Zorunlu alanlardan biri veya birkaçı boş.")

            
            if txn_id in seen_transactions:
                raise ValueError(f"Tekrar eden işlem ID'si (Duplicate): {txn_id}")

            
            normalized_date = raw_date.replace("/", "-")
            datetime.strptime(normalized_date, "%Y-%m-%d")

           
            quantity = int(raw_qty)
            unit_price = float(raw_price)
            if quantity <= 0 or unit_price <= 0:
                raise ValueError(f"Adet ({quantity}) ve birim fiyat ({unit_price}) sıfırdan büyük olmalıdır.")

            
            if "@" not in email or "." not in email:
                raise ValueError(f"Geçersiz e-posta formatı: {email}")

            
            clean_record = {
                "transaction_id": txn_id.upper(),
                "date": normalized_date,
                "product_name": product.title(),
                "category": category.title() if category else "Uncategorized",
                "quantity": quantity,
                "unit_price": round(unit_price, 2),
                "total_amount": round(quantity * unit_price, 2),  # Yeni hesaplanan sütun
                "customer_email": email.lower(),
            }

            cleaned_rows.append(clean_record)
            seen_transactions.add(txn_id)

        except (ValueError, TypeError) as err:
            error_count += 1
            log_error(row_number=idx, row_data=row, reason=str(err))

    return cleaned_rows, error_count


def save_clean_data(cleaned_rows: list[dict[str, Any]], output_path: Path) -> None:
    """Temizlenmiş veriyi yeni bir CSV dosyası olarak kaydeder."""
    if not cleaned_rows:
        return

    fieldnames = list(cleaned_rows[0].keys())
    with open(output_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)


def generate_report(total_rows: int, cleaned_rows: list[dict[str, Any]], error_count: int) -> None:
    
    clean_count = len(cleaned_rows)
    success_rate = (clean_count / total_rows * 100) if total_rows > 0 else 0.0
    total_revenue = sum(item["total_amount"] for item in cleaned_rows)

    report_content = (
        "==================================================\n"
        "       DATACLEANSE-PY EXECUTION REPORT            \n"
        "==================================================\n"
        f"Çalışma Zamanı       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Toplam Okunan Satır  : {total_rows}\n"
        f"Temizlenen Satır     : {clean_count}\n"
        f"Karantinaya Alınan   : {error_count}\n"
        f"Veri Kalite Oranı    : %{success_rate:.2f}\n"
        f"Toplam Geçerli Ciro  : ${total_revenue:,.2f}\n"
        "==================================================\n"
    )

    with open(REPORT_PATH, mode="w", encoding="utf-8") as report_file:
        report_file.write(report_content)

    print(report_content)


def main() -> None:
    """ETL veri işleme hattını (pipeline) uçtan uca çalıştırır."""
    setup_directories()

    
    if ERROR_LOG_PATH.exists():
        ERROR_LOG_PATH.unlink()

    try:
        raw_data = read_raw_data(RAW_DATA_PATH)
        cleaned_data, error_count = validate_and_clean(raw_data)
        save_clean_data(cleaned_data, CLEAN_DATA_PATH)
        generate_report(len(raw_data), cleaned_data, error_count)
        print(f"İşlem tamamlandı! Çıktılar '{BASE_DIR}' altına kaydedildi.")
    except FileNotFoundError as fnf_err:
        print(f"Sistem Hatası: {fnf_err}")
    except Exception as unexpected_err:
        print(f"Beklenmeyen Kritik Hata: {unexpected_err}")


if __name__ == "__main__":
    main()        