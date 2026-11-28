"""Verify the shared palette and export non-data sample plots at both widths."""

import argparse
from pathlib import Path
import subprocess

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import colors, font_manager


FIGURES = Path(__file__).resolve().parents[1]
TEXT_WIDTH_PT = 452.9679  # Thesis build, as recorded in VISUAL_STYLE.md.
TEX_POINTS_PER_INCH = 72.27
ROLES = (
    "Vision", "Sensor", "Context", "Fusion", "Baseline", "Highlight",
    "Audio", "Thermal", "Depth", "Vibration", "Wrench",
)
EXAMPLES = (
    ("full", 1, "Imaging and audio", (
        ("Vision", "RGB", [0.19, 0.29, 0.53, 0.60, 0.73]),
        ("Thermal", "Thermal", [0.14, 0.34, 0.43, 0.58, 0.64]),
        ("Depth", "Depth", [0.22, 0.43, 0.61, 0.70, 0.79]),
        ("Audio", "Audio", [0.10, 0.20, 0.33, 0.43, 0.58]),
    )),
    ("half", 0.5, "Telemetry signals", (
        ("Sensor", "Combined", [0.19, 0.29, 0.53, 0.60, 0.73]),
        ("Vibration", "Vibration", [0.14, 0.34, 0.43, 0.58, 0.64]),
        ("Wrench", "Force/torque", [0.22, 0.43, 0.61, 0.70, 0.79]),
    )),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=Path("build/figures"))
    parser.add_argument("--font-dir", type=Path, help="directory with lmroman12*.ttf")
    parser.add_argument(
        "--tex-fonts", action="store_true",
        help="export through PGF/XeLaTeX with native Latin Modern fonts",
    )
    args = parser.parse_args()
    if args.tex_fonts and args.font_dir:
        parser.error("choose --tex-fonts or --font-dir")

    if args.font_dir:
        for face in ("regular", "bold"):
            font_manager.fontManager.addfont(args.font_dir / f"lmroman12-{face}.ttf")

    plt.style.use(FIGURES / "thesis.mplstyle")
    if args.tex_fonts:
        # Register native faces for Matplotlib's font metadata queries only;
        # XeLaTeX, rather than the direct PDF backend, embeds the actual fonts.
        for face in ("regular", "bold"):
            native = subprocess.check_output(
                ["kpsewhich", f"lmroman12-{face}.otf"], text=True,
            ).strip()
            font_manager.fontManager.addfont(native)
        plt.switch_backend("pgf")
        plt.rcParams.update({
            "pgf.texsystem": "xelatex",
            "pgf.rcfonts": False,
            "pgf.preamble": (
                r"\usepackage{fontspec}\usepackage{amsmath,amssymb}"
                r"\usepackage{fix-cm}\pagestyle{empty}"
            ),
        })
        # PGF writes TeX pt; the shared style specifies PDF pt (bp).
        for key in ("font.size", "axes.titlesize", "axes.labelsize",
                    "xtick.labelsize", "ytick.labelsize", "legend.fontsize",
                    "legend.title_fontsize"):
            plt.rcParams[key] *= TEX_POINTS_PER_INCH / 72
        print("Text backend: PGF/XeLaTeX, native Latin Modern; verify with pdffonts")

    for weight in (() if args.tex_fonts else ("normal", "bold")):
        properties = font_manager.FontProperties(family=["serif"], weight=weight)
        font = Path(font_manager.findfont(properties))
        if font.suffix.lower() != ".ttf":
            raise ValueError(f"Use a TrueType face for PDF embedding: {font}")
        if args.font_dir and font.parent != args.font_dir.resolve():
            raise ValueError(f"Matplotlib selected {font} instead of the supplied {weight} face")
        print(f"Serif {weight}: {font.name}")
        if not args.font_dir:
            print("Font selection only: use --tex-fonts or verified --font-dir "
                  "to check the thesis face; fallback is not a font-match pass.")

    styles = dict(zip(ROLES, plt.rcParams["axes.prop_cycle"], strict=True))
    tikz = (FIGURES / "tikz_style.tex").read_text(encoding="utf-8")
    rules = (FIGURES / "VISUAL_STYLE.md").read_text(encoding="utf-8")
    for role, props in styles.items():
        hex_code = colors.to_hex(props["color"])[1:].upper()
        if f"`#{hex_code}` | `Thesis{role}`" not in rules:
            raise ValueError(f"{role} in Matplotlib differs from the documented palette")
        if rf"\definecolor{{Thesis{role}}}{{HTML}}{{{hex_code}}}" not in tikz:
            raise ValueError(f"TikZ and Matplotlib disagree on {role}: #{hex_code}")

    args.outdir.mkdir(parents=True, exist_ok=True)
    for name, *_ in EXAMPLES:
        path = args.outdir / f"style_smoke_{name}.pdf"
        if path.exists():
            raise FileExistsError(f"Preserve existing output; choose a new --outdir: {path}")
    for name, fraction, title, series in EXAMPLES:
        width_inches = fraction * TEXT_WIDTH_PT / TEX_POINTS_PER_INCH
        fig, ax = plt.subplots(figsize=(width_inches, 2.2))
        points = range(5)
        for role, label, values in series:
            ax.plot(points, values, label=label, **styles[role])
        ax.set(title=title, xlabel=r"Step $t$", ylabel="Illustrative value")
        ax.set_xticks(points)
        ax.set_ylim(0, 1)
        ax.legend(loc="upper left")
        path = args.outdir / f"style_smoke_{name}.pdf"
        fig.savefig(path)
        plt.close(fig)

        # XeLaTeX may compress page objects and rounds dimensions to 0.01 bp.
        from pypdf import PdfReader

        pdf = PdfReader(path)
        width_bp = float(pdf.pages[0].mediabox.width)
        if len(pdf.pages) != 1 or abs(width_bp - 72 * width_inches) > 0.01:
            raise ValueError(f"Unexpected PDF canvas width in {path}")
        print(f"{path} ({width_inches:.6f} in; PDF width {width_bp:.6f} bp)")


if __name__ == "__main__":
    main()
