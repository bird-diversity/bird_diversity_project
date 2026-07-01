"""Train/test validation for cell-level Poisson GLM (80/20 split)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.model_selection import train_test_split

RANDOM_SEED = 42
MIN_LC_CELLS = 25
GRID_KM = 5.0
TEST_SIZE = 0.2

CORE = [
    "verbatimScientificName",
    "stateProvince",
    "individualCount",
    "decimalLatitude",
    "decimalLongitude",
    "eventDate",
]
ENV_NUM = [
    "avg_rad",
    "NDVI_raw",
    "elevation_meters",
    "Total_Aerosol_Extinction",
    "temp_mean",
    "rainfall",
]
ENV_CAT = ["LandCover_Class"]


def find_data_path() -> Path:
    candidates = [
        Path(__file__).resolve().parent / "SriLanka-Bird-Diversity-Dataset.csv",
        Path(__file__).resolve().parent.parent / "SriLanka-Bird-Diversity-Dataset.csv",
        Path(__file__).resolve().parent / "file6.csv",
        Path(__file__).resolve().parent / "final5.csv",
        Path("/home/dilusha/Downloads/SriLanka-Bird-Diversity-Dataset.csv"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("Could not locate SriLanka-Bird-Diversity-Dataset.csv")


def add_planar_grid_km(frame: pd.DataFrame, lon0: float, lat0: float, grid_km: float) -> pd.DataFrame:
    out = frame.copy()
    lat = out["decimalLatitude"].to_numpy()
    lon = out["decimalLongitude"].to_numpy()
    lat_rad = np.radians(lat)
    out["x_km"] = (lon - lon0) * 111.320 * np.cos(lat_rad)
    out["y_km"] = (lat - lat0) * 110.574
    out["grid_x"] = np.floor(out["x_km"] / grid_km).astype(int)
    out["grid_y"] = np.floor(out["y_km"] / grid_km).astype(int)
    out["cell_id"] = (
        out["stateProvince"].astype(str) + "|" + out["grid_x"].astype(str) + "_" + out["grid_y"].astype(str)
    )
    return out


def thin_per_species_cell(frame: pd.DataFrame, seed: int) -> pd.DataFrame:
    work = frame.copy()
    work["_thin_key"] = (
        work["stateProvince"].astype(str)
        + "|"
        + work["cell_id"].astype(str)
        + "|"
        + work["verbatimScientificName"].astype(str)
    )
    rng = np.random.default_rng(seed)
    work["_rand"] = rng.random(len(work))
    return work.sort_values("_rand").groupby("_thin_key", as_index=False).head(1).drop(columns=["_thin_key", "_rand"])


def build_cell_table(df_thin: pd.DataFrame) -> pd.DataFrame:
    num_for_agg = [c for c in ENV_NUM if c in df_thin.columns]
    if "NDVI" in df_thin.columns:
        num_for_agg = ["NDVI"] + [c for c in num_for_agg if c != "NDVI_raw"]

    agg_dict = {"verbatimScientificName": "nunique", "individualCount": "sum"}
    for c in num_for_agg:
        agg_dict[c] = "mean"

    gcell = df_thin.groupby("cell_id", as_index=False).agg(agg_dict)
    gcell = gcell.rename(columns={"verbatimScientificName": "species_richness", "individualCount": "sum_count_thin"})

    if "LandCover_Class" in df_thin.columns:
        mode_lc = (
            df_thin.groupby("cell_id")["LandCover_Class"]
            .agg(lambda s: s.mode().iloc[0] if not s.mode().empty else np.nan)
            .rename("LandCover_mode")
        )
        gcell = gcell.merge(mode_lc.reset_index(), on="cell_id", how="left")

    for c in ["species_richness", "NDVI"] + num_for_agg:
        if c in gcell.columns:
            gcell = gcell.dropna(subset=[c])
    return gcell


def prepare_glm_data(gcell: pd.DataFrame) -> pd.DataFrame:
    g_fit = gcell.copy()
    cont_terms = [
        c
        for c in ["NDVI", "avg_rad", "elevation_meters", "temp_mean", "rainfall", "Total_Aerosol_Extinction"]
        if c in g_fit.columns
    ]

    if "LandCover_mode" in g_fit.columns and "NDVI" in g_fit.columns:
        g_fit = g_fit.dropna(subset=["LandCover_mode", "NDVI"])
        vc = g_fit["LandCover_mode"].value_counts()
        keep_lc = vc[vc >= MIN_LC_CELLS].index
        if len(keep_lc) >= 2:
            g_fit = g_fit[g_fit["LandCover_mode"].isin(keep_lc)]
        else:
            raise ValueError("Too few cells per land-cover class for GLM.")

    need = ["species_richness"] + cont_terms
    if "LandCover_mode" in g_fit.columns:
        need.append("LandCover_mode")
    return g_fit.dropna(subset=[c for c in need if c in g_fit.columns]).copy()


def glm_formula(g_fit: pd.DataFrame) -> str:
    cont_terms = [
        c
        for c in ["NDVI", "avg_rad", "elevation_meters", "temp_mean", "rainfall", "Total_Aerosol_Extinction"]
        if c in g_fit.columns
    ]
    parts = []
    if "NDVI" in cont_terms:
        parts.append("NDVI")
    if "LandCover_mode" in g_fit.columns:
        parts.append("C(LandCover_mode)")
    for c in cont_terms:
        if c != "NDVI":
            parts.append(c)
    return "species_richness ~ " + " + ".join(parts)


def poisson_deviance(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.maximum(np.asarray(y_pred, dtype=float), 1e-10)
    mask = y_true > 0
    term = np.zeros_like(y_true, dtype=float)
    term[mask] = y_true[mask] * np.log(y_true[mask] / y_pred[mask]) - (y_true[mask] - y_pred[mask])
    term[~mask] = y_pred[~mask]
    return float(2.0 * np.sum(term))


def evaluate_split(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    residuals = y_true - y_pred
    mae = float(np.mean(np.abs(residuals)))
    rmse = float(np.sqrt(np.mean(residuals**2)))
    dev = poisson_deviance(y_true, y_pred)
    corr_pearson, _ = stats.pearsonr(y_true, y_pred)
    corr_spearman, _ = stats.spearmanr(y_true, y_pred)
    return {
        "MAE": mae,
        "RMSE": rmse,
        "Poisson_deviance": dev,
        "Pearson_r": float(corr_pearson),
        "Spearman_r": float(corr_spearman),
        "n": int(len(y_true)),
    }


def cox_snell_pseudo_r2(result) -> float:
    """Cox--Snell pseudo R² from GLM deviance."""
    return float(1.0 - np.exp((result.deviance - result.null_deviance) / result.nobs))


def test_deviance_pseudo_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Deviance-based pseudo R² on hold-out data vs intercept-only null."""
    y_true = np.asarray(y_true, dtype=float)
    y_bar = float(np.mean(y_true))
    y_pred = np.maximum(np.asarray(y_pred, dtype=float), 1e-10)
    y_bar = max(y_bar, 1e-10)
    d_null = poisson_deviance(y_true, np.full_like(y_true, y_bar))
    d_model = poisson_deviance(y_true, y_pred)
    return float(1.0 - d_model / d_null)


