# Module 3: Advanced Python Concepts

- **LMS course:** [Modern Python & AI-Assisted Development](https://lms.snvaveranda.com/course/view.php?id=248)
- **Presentation URL/ID:** `https://lms.snvaveranda.com/mod/resource/view.php?id=8612` / `8612`

## Deck map

| Slides | Topic |
| --- | --- |
| 1–7 | Decorators for reusable pipeline behavior |
| 8–24 | Classes, objects, inheritance, and polymorphism |
| 25–35 | Exceptions, custom errors, cleanup, and logging |
| 36–59 | Modules, packages, standard modules, and `pip` |
| 60–62 | JSON and CSV file workflows |
| 63–75 | `asyncio`, concurrent LLM calls, and benchmarking |
| 76–79 | Summary and review |

## Learning objectives

Compose pipeline decorators, model behavior with OOP, handle expected failures, emit useful logs, organize/import packages, manage dependencies, process structured files, and compare sequential with concurrent I/O.

> These notes summarize the protected deck for study; they do not reproduce its slide text, examples, or artwork.

## LMS demonstration walkthrough

- **Resource:** <https://lms.snvaveranda.com/mod/resource/view.php?id=8613>.
- **Actual assignment:** the archive progresses from class/object scope and inheritance (including a customer/privilege scenario), to standard modules, exception propagation/custom exceptions, regular expressions, and finally concurrent LLM calls to Groq with `asyncio` and timing.
- **Input/data shape:** class records such as customer ID/name/type/amount, strings for regex, module/path values, and a list of independent prompts for the async activity; the API variant also needs a user-supplied Groq key.
- **Beginner workflow:** (1) model one plain object, (2) introduce one child class, (3) predict method resolution and failure flow, (4) isolate one regex input, (5) run a local delayed coroutine, (6) compare sequential/concurrent timing, and only then attach a real provider.
- **Relationship to current examples:** the class/file examples preserve the concepts at a smaller scale. `async_vendor_monitor.py` is an **offline original extension beyond the LMS Groq demonstration**: it uses the same concurrency contract without an API key or copied provider implementation.
- **Deliberate practice:** draw the inheritance diagram and exception route first; use three synthetic prompts; force a timeout-like failure; verify every result still appears; run twice but interpret timing as observational rather than a guaranteed speedup.

See the detailed walkthrough at the end of `NOTES.md`.
