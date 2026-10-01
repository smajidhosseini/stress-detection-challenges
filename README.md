# Stress Detection Challenges

Python scripts for the descriptive EDA distributions (Figure 2), the selected
EmpathicSchool and AffectiveROAD transition plots (Figure 4A-D), and the existing
all-participant transition appendix. Original analysis choices and selected event
numbers are preserved; paths are configurable. Python 3.12 was used for verification.

This repository contains code only. Obtain the datasets separately under their
respective access and license terms. Neither participant data nor manuscript files
are included.

## Scope

| Script | What it produces |
| --- | --- |
| `regenerate_figure1.py` | Four participant EDA distribution plots, combined plots, summary statistics, mean/median direction checks, and method manifest. These are Figure 2 in the current manuscript; historical output filenames begin with Figure1. |
| `generate_empathic_temporal_examples.py` | Figure 4A: participant 1, event 2, label 1 to 2; Figure 4B: participant 2, event 6, label 1 to 2. |
| `generate_affectiveroad_temporal_examples.py` | Figure 4C: participant GM2, event 38, label 1 to 2; Figure 4D: participant SJ1, event 1, label 0 to 2. |
| `generate_figure4_all_subjects.py` | Existing appendix PDFs and page manifest for WESAD, EmpathicSchool, and AffectiveROAD; all adjacent changes among labels 0, 1, and 2, including reverse transitions. These appendix plots also include HR. Nurses is excluded from transition analyses. |

Figure 1 (conceptual diagram) and Figure 3 (activity/artifact illustration) are not
reproduced by these scripts. Their original source code was not available in this
package. Therefore the manuscript code-availability statement should specify
Figures 2 and 4 and the transition appendix.

## Required prepared data

Set `STRESS_DATA_ROOT` to the parent directory of this structure:

```text
data/
  WESAD/
    wrist_data_all.csv
    downsampled_dataset.csv
  EmpathicSchool/
    biometric_features.csv
    2005.csv
  AffectiveRoad/
    Combined3015.csv
  Nurses/
    Semisupervised/
      featured_data/
        *_featured.csv
```

These are prepared local exports, not the datasets' original downloadable formats.
The upstream export/feature-generation code is not included. The scripts reproduce
plots from the specified prepared files; they do not yet provide complete
reproduction from the original dataset downloads. `generate_figure4_all_subjects.py`
requires `downsampled_dataset.csv` for its WESAD HR/EDA/temperature appendix.

Required columns:

| Input | Required columns |
| --- | --- |
| WESAD `wrist_data_all.csv` | `Subject`, `label`, `EDA` |
| WESAD `downsampled_dataset.csv` | `Subject`, `label`, `HR`, `EDA`, `Temp` |
| EmpathicSchool `biometric_features.csv` | `subject`, `label`, `eda_mean` |
| EmpathicSchool `2005.csv` | `subject`, `label`, `window_start`, `hr_mean`, `eda_mean`, `temp_mean` |
| AffectiveROAD `Combined3015.csv` | `ID`, `Stress`, `HRL_Mean`, `EDAL_Mean`, `TEMPL_Mean` |
| Nurses feature CSVs | `id`, `n_stress`, `EDA_mean` |

## Run

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

Activate the virtual environment before installing dependencies if using this
environment (`.venv\Scripts\Activate.ps1` on PowerShell,
`source .venv/bin/activate` on macOS/Linux).

On Windows PowerShell:

```powershell
$env:STRESS_DATA_ROOT = 'C:\path\to\dataset-parent'
$env:STRESS_OUTPUT_ROOT = 'C:\path\to\generated-figures'
python regenerate_figure1.py
python generate_empathic_temporal_examples.py
python generate_affectiveroad_temporal_examples.py
python generate_figure4_all_subjects.py
python -m unittest discover -p 'test_*.py'
```

On macOS/Linux, set these variables with `export STRESS_DATA_ROOT=/path/to/data`
and `export STRESS_OUTPUT_ROOT=/path/to/results`, then run the same Python commands.
The default locations are `data/` and `results/` beside the scripts. Regenerating
the full appendix may take substantially longer than the four selected panels.

## Analysis details and interpretation

Figure 2 keeps labels 1/2 for WESAD and 0/2 for the other datasets. Participants
without both retained classes are excluded. Numeric, nonnegative EDA values are
retained. Plot outliers are hidden visually but remain in calculations. No extra
artifact filtering or normalization is applied by this script. WESAD uses the EDA
column; the other datasets use precomputed window-mean EDA features. All four
datasets should not be described as raw 4 Hz observations.

The transition scripts use an assumed row spacing of 0.25 seconds for the prepared
WESAD export, 5 seconds for EmpathicSchool, and 15 seconds for AffectiveROAD. These
spacings concern the prepared inputs, not stress-label annotation frequency.
The EmpathicSchool file contains 20-second windows (80 samples at 4 Hz) advancing
by 5 seconds (20 samples). The AffectiveROAD filename suggests a 30-second/15-second
window configuration, but the averaging-window definition must be checked against
the upstream exporter; the code assumes only its 15-second row spacing.
Temporal plots therefore display window means, not raw 4 Hz samples.

Within each participant, input order is preserved. EmpathicSchool recording
segments are split when `window_start` resets or stops increasing. Other inputs
assume that each participant's rows form a continuous, ordered recording; session
boundaries or missing-row gaps require explicit upstream handling. Relative time
is computed from row offsets. The plotting routines do not interpolate the data;
the plotted line simply connects successive observations. Windows cover up to
60 seconds before and after a label transition and may be clipped at boundaries.
Missing/invalid label values are not bridged when detecting adjacent transitions.

The selected event numbers refer to the ordinal adjacent label change within each
participant in the prepared files. They are explicitly selected illustrative
examples, not a random or representative sample. Plots centered on annotated
transitions cannot establish true stress onset or physiological latency. No
cross-correlation or dynamic time warping is used to generate these Figure 4 panels.

The mean and median comparisons are different summaries. The manuscript must
name the chosen metric and use the corresponding exported counts. With the
current prepared inputs, high median EDA is not greater than low median EDA for
1/15 WESAD, 9/22 EmpathicSchool, 3/12 Nurses, and 7/12 AffectiveROAD participants.
These differ from numbers in an earlier manuscript draft and must be reconciled
before submission. These counts describe signal-label relationships, not confirmed
physiological response differences.

## Citation in the manuscript

The repository URL for the manuscript is:

```latex
Code used to generate Figure~\ref{fig:eda}, Figure~\ref{fig:temporal-differences},
and the transition plots in the appendix is available at
\url{https://github.com/smajidhosseini/stress-detection-challenges}.
The scripts operate on prepared dataset exports; required file formats and
analysis assumptions are documented in the repository.
```

For a stable submission record, cite the specific commit or an archived release.
