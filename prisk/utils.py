from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import re
from scipy.stats import norm
from shapely.geometry import Point

from prisk.firm import Holding
from prisk.asset import PowerPlant
from prisk.cyclone import CycloneExposure

def convert_to_continous_damage(damage_curves):
    continuous_curves = pd.DataFrame({"index": range(0, int(max((damage_curves["intensity"] + 0.01)*100)))})
    continuous_curves["index"] = continuous_curves["index"]/100
    continuous_curves.set_index("index", inplace=True)
    continuous_curves = continuous_curves.merge(damage_curves, how="left", left_index=True, right_on="intensity")
    continuous_curves.interpolate(method="linear", inplace=True)
    continuous_curves.set_index("intensity", inplace=True)
    return continuous_curves

damage_curves = pd.read_excel("../intensity_filled.xlsx")
power = pd.read_excel("../etc/power.xlsx")
indian_firms = pd.read_excel("../Data/Indian_firms.xlsx")
indian_firm_mapping = mapping = {row["name"]: row["clean"] for _, row in indian_firms[["name", "clean"]].iterrows()}
#power.drop(columns=[2], inplace=True)
continuous_curves = convert_to_continous_damage(damage_curves)
return_period_columns = [5, 10, 25, 50, 100, 200, 500, 1000]


def bootstrap_mean(data, column_name, samples=100):
    bootstrapped = data.sample(n=samples, replace=True)
    return bootstrapped[column_name].mean()


def plot_bootstrap(data, column_name):
    bootstraps = [bootstrap_mean(data, column_name, samples=100) for i in range(10000)]
    bootstraps = np.array(bootstraps)
    plt.hist(bootstraps, bins=50, density=True)
    plt.axvline(np.quantile(bootstraps, 0.01), color="red")
    plt.axvline(np.quantile(bootstraps, 0.99), color="red");
    plt.title("Bootstrapped mean of " + column_name)
    print("Width of CI: ", round(np.quantile(bootstraps, 0.95) - np.quantile(bootstraps, 0.05), 4))
    print("Mean of CI:  ", round(np.mean(bootstraps), 4))
    print("Std of CI:   ", round(np.std(bootstraps), 4))
    print("Q1:          ", round(np.quantile(bootstraps, 0.05), 4))
    print("Q99:         ", round(np.quantile(bootstraps, 0.95), 4))
    print("Skewness:    ", round(pd.Series(bootstraps).skew(), 4))
    print("Kurtosis:    ", round(pd.Series(bootstraps).kurtosis(), 4))


def plot_risk_factors(base_value, capital_damages, business_disruption, fair_premium, insurance_adjustment, npv):
    fig = go.Figure(go.Waterfall(
        name = "PRISK - Waterfall", 
        orientation = "v",
        measure = ["relative", "relative", "relative", "relative", "relative", "total"],
        x = ["Base Value", "Capital Damages", "Business disruptions", "Fair insurance premiums",
                "Insurance adjustments", "Adjusted Value"],
        textposition = "outside",
        text = ["{:,.2f}M".format(base_value/1e6), 
                "{:,.2f}M".format(capital_damages/1e6), 
                "{:,.2f}M".format(business_disruption/1e6), 
                "{:,.2f}M".format(fair_premium/1e6),
                "{:,.2f}M".format(abs(insurance_adjustment)/1e6),
                "{:,.2f}M".format(npv/1e6)],
        y = [base_value, 
            -capital_damages,
            -business_disruption,
            -fair_premium, 
            -insurance_adjustment,
            npv],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
    ))

    fig.update_layout(
            title = "PRISK - Waterfall chart",
            showlegend = False,
            template="simple_white",
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title="Asset value impacts",
            yaxis_title="Value",
            yaxis_tickprefix="$",
            yaxis_tickformat=",",
            yaxis_showgrid=True,
    )
    return fig


def clean_owner_name(owner):
    owner = re.sub(r'\[[^)]*\]', "", owner)
    owner = owner.strip()
    owner = owner.title()
    if owner in indian_firm_mapping:
        owner = indian_firm_mapping[owner]
        return owner
    return owner

