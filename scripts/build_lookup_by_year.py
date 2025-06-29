#!/usr/bin/env python3
"""
build_lookup_by_year.py  (delayed-mode only)

• Reads data/ar_index_global_prof.txt(.gz)
• Keeps ONLY files whose basename starts exactly with 'D' (delayed-mode
  core files, e.g. D6901234_012.nc)
• Drops placeholder coordinates  -99.9990 / -999.9990
• Converts longitude to 0–360°
• Writes docs/<YEAR>.json (plain JSON)
"""

from __future__ import annotations
import gzip, io, pathlib, sys
import pandas as pd
import re

ROOT  = pathlib.Path(__file__).resolve().parent.parent
DATA  = ROOT / "data"
DOCS  = ROOT / "docs"

TXT = DATA / "ar_index_global_prof.txt"
GZ  = TXT.with_suffix(".txt.gz")

# -------------------------------------------------------------------
def open_index():
    if TXT.exists():
        return TXT.open("rt", encoding="utf-8")
    if GZ.exists():
        return io.TextIOWrapper(gzip.open(GZ, "rb"), encoding="utf-8")
    sys.exit("✖  Index file not found in data/")

# -------------------------------------------------------------------
def is_core_d_file(path: str) -> bool:
    """
    Return True if basename matches ^D.*\.nc$
    but NOT BD*.nc or SD*.nc.
    """
    base = path.rsplit("/", 1)[-1]
    return bool(re.match(r"^D[^/]*\.nc$", base))

# -------------------------------------------------------------------
def main() -> None:
    DOCS.mkdir(exist_ok=True)

    cols = ["file", "date", "latitude", "longitude"]
    with open_index() as f:
        df = pd.read_csv(f, comment="#", usecols=cols)

    # 1. keep only core delayed-mode files
    mask_d = df["file"].apply(is_core_d_file)
    df = df[mask_d]
    print(f"Kept {len(df):,} delayed-mode core profiles")

    # 2. drop placeholder coords
    bad = (df.latitude == -99.9990) | (df.longitude == -999.9990)
    if bad.any():
        print(f"Removed {bad.sum():,} rows with placeholder lat/lon")
        df = df[~bad]

    # 3. derive columns
    df["YYYYMMDD"] = (df.date // 1_0000_00).astype("Int32")
    df["year"] = df["YYYYMMDD"] // 10_000
    df["lat_round"] = df.latitude.round().astype("Int16")
    lon360 = (df.longitude % 360 + 360) % 360
    df["lon_round"] = lon360.round().astype("Int16")
    slim = df[["file", "YYYYMMDD", "lat_round", "lon_round"]]

    # 4. write per-year JSON
    for yr, grp in slim.groupby(df["year"]):
        out = DOCS / f"{yr}.json"
        grp.to_json(out, orient="records")
        size = out.stat().st_size / 1_048_576
        print(f"{yr}: {len(grp):,} rows  → {size:.2f} MB")

# -------------------------------------------------------------------
if __name__ == "__main__":
    main()