#!/usr/bin/env python3
"""Check the compact F169 case-study data used in the README."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def row_by_key(path: Path, key: str, value: str) -> dict[str, str]:
    for row in read_csv(path):
        if row[key] == value:
            return row
    raise AssertionError(f"missing {key}={value} in {path}")


def main() -> None:
    card = json.loads((DATA / "f169_observation_card.json").read_text(encoding="utf-8"))
    assert card["truth_table"] == "0x169AE443"
    assert card["n_inputs"] == 5
    assert card["component_signature"] == "A2 + E6 + E6"
    assert card["on_set_size"] == 14
    assert card["on_set_edge_count"] == 11
    assert card["full_npn5_f169_signature_count"] == 3
    assert card["full_npn5_f169_signature_examples"] == [
        "0x013D3EC2",
        "0x035ABC83",
        "0x169AE443",
    ]

    vertices = read_csv(DATA / "f169_support_graph_vertices.csv")
    edges = read_csv(DATA / "f169_support_graph_edges.csv")
    assert len(vertices) == 14
    assert len(edges) == 11
    assert all(len(row["bits5"]) == 5 for row in vertices)

    component_vertices: dict[str, list[dict[str, str]]] = defaultdict(list)
    component_types: dict[str, str] = {}
    for row in vertices:
        component_vertices[row["component_id"]].append(row)
        component_types[row["component_id"]] = row["component_type"]

    size_by_type = sorted(
        (component_types[component_id], len(rows))
        for component_id, rows in component_vertices.items()
    )
    assert size_by_type == [("A2", 2), ("E6", 6), ("E6", 6)]

    e6e6 = row_by_key(
        DATA / "npn5_e_component_multiset_breakdown.csv",
        "e_component_multiset",
        "E6 + E6",
    )
    assert int(e6e6["object_count"]) == 79

    e6_presence = row_by_key(
        DATA / "npn5_e_type_family_breakdown.csv",
        "e_family_bucket",
        "E6",
    )
    assert int(e6_presence["object_count"]) == 3617

    edge_types = Counter(row["component_type"] for row in edges)
    print("F169 case-study check OK")
    print(f"truth_table={card['truth_table']}")
    print(f"signature={card['component_signature']}")
    print(f"vertices={len(vertices)} edges={len(edges)}")
    print(f"component_sizes={size_by_type}")
    print(f"edge_types={dict(edge_types)}")
    print("A2+E6+E6 representatives=3")
    print("E6+E6 multiset classes=79")
    print("E6-present classes=3617")


if __name__ == "__main__":
    main()
