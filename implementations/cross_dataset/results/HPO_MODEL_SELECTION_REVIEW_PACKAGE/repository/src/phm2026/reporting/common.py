"""Small deterministic helpers shared by professor-facing report generators."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import csv
import json
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt

from ..utils.provenance import ArtifactRecord, RunContext

ACADEMIC_COLORS = ("#24476B", "#2A788E", "#56A86C", "#D79A2B", "#B64D5B")


def apply_academic_style() -> None:
    """Apply a restrained, legible style without requiring external fonts."""

    mpl.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#444444",
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": "#D9DEE3",
            "grid.linewidth": 0.7,
            "font.size": 10,
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "legend.frameon": False,
            "savefig.bbox": "tight",
        }
    )


def save_figure_pair(figure: plt.Figure, stem: Path) -> tuple[Path, Path]:
    """Write a 300-DPI PNG and an SVG with the same basename."""

    png = stem.with_suffix(".png")
    svg = stem.with_suffix(".svg")
    figure.savefig(png, dpi=300, facecolor="white")
    figure.savefig(svg, format="svg", facecolor="white")
    plt.close(figure)
    return png, svg


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    columns = sorted({str(key) for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(
            {column: row.get(column) for column in columns} for row in rows
        )


def json_text(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def finalize_run(
    run: RunContext,
    artifacts: list[ArtifactRecord],
) -> list[ArtifactRecord]:
    """Write provenance and a final output manifest without self-hashing."""

    provenance_path = run.write_provenance(artifacts)
    artifacts.append(run.artifact(provenance_path, role="provenance"))
    run.write_output_manifest(artifacts)
    return artifacts
