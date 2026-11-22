"""Plan and validate a course production workspace using Python fundamentals."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import json


ALLOWED_ASSET_TYPES = {"video", "audio", "graphics"}


@dataclass(frozen=True)
class CourseSpec:
    """Validated immutable input for one course workspace."""

    slug: str
    lessons: int
    assets: tuple[str, ...]

    @classmethod
    def from_mapping(cls, value: dict[str, object]) -> "CourseSpec":
        """Parse loose JSON-shaped values into a safe, typed course record."""
        if not isinstance(value.get("slug"), str) or not value["slug"].strip():
            raise ValueError("slug must be a non-empty string")
        slug = str(value["slug"]).strip()
        if not all(part.replace("-", "").isalnum() for part in slug.split("_")):
            raise ValueError("slug may contain only letters, numbers, underscores, and hyphens")
        lessons = value.get("lessons")
        if isinstance(lessons, bool) or not isinstance(lessons, int) or not 1 <= lessons <= 500:
            raise ValueError("lessons must be an integer from 1 to 500")
        raw_assets = value.get("assets", sorted(ALLOWED_ASSET_TYPES))
        if not isinstance(raw_assets, list) or not raw_assets:
            raise ValueError("assets must be a non-empty list")
        assets = tuple(str(item).lower().strip() for item in raw_assets)
        if len(set(assets)) != len(assets):
            raise ValueError("assets must not contain duplicates")
        unsupported = set(assets) - ALLOWED_ASSET_TYPES
        if unsupported:
            raise ValueError(f"unsupported asset types: {sorted(unsupported)}")
        return cls(slug=slug, lessons=lessons, assets=assets)


def build_plan(root: Path, specs: list[CourseSpec]) -> dict[str, object]:
    """Calculate deterministic output paths without changing the filesystem."""
    if root.exists() and not root.is_dir():
        raise ValueError(f"workspace root is not a directory: {root}")
    folders: list[str] = []
    for spec in specs:
        for lesson in range(1, spec.lessons + 1):
            # Path composition represents the folder hierarchy without relying on OS separators.
            lesson_dir = root / spec.slug / f"lesson_{lesson:02d}"
            for asset_type in spec.assets:
                folders.append(str(lesson_dir / asset_type))
    unique_folders = sorted(set(folders))
    total = len(unique_folders)
    if total > 10_000:
        raise ValueError(f"plan creates too many folders ({total})")
    return {
        "root": str(root),
        "courses": [spec.slug for spec in specs],
        "folder_count": total,
        "folders": unique_folders,
    }


def materialize(plan: dict[str, object]) -> None:
    """Create the folders from a previously validated dry-run plan."""
    root = Path(str(plan["root"]))
    root.mkdir(parents=True, exist_ok=True)
    for folder in plan["folders"]:
        (root.parent / Path(str(folder)).relative_to(root.parent)).mkdir(parents=True, exist_ok=True)


def parse_args() -> argparse.Namespace:
    """Define the command-line boundary, including the explicit apply switch."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("course_workspace"))
    parser.add_argument("--apply", action="store_true", help="create the planned directories")
    parser.add_argument("--json", type=Path, help="optional JSON array of course specifications")
    return parser.parse_args()


def load_specs(path: Path | None) -> list[CourseSpec]:
    """Load course JSON or provide a small repeatable classroom dataset."""
    source: list[dict[str, object]]
    if path:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, list):
            raise ValueError("input JSON must contain an array")
        if not all(isinstance(item, dict) for item in loaded):
            raise ValueError("each course specification must be an object")
        source = loaded
    else:
        source = [
            {"slug": "python_genai", "lessons": 3, "assets": ["video", "graphics"]},
            {"slug": "data_analytics", "lessons": 2},
        ]
    specs = [CourseSpec.from_mapping(item) for item in source]
    if len({spec.slug for spec in specs}) != len(specs):
        raise ValueError("course slugs must be unique")
    return specs


def main() -> int:
    """Validate inputs, preview or apply work, and return a scheduler-friendly status."""
    args = parse_args()
    try:
        plan = build_plan(args.root, load_specs(args.json))
        if args.apply:
            materialize(plan)
        print(json.dumps(plan, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
