from climada.hazard import TCTracks, Centroids, TropCyclone
from pathos.pools import ProcessPool as Pool

pool = Pool() # start a pathos pool

lon_min, lat_min, lon_max, lat_max = 8, 36, 68, 98
centr = Centroids.from_pnt_bounds((lon_min, lat_min, lon_max, lat_max), 0.1)

tc_track = TCTracks.from_ibtracs_netcdf(provider='newdelhi', year_range=(1992, 1994), basin='NI')
tc_track.equal_timestep(pool=pool)
tc_track.calc_perturbed_trajectories(pool=pool) # OPTIONAL: if you want to generate a probabilistic set of TC tracks.
# tc_track.apply_climate_scenario_knu(ref_year = 2080, rcp_scenario = 45) # OPTIONAL: if you want to apply a climate scenario to the tracks.

tc_haz = TropCyclone.from_tracks(tc_track, centroids=centr, pool=pool)
tc_haz.check()

pool.close()
pool.join()