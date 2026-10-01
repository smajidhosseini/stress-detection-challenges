from __future__ import annotations

import glob
import json

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.patches import Patch

from reproduction_config import DATA_ROOT, OUTPUT_ROOT


OUT = OUTPUT_ROOT / "figure1"
OUT.mkdir(parents=True, exist_ok=True)


def natural_subject_key(value: object):
    text = str(value)
    prefix = "".join(ch for ch in text if not ch.isdigit())
    digits = "".join(ch for ch in text if ch.isdigit())
    return (prefix, int(digits) if digits else -1, text)


def standardize(df, subject, eda, label, low, high, name):
    out = df[[subject, eda, label]].copy()
    out.columns = ["Subject", "EDA", "NativeLabel"]
    out = out[out["NativeLabel"].isin([low, high])]
    out["Stress"] = out["NativeLabel"].map({low: "Low stress", high: "High stress"})
    out["Subject"] = out["Subject"].astype(str).str.replace(r"\.0$", "", regex=True)
    out["EDA"] = pd.to_numeric(out["EDA"], errors="coerce")
    out = out.dropna(subset=["Subject", "EDA", "Stress"])
    out = out[out["EDA"] >= 0]
    # A paired low-versus-high comparison is only interpretable when both
    # retained classes are present for the subject.
    class_counts = out.groupby(["Subject", "Stress"], observed=True).size().unstack(fill_value=0)
    paired_subjects = class_counts.index[
        (class_counts.get("Low stress", 0) > 0) & (class_counts.get("High stress", 0) > 0)
    ]
    out = out[out["Subject"].isin(paired_subjects)]
    out["Dataset"] = name
    return out


wesad_path = DATA_ROOT / "WESAD" / "wrist_data_all.csv"
wesad = pd.read_csv(wesad_path, usecols=["EDA", "Subject", "label"])
wesad = standardize(wesad, "Subject", "EDA", "label", 1, 2, "WESAD")

empathic_path = DATA_ROOT / "EmpathicSchool" / "biometric_features.csv"
empathic = pd.read_csv(empathic_path, usecols=["eda_mean", "subject", "label"])
empathic = standardize(empathic, "subject", "eda_mean", "label", 0, 2, "EmpathicSchool")

nurses_glob = str(DATA_ROOT / "Nurses" / "Semisupervised" / "featured_data" / "*_featured.csv")
nurses_files = sorted(glob.glob(nurses_glob))
nurses_raw = pd.concat(
    [pd.read_csv(path, usecols=["EDA_mean", "id", "n_stress"]) for path in nurses_files],
    ignore_index=True,
)
nurses = standardize(nurses_raw, "id", "EDA_mean", "n_stress", 0, 2, "Nurses")

affective_path = DATA_ROOT / "AffectiveRoad" / "Combined3015.csv"
affective = pd.read_csv(affective_path, usecols=["EDAL_Mean", "ID", "Stress"])
affective = standardize(affective, "ID", "EDAL_Mean", "Stress", 0, 2, "AffectiveROAD")

datasets = [wesad, empathic, nurses, affective]
titles = ["(a) WESAD", "(b) EmpathicSchool", "(c) Nurses", "(d) AffectiveROAD"]
palette = {"Low stress": "#2E8B57", "High stress": "#C44E52"}

sns.set_theme(style="whitegrid", context="paper", font_scale=1.15)
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": "#222222",
    "axes.linewidth": 0.8,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

fig, axes = plt.subplots(2, 2, figsize=(14.2, 9.2), constrained_layout=False)
for ax, data, title in zip(axes.flat, datasets, titles):
    order = sorted(data["Subject"].unique(), key=natural_subject_key)
    sns.boxplot(
        data=data,
        x="Subject",
        y="EDA",
        hue="Stress",
        order=order,
        hue_order=["Low stress", "High stress"],
        palette=palette,
        showfliers=False,
        width=0.72,
        linewidth=0.75,
        saturation=0.9,
        ax=ax,
    )
    if ax.legend_ is not None:
        ax.legend_.remove()
    ax.set_title(title, loc="left", fontweight="bold", fontsize=12, pad=8)
    ax.set_xlabel("Subject")
    ax.set_ylabel("EDA (µS)")
    ax.tick_params(axis="x", rotation=45, labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.6)
    ax.grid(axis="x", visible=False)
    sns.despine(ax=ax)

legend_handles = [
    Patch(facecolor=palette["Low stress"], edgecolor="#333333", label="Low stress"),
    Patch(facecolor=palette["High stress"], edgecolor="#333333", label="High stress"),
]
fig.legend(
    handles=legend_handles,
    loc="upper center",
    bbox_to_anchor=(0.5, 0.995),
    ncol=2,
    frameon=False,
    fontsize=10,
)
fig.subplots_adjust(left=0.075, right=0.985, bottom=0.08, top=0.94, hspace=0.34, wspace=0.22)

