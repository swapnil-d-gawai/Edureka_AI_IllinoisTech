# Modern Python & AI-Assisted Development

LMS course: [Modern Python & AI-Assisted Development B-22](https://lms.snvaveranda.com/course/view.php?id=248)

Existing course work is preserved in the original abbreviated module folders.

## Study workflow

The material is written for a learner moving from SQL, Informatica, Unix,
AutoSys, or IBM TWS into Python. Treat a Python script like a batch job:
inputs enter, transformations run in a defined order, validation checks the
result, and the script exits with a status. New terms are introduced in the
notes before they appear in an example.

Each module is organized as:

- `docs/README.md` — links to the protected LMS presentation, learning objectives, and slide-to-topic map
- `docs/NOTES.md` — concise implementation notes based on the presentation
- `examples/` — medium-complexity, industry-style exercises for hands-on practice
- Existing files beside these folders — original classroom demonstrations

Recommended sequence:

1. Review the slide map in `docs/README.md`.
2. Read `docs/NOTES.md` from top to bottom; do not skip the “mental model”
   and terminology sections.
3. Read the matching `examples/*.py` before executing it. Follow its comments
   from imports, to input, transformation, validation, and output.
4. Predict the behavior, then run the exercise and compare its actual data,
   charts, logs, or API responses with that prediction.
5. Change one value at a time and rerun. If a result changes, explain why
   before continuing.
6. Complete the extension challenges in `examples/README.md`.

## Module map

| Module | Focus |
| --- | --- |
| `M1_PPE` | Python fundamentals, data types, and operators |
| `M2_DCF` | Data structures, control flow, pattern matching, and files |
| `M3_APC` | Advanced Python, OOP, decorators, exceptions, and logging |
| `M4_NCDA` | NumPy and pandas data analysis |
| `M5_DV` | Matplotlib and seaborn visualization |
| `M6_AF` | FastAPI backends |
| `M7_SG` | Streamlit and Gradio AI-native applications |
| `M8_AGC` | GitHub Copilot-assisted development |
