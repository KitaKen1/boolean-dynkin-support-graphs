#!/usr/bin/env python3
"""Draw a compact A/D/E Dynkin diagram shape legend."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "figures" / "dynkin_diagram_shapes_ADE.svg"


def esc(text: object) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


class Svg:
    def __init__(self) -> None:
        self.parts: list[str] = []

    def add(self, text: str) -> None:
        self.parts.append(text)

    def line(self, x1: float, y1: float, x2: float, y2: float, color: str) -> None:
        self.add(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="2.2" stroke-linecap="round"/>'
        )

    def node(self, x: float, y: float, color: str) -> None:
        self.add(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="#ffffff" '
            f'stroke="{color}" stroke-width="2.2"/>'
        )

    def text(
        self,
        x: float,
        y: float,
        text: object,
        size: int = 13,
        weight: str = "400",
        color: str = "#17201c",
        anchor: str = "start",
    ) -> None:
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            'font-family="Arial, Helvetica, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>'
        )


def draw_path(svg: Svg, x: float, y: float, n: int, color: str, step: float = 28) -> None:
    coords = [(x + i * step, y) for i in range(n)]
    for (x1, y1), (x2, y2) in zip(coords, coords[1:]):
        svg.line(x1, y1, x2, y2, color)
    for px, py in coords:
        svg.node(px, py, color)


def draw_d(svg: Svg, x: float, y: float, n: int, color: str) -> None:
    # Standard schematic D_n: a path with one extra leaf attached to the second node.
    chain = [(x + i * 29, y) for i in range(n - 1)]
    leaf = (x + 29, y - 27)
    for (x1, y1), (x2, y2) in zip(chain, chain[1:]):
        svg.line(x1, y1, x2, y2, color)
    svg.line(chain[1][0], chain[1][1], leaf[0], leaf[1], color)
    for px, py in chain + [leaf]:
        svg.node(px, py, color)


def draw_e(svg: Svg, x: float, y: float, n: int, color: str) -> None:
    # E6/E7/E8: horizontal chain of n-1 nodes with one vertical branch at node 3.
    chain = [(x + i * 30, y) for i in range(n - 1)]
    leaf = (x + 60, y - 31)
    for (x1, y1), (x2, y2) in zip(chain, chain[1:]):
        svg.line(x1, y1, x2, y2, color)
    svg.line(chain[2][0], chain[2][1], leaf[0], leaf[1], color)
    for px, py in chain + [leaf]:
        svg.node(px, py, color)


def main() -> None:
    width = 1180
    height = 650
    svg = Svg()
    svg.add(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
    )
    svg.add("<title id=\"title\">A/D/E Dynkin diagram shape legend</title>")
    svg.add(
        "<desc id=\"desc\">Schematic simply-laced A, D, and E Dynkin diagram shapes used by the support-graph classifier.</desc>"
    )
    svg.add('<rect width="100%" height="100%" fill="#ffffff"/>')
    svg.text(34, 40, "A/D/E Dynkin diagram shapes used in the classifier", 22, "700")
    svg.text(
        34,
        66,
        "Schematic simple unweighted shapes. A_n is a path; D_n is a forked path; E6/E7/E8 are exceptional trees.",
        13,
        "400",
        "#5e6a64",
    )

    panels = [
        (34, 91, 342, 492, "#315f4d", "A_n paths"),
        (414, 91, 306, 492, "#355f86", "D_n forked paths"),
        (758, 91, 388, 492, "#8e3f35", "Exceptional E types"),
    ]
    for x, y, w, h, color, title in panels:
        svg.add(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" '
            f'fill="#fbfcfa" stroke="#d9ded8"/>'
        )
        svg.text(x + 18, y + 31, title, 17, "700", color)

    green = "#315f4d"
    blue = "#355f86"
    red = "#8e3f35"

    for n in range(1, 9):
        y = 150 + (n - 1) * 49
        svg.text(58, y + 5, f"A{n}", 13, "700", green)
        draw_path(svg, 102, y, n, green, 27)

    for idx, n in enumerate(range(4, 9)):
        y = 163 + idx * 78
        svg.text(438, y + 5, f"D{n}", 13, "700", blue)
        draw_d(svg, 489, y, n, blue)

    for idx, n in enumerate((6, 7, 8)):
        y = 178 + idx * 121
        svg.text(782, y + 5, f"E{n}", 14, "700", red)
        draw_e(svg, 837, y, n, red)

    svg.add('<rect x="34" y="603" width="1112" height="1" fill="#d9ded8"/>')
    svg.text(
        34,
        629,
        "Only simply-laced A/D/E shapes are used here. B/C/F/G would need extra structure beyond a simple unweighted support graph.",
        12,
        "400",
        "#5e6a64",
    )
    svg.add("</svg>")
    OUTPUT.write_text("\n".join(svg.parts) + "\n")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
