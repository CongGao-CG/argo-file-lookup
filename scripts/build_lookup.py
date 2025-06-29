#!/usr/bin/env python3
"""
build_lookup.py
---------------

Convert the giant ar_index_global_prof.txt into a lightweight lookup
table that the browser can filter quickly.

Input  : data/ar_index_global_prof.txt   (plain)  OR
         data/ar_index_global_prof.txt.gz (gzip)

Outputs: data/search_table.json          (plain, local only)
         docs/search_table.json.gz       (gzip, to be committed)

JSON record schema
------------------
{ "file": "aoml/13857/profiles/R13857_001.nc",
  "YYYYMMDD": 19970729,
  "lat_round": 0,
  "lon_round": -16 }
"""

from __future__ import annotations
import gzip, io, json, pathlib, sys

import pandas as pd

# ----------------------------------------------------------------------
# File locations
# ----------------------------------------------------------------------
ROOT   = pathlib.Path(__file__).resolve().parent.parent
DATA   = ROOT / "data"
DOCS   = ROOT / "docs"

SRC_TXT = DATA / "ar_index_global_prof.txt"
SRC_GZ  = DATA / "ar_index_global_prof.txt.gz"   # optional

DST_JSON      = DATA / "search_table.json"
DST_JSON_GZ   = DOCS / "search_table.json.gz"

# ----------------------------------------------------------------------
def open_source():
    """
    Return a text file‐like object for the index, regardless of .gz or not.
    Exits with an error if neither file is present.
    """
    if SRC_TXT.exists():
        return SRC_TXT.open("rt", encoding="utf-8")
    if SRC_GZ.exists():
        return io.TextIOWrapper(gzip.open(SRC_GZ, "rb"), encoding="utf-8")
    sys.exit("✖  ar_index_global_prof.txt(.gz) not found in data/")

# ----------------------------------------------------------------------
def main() -> None:
    DOCS.mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)

    with open_source() as f:
        # skip header lines that start with '#'
        df = pd.read_csv(f, comment="#")

    # --- derive columns -------------------------------------------------
    df["YYYYMMDD"] = (df["date"] // 1_0000_00).astype("Int32")
    df["lat_round"] = df["latitude"].round().astype("Int16")
    df["lon_round"] = df["longitude"].round().astype("Int16")

    slim = df[["file", "YYYYMMDD", "lat_round", "lon_round"]]

    # --- write plain JSON to data/ (local only) -------------------------
    slim.to_json(DST_JSON, orient="records")
    print(f"✓ wrote {DST_JSON.relative_to(ROOT)} "
          f"({DST_JSON.stat().st_size/1_048_576:.1f} MB)")

    # --- write gzip JSON to docs/ (for GitHub Pages) --------------------
    with gzip.open(DST_JSON_GZ, "wt", encoding="utf-8") as gz:
        slim.to_json(gz, orient="records")

    print(f"✓ wrote {DST_JSON_GZ.relative_to(ROOT)} "
          f"({DST_JSON_GZ.stat().st_size/1_048_576:.1f} MB, gzip)")
    print(f"Rows in table: {len(slim):,}")

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()