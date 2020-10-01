* I'm sharing this as a github repo for other members of BAS who need it. Feel free to fork/raise issues.
* This is a simple module that I use for getting the mean surface temperature
for a given year range, for a given model.
* It uses [baspy](https://github.com/scotthosking/baspy).
* You need access to JASMIN, and the CEDA archive in order for it to find the data.
* Requires a recent (v0.15.1) version of xarray for weighted averages to work.

Usage example:
```
from mean_surface_temp import get_global_mean
result = get_global_mean(
    'UKESM1-0-LL',
    'historical',
    'r11i1p1f2',
    [slice(1850,1900), slice(1950,2000)],
    'tas'
)
```

