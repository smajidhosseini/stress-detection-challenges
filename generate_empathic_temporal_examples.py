from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from reproduction_config import OUTPUT_ROOT

from generate_figure4_all_subjects import (
    centered_event_window,
    dataset_specs,
    detect_transitions,
    load_frame,
)


OUT = OUTPUT_ROOT / "figure4_selected_empathic"
OUT.mkdir(parents=True, exist_ok=True)

SELECTED_EXAMPLES = [
    {"subject": "1.0", "subject_event": 2, "transition": (1, 2), "panel": "A"},
    {"subject": "2.0", "subject_event": 6, "transition": (1, 2), "panel": "B"},
]


def main() -> None:
    spec = next(item for item in dataset_specs() if item["name"] == "EmpathicSchool")
    frame = load_frame(spec)

    for selection in SELECTED_EXAMPLES:
        display_subject = selection["subject"][:-2] if selection["subject"].endswith(".0") else selection["subject"]
        subject_frame = frame[frame[spec["subject"]].astype(str) == selection["subject"]]
        event_count = 0
        selected = None
        for segment, group in subject_frame.groupby("_segment", sort=False):
            group = group.reset_index(drop=True)
            for transition in detect_transitions(group[spec["label"]]):
                event_count += 1
                if event_count == selection["subject_event"]:
                    selected = (group, transition)
                    break
            if selected:
                break
        if selected is None:
            raise RuntimeError(f"Selected event not found: {selection}")
        group, transition = selected
        if (transition.before, transition.after) != selection["transition"]:
            raise RuntimeError(
                f"Unexpected transition for {selection}: {transition.before}->{transition.after}"
            )

        window = centered_event_window(group, transition.index, spec["step"], 60)
        x = window["relative_seconds"].to_numpy(float)
        fig, axes = plt.subplots(
            3, 1, figsize=(7.2, 7.4), sharex=True,
            gridspec_kw={"height_ratios": [1, 1, .72]},
        )
        axes[0].plot(x, window[spec["eda"]], color="#0072B2", lw=2)
        axes[0].set_ylabel("EDA (µS)")
        axes[1].plot(x, window[spec["temp"]], color="#D55E00", lw=2)
        axes[1].set_ylabel("Temperature (°C)")
        axes[2].step(x, window[spec["label"]], where="post", color="#333333", lw=2)
        axes[2].scatter([0], [transition.after], color="#CC3311", s=34, zorder=4)
        axes[2].set_ylabel("Stress label")
        axes[2].set_yticks([0, 1, 2])
        axes[2].set_ylim(-.2, 2.2)
        axes[2].set_xlabel("Time from stress-label transition (s)")
        axes[2].set_xlim(-60, 60)

        for ax in axes:
            ax.axvline(0, color="black", ls="--", lw=1.1)
            ax.axvspan(0, 60, color="#CC79A7", alpha=.07, lw=0)
            ax.grid(alpha=.2)

        fig.suptitle(
            f"Figure 4{selection['panel']}. EmpathicSchool Subject {display_subject} - "
            f"label {transition.before} → {transition.after}",
            fontsize=13.5, y=.985,
        )
        fig.text(
            .5, .012,
            "Dashed line: observed stress-label transition at 0 s; shading: post-transition period",
            ha="center", fontsize=8, color="0.35",
        )
        fig.tight_layout(rect=(.07, .035, .98, .95))
        output = OUT / (
            f"Figure4{selection['panel']}_EmpathicSchool_Subject_"
            f"{selection['subject'].replace('.', '_')}_Event_{selection['subject_event']}.pdf"
        )
        fig.savefig(output, bbox_inches="tight")
        plt.close(fig)
        print(output)


if __name__ == "__main__":
    main()
