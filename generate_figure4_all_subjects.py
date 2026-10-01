from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd

from reproduction_config import DATA_ROOT, OUTPUT_ROOT


OUT = OUTPUT_ROOT / "figure4_all_subjects"
OUT.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Transition:
    index: int
    before: int
    after: int


def detect_transitions(labels: pd.Series) -> list[Transition]:
    """Return adjacent changes among labels 0, 1, and 2 without bridging gaps."""
    numeric = pd.to_numeric(labels, errors="coerce")
    previous = numeric.shift(1)
    valid = numeric.isin([0, 1, 2]) & previous.isin([0, 1, 2])
    changed = valid & numeric.ne(previous)
    return [
        Transition(int(i), int(previous.iloc[i]), int(numeric.iloc[i]))
        for i in np.flatnonzero(changed.to_numpy())
    ]


def centered_event_window(
    frame: pd.DataFrame,
    event_index: int,
    step_seconds: float,
    radius_seconds: float = 60,
) -> pd.DataFrame:
    radius_rows = int(np.floor(radius_seconds / step_seconds))
    lo = max(0, event_index - radius_rows)
    hi = min(len(frame) - 1, event_index + radius_rows)
    result = frame.iloc[lo : hi + 1].copy()
    result["relative_seconds"] = (
        np.arange(lo, hi + 1, dtype=float) - float(event_index)
    ) * float(step_seconds)
    return result


def dataset_specs() -> list[dict]:
    return [
        {
            "name": "WESAD",
            "files": [DATA_ROOT / "WESAD" / "downsampled_dataset.csv"],
            "subject": "Subject", "label": "label", "hr": "HR", "eda": "EDA", "temp": "Temp",
            "step": 0.25, "time": None, "segment_mode": "none",
        },
        {
            "name": "EmpathicSchool",
            "files": [DATA_ROOT / "EmpathicSchool" / "2005.csv"],
            "subject": "subject", "label": "label", "hr": "hr_mean", "eda": "eda_mean", "temp": "temp_mean",
            "step": 5.0, "time": "window_start", "segment_mode": "reset_samples_4hz",
        },
        {
            "name": "AffectiveROAD",
            "files": [DATA_ROOT / "AffectiveRoad" / "Combined3015.csv"],
            "subject": "ID", "label": "Stress", "hr": "HRL_Mean", "eda": "EDAL_Mean", "temp": "TEMPL_Mean",
            "step": 15.0, "time": None, "segment_mode": "none",
        },
    ]


def load_frame(spec: dict) -> pd.DataFrame:
    cols = [spec[k] for k in ("subject", "label", "hr", "eda", "temp")]
    if spec["time"]:
        cols.append(spec["time"])
    parts = [pd.read_csv(path, usecols=cols, low_memory=False) for path in spec["files"]]
    frame = pd.concat(parts, ignore_index=True)
    frame["_source_row"] = np.arange(len(frame))
    for key in ("label", "hr", "eda", "temp"):
        frame[spec[key]] = pd.to_numeric(frame[spec[key]], errors="coerce")

    if spec["segment_mode"] == "timestamp_gap":
        frame["_time"] = pd.to_datetime(frame[spec["time"]], errors="coerce", utc=True)
        frame = frame.sort_values([spec["subject"], "_time", "_source_row"], kind="stable")
        gap = frame.groupby(spec["subject"])["_time"].diff().dt.total_seconds()
        new_segment = gap.isna() | gap.gt(spec["step"] * 2.1) | gap.le(0)
    elif spec["segment_mode"] == "reset_samples_4hz":
        frame["_time"] = pd.to_numeric(frame[spec["time"]], errors="coerce") / 4.0
        difference = frame.groupby(spec["subject"])["_time"].diff()
        new_segment = difference.isna() | difference.le(0)
    else:
        new_segment = frame.groupby(spec["subject"]).cumcount().eq(0)

    frame["_segment"] = new_segment.groupby(frame[spec["subject"]]).cumsum().astype(int)
    return frame.reset_index(drop=True)


