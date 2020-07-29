import baspy as bp
import numpy as np
import xarray as xr
from pathlib import Path
import pandas as pd
import logging
from typing import List

# load the baspy catalogue
df = bp.catalogue(dataset="cmip6", CMOR="Amon")


def get_global_mean(
    Model: str,
    Experiment: str,
    RunID: str = None,
    year_ranges: List[slice] = [slice(1850, 1950), slice(2000, 2010)],
    var: str = "tas",
) -> List[float]:
    """Get area weighted global mean values for a CMIP6 run for year slices.

    The actual calculation is all done by xarray. Most of this code is a baspy
     wrapper.

    A match is looked for in the baspy catalogue, then the global surface mean
     temperature is calculated from atmospheric monthly data.
    Only tested with CMIP6.
    Input:
        Model, Experiment RunID --- same meaning as in baspy module
        year_ranges --- a list of slices
          specifying years (as integers) between which to average,
          e.g.  [slice(1850, 1950), slice(2000, 2010)],
        var --- the variable to be averaged e.g. 'tas'

    Returned list will have same length as year_ranges.
    Returns list of NaN if no match is found.
    """
    row = df[
        (df["Model"] == Model)
        & (df["Experiment"] == Experiment)
        & (df["Var"] == var)
    ]
    if RunID is not None:
        row = row[row["RunID"] == RunID]

    if row.shape[0] != 1:
        logging.warning(
            "Specification in get_global_mean does not select exactly one row in the baspy catalogue."
        )
        return [np.nan] * len(year_ranges)

    filenames = bp.get_files(row)
    yearly_means = []
    for filename in filenames:
        try:
            with xr.open_dataset(filename, use_cftime=True) as ds:
                weights = np.cos(np.deg2rad(ds.lat))
                weights.name = "weights"
                yearly_means.append(
                    ds.groupby("time.year")
                    .mean()
                    .weighted(weights)
                    .mean(("lat", "lon"))
                )
        except FileNotFoundError:
            logging.warning(f"{filename} not found")
            return [np.nan] * len(year_ranges)

    yearly_means = xr.concat(yearly_means, dim="time")
    decadal_means = [
        yearly_means.sel(year=year_range).mean()[var].values
        for year_range in year_ranges
    ]

    return decadal_means


def get_model_resolution(Model: str, Var: str = "tas") -> dict:
    """Get latitude and longitude grid-spacing from a model string"""
    row = df[
        (df["Var"] == Var)
        & (df["Model"] == Model)
        & (df["Experiment"] == "historical")
    ].iloc[0]
    filenames = bp.get_files(row)
    filename = filenames[0]
    with xr.open_dataset(filename, decode_times=False) as ds:
        try:
            lat = np.sort(ds.lat.values[0:2])
            lon = np.sort(ds.lon.values[0:2])
        except AttributeError:
            breakpoint()
    return {"lat": lat[1] - lat[0], "lon": lon[1] - lon[0]}


if __name__ == "__main__":
    print("testing")
    reduced_list_path = Path("UMR_list-CMIP6_day.txt")
    used_models = pd.read_csv(
        reduced_list_path,
        delimiter="\t",
        names=["Model", "UMR", "Experiment", "RunID"]
    )
    print(used_models)
    print(get_model_resolution(Model=used_models.iloc[0]["Model"],))
    print(
        get_global_mean(
            Model=used_models.iloc[0]["Model"],
            Experiment=used_models.iloc[0]["Experiment"],
            RunID=used_models.iloc[0]["RunID"],
            year_ranges=[slice(1850, 1950), slice(2000, 2010)],
            var="tas",
        )
    )
    print(
        get_global_mean(
            Model=used_models.iloc[0]["Model"],
            Experiment="piControl",
            RunID=used_models.iloc[0]["RunID"],
            year_ranges=[slice(None, None)],
            var="tas",
        )
    )
