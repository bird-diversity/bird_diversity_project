---
license: cc-by-4.0
task_categories:
  - tabular-classification
  - other
language:
  - en
tags:
  - biology
  - ecology
  - birds
  - sri-lanka
  - biodiversity
  - species-distribution-modeling
  - environmental-variables
  - citizen-science
  - remote-sensing
size_categories:
  - 1M<n<10M
pretty_name: Sri Lanka Bird Diversity Dataset
dataset_info:
  features:
    - name: index
      dtype: int64
    - name: verbatimScientificName
      dtype: string
    - name: stateProvince
      dtype: string
    - name: individualCount
      dtype: float64
    - name: decimalLatitude
      dtype: float64
    - name: decimalLongitude
      dtype: float64
    - name: eventDate
      dtype: string
    - name: avg_rad
      dtype: float64
    - name: NDVI_raw
      dtype: float64
    - name: LandCover_Class
      dtype: int64
    - name: elevation_meters
      dtype: int64
    - name: Carbon_Mass
      dtype: float64
    - name: Dust_Mass
      dtype: float64
    - name: SO2_Mass
      dtype: float64
    - name: Sulfate_Mass
      dtype: float64
    - name: Sea_Salt_Mass
      dtype: float64
    - name: Total_Aerosol_Extinction
      dtype: float64
    - name: temp_mean
      dtype: float64
    - name: rainfall
      dtype: float64
    - name: wind_mean
      dtype: float64
    - name: humid_mean
      dtype: float64
    - name: shortwave_radiation
      dtype: float64
    - name: lka_general_2020
      dtype: float64
    - name: NDVI
      dtype: float64
---

# Sri Lanka Bird Diversity Dataset

Companion dataset for the paper **["How Environment and Urbanization Shape Bird Diversity in Sri Lanka"](paper_overleaf.tex)**.

