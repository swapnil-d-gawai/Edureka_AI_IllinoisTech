# Module 2: Data Structures, Control Flow, and File Operations

- **LMS course:** [Modern Python & AI-Assisted Development](https://lms.snvaveranda.com/course/view.php?id=248)
- **Presentation URL/ID:** `https://lms.snvaveranda.com/mod/resource/view.php?id=8610` / `8610`

## Deck map

| Slides | Topic |
| --- | --- |
| 1–17 | `while`/`for`, loop controls, nested loops, and `match` patterns |
| 18–21 | Interactive input and safe interpretation guidance |
| 22–36 | Text/binary file operations, modes, attributes, seek, and close |
| 37–44 | Sequence operations: concatenation, repetition, membership, index, slice |
| 45–67 | Lists, tuples, strings, sets, dictionaries, and dictionary methods |
| 68–72 | `bytes`, `bytearray`, and `range` |
| 73–77 | Demonstration, summary, and review |

## Learning objectives

Select control structures, use structural pattern matching, validate interactive input, safely read/write files, manipulate sequences, choose set and mapping operations, and distinguish immutable bytes from mutable byte arrays.

> These notes summarize the protected deck for study; they do not reproduce its slide text, examples, or artwork.

## LMS demonstration walkthrough

- **Resources:** <https://lms.snvaveranda.com/mod/resource/view.php?id=8611> and <https://lms.snvaveranda.com/mod/resource/view.php?id=15705>.
- **Actual assignment:** 8611 contains nine focused exercises on conditionals/loops, terminal and file input, lists, tuples, strings, sets, dictionaries, bytes/byte arrays, and `range`. The 15705 extracted bundle repeats introductory `module-1` review scripts (keyword-based reviews, types, an LLM-cost calculation, and a mini assistant), so treat it as review rather than as a replacement for the 8611 control-flow/data-structure archive.
- **Input/data shape:** small scalar collections, text files, strings, nested collection examples, UTF-8 text converted to bytes, and lazy integer ranges; no protected dataset is needed.
- **Beginner workflow:** choose an input, trace each branch, track loop state on paper, use a context manager for a tiny text file, mutate only one collection at a time, print `repr(value)` and `type(value)`, then compare expected and actual values.
- **Relationship to current examples:** `incident_batch.py` is an **original extension beyond the LMS demonstration**. It combines the demonstrated structures into a validated JSON Lines batch with routing, duplicate detection, and an atomic-style report replacement.
- **Deliberate practice:** make a three-row synthetic table for each branch (`true`, `false`, `edge`), manually predict list/set/dict changes, create an empty file and a missing file, and explain each inclusive/exclusive boundary before writing code.

See the detailed walkthrough at the end of `NOTES.md`.
