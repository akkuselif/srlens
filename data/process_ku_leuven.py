"""
Process KU Leuven VLE clickstream data into ku_leuven_profiles.json.

Download from: Data Availability section of the Scientific Data paper
               https://www.nature.com/articles/s41597-026-06821-3
Files needed:  interactions.csv   -- one row per VLE click
               students.csv       -- one row per student with demographics
               assessments.csv    -- assessment results per student

Install deps:  pip install pandas numpy scikit-learn
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

RAW_DIR = Path(__file__).parent / "raw"
OUT_FILE = Path(__file__).parent / "ku_leuven_profiles.json"

RESOURCE_TYPES = ["Document", "Video", "Quiz", "Assignment", "Announcement", "Discussion", "Syllabus", "Link"]

# Map raw VLE activity_type values to canonical resource labels
# Adjust these keys to match the actual column values in interactions.csv
RESOURCE_MAP = {
    "resource":      "Document",
    "url":           "Link",
    "page":          "Document",
    "file":          "Document",
    "video":         "Video",
    "quiz":          "Quiz",
    "assign":        "Assignment",
    "forum":         "Discussion",
    "announcement":  "Announcement",
    "syllabus":      "Syllabus",
    "book":          "Document",
    "lesson":        "Document",
    "scorm":         "Document",
}

PROFILE_LABELS = ["High SRL", "Surface learner", "Anxious striver", "Disengaged"]
N_WEEKS = 13


def load_raw() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    interactions = pd.read_csv(RAW_DIR / "interactions.csv", parse_dates=["timestamp"])
    students     = pd.read_csv(RAW_DIR / "students.csv")
    assessments  = pd.read_csv(RAW_DIR / "assessments.csv")
    return interactions, students, assessments


def assign_week(df: pd.DataFrame, start_col: str = "course_start") -> pd.DataFrame:
    """Add week_num (1-indexed) relative to each course's start date."""
    df = df.copy()
    df["week_num"] = ((df["timestamp"] - df[start_col]).dt.days // 7 + 1).clip(1, N_WEEKS)
    return df


def resource_proportions(interactions: pd.DataFrame) -> pd.DataFrame:
    """Return (student_id, resource_type, proportion) for each student."""
    interactions = interactions.copy()
    interactions["resource_label"] = interactions["activity_type"].str.lower().map(RESOURCE_MAP).fillna("Document")
    totals = interactions.groupby("student_id").size().rename("total")
    counts = interactions.groupby(["student_id", "resource_label"]).size().rename("count").reset_index()
    counts = counts.join(totals, on="student_id")
    counts["proportion"] = (counts["count"] / counts["total"] * 100).round(2)
    pivot = counts.pivot(index="student_id", columns="resource_label", values="proportion").fillna(0)
    # Ensure all canonical resource columns are present
    for r in RESOURCE_TYPES:
        if r not in pivot.columns:
            pivot[r] = 0.0
    return pivot[RESOURCE_TYPES]


def weekly_sessions(interactions: pd.DataFrame) -> pd.DataFrame:
    """Return (student_id, week_num) unique study-day counts."""
    daily = interactions.copy()
    daily["date"] = daily["timestamp"].dt.date
    daily = daily.drop_duplicates(subset=["student_id", "date"])
    daily["week_num"] = ((daily["timestamp"] - daily["timestamp"].min()).dt.days // 7 + 1).clip(1, N_WEEKS)
    counts = daily.groupby(["student_id", "week_num"]).size().rename("days").reset_index()
    pivot = counts.pivot(index="student_id", columns="week_num", values="days").fillna(0)
    pivot.columns = [f"wk{int(c)}" for c in pivot.columns]
    for w in range(1, N_WEEKS + 1):
        col = f"wk{w}"
        if col not in pivot.columns:
            pivot[col] = 0.0
    return pivot[[f"wk{w}" for w in range(1, N_WEEKS + 1)]]


def fit_profiles(features: pd.DataFrame) -> pd.Series:
    """Gaussian Mixture Model with 4 components -- returns profile labels per student."""
    scaler = StandardScaler()
    X = scaler.fit_transform(features)
    gmm = GaussianMixture(n_components=4, covariance_type="full", random_state=42, n_init=5)
    raw_labels = gmm.fit_predict(X)

    # Identify which GMM cluster maps to which named profile by highest mean self-frequency
    # and resource diversity (heuristic; verify against theory after running)
    cluster_means = pd.DataFrame(X, columns=features.columns)
    cluster_means["cluster"] = raw_labels
    summary = cluster_means.groupby("cluster").mean()

    diversity_col = [c for c in summary.columns if "diversity" in c.lower()]
    quiz_col      = [c for c in summary.columns if "quiz" in c.lower()]

    if diversity_col and quiz_col:
        order = summary.sort_values([diversity_col[0], quiz_col[0]], ascending=[False, False]).index.tolist()
        # Heuristic mapping: highest diversity + moderate quiz = High SRL
        mapping = {order[0]: "High SRL", order[1]: "Anxious striver", order[2]: "Surface learner", order[3]: "Disengaged"}
    else:
        mapping = {i: PROFILE_LABELS[i] for i in range(4)}

    return pd.Series(raw_labels, index=features.index).map(mapping)


def main():
    for fname in ["interactions.csv", "students.csv", "assessments.csv"]:
        if not (RAW_DIR / fname).exists():
            print(f"Missing: {RAW_DIR / fname}")
            print("Download from the Scientific Data paper's data availability section.")
            sys.exit(1)

    print("Loading KU Leuven data...")
    interactions, students, assessments = load_raw()
    print(f"  {len(interactions):,} interaction records, {interactions['student_id'].nunique():,} students")

    res_props  = resource_proportions(interactions)
    wk_sess    = weekly_sessions(interactions)

    features = res_props.copy()
    features["diversity"] = (res_props > 0).sum(axis=1)
    features["total_days"] = wk_sess.sum(axis=1)

    profiles = fit_profiles(features)
    features["profile"] = profiles

    weekly_by_profile = []
    for label in PROFILE_LABELS:
        grp = wk_sess[features["profile"] == label]
        weekly_by_profile.append(grp.mean().round(2).tolist())

    resource_by_profile = []
    for label in PROFILE_LABELS:
        grp = res_props[features["profile"] == label]
        resource_by_profile.append(grp.mean().round(2).tolist())

    # Outcome correlations
    assess = assessments.set_index("student_id")
    outcomes = []
    for label in PROFILE_LABELS:
        ids = features[features["profile"] == label].index
        grp = assess.loc[assess.index.intersection(ids)]
        outcomes.append({
            "profile":         label,
            "final_grade_mean": round(float(grp["final_grade"].mean()), 1) if "final_grade" in grp else None,
            "pass_rate":        round(float((grp["final_grade"] >= 50).mean()), 3) if "final_grade" in grp else None,
            "n":                len(grp),
        })

    out = {
        "meta": {
            "students":    int(interactions["student_id"].nunique()),
            "records":     len(interactions),
            "courses":     2,
            "years":       "2018-2021",
            "source":      "https://www.nature.com/articles/s41597-026-06821-3",
        },
        "profiles":      PROFILE_LABELS,
        "weeks":         [f"Wk{w}" for w in range(1, N_WEEKS + 1)],
        "resources":     RESOURCE_TYPES,
        "weekly_sessions":       weekly_by_profile,
        "resource_proportions":  resource_by_profile,
        "outcomes":      outcomes,
        "profile_counts": {
            label: int((features["profile"] == label).sum())
            for label in PROFILE_LABELS
        },
    }

    OUT_FILE.write_text(json.dumps(out, indent=2))
    print(f"Written: {OUT_FILE}")


if __name__ == "__main__":
    main()
