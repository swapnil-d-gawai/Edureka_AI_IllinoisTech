# Module 5 Notes: Data Visualization

This module follows the LMS progression from choosing a graphical encoding through Matplotlib chart types/customization and Seaborn relational, categorical, distribution, and matrix plots. A chart is an interface to a decision, not decoration.

## 1. Begin with a decision question

Name the question before the chart:

- Is latency increasing over time?
- Which service has the highest error rate?
- Where do latencies cluster by region?
- Is request volume related to availability?

A useful chart title and visual encoding follow naturally. “Data dashboard” is not a question.

Visualizations resemble operational reports: a useful one exposes exceptions and trend; a misleading one can trigger the wrong AutoSys/incident action.

## 2. Choose the chart for the data relationship

| Question | Good starting point |
| --- | --- |
| ordered change | line |
| category comparison | bar (usually sorted) |
| distribution shape | histogram, KDE, box/violin |
| relationship | scatter |
| part of complete whole | stacked bar; pie only for few clear slices |
| matrix intensity | heatmap |
| median, spread, outliers | box plot |

Never use a line between unordered categories to imply continuity. Never use a pie chart with many nearly equal slices; a sorted bar is easier to compare.

## 3. Matplotlib object model

A **figure** is the overall canvas. An **axes** is one plotting area. Axes contain lines, bars, ticks, labels, a title, and a legend.

```python
fig, ax = plt.subplots()
ax.plot(days, latency)
ax.set_xlabel("Date")
ax.set_ylabel("Latency (ms)")
```

The object-oriented style names the exact axes and scales better to subplots than relying on global `plt` state.

Close figures after batch export:

```python
fig.savefig(path, dpi=180, bbox_inches="tight")
plt.close(fig)
```

`Agg` is a non-interactive backend suitable for servers and scheduler jobs.

## 4. Telling the truth with axes

For bars, a zero baseline usually lets length comparisons represent magnitude honestly. For line charts, a truncated axis can be appropriate only when clearly communicated.

Checklist:

- label units (`ms`, `%`, requests),
- show scope in title/caption,
- avoid dual axes unless necessary and clearly distinguished,
- use comparable scales across small multiples,
- represent uncertainty if claiming estimates,
- use direct labels when the legend is hard to follow.

An error rate value `0.012` formatted as `1.2%` is a display transformation; retain the underlying unit in calculations.

## 5. Trends and thresholds

Line chart sample:

```text
date,avg_latency_ms
2026-11-20,210
2026-11-21,245
2026-11-22,280
```

Chart the ordered date and add a threshold:

```python
ax.plot(frame["date"], frame["latency_ms"])
ax.axhline(260, linestyle="--", color="#c0392b", label="SLA 260 ms")
```

Output interpretation: the last point breaches the SLA. A line does not prove that releases caused the increase; that requires further evidence.

## 6. Bars and comparison

Sort categories by the metric unless category order carries meaning:

```python
ordered = summary.sort_values("error_rate")
sns.barplot(data=ordered, x="error_rate", y="service")
```

Label percentages directly and avoid 3D perspective. A bar plot may aggregate observations by estimator (often mean) and optionally uncertainty; a count plot counts rows.

## 7. Distributions

A histogram groups numeric values into bins. Too few bins hide structure; too many create noise. A box plot summarizes median, quartiles, and outliers but hides detailed multimodality. Pair it with raw points or distribution plots when sample size is manageable.

The dashboard histogram overlays regional latency distributions and a vertical SLA. Confirm bins are comparable before judging region differences.

## 8. Relationships

A scatter plot maps two numeric variables, and optional hue/size/style adds dimensions. More dimensions can overwhelm a graph and become an accidental legend puzzle.

```python
sns.scatterplot(data=frame, x="requests", y="availability", hue="service")
```

Correlation is not causation. A service may have high volume and good availability because of architecture, not because volume improves availability.

## 9. Matplotlib customizations

Useful controls:

- `set(title=..., xlabel=..., ylabel=...)`
- `tick_params(rotation=...)`
- `legend`
- `grid`
- colors, linestyles, markers
- `fig.tight_layout()`
- `subplots(nrows, ncols)`

Customization should improve interpretation. Choose colorblind-safe palettes and do not encode meaning by color alone when possible; add labels, markers, or line style.

## 10. Seaborn's role

Seaborn provides statistical defaults on Matplotlib. It accepts tidy DataFrames and semantic mappings such as `hue`, `style`, and `size`.

Families:

- relational: `scatterplot`, `lineplot`
- categorical: `barplot`, `boxplot`, `countplot`, `stripplot`
- distribution: `histplot`, `kdeplot`
- matrix: `heatmap`, `clustermap`

Seaborn's convenience does not remove the need to explain the estimator, aggregation, missing values, or confidence behavior.

## 11. Multiple-panel dashboard

The generated operations example asks four questions in four axes:

1. trend of daily average latency versus SLA,
2. mean error rate by service,
3. latency distribution by region,
4. volume versus availability by service/region.

The `2 x 2` subplot allows a review meeting to move from overall time trend to causes/segments. Each panel still needs units and an honest scale.

## 12. Data preparation before plotting

The raw visualization input must be validated:

- required columns present,
- dataset not empty,
- dates parsed,
- required fields not missing,
- rates within range,
- negative requests/latency rejected.

Grouping:

```python
daily = frame.groupby("date", as_index=False).agg(
    requests=("requests", "sum"),
    latency_ms=("latency_ms", "mean"),
)
```

is comparable to a SQL summary but needs attention to weighting. Averaging daily averages can differ from a request-weighted overall average.

## 13. Export and reproducibility

PNG is suitable for reports/screens; SVG/PDF can preserve vector text/lines. `dpi` controls raster resolution. `bbox_inches="tight"` may alter the image dimensions to include labels, so it should be deliberate in screenshot tests.

Generate a fixed seed for synthetic data, record the version of key libraries, and save a numeric summary alongside the image. Visual evidence becomes easier to review and reproduce.

## 14. Debugging checklist

1. Verify the data column names, units, and types.
2. Print `min`, `max`, `nunique`, and missing counts.
3. Test one tiny DataFrame before the full dashboard.
4. Confirm figure and axes dimensions.
5. If labels are missing, check each `ax` rather than the global state.
6. If the graphic is blank in batch mode, inspect aggregation and save backend, not only display settings.
7. Confirm output parent exists and file is nonempty.
8. Compare plotted values to expected numeric summary.

## 15. Common mistakes

- Treating categorical order as time.
- Confusing counts and averages.
- Misrepresenting percent values.
- Using a bright color palette without labels.
- Plotting raw values when an aggregation is required.
- Ignoring missing values or invalid rates.
- Saving before `tight_layout` and clipping labels.
- Claiming causation from a chart.

## 16. Practice

1. Draw a line chart with a known three-point input and state which point breaches.
2. Compare two service error rates with a sorted bar chart.
3. Use a box plot for region latency and list what it hides.
4. Add a heatmap of service × region error rates.
5. Change the SLA and verify both line/threshold and summary breach rate change together.
6. Add an annotation for the worst service without obscuring data.
7. Build a smoke test that verifies PNG signature and dimensions.
8. Explain one reason a weighted latency KPI could differ from a simple mean.
