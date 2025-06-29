#!/usr/bin/env python3
"""
build_lookup_by_year.py
-----------------------
Convert the GDAC master index into one JSON file per year, after

✓ removing placeholder coordinates
      latitude  == -99.9990  OR
      longitude == -999.9990
✓ converting longitude to [0 … 360)

Output files live in docs/<YEAR>.json (uncompressed, ~1–15 MB each).
"""

from __future__ import annotations
import gzip, io, json, pathlib, sys
import pandas as pd

# ----------------------------------------------------------------------
ROOT  = pathlib.Path(__file__).resolve().parent.parent
DATA  = ROOT / "data"
DOCS  = ROOT / "docs"

SRC_TXT = DATA / "ar_index_global_prof.txt"
SRC_GZ  = SRC_TXT.with_suffix(".txt.gz")

# ----------------------------------------------------------------------
def open_index():
    if SRC_TXT.exists():
        return SRC_TXT.open("rt", encoding="utf-8")
    if SRC_GZ.exists():
        return io.TextIOWrapper(gzip.open(SRC_GZ, "rb"), encoding="utf-8")
    sys.exit("✖  Index file not found in data/")

# ----------------------------------------------------------------------
def main() -> None:
    DOCS.mkdir(exist_ok=True)

    with open_index() as f:
        df = pd.read_csv(f, comment="#",
                         usecols=["file", "date", "latitude", "longitude"])

    # 1. Drop placeholder coordinates
    mask_bad = (df.latitude == -99.9990) | (df.longitude == -999.9990)
    removed  = mask_bad.sum()
    if removed:
        print(f"Removed {removed:,} rows with placeholder lat/lon")
    df = df[~mask_bad]

    # 2. Derive year, rounded coords, lon 0–360
    df["YYYYMMDD"] = (df.date // 1_0000_00).astype("Int32")
    df["year"]     = df["YYYYMMDD"] // 10_000
    df["lat_round"] = df.latitude.round().astype("Int16")

    # normalise longitude
    lon360 = (df.longitude % 360 + 360) % 360
    df["lon_round"] = lon360.round().astype("Int16")

    slim = df[["file", "YYYYMMDD", "lat_round", "lon_round"]]

    # 3. Write one JSON per year
    for yr, grp in slim.groupby(df["year"]):
        out = DOCS / f"{yr}.json"
        grp.to_json(out, orient="records")
        size = out.stat().st_size / 1_048_576
        print(f"{yr}: {len(grp):,} rows → {size:.2f} MB")

if __name__ == "__main__":
    main()