# Precipitation Analysis in Puglia

This project is dedicated to analyzing precipitation patterns in the Puglia region using meteorological data from the ERA5 dataset. The data is sourced from the following dataset: **Agroclimatic indicators from 1951 to 2099 derived from climate projections**, and the analyzed time period is **198101-201012**. The dataset is provided as NetCDF (.nc) files and imported into the project for processing and visualization on an interactive map.

The primary variable of interest in this dataset is **R10mm**, which represents the number of consecutive days with precipitation exceeding 10 mm in a given area. This metric is particularly useful for agricultural planning as it helps assess the risk of excessive rainfall, which can lead to soil erosion, waterlogging, and crop damage. Additionally, understanding these precipitation patterns allows farmers and agronomists to implement better irrigation management strategies, optimize planting schedules, and mitigate potential climate-related risks.

## System Requirements

- Python 3.x
- Required libraries (installed via `requirements.txt`)
- A NetCDF (.nc) dataset containing ERA5 precipitation data

## Expected Dataset Format

The dataset should be in **NetCDF (.nc) format** and contain the following key variables:
- **lat**: Latitude coordinates
- **lon**: Longitude coordinates
- **R10mm**: Days with precipitation >10mm
- **time** (if available): Time dimension for computing temporal averages

## Project Structure

```
project_root/
│── data/		   # Directory for storing NetCDF files
│   ├── Example_file.nc   # Sample dataset (to be placed here)
│
│── scripts/		   # Directory for storing scripts
│   ├── Puglia_folium.py  # Main script to process and visualize data
│
│── output/		   # Directory where generated files are stored
│   ├── weather_data.json  # Exported JSON file
│   ├── mappa_interattiva.html # Interactive map
│
│── requirements.txt  # List of required dependencies
│── README.md         # Project documentation
```

## Installation

To install and set up the program, follow these steps:

1. Clone the repository from your GitHub account:
    ```sh
    git clone https://github.com/youraccount/your-repository.git
    ```

2. Navigate to the project directory:
    ```sh
    cd your-repository
    ```

3. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

4. Activate the virtual environment:
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```
    - On Windows:
        ```sh
        .\venv\Scripts\activate
        ```

5. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To use the script, follow these steps:

1. Ensure that you have a NetCDF (.nc) file containing ERA5 precipitation data inside the `data/` directory.
2. Run the script `Puglia_folium.py`:
    ```sh
    python scripts/Puglia_folium.py
    ```

### Key Code Elements

Below are the fundamental parts of the code necessary for understanding its core functionality:

- **Import necessary libraries:**
  ```python
  import sqlite3
  import xarray as xr
  import numpy as np
  import folium
  import json
  ```

- **Load the dataset:**
  ```python
  nc_file = "path_to_your_file.nc"  # Update this path with your actual file location
  ds = xr.open_dataset(nc_file)
  ```

- **Define Puglia boundaries and select nearest coordinates:**
  ```python
  lat_min, lat_max = 39.8, 42.2
  lon_min, lon_max = 15.0, 19.5

  lat_available = ds["lat"].values
  lon_available = ds["lon"].values

  lat_min_nearest = min(lat_available, key=lambda x: abs(x - lat_min))
  lat_max_nearest = min(lat_available, key=lambda x: abs(x - lat_max))
  lon_min_nearest = min(lon_available, key=lambda x: abs(x - lon_min))
  lon_max_nearest = min(lon_available, key=lambda x: abs(x - lon_max))
  ```

- **Extract R10mm values:**
  ```python
  if np.all(np.diff(ds["lat"].values) > 0):
      precip_puglia = ds["R10mm"].sel(lat=slice(lat_min_nearest, lat_max_nearest), lon=slice(lon_min_nearest, lon_max_nearest))
  else:
      precip_puglia = ds["R10mm"].sel(lat=slice(lat_max_nearest, lat_min_nearest), lon=slice(lon_min_nearest, lon_max_nearest))

  if "time" in ds.dims:
      precip_puglia = precip_puglia.mean(dim="time")
  ```

SQLite Database Structure for Precipitation Data
To efficiently store and query the precipitation data for visualization, the dataset is processed and saved into an SQLite database. The database consists of a single table, precipitation_data, which holds relevant climate metrics for the Puglia region. Below is the schema of the table:

### **SQLite Database Structure for Precipitation Data**

To efficiently store and query the precipitation data for visualization, the dataset is processed and saved into an SQLite database. The database consists of a single table, `precipitation_data`, which holds relevant climate metrics for the Puglia region. Below is the schema of the table:

#### **Table: `precipitation_data`**
| Column Name   | Data Type | Description |
|--------------|-----------|-------------|
| `id`         | INTEGER (PRIMARY KEY) | Unique identifier for each record |
| `latitude`   | REAL      | Latitude coordinate of the measurement location |
| `longitude`  | REAL      | Longitude coordinate of the measurement location |
| `R10mm`      | REAL      | Number of days with precipitation >10mm in the recorded period |
| `timestamp`  | TEXT      | Time of data recording (if available in the dataset) |

This structured approach allows easy querying, filtering, and visualization of precipitation trends in the Puglia region.

### **How to Read and Interpret the Interactive Map**
The interactive map generated by the script visualizes precipitation patterns in the Puglia region based on the **R10mm** metric. This metric represents the number of days with precipitation exceeding 10mm in a given period.

#### **Map Visualization Components**
- **Geographic markers:** Each data point on the map corresponds to a specific location in Puglia, identified by its latitude and longitude.
- **Intensity-based color coding:** All points are displayed in shades of **blue**, with the intensity increasing as the number of heavy rainfall days (`R10mm`) rises.  
  - **Light blue** → Low precipitation (`R10mm ≈ 0.2`, occasional rainfall)  
  - **Medium blue** → Moderate precipitation (`R10mm ≈ 0.8`, frequent rainfall)  
  - **Dark blue** → High precipitation (`R10mm ≥ 1.6`, prolonged heavy rainfall)  
- **Tooltip Information:** Hovering over a marker displays detailed information, including:
  - **Latitude and Longitude** (exact geographic location)
  - **Number of days with heavy rainfall (R10mm)**, ranging from 0 to 1.6 days
  - **Timestamp** (if available, showing the recording period)

### How to Extend the Code for Further Use

This script can be expanded for other meteorological applications:

- **Time Series Analysis**: Modify the script to analyze precipitation trends over time.
- **Different Climate Variables**: Adapt the script to process other variables like temperature, humidity, or wind speed.
- **Real-Time Data**: Integrate with online meteorological APIs to update precipitation data dynamically.
- **Machine Learning Integration**: Use precipitation data as input for predictive models to forecast rainfall patterns.
- **Web Dashboard**: Build a web-based dashboard using **Dash** or **Streamlit** to interactively explore precipitation trends.

## Conclusion

This project provides an in-depth analysis of precipitation patterns in the Puglia region using ERA5 data. The interactive map and exported data offer an effective way to visualize and analyze rainfall distribution across the area. Understanding R10mm values can aid in agricultural planning by helping mitigate risks associated with excessive rainfall. Feel free to contribute to the project or use it as a foundation for further meteorological studies.


