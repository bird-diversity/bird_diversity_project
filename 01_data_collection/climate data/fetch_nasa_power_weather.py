#!/usr/bin/env python3
import argparse
import csv
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import urlencode
from urllib.request import urlopen


API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMETERS = [
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "PRECTOTCORR",
    "WS2M",
    "RH2M",
    "ALLSKY_SFC_SW_DWN",
]

OUTPUT_COLUMNS = [
    "decimalLatitude",
    "decimalLongitude",
    "eventDate",
    "provider",
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "wind_speed_2m_mean",
    "relative_humidity_2m_mean",
    "shortwave_radiation_sum",
]


def parse_date(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y-%m-%d")


def split_dates_by_span(dates: Sequence[str], max_span_days: int) -> List[List[str]]:
    """Split a sorted list of date strings into chunks where each chunk
    covers at most ``max_span_days`` days between its first and last date.

    This limits how much data we request from the NASA API in a single call.
    """
    if not dates:
        return []
    if max_span_days <= 0:
        # No limit requested; keep existing behaviour.
        return [sorted(dates, key=parse_date)]

    sorted_dates = sorted(dates, key=parse_date)
    chunks: List[List[str]] = []
    current_chunk: List[str] = [sorted_dates[0]]
    start_dt = parse_date(sorted_dates[0])

    for value in sorted_dates[1:]:
        dt = parse_date(value)
        # If adding this date would keep the span within the limit, add it;
        # otherwise, start a new chunk.
        if (dt - start_dt).days <= max_span_days:
            current_chunk.append(value)
        else:
            chunks.append(current_chunk)
            current_chunk = [value]
            start_dt = dt

    chunks.append(current_chunk)
    return chunks


def load_input_pairs(input_csv: Path) -> Dict[Tuple[str, str], Set[str]]:
    grouped: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
    with input_csv.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required = {"decimalLatitude", "decimalLongitude", "eventDate"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns in {input_csv}: {', '.join(sorted(missing))}")

        for row in reader:
            lat = (row.get("decimalLatitude") or "").strip()
            lon = (row.get("decimalLongitude") or "").strip()
            event_date = (row.get("eventDate") or "").strip()
            if not lat or not lon or not event_date:
                continue
            grouped[(lat, lon)].add(event_date)

    return grouped


def load_existing_keys(output_csv: Path) -> Set[Tuple[str, str, str]]:
    existing: Set[Tuple[str, str, str]] = set()
    if not output_csv.exists() or output_csv.stat().st_size == 0:
        return existing

    with output_csv.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required = {"decimalLatitude", "decimalLongitude", "eventDate"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            return existing

        for row in reader:
            lat = (row.get("decimalLatitude") or "").strip()
            lon = (row.get("decimalLongitude") or "").strip()
            event_date = (row.get("eventDate") or "").strip()
            if lat and lon and event_date:
                existing.add((lat, lon, event_date))

    return existing


def to_api_day(value: str) -> str:
    return parse_date(value).strftime("%Y%m%d")


def request_daily(lat: str, lon: str, start_day: str, end_day: str, timeout: int = 40) -> dict:
    params = {
        "parameters": ",".join(PARAMETERS),
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start_day,
        "end": end_day,
        "format": "JSON",
    }
    url = f"{API_URL}?{urlencode(params)}"
    with urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_coordinate_payload(
    lat: str,
    lon: str,
    pending_dates: Sequence[str],
    min_interval: float,
) -> Optional[dict]:
    if not pending_dates:
        return None

    start_day = to_api_day(pending_dates[0])
    end_day = to_api_day(pending_dates[-1])

    try:
        payload = request_daily(lat=lat, lon=lon, start_day=start_day, end_day=end_day)
    except Exception:
        if min_interval > 0:
            time.sleep(min_interval)
        return None

    if min_interval > 0:
        time.sleep(min_interval)
    return payload


def clean_value(value):
    if value is None:
        return None
    if isinstance(value, (int, float)) and float(value) <= -900:
        return None
    return value


def row_from_parameters(lat: str, lon: str, event_date: str, param_data: dict) -> dict:
    key = to_api_day(event_date)
    return {
        "decimalLatitude": lat,
        "decimalLongitude": lon,
        "eventDate": event_date,
        "provider": "nasa_power",
        "temperature_2m_mean": clean_value(param_data.get("T2M", {}).get(key)),
        "temperature_2m_max": clean_value(param_data.get("T2M_MAX", {}).get(key)),
        "temperature_2m_min": clean_value(param_data.get("T2M_MIN", {}).get(key)),
        "precipitation_sum": clean_value(param_data.get("PRECTOTCORR", {}).get(key)),
        "wind_speed_2m_mean": clean_value(param_data.get("WS2M", {}).get(key)),
        "relative_humidity_2m_mean": clean_value(param_data.get("RH2M", {}).get(key)),
        "shortwave_radiation_sum": clean_value(param_data.get("ALLSKY_SFC_SW_DWN", {}).get(key)),
    }


def write_rows(output_csv: Path, rows: Iterable[dict], write_header: bool) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=OUTPUT_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
        file.flush()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch historical daily weather from NASA POWER for coordinate/date pairs in final3.csv"
    )
    parser.add_argument(
        "--input",
        default="data sets/final3.csv",
        help="Path to source CSV containing decimalLatitude, decimalLongitude, eventDate",
    )
    parser.add_argument(
        "--output",
        default="data sets/final3_weather_nasapower.csv",
        help="Path to output weather CSV",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=25,
        help="Print progress every N coordinates",
    )
    parser.add_argument(
        "--coord-limit",
        type=int,
        default=0,
        help="Optional limit for number of coordinates to process in this run (0 = no limit)",
    )
    parser.add_argument(
        "--min-interval",
        type=float,
        default=0.05,
        help="Minimum delay between requests in seconds (lower is faster but may hit API limits)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Number of concurrent coordinate requests (higher is faster but heavier on API)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Number of rows to buffer in memory before writing to CSV (larger is faster)",
    )
    parser.add_argument(
        "--max-days-per-request",
        type=int,
        default=365,
        help="Maximum number of days covered by each NASA request (limits response size)",
    )
    args = parser.parse_args()

    input_csv = Path(args.input)
    output_csv = Path(args.output)

    grouped = load_input_pairs(input_csv)
    existing = load_existing_keys(output_csv)

    total_coords = len(grouped)
    total_pairs = sum(len(dates) for dates in grouped.values())
    print(f"Loaded {total_coords} unique coordinates and {total_pairs} coordinate/date pairs", flush=True)
    if existing:
        print(f"Resuming: found {len(existing)} existing rows in output", flush=True)

    write_header = (not output_csv.exists()) or output_csv.stat().st_size == 0
    total_written = 0
    total_missing = 0
    failed_coords = 0

    tasks: List[Tuple[str, str, List[str]]] = []
    for (lat, lon), date_set in grouped.items():
        pending_dates = sorted(
            event_date for event_date in date_set if (lat, lon, event_date) not in existing
        )
        if not pending_dates:
            continue

        # Optionally split long date ranges into smaller spans so we don't
        # request too much data from the API in a single call.
        for chunk in split_dates_by_span(pending_dates, max_span_days=args.max_days_per_request):
            tasks.append((lat, lon, chunk))

    if args.coord_limit and args.coord_limit > 0:
        tasks = tasks[: args.coord_limit]

    min_interval = max(0.0, args.min_interval)
    max_workers = max(1, args.workers)

    batch_size = max(1, args.batch_size)  # Number of rows to buffer before writing to CSV
    batch_rows = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(fetch_coordinate_payload, lat, lon, pending_dates, min_interval): (lat, lon, pending_dates)
            for lat, lon, pending_dates in tasks
        }

        for index, future in enumerate(as_completed(future_to_task), start=1):
            lat, lon, pending_dates = future_to_task[future]
            try:
                payload = future.result()
            except Exception as exc:
                failed_coords += 1
                print(
                    f"Error for coordinate {lat},{lon} with {len(pending_dates)} dates: {exc}",
                    flush=True,
                )
                continue
            if not payload:
                failed_coords += 1
                continue

            param_data = payload.get("properties", {}).get("parameter", {})
            if not param_data:
                failed_coords += 1
                continue

            for event_date in pending_dates:
                row = row_from_parameters(lat=lat, lon=lon, event_date=event_date, param_data=param_data)
                values = [row[col] for col in OUTPUT_COLUMNS[4:]]
                if all(value is None for value in values):
                    total_missing += 1
                    continue
                batch_rows.append(row)
                existing.add((lat, lon, event_date))

            # Write rows in chunks
            if len(batch_rows) >= batch_size:
                write_rows(output_csv=output_csv, rows=batch_rows, write_header=write_header)
                write_header = False
                total_written += len(batch_rows)
                batch_rows = []

            if index % max(1, args.progress_every) == 0:
                print(
                    f"Coordinates: {index}/{len(tasks)} | written this run: {total_written} | missing days: {total_missing} | failed coordinates: {failed_coords}",
                    flush=True,
                )

    # Write any remaining rows
    if batch_rows:
        write_rows(output_csv=output_csv, rows=batch_rows, write_header=write_header)
        total_written += len(batch_rows)


    print(
        f"Saved/updated {total_written} rows in {output_csv} | missing days: {total_missing} | failed coordinates: {failed_coords}",
        flush=True,
    )


if __name__ == "__main__":
    main()
