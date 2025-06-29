#!/usr/bin/env python3
"""
minmax_latlon.py
----------------
Report geographic extents in Argo's profile index.

Outputs
--------
• Overall min / max latitude & longitude
• Min / max after removing placeholder coords
    latitude  == -99.9990 OR
    longitude == -999.9990
• List of offending records

Folder layout assumed:
repo/
├─ data/ar_index_global_prof.txt(.gz)
└─ scripts/minmax_latlon.py   ← this file
"""

from pathlib import Path
import gzip, io
import pandas as pd

# ------------------------------------------------------------------
# Locate the index file relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT       = SCRIPT_DIR.parent
DATA_DIR   = ROOT / "data"

TXT = DATA_DIR / "ar_index_global_prof.txt"
GZ  = TXT.with_suffix(".txt.gz")

def open_index():
    if TXT.exists():
        return TXT.open("rt", encoding="utf-8")
    if GZ.exists():
        return io.TextIOWrapper(gzip.open(GZ, "rb"), encoding="utf-8")
    raise FileNotFoundError("Index file not found in data/")

# ------------------------------------------------------------------
def main():
    cols = ["file", "date", "latitude", "longitude"]
    with open_index() as f:
        df = pd.read_csv(f, comment="#", usecols=cols)

    # -------- overall min/max -------------------------------------
    lat_min_o, lat_max_o = df.latitude.min(),  df.latitude.max()
    lon_min_o, lon_max_o = df.longitude.min(), df.longitude.max()

    print("Overall:")
    print(f"  Latitude : {lat_min_o:9.4f}  →  {lat_max_o:9.4f}")
    print(f"  Longitude: {lon_min_o:9.4f}  →  {lon_max_o:9.4f}")

    # -------- identify placeholder rows ---------------------------
    mask_bad = (df.latitude == -99.9990) | (df.longitude == -999.9990)
    bad = df[mask_bad]

    # -------- min/max after removing placeholders -----------------
    clean = df[~mask_bad]
    lat_min_c, lat_max_c = clean.latitude.min(),  clean.latitude.max()
    lon_min_c, lon_max_c = clean.longitude.min(), clean.longitude.max()

    print("\nAfter excluding placeholder coordinates (-99.9990 / -999.9990):")
    print(f"  Latitude : {lat_min_c:9.4f}  →  {lat_max_c:9.4f}")
    print(f"  Longitude: {lon_min_c:9.4f}  →  {lon_max_c:9.4f}")

    # -------- list offending records ------------------------------
    if bad.empty:
        print("\n✓ No placeholder coordinates found.")
    else:
        print(f"\n⚠ Found {len(bad)} record(s) with placeholder coordinates:")
        for _, row in bad.iterrows():
            print(f"  {row.file:60s}  date={row.date}  "
                  f"lat={row.latitude:.4f}  lon={row.longitude:.4f}")

# ------------------------------------------------------------------
if __name__ == "__main__":
    main()