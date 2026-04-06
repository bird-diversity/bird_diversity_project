import csv
from pathlib import Path

INPUT_FILE = Path("final5.csv")
OUTPUT_FILE = Path("null_lkagenrel2020_rows.csv")
COLUMN_NAME = "lka_general_2020"
NULL_LIKE = {"", "null", "na", "n/a", "nan", "none"}


def is_null_like(value: str | None) -> bool:
    if value is None:
        return True
    return value.strip().lower() in NULL_LIKE


def main() -> None:
    if not INPUT_FILE.exists():
        print(f"ERROR: Missing file: {INPUT_FILE}")
        return

    try:
        with INPUT_FILE.open("r", encoding="utf-8-sig", newline="") as src:
            reader = csv.DictReader(src)
            if not reader.fieldnames:
                print("ERROR: CSV has no header row")
                return

            if COLUMN_NAME not in reader.fieldnames:
                print(f"ERROR: Column not found: {COLUMN_NAME}")
                print("Available columns:")
                for col in reader.fieldnames:
                    print(f"- {col}")
                return

            rows_with_null = []
            for line_no, row in enumerate(reader, start=2):
                if is_null_like(row.get(COLUMN_NAME)):
                    row_with_line = {"__line__": str(line_no), **row}
                    rows_with_null.append(row_with_line)
    except PermissionError:
        print("ERROR: final5.csv is locked by another process.")
        print("Close any app using it (for example Excel), then run this script again.")
        return

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as dst:
        fieldnames = ["__line__"] + [f for f in reader.fieldnames if f is not None]
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_with_null)

    print(f"Total rows with null-like '{COLUMN_NAME}': {len(rows_with_null)}")
    print(f"Saved matching rows to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