base = OUT / "Figure1_EDA_subject_variability"
fig.savefig(base.with_suffix(".png"), dpi=600, bbox_inches="tight", facecolor="white")
fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight", facecolor="white")
fig.savefig(base.with_suffix(".svg"), bbox_inches="tight", facecolor="white")
plt.close(fig)

# Export each dataset panel as its own publication-ready vector PDF.
for data, title, slug in zip(
    datasets,
    titles,
    ["WESAD", "EmpathicSchool", "Nurses", "AffectiveROAD"],
):
    panel_fig, panel_ax = plt.subplots(figsize=(8.2, 5.2))
    order = sorted(data["Subject"].unique(), key=natural_subject_key)
    sns.boxplot(
        data=data,
        x="Subject",
        y="EDA",
        hue="Stress",
        order=order,
        hue_order=["Low stress", "High stress"],
        palette=palette,
        showfliers=False,
        width=0.72,
        linewidth=0.8,
        saturation=0.9,
        ax=panel_ax,
    )
    panel_ax.set_title(title, loc="left", fontweight="bold", fontsize=13, pad=9)
    panel_ax.set_xlabel("Subject")
    panel_ax.set_ylabel("EDA (µS)")
    panel_ax.tick_params(axis="x", rotation=45, labelsize=8)
    panel_ax.tick_params(axis="y", labelsize=9)
    panel_ax.grid(axis="y", color="#D9D9D9", linewidth=0.6)
    panel_ax.grid(axis="x", visible=False)
    panel_ax.legend(title=None, frameon=False, ncol=2, loc="upper right")
    sns.despine(ax=panel_ax)
    panel_fig.tight_layout()
    panel_fig.savefig(OUT / f"Figure1_{slug}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(panel_fig)

combined = pd.concat(datasets, ignore_index=True)
summary = (
    combined.groupby(["Dataset", "Subject", "Stress"], observed=True)["EDA"]
    .agg(n="size", mean="mean", median="median", q1=lambda x: x.quantile(0.25), q3=lambda x: x.quantile(0.75))
    .reset_index()
)
summary.to_csv(OUT / "Figure1_EDA_summary.csv", index=False)

comparison = summary.pivot(index=["Dataset", "Subject"], columns="Stress", values="mean").reset_index()
comparison["High_mean_gt_low_mean"] = comparison["High stress"] > comparison["Low stress"]
median_comparison = summary.pivot(index=["Dataset", "Subject"], columns="Stress", values="median").reset_index()
median_comparison = median_comparison.rename(columns={
    "High stress": "High_median",
    "Low stress": "Low_median",
})
median_comparison["High_median_gt_low_median"] = median_comparison["High_median"] > median_comparison["Low_median"]
comparison = comparison.merge(median_comparison, on=["Dataset", "Subject"], validate="one_to_one")
comparison.to_csv(OUT / "Figure1_subject_direction_check.csv", index=False)

dataset_count_rows = []
for dataset_name, group in comparison.groupby("Dataset", observed=True):
    for metric in ["mean", "median"]:
        subjects = len(group)
        high_not_greater = int((~group[f"High_{metric}_gt_low_{metric}"]).sum())
        dataset_count_rows.append({
            "Dataset": dataset_name,
            "comparison_metric": metric,
            "subjects_with_both_labels": subjects,
            "high_not_greater": high_not_greater,
            "fraction": high_not_greater / subjects,
        })
pd.DataFrame(dataset_count_rows).to_csv(OUT / "Figure1_dataset_direction_counts.csv", index=False)

manifest = {
    "figure": "Figure 1: subject-level EDA distributions by binary stress class",
    "processing": (
        "Only the specified low/high native labels retained; numeric nonnegative EDA retained; "
        "subjects without both retained classes excluded. WESAD uses the EDA column in the prepared "
        "wrist CSV; EmpathicSchool, Nurses, and AffectiveROAD use upstream window-mean EDA features, "
        "not raw 4 Hz EDA samples. No additional signal filtering or feature extraction is applied "
        "by this script; outliers hidden visually only (all retained observations used for quartiles)."
    ),
    "sources": {
        "WESAD": {"path": str(wesad_path), "value": "EDA", "subject": "Subject", "low": "label=1 (baseline)", "high": "label=2 (stress)"},
        "EmpathicSchool": {"path": str(empathic_path), "value": "eda_mean", "subject": "subject", "low": "label=0", "high": "label=2"},
        "Nurses": {"path_glob": nurses_glob, "files": len(nurses_files), "value": "EDA_mean", "subject": "id", "low": "n_stress=0", "high": "n_stress=2"},
        "AffectiveROAD": {"path": str(affective_path), "value": "EDAL_Mean", "subject": "ID", "low": "Stress=0", "high": "Stress=2"},
    },
    "counts": {
        name: {"rows": int(len(data)), "subjects": int(data.Subject.nunique())}
        for name, data in zip(["WESAD", "EmpathicSchool", "Nurses", "AffectiveROAD"], datasets)
    },
}
(OUT / "Figure1_method_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

print(json.dumps(manifest, indent=2))