def make_event_figure(spec: dict, subject: str, segment: int, event_number: int,
                      transition: Transition, window: pd.DataFrame) -> plt.Figure:
    x = window["relative_seconds"].to_numpy(dtype=float)
    fig, axes = plt.subplots(4, 1, figsize=(8.27, 10.4), sharex=True,
                             gridspec_kw={"height_ratios": [1, 1, 1, .72]})
    series = [
        (spec["hr"], "Heart rate (bpm)", "#6A3D9A"),
        (spec["eda"], "EDA (µS)", "#0072B2"),
        (spec["temp"], "Temperature (°C)", "#D55E00"),
    ]
    for ax, (column, ylabel, color) in zip(axes[:3], series):
        y = window[column].to_numpy(dtype=float)
        ax.plot(x, y, color=color, lw=1.45)
        ax.set_ylabel(ylabel)
        ax.grid(alpha=.2)
        ax.axvline(0, color="black", ls="--", lw=1)
        ax.axvspan(0, 60, color="#CC79A7", alpha=.07, lw=0)

    label_values = window[spec["label"]].to_numpy(dtype=float)
    axes[3].step(x, label_values, where="post", color="#333333", lw=1.65)
    axes[3].scatter([0], [transition.after], color="#CC3311", s=24, zorder=3)
    axes[3].set_ylabel("Stress label")
    axes[3].set_yticks([0, 1, 2])
    axes[3].set_ylim(-.2, 2.2)
    axes[3].grid(alpha=.2)
    axes[3].axvline(0, color="black", ls="--", lw=1)
    axes[3].axvspan(0, 60, color="#CC79A7", alpha=.07, lw=0)
    axes[3].set_xlabel("Time from stress-label transition (s)")
    axes[3].set_xlim(-60, 60)

    fig.suptitle(
        f"{spec['name']} - Subject {subject} - Event {event_number}: "
        f"label {transition.before} → {transition.after}",
        fontsize=14, y=.992,
    )
    boundary_note = ""
    if x.min() > -60 or x.max() < 60:
        boundary_note = "  |  Window clipped at recording boundary"
    fig.text(.5, .008,
             f"Dashed line: observed adjacent label transition at 0 s{boundary_note}",
             ha="center", fontsize=8, color="0.35")
    fig.tight_layout(rect=(.06, .025, .98, .965))
    return fig


def generate_dataset(spec: dict) -> tuple[Path, list[dict]]:
    frame = load_frame(spec)
    output = OUT / f"Figure4_all_subjects_{spec['name']}.pdf"
    records: list[dict] = []
    page = 0
    with PdfPages(output) as pdf:
        for subject_value, subject_frame in frame.groupby(spec["subject"], sort=True):
            subject = str(subject_value)
            subject_event = 0
            for segment, group in subject_frame.groupby("_segment", sort=False):
                group = group.reset_index(drop=True)
                for transition in detect_transitions(group[spec["label"]]):
                    subject_event += 1
                    page += 1
                    window = centered_event_window(group, transition.index, spec["step"], 60)
                    fig = make_event_figure(spec, subject, int(segment), subject_event, transition, window)
                    pdf.savefig(fig)
                    plt.close(fig)
                    records.append({
                        "dataset": spec["name"], "pdf_page": page, "subject": subject,
                        "subject_event": subject_event, "segment": int(segment),
                        "source_row": int(group.loc[transition.index, "_source_row"]),
                        "from_label": transition.before, "to_label": transition.after,
                        "step_seconds": spec["step"],
                        "window_start_seconds": float(window["relative_seconds"].iloc[0]),
                        "window_end_seconds": float(window["relative_seconds"].iloc[-1]),
                    })
            if subject_event == 0:
                page += 1
                fig, ax = plt.subplots(figsize=(8.27, 10.4))
                ax.axis("off")
                ax.text(.5, .55, f"{spec['name']} - Subject {subject}", ha="center", fontsize=16)
                ax.text(.5, .47, "No adjacent transition among labels 0, 1, and 2 was observed.",
                        ha="center", fontsize=11)
                pdf.savefig(fig)
                plt.close(fig)
                records.append({
                    "dataset": spec["name"], "pdf_page": page, "subject": subject,
                    "subject_event": 0, "segment": np.nan, "source_row": np.nan,
                    "from_label": np.nan, "to_label": np.nan, "step_seconds": spec["step"],
                    "window_start_seconds": np.nan, "window_end_seconds": np.nan,
                })
    return output, records


def main() -> None:
    all_records: list[dict] = []
    for spec in dataset_specs():
        output, records = generate_dataset(spec)
        all_records.extend(records)
        transitions = sum(pd.notna(r["from_label"]) for r in records)
        subjects = len({r["subject"] for r in records})
        print(f"{spec['name']}: {subjects} subjects, {transitions} transitions, {len(records)} pages -> {output}")
    pd.DataFrame(all_records).to_csv(OUT / "Figure4_page_manifest.csv", index=False)


if __name__ == "__main__":
    main()
