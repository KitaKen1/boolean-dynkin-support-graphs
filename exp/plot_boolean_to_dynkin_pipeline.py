#!/usr/bin/env python3
"""Draw a compact Boolean-function to support-graph schematic using Q3."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "figures" / "boolean_to_support_dynkin_pipeline.svg"
ON_SET = {1, 2, 4, 5, 6}


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

    def text(
        self,
        x: float,
        y: float,
        text: object,
        size: int = 13,
        weight: str = "400",
        color: str = "#17201c",
        anchor: str = "start",
        family: str = "Arial, Helvetica, sans-serif",
    ) -> None:
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}">{esc(text)}</text>'
        )

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: str = "#9aa59f",
        width: float = 2.0,
    ) -> None:
        self.add(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>'
        )

    def circle(
        self,
        x: float,
        y: float,
        r: float,
        fill: str,
        stroke: str,
        width: float = 2.0,
    ) -> None:
        self.add(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{width}"/>'
        )

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str,
        stroke: str = "#d9ded8",
        rx: float = 8,
    ) -> None:
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx:.1f}" fill="{fill}" stroke="{stroke}"/>'
        )


def bits3(index: int) -> str:
    return format(index, "03b")


def arrow(svg: Svg, x1: float, y: float, x2: float, label: str) -> None:
    svg.line(x1, y, x2, y, "#b8c0bb", 2.2)
    svg.add(f'<path d="M {x2:.1f} {y:.1f} l -9 -6 v 12 z" fill="#b8c0bb"/>')
    svg.text((x1 + x2) / 2, y - 12, label, 11, "700", "#5e6a64", "middle")


def q3_coord(index: int, x: float, y: float) -> tuple[float, float]:
    coords = {
        0: (0, 54),
        1: (52, 24),
        2: (0, 142),
        3: (52, 112),
        4: (106, 54),
        5: (158, 24),
        6: (106, 142),
        7: (158, 112),
    }
    cx, cy = coords[index]
    return x + cx, y + cy


def draw_truth_table(svg: Svg, x: float, y: float) -> None:
    svg.text(x, y, "Boolean function", 16, "700")
    svg.text(x, y + 23, "3-input example", 13, "700", "#5e6a64")
    svg.rect(x, y + 48, 180, 214, "#ffffff", "#e1e5df", 7)
    svg.text(x + 18, y + 72, "x", 12, "700", "#5e6a64")
    svg.text(x + 118, y + 72, "f(x)", 12, "700", "#5e6a64")
    for i in range(8):
        yy = y + 98 + i * 20
        val = 1 if i in ON_SET else 0
        if val:
            svg.rect(x + 10, yy - 15, 160, 18, "#e6efe8", "#e6efe8", 4)
        svg.text(x + 18, yy, bits3(i), 12, "700", "#17201c", family="Menlo, Consolas, monospace")
        svg.text(x + 132, yy, val, 12, "700", "#315f4d" if val else "#8a938e")
    svg.text(x + 18, y + 246, "on-set = rows with 1", 12, "700", "#315f4d")


def draw_q3(svg: Svg, x: float, y: float) -> None:
    svg.text(x, y, "Boolean cube Q3", 16, "700")
    svg.text(x, y + 23, "each 3-bit string is a vertex", 13, "400", "#5e6a64")
    ox = x + 28
    oy = y + 58
    edges = [(i, j) for i in range(8) for j in range(i + 1, 8) if bin(i ^ j).count("1") == 1]
    for a, b in edges:
        ax, ay = q3_coord(a, ox, oy)
        bx, by = q3_coord(b, ox, oy)
        both_on = a in ON_SET and b in ON_SET
        svg.line(ax, ay, bx, by, "#315f4d" if both_on else "#d7ded8", 3.0 if both_on else 1.4)
    for i in range(8):
        cx, cy = q3_coord(i, ox, oy)
        selected = i in ON_SET
        svg.circle(cx, cy, 8.2, "#315f4d" if selected else "#ffffff", "#315f4d" if selected else "#aeb7b2", 2.0)
        svg.text(cx, cy - 15, bits3(i), 10, "700", "#5e6a64", "middle", "Menlo, Consolas, monospace")
    svg.text(x + 28, y + 246, "green = on-set vertices and inherited edges", 12, "700", "#315f4d")


def draw_support(svg: Svg, x: float, y: float) -> None:
    green = "#315f4d"
    svg.text(x, y, "Support graph", 16, "700")
    svg.text(x, y + 23, "induced graph on the on-set", 13, "400", "#5e6a64")
    coords = {
        1: (x + 38, y + 122),
        5: (x + 90, y + 122),
        4: (x + 142, y + 122),
        6: (x + 142, y + 190),
        2: (x + 90, y + 190),
    }
    edges = [(1, 5), (5, 4), (4, 6), (6, 2)]
    for a, b in edges:
        svg.line(coords[a][0], coords[a][1], coords[b][0], coords[b][1], green, 3.0)
    for node, (cx, cy) in coords.items():
        svg.circle(cx, cy, 8.3, "#ffffff", green, 2.3)
        svg.text(cx, cy - 15, bits3(node), 10, "700", "#5e6a64", "middle", "Menlo, Consolas, monospace")
    svg.text(x + 90, y + 244, "one connected component", 12, "700", "#5e6a64", "middle")


def draw_signature(svg: Svg, x: float, y: float) -> None:
    green = "#315f4d"
    gold = "#8b6b24"
    svg.text(x, y, "Dynkin diagram match", 16, "700")
    svg.text(x, y + 23, "same graph shape", 13, "400", "#5e6a64")
    step = 34
    coords = [(x + 24 + i * step, y + 148) for i in range(5)]
    for (x1, y1), (x2, y2) in zip(coords, coords[1:]):
        svg.line(x1, y1, x2, y2, gold, 3.0)
    for cx, cy in coords:
        svg.circle(cx, cy, 8.0, "#ffffff", gold, 2.4)
    svg.rect(x + 2, y + 194, 198, 44, "#f3edd9", "#d3bd77", 999)
    svg.text(x + 101, y + 222, "A5 Dynkin diagram", 17, "700", gold, "middle")
    svg.text(x + 101, y + 254, "component shape = A-type path", 12, "700", "#5e6a64", "middle")


def main() -> None:
    width = 1180
    height = 360
    svg = Svg()
    svg.add(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
    )
    svg.add('<title id="title">Boolean strings become vertices of Q3</title>')
    svg.add(
        '<desc id="desc">A three-input Boolean function is shown as truth-table rows, '
        'vertices of Q3, an induced on-set support graph, and a simple A-type shape label.</desc>'
    )
    svg.rect(0, 0, width, height, "#ffffff", "#ffffff", 0)
    svg.text(34, 42, "Boolean strings become vertices of Q3", 22, "700")

    draw_truth_table(svg, 46, 82)
    arrow(svg, 250, 214, 320, "vertices")
    draw_q3(svg, 350, 82)
    arrow(svg, 610, 214, 680, "induce")
    draw_support(svg, 710, 82)
    arrow(svg, 880, 214, 950, "read")
    draw_signature(svg, 970, 82)

    svg.add("</svg>")
    OUTPUT.write_text("\n".join(svg.parts) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
