import xarray as xr

# open a NetCDF file
df = xr.open_dataset("35633dd37ac7562c8bd6e2a9a69e45dd.nc")

# change to a pandas DataFrame
df = df.to_dataframe().reset_index()
print(df.head())

# save to a CSV file
df.to_csv("35633dd37ac7562c8bd6e2a9a69e45dd.csv", index=False)