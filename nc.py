import xarray as xr

# Open the NetCDF file
ds = xr.open_dataset("4c17bf031822a1954b59632b9581ae00.nc")

# convert to pandas DataFrame
df = ds.to_dataframe().reset_index()

# Save to CSV
df.to_csv("4c17bf031822a1954b59632b9581ae00.csv", index=False)