import urllib.request
import zipfile
from pathlib import Path

ASSETS_DIR = Path(__file__).parent.parent / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

URL = "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/Countries_December_2023_Boundaries_UK_BUC/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"
GEOJSON_PATH = ASSETS_DIR / "uk_nations.geojson"


def main():
    print("Downloading UK nations boundary data...")
    urllib.request.urlretrieve(URL, GEOJSON_PATH)
    print(f"Done. Saved to assets/uk_nations.geojson")


if __name__ == "__main__":
    main()