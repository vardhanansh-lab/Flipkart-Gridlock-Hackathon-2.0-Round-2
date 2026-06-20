# 🛰️ GRIDLOCK — Predictive Illegal-Parking Enforcement Intelligence

**Flipkart Gridlock Hackathon · Round 2 Prototype**
Team: **Last Mile Legends**
Theme: *Poor Visibility on Parking-Induced Congestion*

> Most teams show you **where** illegal parking happens.
> We predict **where it will happen tomorrow**, ranked by **how much it hurts traffic flow** — so police deploy patrols by data, not guesswork.

---

## The problem

Bengaluru traffic police enforce illegal parking **reactively** — patrol-based, no forecast, no way to prioritise which of the city's hundreds of zones to police first. The official problem statement asks:

> *"How can AI-driven parking intelligence detect illegal parking hotspots and quantify their impact on traffic flow to enable targeted enforcement?"*

We answer **both halves**: detect tomorrow's hotspots **and** quantify their traffic-flow impact.

---

## What we built

A three-part system, trained on **298,000 real Bengaluru violation records** (Jan–May):

| Layer | What it does |
|-------|--------------|
| **1. Forecaster** | LightGBM spatio-temporal model predicts each city cell's hotspot probability **one day ahead** |
| **2. Impact layer** | Weights each hotspot by **road criticality** (throughput + freight-vehicle share) → **Enforcement Priority Score** |
| **3. Dashboard** | Deployable Streamlit tool: map + ranked patrol-deployment queue for tomorrow |

### Key insight that drives the design
**61.7% of all violations occur in just 5% of city cells.** Enforcement *should* be targeted — the data proves hotspots are real, concentrated, and (as the model shows) predictable.

---

## Results — honest, validated

Evaluated with **3-fold rolling time-series cross-validation** (train on past, test on future — never on data the model could have seen).

| Metric | Score | Meaning |
|--------|-------|---------|
| **ROC-AUC** | **0.945 ± 0.018** | identifies tomorrow's top-5% critical hotspots |
| Precision@20 | 0.61 | of top-20 predicted hotspots, ~12 are correct |
| F1 | 0.60 | balanced hotspot classification |
| Precision / Recall | 0.63 / 0.57 | — |

Beats naive "same as last week" baseline. The top-5% threshold is chosen because it matches **real patrol capacity** and the 61.7% concentration — it's the operationally relevant operating point, not a tuned number.

**Top predictive feature:** `cell × day-of-week mean` — illegal parking follows a **weekly rhythm per location** (a cell floods every Saturday; another every weekday rush). Hotspots aren't random; we learn their schedule.

> Note on mAP: the problem statement lists mAP, an object-detection metric. For a forecasting formulation the equivalent ranking metric is **Precision@K / PR-AUC**, which we report instead.

---

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens the dashboard at `http://localhost:8501`.

## Deploy (free)
Push to GitHub → [share.streamlit.io](https://share.streamlit.io) → point at `app.py`. Live demo link in minutes.

---

## Repo contents
```
app.py                       # Streamlit dashboard (map + priority queue)
gridlock_pipeline.ipynb      # full pipeline: data → features → model → evaluation
dashboard_predictions.csv    # tomorrow's per-cell predictions + priority scores
requirements.txt
README.md
```

## Stack
Python · LightGBM · pandas · pygeohash · Streamlit · pydeck

---
*Built for Flipkart Gridlock 2026 · Last Mile Legends*
