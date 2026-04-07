# Temporal Occupancy Analysis: What Went Wrong and How It Was Fixed

## Background
The original temporal notebook analysis used raw yearly counts:
- Number of occupied cells
- Number of observed species (richness)

These counts increased over time, but this did not necessarily mean bird populations increased.

## What went wrong before
The earlier interpretation mixed two signals:
1. Ecological signal (true distribution/occupancy changes)
2. Observation effort signal (more people reporting over time)

Because reporting effort grew strongly across years, raw occupied-cell and raw richness trends were biased upward.

## Why the old graph was misleading
If sampled cells per year increase, then both occupied cells and observed richness usually increase even when the underlying ecology is stable.

In short, the old trend mostly reflected effort expansion, not true biodiversity growth.

## How it was fixed
The notebook was changed to effort-corrected temporal metrics.

### 1) Rarefied annual richness
Method:
- For each year, create species sets per grid cell.
- Find the minimum number of sampled cells across years.
- Randomly sample that same number of cells from each year (without replacement), many times.
- Compute median richness and uncertainty intervals from these repeats.

Reasoning:
This puts all years on equal sampling effort, so year-to-year richness is comparable.

### 2) District richness standardized by effort
Method:
- Compute district-year richness and sampled cells.
- Standardize as richness per 100 sampled cells.

Formula:
richness per 100 cells = 100 x richness / sampled cells

Reasoning:
Districts with different or changing effort become more comparable.

### 3) Species occupancy on a stable panel of cells
Method:
- Keep only cells observed in many years (stable panel).
- For each species-year, compute occupied panel cells.
- Convert to occupancy rate percent using panel sampled cells in that year.

Formula:
occupancy rate percent = 100 x occupied panel cells / panel sampled cells

Reasoning:
This reduces artificial trend inflation from continuously adding new sampling locations.

## What changed in the notebook
File updated: stateProvince/temporal_occupancy_richness_analysis.ipynb

- Cell 1: Description updated to effort-corrected framing.
- Cell 5: Added effort trend, rarefied richness, and uncertainty intervals.
- Cell 6: Replaced raw district richness trend with richness per 100 sampled cells.
- Cell 7: Replaced raw occupied-cell trend with occupancy rate on stable panel cells.

## Outcome after fix
- Sampling effort still rises sharply over time.
- Effort-corrected richness is more stable and biologically plausible.
- District and species trends are now interpreted as standardized indices, not raw observation totals.

## Remaining caveat
This is a strong improvement, but still an index-style correction.
A full detectability model (for example dynamic occupancy modeling with explicit detection probability) would be the next step for strongest causal inference.
