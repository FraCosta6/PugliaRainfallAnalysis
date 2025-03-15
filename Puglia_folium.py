import sqlite3
import xarray as xr
import numpy as np
import folium
import json

# Path to the NetCDF file
nc_file = "/Users/francesco/Desktop/opengeo/Dati_puglia.nc"

# Load the dataset
ds = xr.open_dataset(nc_file)

# Define the geographical boundaries of Puglia
lat_min, lat_max = 39.8, 42.2
lon_min, lon_max = 15.0, 19.5

# Find the closest available coordinates in the dataset
lat_available = ds["lat"].values
lon_available = ds["lon"].values

lat_min_nearest = min(lat_available, key=lambda x: abs(x - lat_min))
lat_max_nearest = min(lat_available, key=lambda x: abs(x - lat_max))
lon_min_nearest = min(lon_available, key=lambda x: abs(x - lon_min))
lon_max_nearest = min(lon_available, key=lambda x: abs(x - lon_max))

# Select data using the correct coordinates
if np.all(np.diff(ds["lat"].values) > 0):
    precip_puglia = ds["R10mm"].sel(lat=slice(lat_min_nearest, lat_max_nearest), lon=slice(lon_min_nearest, lon_max_nearest))
else:
    precip_puglia = ds["R10mm"].sel(lat=slice(lat_max_nearest, lat_min_nearest), lon=slice(lon_min_nearest, lon_max_nearest))

# Check if the dataset has a time dimension and compute the temporal average
if "time" in ds.dims:
    precip_puglia = precip_puglia.mean(dim="time")

# Connect to SQLite database
db_name = "weather_data.sqlite"
conn = sqlite3.connect(db_name)
cur = conn.cursor()

# Create table if it doesn't exist
cur.execute('''
    CREATE TABLE IF NOT EXISTS Rainfall (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        latitude REAL,
        longitude REAL,
        r10mm REAL
    )
''')

# Insert data into the database
for lat in precip_puglia.lat.values:
    for lon in precip_puglia.lon.values:
        r10mm_value = precip_puglia.sel(lat=lat, lon=lon).values.item()
        cur.execute('''
            INSERT INTO Rainfall (latitude, longitude, r10mm)
            VALUES (?, ?, ?)
        ''', (lat, lon, r10mm_value))

conn.commit()

# Retrieve data from the database
cur.execute('SELECT latitude, longitude, r10mm FROM Rainfall')
rows = cur.fetchall()

# Create an interactive map with Folium
mappa = folium.Map(location=[41.0, 16.5], zoom_start=7)

# Add data points to the map, filtering out points outside Puglia
for row in rows:
    lat, lon, r10mm = row
    if r10mm is not None and lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:  # Filter points within Puglia
        # Normalize r10mm to a range between 0 and 1 for opacity
        fill_opacity = min(r10mm / 1.6, 1.0)
        color = f'rgba(0, 0, 255, {fill_opacity})'  # Blue color with varying opacity
        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=fill_opacity,
            popup=f"Days with rainfall >10mm: {r10mm:.2f}"
        ).add_to(mappa)

# Save the interactive map as an HTML file
mappa.save("Interactive_map.html")

print("Interactive map saved as Interactive_map.html! Open it in a browser to view it.")

# Export data to JSON, ignoring NaN values
data_json = []
for row in rows:
    lat, lon, r10mm = row
    if r10mm is not None and lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:  # Filter points within Puglia
        data_json.append({"latitude": lat, "longitude": lon, "r10mm": r10mm})

# Save data to a JSON file
json_file = "weather_data.json"
with open(json_file, "w") as f:
    json.dump(data_json, f, indent=4)

print(f"Data successfully exported to {json_file}!")

# Close the database connection
conn.close()




