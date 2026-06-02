"""
Process PISA 2022 student questionnaire data into pisa_constructs.json.

Download from: https://www.oecd.org/en/data/datasets/pisa-2022-database.html
File needed:   STU_QQQ_SAS.zip  (student questionnaire, SAS format)
               or the SPSS equivalent STU_QQQ_SPSS.zip

Install deps:  pip install pyreadstat pandas numpy
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

RAW_FILE = Path(__file__).parent / "raw" / "STU_QQQ.sav"
OUT_FILE = Path(__file__).parent / "pisa_constructs.json"

# PISA 2022 variable names for SRL-relevant constructs
# Full codebook: Table of Contents in the PISA 2022 Technical Report
CONSTRUCT_VARS = {
    "Motivation":             ["ST036Q01TA", "ST036Q02TA", "ST036Q03TA", "ST036Q04TA"],  # Intrinsic motivation (math)
    "Metacog. monitoring":    ["ST164Q01IA", "ST164Q02IA", "ST164Q03IA", "ST164Q04IA"],  # Understanding/monitoring
    "Metacog. planning":      ["ST165Q01IA", "ST165Q02IA", "ST165Q03IA", "ST165Q04IA"],  # Elaboration strategies
    "Emotion regulation":     ["ST188Q01HA", "ST188Q02HA", "ST188Q03HA", "ST188Q06HA"],  # Emotion regulation
    "Self-efficacy":          ["ST196Q01HA", "ST196Q02HA", "ST196Q03HA", "ST196Q04HA"],  # Math self-efficacy
    "Test anxiety":           ["ST118Q01NA", "ST118Q02NA", "ST118Q03NA", "ST118Q04NA"],  # Test anxiety
}

CONSTRUCT_LABELS = list(CONSTRUCT_VARS.keys())

# KMeans-derived cluster definitions based on the six constructs
# Profiles match the KU Leuven behavioral clusters
PROFILE_LABELS = ["High SRL", "Surface learner", "Anxious striver", "Disengaged"]


def load_pisa(path: Path) -> pd.DataFrame:
    df, meta = pyreadstat.read_sav(str(path), apply_value_formats=False)
    return df


def scale_mean(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    """Mean across columns, scaled to 0-100."""
    present = [c for c in cols if c in df.columns]
    if not present:
        raise KeyError(f"None of {cols} found in dataframe. Check variable names against the PISA codebook.")
    raw = df[present].mean(axis=1)
    # PISA Likert items are typically 1-4; rescale to 0-100
    return ((raw - 1) / 3 * 100).round(1)


def assign_profiles(construct_df: pd.DataFrame) -> pd.Series:
    """
    Simple rule-based profile assignment matching the four-cluster solution.
    Replace with sklearn KMeans on the actual data for a proper fit.
    """
    hi_srl  = (construct_df["Self-efficacy"] > 65) & (construct_df["Metacog. planning"] > 60) & (construct_df["Test anxiety"] < 50)
    anxious = (construct_df["Test anxiety"] > 65) & (construct_df["Self-efficacy"] < 60)
    diseng  = (construct_df["Motivation"] < 35) & (construct_df["Metacog. monitoring"] < 35)

    labels = pd.Series("Surface learner", index=construct_df.index)
    labels[diseng]  = "Disengaged"
    labels[anxious & ~diseng] = "Anxious striver"
    labels[hi_srl]  = "High SRL"
    return labels


def build_country_rows(df: pd.DataFrame, construct_scores: pd.DataFrame) -> list[dict]:
    rows = []
    country_col = "CNT"
    name_col    = "CNTRYID"  # numeric; map via ISO codes below

    for cnt, grp in construct_scores.groupby(df[country_col]):
        means = grp[CONSTRUCT_LABELS].mean().round(1).tolist()
        rows.append({"code": cnt, "scores": means})

    rows.sort(key=lambda r: r["code"])
    return rows


def main():
    if not RAW_FILE.exists():
        print(f"Raw file not found: {RAW_FILE}")
        print("Download STU_QQQ_SPSS.zip from the PISA 2022 database and extract to data/raw/")
        sys.exit(1)

    print("Loading PISA 2022 data (this may take a minute)...")
    df = load_pisa(RAW_FILE)
    print(f"  {len(df):,} students loaded")

    construct_scores = pd.DataFrame({
        label: scale_mean(df, vars_)
        for label, vars_ in CONSTRUCT_VARS.items()
    })

    profiles = assign_profiles(construct_scores)
    construct_scores["profile"] = profiles

    # Per-profile means (for radar chart)
    profile_means = []
    for label in PROFILE_LABELS:
        grp = construct_scores[construct_scores["profile"] == label]
        profile_means.append(grp[CONSTRUCT_LABELS].mean().round(1).tolist())

    country_rows = build_country_rows(df, construct_scores)

    out = {
        "meta": {
            "cycle": "PISA 2022",
            "students": len(df),
            "countries": len(set(df["CNT"])),
            "source": "https://www.oecd.org/en/data/datasets/pisa-2022-database.html",
        },
        "constructs": CONSTRUCT_LABELS,
        "profiles":   PROFILE_LABELS,
        "profile_scores": profile_means,
        "countries":  country_rows,
    }

    OUT_FILE.write_text(json.dumps(out, indent=2))
    print(f"Written: {OUT_FILE}  ({len(country_rows)} countries)")


if __name__ == "__main__":
    main()