| Resource | Link |
|----------|------|
| **Dataset (Hugging Face)** | [DilushaChandrasiri/SriLanka-Bird-Diversity-Dataset](https://huggingface.co/datasets/DilushaChandrasiri/SriLanka-Bird-Diversity-Dataset) |
| **Code & analysis** | [bird-diversity/bird_diversity_project](https://github.com/bird-diversity/bird_diversity_project) |
| **Data dictionary** | [data_dictionary.md](data_dictionary.md) |
| **Feature metadata** | [metadata.md](metadata.md) |

## Dataset Title

**Sri Lanka Bird Diversity Dataset with Environmental, Climate, and Anthropogenic Features**

## Dataset Description

This dataset integrates **1,552,048** bird occurrence records from **429** species across **25** administrative districts in Sri Lanka, spanning **2014–2024**. Each record links a citizen-science observation to satellite-derived vegetation, land cover, elevation, climate, aerosol pollution, nighttime lights (ALAN), and population-density variables at the observation location and month.

The dataset supports the integrated analytical framework described in our study, which examines how environmental conditions, habitat structure, and urbanization jointly shape avian diversity in a tropical island system. Key findings from the associated research include:

- **Land-cover type** (IGBP classification) is a stronger predictor of bird diversity than individual continuous variables such as NDVI or temperature alone.
- **Artificial Light At Night (ALAN)**, proxied by `avg_rad`, shows scale-dependent urbanization effects and is associated with biotic homogenization—high abundance of a few generalist species alongside reduced overall richness.
- **Spatial thinning** and grid-based aggregation (2 km, 5 km, 10 km) produce stable island-wide species counts and comparable district-level richness estimates.

The released CSV (`SriLanka-Bird-Diversity-Dataset.csv`) is the harmonized, observation-level integration used as input to preprocessing and modelling in the repository. For full reproducibility, see the notebooks under `01_data_collection/`, `02_data_preprocessing/`, and `stateProvince/`.

## Dataset Features

| Feature | Type | Description | Unit / Scale |
|---------|------|-------------|--------------|
| `index` | int | Row identifier | — |
| `verbatimScientificName` | string | Scientific name of the observed species | — |
| `stateProvince` | string | Administrative district of the observation | — |
| `individualCount` | float | Number of individuals recorded | Count |
| `decimalLatitude` | float | Observation latitude (WGS84) | Decimal degrees |
| `decimalLongitude` | float | Observation longitude (WGS84) | Decimal degrees |
| `eventDate` | date | Date of observation | `YYYY-MM-DD` |
| `avg_rad` | float | VIIRS nighttime radiance (ALAN / urbanization proxy) | nW/cm²/sr |
| `NDVI_raw` | float | Raw MODIS NDVI (storage-scaled) | −10000 to +10000 |
| `LandCover_Class` | int | MODIS IGBP land-cover class | 1–17 |
| `elevation_meters` | int | SRTM elevation above sea level | Meters |
| `Carbon_Mass` | float | Black carbon surface mass concentration | µg/m³ |
| `Dust_Mass` | float | Dust surface mass concentration | µg/m³ |
| `SO2_Mass` | float | Sulfur dioxide surface mass concentration | µg/m³ |
| `Sulfate_Mass` | float | Sulfate surface mass concentration | µg/m³ |
| `Sea_Salt_Mass` | float | Sea-salt surface mass concentration | µg/m³ |
| `Total_Aerosol_Extinction` | float | Total aerosol optical depth (AOD) | Dimensionless |
| `temp_mean` | float | Mean daily temperature | °C |
| `rainfall` | float | Total daily rainfall | mm/day |
| `wind_mean` | float | Mean daily wind speed | m/s |
| `humid_mean` | float | Mean daily relative humidity | % |
| `shortwave_radiation` | float | Mean daily shortwave radiation | kWh/m²/day |
| `lka_general_2020` | float | Population density grid (Sri Lanka 2020) | Persons/km² |
| `NDVI` | float | Scaled vegetation index (`NDVI_raw / 10000`) | −1.0 to 1.0 |

### Dataset Statistics

| Statistic | Value |
|-----------|-------|
| Total records | 1,552,048 |
| Unique species | 429 |
| Districts covered | 25 |
| Date range | 2014-01-01 – 2024-12-31 |
| Land-cover classes present | 2, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17 |
| Missing values | None (after integration pipeline) |

### Spatial Coverage Note

Observations are unevenly distributed: western and southern coastal areas account for ~56% of records, central ~26%, northern ~16%, and eastern ~2%. Spatial thinning and effort correction are recommended before richness comparisons (see [Usage](#usage)).

### IGBP Land-Cover Classes

`LandCover_Class` follows the MODIS MCD12Q1 IGBP scheme. Full class definitions are in [metadata.md](metadata.md). Examples present in this dataset:

| Code | Habitat |
|------|---------|
| 2 | Evergreen Broadleaf Forests |
| 7 | Open Shrublands |
| 8 | Woody Savannas |
| 9 | Savannas |
| 10 | Grasslands |
| 11 | Permanent Wetlands |
| 12 | Cropland |
| 13 | Urban and Built-up Lands |
| 14 | Cropland / Natural Mosaics |
| 16 | Barren |
| 17 | Water Bodies |

## Data Source

| Component | Source | Reference |
|-----------|--------|-----------|
| Bird occurrences | [GBIF](https://www.gbif.org/) via [eBird](https://ebird.org/) citizen-science platform | [GBIF dataset](https://www.gbif.org/dataset/4fa7b334-ce0d-4e88-aaae-2e0c138d049e) |
| NDVI | MODIS MOD13Q1 | [NASA LP DAAC](https://lpdaac.usgs.gov/products/mod13q1v061/) |
| Land cover | MODIS MCD12Q1 (IGBP, 17 classes) | [NASA LP DAAC](https://lpdaac.usgs.gov/products/mcd12q1v061/) |
| Nighttime lights (ALAN) | VIIRS Day/Night Band | [EOG VIIRS VNL](https://eogdata.mines.edu/products/vnl/) |
| Climate | NASA POWER API | [POWER documentation](https://power.larc.nasa.gov/docs/services/api/) |
| Aerosols & air pollution | MERRA-2 reanalysis (`tavgM_2d_aer_Nx`) | [NASA GES DISC](https://disc.gsfc.nasa.gov/datasets?project=MERRA-2) |
| Elevation | SRTM | [NASA Earthdata SRTM](https://www.earthdata.nasa.gov/data/catalog/lpcloud-srtmgl1-003) |
| Population density | `lka_general_2020` (HDX / WorldPop grid) | [HDX Sri Lanka 2020](https://data.humdata.org/) |

## Preprocessing Steps

The integration and cleaning pipeline (documented in `02_data_preprocessing/` and the paper Methodology section) includes:

1. **Record cleaning** — Incomplete, duplicate, and unreliable GBIF/eBird records were removed.
2. **Spatiotemporal matching** — Bird occurrences were merged with environmental layers by geographic coordinates and **observation month**, so dynamic variables (NDVI, climate, aerosols, ALAN) reflect conditions at the time of observation.
3. **Cloud-quality filtering** — Records with zero cloud-free VIIRS coverage (`cf_cvg = 0`) were excluded during ALAN integration.
4. **Population assignment** — `lka_general_2020` was spatially joined from the 2020 population grid; missing values were filled via nearest-neighbour lookup where needed.
5. **NDVI scaling** — `NDVI = NDVI_raw / 10000`.
6. **Transformation (analysis stage)** — In downstream analyses, NDVI and ALAN were Yeo–Johnson transformed and abundance was log-transformed where appropriate; these transforms are **not** applied in the released CSV.

### Recommended downstream preprocessing

For analyses mirroring the paper:

- Apply **grid-based spatial thinning** (one record per species per grid cell per district; 5 km baseline).
- Aggregate continuous covariates by cell mean and categorical land cover by modal class.
- Use **effort-corrected metrics** (rarefied richness, occupancy per 100 cells) for temporal comparisons.

See `stateProvince/stateprovince_species_spatial_thinning_analysis.ipynb` and related notebooks.

## Usage

### Load from Hugging Face

```python
from datasets import load_dataset

ds = load_dataset("DilushaChandrasiri/SriLanka-Bird-Diversity-Dataset", split="train")
print(ds)
print(ds[0])
```

### Load with Pandas

```python
import pandas as pd

df = pd.read_csv("SriLanka-Bird-Diversity-Dataset.csv")
print(f"Records: {len(df):,} | Species: {df['verbatimScientificName'].nunique()}")
df["eventDate"] = pd.to_datetime(df["eventDate"])
print(df.head())
```

### Species richness by land cover

```python
import pandas as pd

df = pd.read_csv("SriLanka-Bird-Diversity-Dataset.csv")
richness_by_cover = (
    df.groupby("LandCover_Class")["verbatimScientificName"]
    .nunique()
    .sort_values(ascending=False)
)
print(richness_by_cover)
```

### Poisson GLM (cell-level, after thinning & aggregation)

```python
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Expect a pre-aggregated grid-cell table (see repo notebooks)
cells = pd.read_csv("thinned_5km_cell_summary.csv")  # produced by analysis pipeline

model = smf.glm(
    "species_richness ~ NDVI + avg_rad + temp_mean + C(LandCover_Class)",
    data=cells,
    family=sm.families.Poisson(),
)
result = model.fit(cov_type="HC1")  # robust SEs as in the paper
print(result.summary())
```

### Intended use cases

| Task | Target | Suggested features |
|------|--------|-------------------|
| Species distribution modelling | `verbatimScientificName` | NDVI, land cover, climate, elevation, ALAN |
| Abundance / count modelling | `individualCount` | Environmental + anthropogenic covariates |
| Habitat association analysis | Richness or counts | `LandCover_Class`, NDVI, elevation |
| Urbanization impact | Community metrics | `avg_rad`, aerosol variables |
| Temporal trend analysis | Yearly richness | Effort-corrected grid metrics (see repo) |

## Repository Structure

```
bird_diversity_project/
├── 01_data_collection/     # Raw source integration (GBIF, MODIS, VIIRS, MERRA-2, POWER, population)
├── 02_data_preprocessing/  # Cleaning, merging, final dataset construction
├── 03_data_analysis/       # Exploratory and bivariate analyses
├── 04_time_series_analysis/# Temporal NDVI, climate, ALAN, diversity trends
├── stateProvince/          # District-level thinning, GLMs, beta diversity, temporal metrics
├── EDA/                    # Relationship exploration
├── data_dictionary.md      # Column definitions
├── metadata.md             # Per-source feature documentation
└── paper_overleaf.tex      # LaTeX manuscript
```

## Authors

Dilusha Chandrasiri, Maneesha Herath, Yasith Hewarathna, Muditha Herath, Gishan Bandara, Madara Mendis, Nathali Athukorala, Nisansa de Silva, and Sandareka Wickramanayake

Dept. of Computer Science & Engineering, University of Moratuwa, Sri Lanka

## License

This dataset is released under the **[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)** license.

You are free to share and adapt the material for any purpose, provided you give appropriate credit and indicate if changes were made.

## Citation

If you use this dataset or code, please cite:

```bibtex
@misc{chandrasir2026sri_lanka_bird_diversity,
  title        = {Sri Lanka Bird Diversity Dataset with Environmental, Climate, and Anthropogenic Features},
  author       = {Chandrasiri, Dilusha and Herath, Maneesha and Hewarathna, Yasith and Herath, Muditha and Bandara, Gishan and Mendis, Madara and Athukorala, Nathali and de Silva, Nisansa and Wickramanayake, Sandareka},
  year         = {2026},
  publisher    = {Hugging Face},
  howpublished = {\url{https://huggingface.co/datasets/DilushaChandrasiri/SriLanka-Bird-Diversity-Dataset}},
  license      = {CC-BY-4.0}
}
```

```bibtex
@inproceedings{chandrasir2026environment_urbanization_birds,
  title     = {How Environment and Urbanization Shape Bird Diversity in Sri Lanka},
  author    = {Chandrasiri, Dilusha and Herath, Maneesha and Hewarathna, Yasith and Herath, Muditha and Bandara, Gishan and Mendis, Madara and Athukorala, Nathali and de Silva, Nisansa and Wickramanayake, Sandareka},
  year      = {2026},
  note      = {Dept. of Computer Science \& Engineering, University of Moratuwa, Sri Lanka}
}
```

Please also acknowledge the underlying data providers: **GBIF**, **eBird**, **NASA** (MODIS, MERRA-2, POWER, SRTM), **EOG/VIIRS**, and **HDX/WorldPop**.
