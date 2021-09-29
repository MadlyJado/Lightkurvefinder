# Credits to ineeve on github for this exoplanet finder script. 
# Link to repository: 
# https://github.com/ineeve/exoplanetFinder

from platform import python_version

print(python_version())
def filterLightCurves(lc):
    isGood = False
    for flux in lc.flux: 
        if flux < 0.95:
            isGood=True
            break

    return isGood
def openLCFile(f):
    return lk.open(f).PDCSAP_FLUX.remove_nans().remove_outliers(sigma=6).normalize()

import glob
import lightkurve as lk
import lightkurve.lightcurvefile as lcf
import pathlib
import numpy as np

path = "TESS-Sector-5/*lc.fits"
txtpath = pathlib.Path("./interestingsystems.txt")

lcFiles = [f for f in glob.glob(path)]

LCs = list(map(openLCFile, lcFiles))
print(len(LCs))
filteredLCs = [lc for lc in LCs if filterLightCurves(lc)]
print(len(filteredLCs))

interesting_systems = []
for lc in filteredLCs:
    pg = lc.to_periodogram(method="bls", period=np.arange(0.3, 30, 0.01))
    if (pg.max_power > 100):
        interesting_systems.append(str(lc))
        print(pg.period_at_max_power)
        folded_lc = lc.fold(period=pg.period_at_max_power)
        binned_lc = folded_lc.bin(binsize=5)  # Average 5 points per bin
        lc.scatter()
        pg.plot()
        print(lc.label, ": Folding on period ", pg.period_at_max_power)
        folded_lc.scatter()
        binned_lc.scatter()
    else:
        print(lc.label, " was discarded due to low pg power", pg.max_power)

with open(str(txtpath.absolute()), 'w+') as f:
    f.writelines(interesting_systems)