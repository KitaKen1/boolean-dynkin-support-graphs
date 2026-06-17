#!/usr/bin/env python3
"""Smoke-test the GitHub-facing Dynkin support-graph package."""

from __future__ import annotations

import csv
import json
import re
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGURES = ROOT / "figures"


class RefParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value for key, value in attrs if value is not None}
        if "id" in values:
            self.ids.add(values["id"])
        if tag == "img" and "src" in values:
            self.refs.append(values["src"])
        if tag == "a" and "href" in values:
            self.refs.append(values["href"])


def read_csv(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return len(rows)


def assert_local_ref(ref: str, ids: set[str]) -> None:
    if ref.startswith("#"):
        assert ref[1:] in ids, f"missing anchor: {ref}"
        return
    if re.match(r"^[a-z]+:", ref):
        return
    target = ROOT / ref
    assert target.exists(), f"missing local reference: {ref}"


def main() -> None:
    for path in DATA.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    for path in DATA.glob("*.csv"):
        read_csv(path)

    for path in FIGURES.glob("*.svg"):
        text = path.read_text(encoding="utf-8")
        assert "<svg" in text and "</svg>" in text, path

    parser = RefParser()
    parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
    for ref in parser.refs:
        assert_local_ref(ref, parser.ids)

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    markdown_refs = re.findall(r"!?\[[^\]]+\]\(([^)]+)\)", readme)
    for ref in markdown_refs:
        assert_local_ref(ref, parser.ids)

    for path in [ROOT / "README.md", ROOT / "index.html"]:
        text = path.read_text(encoding="utf-8")
        for forbidden in ["/" + "Users" + "/", "Drop" + "box"]:
            assert forbidden not in text

    print("package validation OK")


if __name__ == "__main__":
    main()
