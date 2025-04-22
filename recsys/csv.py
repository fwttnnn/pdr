import csv
import io
import os

def load(path: str) -> list[list[dict[str, str]]]:
    with open(path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

    return []

def load_nth_row(path: str, nth: int) -> set[int]:
    with open(path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        ids = [row[nth] for row in reader]
        if len(ids) >= 1:
            ids.pop(0)

        return set(map(int, ids))

    return set()

def insert_headers(path: str, headers: list[str]) -> tuple[io.TextIOWrapper, csv.DictWriter]:
    f = open(path, mode="a", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=headers)

    if os.stat(path).st_size == 0:
        w.writeheader()

    return f, w

def ensure_exist(path: str) -> None:
    if not os.path.exists(path):
        open(path, "w").close()
