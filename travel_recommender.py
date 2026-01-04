import pandas as pd
import numpy as np
from geopy.distance import geodesic
from pathlib import Path
import time

script_dir = Path(__file__).resolve().parent
csv_path = script_dir / "Top_Indian_Places_to_Visit.csv"

df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip()

col_map = {}
if 'Name' in df.columns:
    col_map['Name'] = 'Place'
if 'Google review rating' in df.columns:
    col_map['Google review rating'] = 'Rating'
if 'Number of google review in lakhs' in df.columns:
    col_map['Number of google review in lakhs'] = 'Popularity'
if col_map:
    df = df.rename(columns=col_map)

for col in ['Rating', 'Popularity']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    else:
        df[col] = np.nan

city_coords_cache = {}

def get_city_coords(city):
    """Return (lat, lon) for a city. Use cache, otherwise attempt geocoding."""
    if pd.isna(city) or not city:
        return (None, None)

    if city in city_coords_cache:
        return city_coords_cache[city]

    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        row = df[df['City'] == city]
        if not row.empty:
            lat = row.iloc[0].get('Latitude')
            lon = row.iloc[0].get('Longitude')
            if pd.notna(lat) and pd.notna(lon):
                coords = (lat, lon)
                city_coords_cache[city] = coords
                return coords

    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="local_travel_recommender")
        loc = geolocator.geocode(f"{city}, India", timeout=10)
        if loc:
            coords = (loc.latitude, loc.longitude)
        else:
            coords = (None, None)
    except Exception:
        coords = (None, None)

    city_coords_cache[city] = coords
    try:
        time.sleep(1)
    except Exception:
        pass
    return coords


def get_distance(a, b):
    return geodesic(a, b).km


def recommend_places(source_city, top_n=5):
    source_city_norm = source_city.lower()
    if source_city_norm not in df['City'].str.lower().values:
        return "Source city not found in dataset."

    source_row = df[df['City'].str.lower() == source_city_norm].iloc[0]
    source_coords = get_city_coords(source_row['City'])
    if source_coords[0] is None or source_coords[1] is None:
        # safe normalization
        rating_max = df['Rating'].max()
        pop_max = df['Popularity'].max()
        df['Rating_Score'] = 0 if pd.isna(rating_max) or rating_max == 0 else df['Rating'] / rating_max
        df['Popularity_Score'] = 0 if pd.isna(pop_max) or pop_max == 0 else df['Popularity'] / pop_max
        df['Final_Score'] = 0.5 * df['Rating_Score'] + 0.5 * df['Popularity_Score']
        candidates = df[df['City'].str.lower() != source_city_norm].sort_values(by='Final_Score', ascending=False)
        return candidates.head(top_n)[['City', 'Place', 'Rating', 'Popularity', 'Final_Score']]

    destinations = df[df['City'].str.lower() != source_city_norm].copy()

    unique_cities = destinations['City'].fillna('').unique()
    max_geocode = 80
    if len(unique_cities) > max_geocode:
        priority = destinations.sort_values(by=['Rating', 'Popularity'], ascending=False)['City'].fillna('').unique()[:max_geocode]
    else:
        priority = unique_cities

    for c in priority:
        if c and c not in city_coords_cache:
            city_coords_cache[c] = get_city_coords(c)

    def _distance_for_row(row):
        coords = city_coords_cache.get(row['City'])
        if not coords or coords[0] is None or coords[1] is None:
            return np.nan
        return get_distance(source_coords, coords)

    destinations['Distance_km'] = destinations.apply(_distance_for_row, axis=1)

    destinations['Distance_Score'] = np.where(destinations['Distance_km'] > 0, 1 / destinations['Distance_km'], 0)

    rating_max = destinations['Rating'].max()
    pop_max = destinations['Popularity'].max()
    destinations['Rating_Score'] = 0 if pd.isna(rating_max) or rating_max == 0 else destinations['Rating'] / rating_max
    destinations['Popularity_Score'] = 0 if pd.isna(pop_max) or pop_max == 0 else destinations['Popularity'] / pop_max

    destinations['Final_Score'] = (
        0.4 * destinations['Rating_Score'] +
        0.35 * destinations['Popularity_Score'] +
        0.25 * destinations['Distance_Score']
    )

    return destinations.sort_values(by='Final_Score', ascending=False).head(top_n)[['City', 'Place', 'Distance_km', 'Rating', 'Popularity', 'Final_Score']]


if __name__ == '__main__':
    for city in ["Delhi", "Mumbai", "Bangalore"]:
        print(f"\nTop weekend destinations from {city}:\n")
        out = recommend_places(city)
        if isinstance(out, str):
            print(out)
        elif hasattr(out, 'empty') and out.empty:
            print("No destinations found or missing data.")
        else:
            print(out.to_string(index=False))
