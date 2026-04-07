import pandas as pd
import numpy as np


def main() -> None:
    final_path = r"d:\population data\final4.csv"
    density_path = r"d:\population data\lka_general_2020.csv"
    output_path = r"d:\population data\final5.csv"

    final_df = pd.read_csv(final_path)
    dens_df = pd.read_csv(density_path)

    dens_df = dens_df[["longitude", "latitude", "lka_general_2020"]].copy()

    final_df["decimalLongitude"] = pd.to_numeric(final_df["decimalLongitude"], errors="coerce")
    final_df["decimalLatitude"] = pd.to_numeric(final_df["decimalLatitude"], errors="coerce")
    dens_df["longitude"] = pd.to_numeric(dens_df["longitude"], errors="coerce")
    dens_df["latitude"] = pd.to_numeric(dens_df["latitude"], errors="coerce")
    dens_df["lka_general_2020"] = pd.to_numeric(dens_df["lka_general_2020"], errors="coerce")

    # First try exact coordinate match.
    merged = final_df.merge(
        dens_df,
        how="left",
        left_on=["decimalLongitude", "decimalLatitude"],
        right_on=["longitude", "latitude"],
    )

    # Fill unmatched rows with nearest density point when available.
    missing_mask = (
        merged["lka_general_2020"].isna()
        & merged["decimalLongitude"].notna()
        & merged["decimalLatitude"].notna()
    )

    if missing_mask.any():
        try:
            from scipy.spatial import cKDTree

            ref_points = dens_df[["longitude", "latitude"]].to_numpy()
            query_points = merged.loc[
                missing_mask, ["decimalLongitude", "decimalLatitude"]
            ].to_numpy()

            tree = cKDTree(ref_points)
            dist, idx = tree.query(query_points, k=1)

            # 0.02 degrees is roughly ~2 km; adjust if needed.
            max_dist = 0.02
            nearest_vals = np.where(
                dist <= max_dist,
                dens_df["lka_general_2020"].to_numpy()[idx],
                np.nan,
            )

            merged.loc[missing_mask, "lka_general_2020"] = nearest_vals
        except ImportError:
            print("scipy not installed. Only exact matches were applied.")
            print("Install scipy with: pip install scipy")

    merged = merged.drop(columns=["longitude", "latitude"], errors="ignore")
    merged.to_csv(output_path, index=False)

    assigned = merged["lka_general_2020"].notna().sum()
    print(f"Saved: {output_path}")
    print(f"Density assigned for {assigned} / {len(merged)} rows")


if __name__ == "__main__":
    main()