def main() -> dict:
    data_path = find_data_path()
    raw = pd.read_csv(data_path, low_memory=False)
    use_cols = [c for c in CORE + ENV_NUM + ENV_CAT if c in raw.columns]
    df = raw[use_cols].copy()

    df["eventDate"] = pd.to_datetime(df["eventDate"], errors="coerce")
    for c in ["decimalLatitude", "decimalLongitude", "individualCount"] + [x for x in ENV_NUM if x in df.columns]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["stateProvince"] = df["stateProvince"].astype(str).str.strip()
    df["verbatimScientificName"] = df["verbatimScientificName"].astype(str).str.strip()
    if "NDVI_raw" in df.columns:
        df["NDVI"] = df["NDVI_raw"] / 10000.0
    df = df.dropna(subset=["verbatimScientificName", "stateProvince", "decimalLatitude", "decimalLongitude", "eventDate"])
    df["individualCount"] = df["individualCount"].fillna(1.0).clip(lower=1.0)

    lon_ref = float(df["decimalLongitude"].median())
    lat_ref = float(df["decimalLatitude"].median())
    df = add_planar_grid_km(df, lon_ref, lat_ref, GRID_KM)
    df_thin = thin_per_species_cell(df, RANDOM_SEED)
    gcell = build_cell_table(df_thin)
    g_fit = prepare_glm_data(gcell)
    formula = glm_formula(g_fit)

    train_df, test_df = train_test_split(g_fit, test_size=TEST_SIZE, random_state=RANDOM_SEED)
    model = smf.glm(formula, data=train_df, family=sm.families.Poisson()).fit()

    train_pred = model.predict(train_df)
    test_pred = model.predict(test_df)

    train_metrics = evaluate_split(train_df["species_richness"].values, train_pred.values)
    test_metrics = evaluate_split(test_df["species_richness"].values, test_pred.values)

    full_fit = smf.glm(formula, data=g_fit, family=sm.families.Poisson()).fit(cov_type="HC1")

    results = {
        "data_path": str(data_path),
        "formula": formula,
        "n_cells_total": int(len(g_fit)),
        "n_train": int(len(train_df)),
        "n_test": int(len(test_df)),
        "train_fraction": 1.0 - TEST_SIZE,
        "test_fraction": TEST_SIZE,
        "random_seed": RANDOM_SEED,
        "train_metrics": train_metrics,
        "test_metrics": test_metrics,
        "cox_snell_train": cox_snell_pseudo_r2(model),
        "cox_snell_full_insample": cox_snell_pseudo_r2(full_fit),
        "deviance_pseudo_r2_test": test_deviance_pseudo_r2(
            test_df["species_richness"].values, test_pred.values
        ),
    }

    out_path = Path(__file__).resolve().parent / "poisson_glm_validation_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    main()
