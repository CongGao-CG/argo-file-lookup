#!/usr/bin/env python3
"""
build_lookup_sample.py
----------------------

Generate a SMALL lookup table (default 5 000 rows) for fast local testing.
Reads the already-downloaded GDAC index in data/, then writes:

    data/search_table_sample.json
    docs/search_table_sample.json.gz
    docs/search_table.json.gz         ← duplicate for the web app
    docs/search_table.json            ← same bytes; header mapping for http-server

Usage
-----
    python scripts/build_lookup_sample.py [nrows]

If *nrows* is omitted, 5 000 rows are kept.
"""

from __future__ import annotations
import gzip, io, pathlib, sys

import pandas as pd

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
ROOT  = pathlib.Path(__file__).resolve().parent.parent
DATA  = ROOT / "data"
DOCS  = ROOT / "docs"

SRC_TXT = DATA / "ar_index_global_prof.txt"
SRC_GZ  = SRC_TXT.with_suffix(".txt.gz")

# default sample size
N_ROWS = int(sys.argv[1]) if len(sys.argv) > 1 else 5_000

# ----------------------------------------------------------------------
def open_source():
    if SRC_TXT.exists():
        return SRC_TXT.open("rt", encoding="utf-8")
    if SRC_GZ.exists():
        return io.TextIOWrapper(gzip.open(SRC_GZ, "rb"), encoding="utf-8")
    sys.exit("✖  Index file not found in data/")

# ----------------------------------------------------------------------
def main():
    DOCS.mkdir(exist_ok=True, parents=True)
    DATA.mkdir(exist_ok=True, parents=True)

    with open_source() as f:
        df = pd.read_csv(f, comment="#", nrows=N_ROWS)

    # derive minimal columns
    df["YYYYMMDD"]  = (df["date"] // 1_0000_00).astype("Int32")
    df["lat_round"] = df.latitude.round().astype("Int16")
    df["lon_round"] = df.longitude.round().astype("Int16")

    slim = df[["file", "YYYYMMDD", "lat_round", "lon_round"]]

    # ---------- write outputs ------------------------------------------
    out_plain = DATA / "search_table_sample.json"
    slim.to_json(out_plain, orient="records")

    out_gz    = DOCS / "search_table_sample.json.gz"
    with gzip.open(out_gz, "wt", encoding="utf-8") as gz:
        slim.to_json(gz, orient="records")

    # duplicate names so app.js can fetch without edits
    (DOCS / "search_table.json.gz").write_bytes(out_gz.read_bytes())
    (DOCS / "search_table.json").write_bytes(out_gz.read_bytes())

    print(f"✓ kept {len(slim):,} rows")
    print(f"✓ wrote {out_plain.relative_to(ROOT)} "
          f"({out_plain.stat().st_size/1_048_576:.2f} MB)")
    print(f"✓ wrote {out_gz.relative_to(ROOT)} "
          f"({out_gz.stat().st_size/1_048_576:.2f} MB gzip)")

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()