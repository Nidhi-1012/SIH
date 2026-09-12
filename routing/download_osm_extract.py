"""
Downloads the Northeast India OSM extract from Geofabrik for GraphHopper to
route against. Run once before starting the graphhopper docker service.

Run: python routing/download_osm_extract.py
"""
import sys
from pathlib import Path
from urllib.request import urlretrieve

EXTRACT_URL = "https://download.geofabrik.de/asia/india/north-eastern-zone-latest.osm.pbf"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "osm"
OUT_FILE = OUT_DIR / "northeast-india.osm.pbf"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if OUT_FILE.exists():
        print(f"Already downloaded: {OUT_FILE} ({OUT_FILE.stat().st_size / 1e6:.1f} MB)")
        return
    print(f"Downloading {EXTRACT_URL} ...")
    try:
        urlretrieve(EXTRACT_URL, OUT_FILE)
    except Exception as e:
        print(f"Download failed: {e}", file=sys.stderr)
        print("Check https://download.geofabrik.de/asia/india.html for the current extract filename/URL — Geofabrik occasionally renames regional extracts.", file=sys.stderr)
        sys.exit(1)
    print(f"Downloaded {OUT_FILE} ({OUT_FILE.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
