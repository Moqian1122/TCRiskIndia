import numpy as np
import pandas as pd

# Define India bounding box
lat_range = np.arange(6.0, 37.1, 0.5)
lon_range = np.arange(68.0, 97.1, 0.5)

# Create mesh grid of lat/lon
lat_grid, lon_grid = np.meshgrid(lat_range, lon_range)

# Flatten and combine into DataFrame
grid_df = pd.DataFrame({
    "Latitude": lat_grid.flatten(),
    "Longitude": lon_grid.flatten()
})

# Optional: Add ID
grid_df["ID"] = ["{}".format(i) for i in range(len(grid_df))]

# Reorder columns
grid_df = grid_df[["ID", "Latitude", "Longitude"]]

# Save to CSV
grid_df.to_csv("india_0.1deg_grid.csv", index=False)