def extract_firms(assets, damage_curves=None, leverage_ratios={}, discount_rate=0.05, unit_price=60, margin=0.2, time_horizon=25):
    assets.sort_values("Owner", inplace=True)
    if damage_curves is None:
        damage_curves = continuous_curves
    assets.loc[:, "asset"] = assets.apply(lambda x: 
                                          PowerPlant(
                                                name=x["Plant / Project name"],
                                                cyclone_damage_curve=damage_curves,
                                                cyclone_exposure=[CycloneExposure(return_period, x[return_period]) 
                                                                for return_period in return_period_columns if x[return_period] > 0],
                                                production_path=np.repeat(x["Capacity (MW)"]*24*365, time_horizon),
                                                replacement_cost=x["Value"],
                                                unit_price=unit_price,
                                                discount_rate=discount_rate,
                                                margin=margin,
                                          ), axis=1)
    list_of_owners = []
    for owners in assets["Owner"].unique():
        if pd.isna(owners):
            continue
        owners = owners.split(";")
        for o in owners:
            o = clean_owner_name(o)
            list_of_owners.append(o)
    list_of_owners = list(OrderedDict.fromkeys(list_of_owners))
    owner_map = {owner: Holding(owner, leverage_ratio=leverage_ratios.get(owner)) for owner in list_of_owners}
    holdings = []
    for i, owner in enumerate(assets["Owner"]):
        if pd.isna(owner):
            continue
        for o in owner.split(";"):
            share = re.findall(r"\[(.*?)\]", o)
            if share:
                share = float(share[0].replace("%", ""))/100
            else: share = 1
            holding = owner_map[clean_owner_name(o)]
            holding.add_asset(assets.loc[i, "asset"], share)
            holdings.append(holding)
    return list(OrderedDict.fromkeys(holdings))

def link_basins(data, basins, visualize=True, save=False):

    geo_data = gpd.GeoDataFrame(data, 
                            geometry=gpd.points_from_xy(data.Longitude, data.Latitude),
                            crs="EPSG:4326")
    
    basins = gpd.read_file(basins)
        
    geo_data = geo_data.reset_index(drop=True)
    basins = basins.reset_index(drop=True)
    # fix the crs issue if they are not the same
    if basins.crs != geo_data.crs:
        basins = basins.to_crs(geo_data.crs)
    
    basins["ID"] = basins.index.astype(str)

    get_colors = lambda n: [(50/256, 100/256, np.random.choice(range(150))/256) for _ in range(n)]
    basins['color'] = get_colors(len(basins))

    # Perform spatial join to link data points with basins
    data_merged = geo_data.sjoin(basins[["ID", "geometry"]], how="left")
    # Handle cases where no basin is found
    data_merged["ID"] = data_merged["ID"].apply(lambda x: str(int(x)) if not pd.isnull(x) else pd.NA)
    data_merged.drop(columns=["index_right"], inplace=True, errors="ignore")

    
    if visualize:
        basins.plot(color=basins.color, figsize=(20, 20))
        plt.scatter(data.Longitude, data.Latitude, c="red", s=50)
        if save:
            plt.savefig('map.png', transparent=True)
    return data_merged, basins

def merton_probability_of_default(V, sigma_V, D, r=0, T=1):
    """
    Calculate the probability of default using the Merton model.

    Parameters:
    V (float): Current value of the company's assets.
    sigma_V (float): Volatility of the company's assets.
    D (float): Face value of the company's debt.
    r (float): Risk-free interest rate.
    T (float): Time to maturity of the debt.

    Returns:
    float: Probability of default.
    """
    # In your `merton_probability_of_default` function:
    
    V_safe = np.maximum(V, 1e-10)
    D_safe = np.maximum(D, 1e-10)
    ratio = V_safe / D_safe

    d2 = (np.log(ratio) + (r - 0.5 * sigma_V**2) * T) / (sigma_V * np.sqrt(T))
    PD = norm.cdf(-d2)

    # Element-wise clamp for arrays
    PD = np.clip(PD, 0, 1)

    return PD