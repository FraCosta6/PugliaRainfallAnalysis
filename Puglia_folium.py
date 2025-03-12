import sqlite3
import xarray as xr
import numpy as np
import folium

# Percorso del file NetCDF
nc_file = "/Users/francesco/Desktop/opengeo/Dati_puglia.nc"

# Caricare il dataset
ds = xr.open_dataset(nc_file)

# Definiamo i confini della Puglia
lat_min, lat_max = 39.8, 42.2
lon_min, lon_max = 15.0, 19.5

# Troviamo le coordinate più vicine disponibili nel dataset
lat_available = ds["lat"].values
lon_available = ds["lon"].values

lat_min_nearest = min(lat_available, key=lambda x: abs(x - lat_min))
lat_max_nearest = min(lat_available, key=lambda x: abs(x - lat_max))
lon_min_nearest = min(lon_available, key=lambda x: abs(x - lon_min))
lon_max_nearest = min(lon_available, key=lambda x: abs(x - lon_max))

# Selezioniamo i dati usando le coordinate corrette
if np.all(np.diff(ds["lat"].values) > 0):
    precip_puglia = ds["R10mm"].sel(lat=slice(lat_min_nearest, lat_max_nearest), lon=slice(lon_min_nearest, lon_max_nearest))
else:
    precip_puglia = ds["R10mm"].sel(lat=slice(lat_max_nearest, lat_min_nearest), lon=slice(lon_min_nearest, lon_max_nearest))

# Controlliamo se il dataset ha una dimensione temporale e calcoliamo la media temporale
if "time" in ds.dims:
    precip_puglia = precip_puglia.mean(dim="time")

# Connessione a SQLite
db_name = "weather_data.sqlite"
conn = sqlite3.connect(db_name)
cur = conn.cursor()

# Creazione tabella
cur.execute('''
    CREATE TABLE IF NOT EXISTS Rainfall (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        latitude REAL,
        longitude REAL,
        r10mm REAL
    )
''')

# Inserimento dati
for lat in precip_puglia.lat.values:
    for lon in precip_puglia.lon.values:
        value = precip_puglia.sel(lat=lat, lon=lon).values.item()
        cur.execute('''INSERT INTO Rainfall (latitude, longitude, r10mm) VALUES (?, ?, ?)''',
                    (lat, lon, value))

# Salva e chiude
conn.commit()
conn.close()

print("Dati estratti da NetCDF e salvati in SQLite con successo!")

# Connessione al database per recuperare i dati
conn = sqlite3.connect(db_name)
cur = conn.cursor()
# Recupera i dati dal database
cur.execute("SELECT latitude, longitude, r10mm FROM Rainfall")
data = cur.fetchall()
conn.close()

# Filtra i dati validi (eliminando i None)
valid_data = [d[2] for d in data if d[2] is not None]

# Calcola il valore massimo di r10mm per scalare l'opacità
max_r10mm = max(valid_data) if valid_data else 1  # Se non ci sono valori validi, usa 1 per evitare errore

# Creazione della mappa interattiva con Folium
mappa = folium.Map(location=[41.0, 16.5], zoom_start=7)

# Aggiunta dei dati alla mappa
for row in data:
    lat, lon, r10mm = row
    if r10mm is not None:  # Evita errori su valori nulli
        fill_opacity = min(r10mm / max_r10mm, 0.8)  # Normalizza i valori tra 0 e 0.8
        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=fill_opacity,
            popup=f"Giorni di pioggia >10mm: {r10mm:.2f}"
        ).add_to(mappa)

# Salva la mappa in un file HTML
mappa.save("mappa_interattiva.html")

print("Mappa interattiva salvata come mappa_interattiva.html! Aprila in un browser per visualizzarla.")




