from datetime import datetime

MAX_TIMESTAMP_LENGTH = 13


def convert_to_iso(timestamp_str: str) -> datetime:
    # Remove the 'Z' and add '+00:00' for UTC
    if timestamp_str.endswith("Z") or timestamp_str.endswith("z"):
        timestamp_str = timestamp_str[:-1] + "+00:00"

    dt = datetime.fromisoformat(timestamp_str)
    return dt


def parse_timestamp(timestamp_str: str) -> int:
    timestamp = convert_to_iso(timestamp_str)

    # Check if timestamp is already in milliseconds (13 digits)
    if len(str(timestamp)) >= MAX_TIMESTAMP_LENGTH:
        return timestamp

    # Convert seconds to milliseconds
    return timestamp * 1000
