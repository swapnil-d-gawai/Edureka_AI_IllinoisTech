# Module 5: Data Visualization

- **LMS course:** [Modern Python & AI-Assisted Development](https://lms.snvaveranda.com/course/view.php?id=248)
- **Presentation URL/ID:** `https://lms.snvaveranda.com/mod/resource/view.php?id=8617` / `8617`

## Deck map

| Slides | Topic |
| --- | --- |
| 1–10 | Visualization purpose and graphical analysis |
| 11–36 | Matplotlib line, bar, histogram, pie, scatter, box, and chart demos |
| 37–59 | Styles, labels, ticks, colors, lines, markers, legends, saving, and subplots |
| 60–79 | Seaborn relational, categorical, distribution, and matrix plots |
| 80–83 | Summary and review |

## Learning objectives

Choose visual encodings for trends, comparisons, distributions, relationships, and composition; create and customize Matplotlib/Seaborn charts; use subplots and grids; and export clear visual evidence.

> These notes summarize the protected deck for study; they do not reproduce its slide text, examples, or artwork.

## LMS demonstration walkthrough

- **Resources:** <https://lms.snvaveranda.com/mod/resource/view.php?id=8618>, <https://lms.snvaveranda.com/mod/resource/view.php?id=8619>, and <https://lms.snvaveranda.com/mod/resource/view.php?id=8620>.
- **Actual assignment:** chart `Car_sales` with line/bar/histogram/pie/scatter/box plots; customize Matplotlib labels, styles, ticks, grid, colors, and saved output; then use `top50.csv` to practice bar charts, subplots, box plots, and `GridSpec`.
- **Input/data shape:** car fields include manufacturer/model, sales/resale, vehicle type, price, engine, horsepower, dimensions, weight, fuel, efficiency, and launch date. `top50` has track/artist/genre plus tempo, energy, danceability, loudness, liveness, valence, length, acousticness, speechiness, and popularity.
- **Beginner workflow:** state the question, profile the relevant columns, select a chart for that relationship, plot a three-row synthetic version, label units/title, customize only what improves reading, save, reopen, and compare the image with numeric summaries.
- **Relationship to current examples:** `ops_dashboard.py` is an **original extension beyond the LMS demonstration**. It applies the same Matplotlib/Seaborn skills to an operations dashboard and provides deterministic offline data rather than committing course CSVs.
- **Deliberate practice:** create two car-like records and one music-like record set; choose the best and deliberately worst chart for each; predict ranking/distribution; add a second panel with the same scale and explain what changed.

See the detailed walkthrough at the end of `NOTES.md`; `examples/README.md` explains an optional local LMS dataset path.
