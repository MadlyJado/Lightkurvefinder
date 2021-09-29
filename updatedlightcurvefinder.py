from platform import python_version

print(python_version())

import glob
import lightkurve as lk
import pathlib
import numpy as np

def filterLightCurves(lc):
    isGood = False
    for flux in lc.flux:
        if flux < 0.95:
            isGood = True
            break
def openLC(p):
    return lk.read(p).remove_nans().remove_outliers(sigma=6).normalize()

path = "TESS-Sector-5/*lc.fits"
txtPath = pathlib.Path("./interestingsystems.txt")

lcFiles = [f for f in glob.glob(path)]

Lcs = list(map(openLC, lcFiles))
print("Amount of LC Files: " + len(Lcs))
filteredLcs = [lc for lc in Lcs if filterLightCurves(lc)]
print("Amount of Filtered LCs: " + len(filteredLcs))

interesting_systems = []
for lc in filteredLcs:
    pg = lc.to_periodogram(method='bls', period=np.arange(0.3, 30, 0.01))
    if(pg.max_power > 100):
        interesting_systems.append(str(lc))
        print(pg.period_at_max_power)
        folded_lc = lc.fold(period=pg.period_at_max_power)
        binned_lc = folded_lc.bin(time_bin_size=5, time_bin_start=pg.period_at_max_power - 4)
        lc.scatter()
        pg.plot()
        print(lc.label, ": Folding on period ", pg.period_at_max_power)
        folded_lc.scatter()
        binned_lc.scatter()
    else:
        print(lc.label + " was discarded due to low pg power ", pg.max_power)

with open(str(txtPath.absolute()), 'w+') as f:
    f.writelines(interesting_systems)