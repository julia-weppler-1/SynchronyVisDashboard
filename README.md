# SynchronyVisDashboard

This repository contains a Dash / Plotly dashboard for exploring parent–child physiologic synchrony and behavioral data. It includes:

* A **Home Summary** view with aggregate charts and timelines
* A **Play** view with synchronized video playback and stacked heatmaps
* Point-in-time (PIT) visualizations of physiologic synchrony and dyadic behavior

> **Data access:**
> The physiological and behavioral data used by this app are **not** included in this repository.
> To run the app with real data, please contact the project team to request access.

## 1. Prerequisites

* **Python**

Make sure you can create and activate a virtual environment (either with `venv`, `conda`, or similar).

## 2. Installation

1. **Clone or download this repository**

```bash
git clone https://github.com/julia-weppler-1/SynchronyVisDashboard.git
cd SynchronyVisDashboard
```

2. **Create and activate a virtual environment**

Using `venv`:

```bash
python -m venv venv
source venv/bin/activate   # on macOS / Linux
# OR
.\venv\Scripts\activate    # on Windows
```

3. **Install Python dependencies**

Run:

```bash
pip install -r requirements.txt
```

## 3. Getting the data 

The app utilizes a module named `load_data.py` that loads:

* a pandas DataFrame named **`df`** with the session time series
* a **`VIDEO`** variable with the path/URL to the corresponding video

### Where to put the data

After you receive the data from us (if you are approved to access the data), place:

* the **xlsx** /file into `data/` and name it Synch_Data.xlsx
* the **video** file into `assets/data_video` and name it Dyad_Video.mp4


## 4. Running the app

From the project root (with your virtual environment activated):

```bash
python app.py
```

By default, Dash will start a server on `http://127.0.0.1:8050/` (or `http://localhost:8050/`).
Open that URL in your browser.

## 5. Contact / data access

Because the underlying physiological and behavioral data are sensitive and not publicly shareable, **datasets are not stored in this repository**.

To get access to the data and/or a sample anonymized dataset, please contact:

* **Project team:** `c.barry@northeastern.edu or weppler.j@northeastern.edu`

Please include in your request:

* Your name and affiliation
* How you plan to use the dashboard

