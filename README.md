# Bar Chart Balancing — Vastu zone balancing tool

A small Streamlit web app for Vastu consultants: enter the area of each of the 16 compass zones of a home or commercial premises, see the distribution as a colour-coded bar chart, balance the zones toward the average and download a PDF report for the client.

**Status:** Working tool, configured for deployment on Render.

## Overview

In Vastu practice, a floor plan is divided into 16 directional zones and the area of each zone is compared with the average. Zones far above or below the average are flagged for correction. Doing this by hand for every project is slow, so this tool automates the arithmetic, the charts and the client report.

For any set of zone areas it computes three reference lines:

- **Average line** = total area / 16
- **Max line** = (largest zone + average) / 2
- **Min line** = (smallest zone + average) / 2

The balancing algorithm (`balance.py`) then repeatedly nudges each zone toward the average by a chosen step, never moving a zone past the current max or min line, until nothing changes or 100 iterations have run.

## Features

- Input form for the 16 zones (NNW, N, NNE, NE, ENE, E, ESE, SE, SSE, S, SSW, SW, WSW, W, WNW, NW)
- Interactive Plotly bar chart, coloured by element group (Water / North, Wood / East, Fire / South, Earth / Southwest, Metal / West), with average, max and min lines
- Three balancing modes: **Add** (raise zones below average), **Subtract** (lower zones above average) or **Both**, with an adjustable step size
- Balanced chart and a side-by-side table of original value, balanced value and the change per zone
- Downloadable multi-page PDF report (ReportLab): executive summary, algorithm settings, zone comparison table, colour legend, both charts and a short conclusion with the reduction in standard deviation
- Simple login gate in front of the app

## Tech stack

| Layer | Technology |
| --- | --- |
| App framework | Streamlit |
| Charts | Plotly (interactive), Kaleido for image export, Matplotlib as a fallback |
| Data | pandas |
| PDF | ReportLab |
| Hosting | Render (`render.yaml`, `build.sh`) |

## Getting started

### Prerequisites

- Python 3.12 (or another recent Python 3)

### Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit opens the app at http://localhost:8501.

Charts in the PDF are rendered with Plotly's Kaleido engine when it is available (`pip install kaleido`, which also needs a Chrome or Chromium browser); otherwise the report falls back to Matplotlib versions of the same charts.

### Usage

1. Sign in.
2. Enter a project name (used in the report title and file name).
3. Enter the area of each zone.
4. Pick a balancing mode and step size in the sidebar.
5. Review the balanced chart and table, then click **Download PDF Report**. The download appears once a project name is set and every zone has an area greater than zero.

### Deploy on Render

`render.yaml` defines a Python web service. `build.sh` installs Chromium (for Kaleido's chart export) and the Python dependencies; the start command is:

```bash
streamlit run app.py --server.port $PORT --server.enableCORS false
```

## Project structure

```
app.py             Streamlit UI: login gate, inputs, charts, balancing controls, PDF download
balance.py         balancing algorithm (add / subtract / both)
pdf.py             ReportLab report: summary, tables, legend, chart images, page numbers
requirements.txt   Python dependencies
build.sh           Render build script (Chromium + pip install)
render.yaml        Render service definition
```

## Author

Tanuj Jain — [tanujs.in](https://tanujs.in) · [GitHub](https://github.com/TANUJ0751)

## License

All rights reserved. No license has been granted for reuse.
