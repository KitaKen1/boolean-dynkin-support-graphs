#!/usr/bin/env python3
"""Plot n=1..5 Dynkin type presence as a GitHub Pages-friendly SVG."""

from __future__ import annotations

import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT
INPUT = PACKAGE / "data" / "dynkin_type_counts_by_n_1_to_5.csv"
OUTPUT = PACKAGE / "figures" / "dynkin_type_presence_matrix_1_to_5.svg"

TYPES = [
    "A1",
    "A2",
    "A3",
    "A4",
    "A5",
    "A6",
    "A7",
    "A8",
    "D4",
    "D5",
    "D6",
    "D7",
    "D8",
    "E6",
    "E7",
    "E8",
]

TOTALS = {1: 4, 2: 16, 3: 256, 4: 65536, 5: 616126}


def fmt_count(value: int) -> str:
    if value >= 1000:
        return f"{value:,}"
    return str(value)


def fmt_rate(value: float) -> str:
    if value == 0:
        return "0%"
    if value < 0.001:
        return f"{value * 100:.3f}%"
    if value < 0.01:
        return f"{value * 100:.2f}%"
    return f"{value * 100:.1f}%"


def esc(text: object) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def family_color(kind: str) -> str:
    if kind.startswith("A"):
        return "#315f4d"
    if kind.startswith("D"):
        return "#355f86"
    return "#8e3f35"


def cell_fill(rate: float, kind: str) -> str:
    if rate <= 0:
        return "#f6f7f3"
    # Square-root scaling keeps small E/D rates visible without saturating A1.
    t = min(1.0, math.sqrt(rate))
    palettes = {
        "A": ((246, 247, 243), (82, 137, 102)),
        "D": ((246, 247, 243), (74, 125, 169)),
        "E": ((246, 247, 243), (174, 83, 71)),
    }
    fam = kind[0]
    lo, hi = palettes[fam]
    rgb = tuple(round(lo[i] + (hi[i] - lo[i]) * t) for i in range(3))
    return f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"


def load_rows() -> dict[tuple[int, str], dict[str, object]]:
    rows: dict[tuple[int, str], dict[str, object]] = {}
    with INPUT.open(newline="") as f:
        for row in csv.DictReader(f):
            typ = row["type"]
            n = int(row["n"])
            if typ not in TYPES or n not in TOTALS:
                continue
            rows[(n, typ)] = {
                "count": int(row["objects_containing_type"]),
                "occurrences": int(row["total_component_occurrences"]),
                "rate": float(row["rate"]),
            }
    return rows


def main() -> None:
    rows = load_rows()
    width = 1040
    left = 102
    top = 124
    cell_w = 150
    cell_h = 42
    gap = 7
    type_w = 74
    height = top + len(TYPES) * (cell_h + gap) + 90
    out: list[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
    )
    out.append("<title id=\"title\">Dynkin type presence matrix for n=1 to n=5</title>")
    out.append(
        "<desc id=\"desc\">Object-level counts by Dynkin type. "
        "Cell color shows rate within each universe; text shows object count and rate.</desc>"
    )
    out.append("<rect width=\"100%\" height=\"100%\" fill=\"#ffffff\"/>")
    out.append(
        '<text x="34" y="38" font-family="Arial, Helvetica, sans-serif" '
        'font-size="22" font-weight="700" fill="#17201c">Dynkin type presence by input size</text>'
    )
    out.append(
        '<text x="34" y="64" font-family="Arial, Helvetica, sans-serif" '
        'font-size="13" fill="#5e6a64">Cell text: objects containing the type. '
        'Cell color: rate inside that n-universe. n=1..4 are all truth tables; n=5 is full NPN canonical representatives.</text>'
    )

    for i, n in enumerate(range(1, 6)):
        x = left + type_w + i * cell_w
        out.append(
            f'<text x="{x + cell_w / 2}" y="101" text-anchor="middle" '
            'font-family="Arial, Helvetica, sans-serif" font-size="16" '
            f'font-weight="700" fill="#17201c">n={n}</text>'
        )
        universe = "all truth tables" if n <= 4 else "NPN reps"
        out.append(
            f'<text x="{x + cell_w / 2}" y="119" text-anchor="middle" '
            'font-family="Arial, Helvetica, sans-serif" font-size="10.5" '
            f'fill="#5e6a64">{esc(universe)} · total {fmt_count(TOTALS[n])}</text>'
        )

    for r, typ in enumerate(TYPES):
        y = top + r * (cell_h + gap)
        fam = typ[0]
        color = family_color(typ)
        out.append(
            f'<rect x="34" y="{y}" width="{type_w}" height="{cell_h}" rx="6" fill="{color}" opacity="0.13"/>'
        )
        out.append(
            f'<text x="70" y="{y + 27}" text-anchor="middle" '
            'font-family="Arial, Helvetica, sans-serif" font-size="15" '
            f'font-weight="700" fill="{color}">{esc(typ)}</text>'
        )
        for i, n in enumerate(range(1, 6)):
            x = left + type_w + i * cell_w
            data = rows.get((n, typ), {"count": 0, "occurrences": 0, "rate": 0.0})
            count = int(data["count"])
            rate = float(data["rate"])
            fill = cell_fill(rate, typ)
            stroke = "#e1e4df"
            stroke_w = 1
            if typ == "E6":
                stroke = "#8e3f35"
                stroke_w = 1.6
            out.append(
                f'<rect x="{x}" y="{y}" width="{cell_w - gap}" height="{cell_h}" rx="6" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}"/>'
            )
            text_color = "#17201c" if rate < 0.35 else "#ffffff"
            sub_color = "#5e6a64" if rate < 0.35 else "#f4f7f3"
            out.append(
                f'<text x="{x + (cell_w - gap) / 2}" y="{y + 17}" text-anchor="middle" '
                'font-family="Arial, Helvetica, sans-serif" font-size="13" '
                f'font-weight="700" fill="{text_color}">{fmt_count(count)}</text>'
            )
            out.append(
                f'<text x="{x + (cell_w - gap) / 2}" y="{y + 34}" text-anchor="middle" '
                'font-family="Arial, Helvetica, sans-serif" font-size="11" '
                f'fill="{sub_color}">{fmt_rate(rate)}</text>'
            )

    legend_y = height - 48
    out.append(
        f'<text x="34" y="{legend_y}" font-family="Arial, Helvetica, sans-serif" '
        'font-size="12" fill="#5e6a64">A/D/E only. B/C/F/G are not classified here because the support graph is simple and unweighted. '
        'Counts are object-level predicates, not component occurrence totals.</text>'
    )
    out.append(
        f'<text x="34" y="{legend_y + 21}" font-family="Arial, Helvetica, sans-serif" '
        'font-size="12" fill="#5e6a64">Component occurrence totals are included in data/dynkin_type_counts_by_n_1_to_5.csv.</text>'
    )
    out.append("</svg>")
    OUTPUT.write_text("\n".join(out) + "\n")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
