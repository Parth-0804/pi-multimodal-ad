# Thesis figure style

## Page layout and canvas

`main.tex` uses XeLaTeX, `report[12pt,a4paper,oneside]` and `geometry[margin=1in]`. **VERIFIED for this working revision on 25 November 2026:** a compiled probe copied the active `main.tex` preamble and applied its normal chapter-body `\apaprose` settings. It measured `\textwidth = \linewidth = 452.9679pt` and `\textheight = 700.50687pt`, matching the archive's November 20 v3 dimensions. The body selected `lmroman12-regular` and `lmroman12-bold` at 12 TeX pt. See [the installation verification](STYLE_INSTALL_VERIFICATION.md) for the probe and build evidence. Inside a minipage, list or subfigure, measure the local `\linewidth`.

| Canvas | TeX width | Millimetres | Inches for Matplotlib |
|---|---:|---:|---:|
| Full | `\textwidth` = 452.9679 TeX pt | 159.20 | 6.267717 |
| Half | `.5\textwidth` = 226.48395 TeX pt | 79.60 | 3.133858 |

Use `width=\linewidth` in `\includegraphics` when the figure should fill its container. Use `width=.5\linewidth` for a half-width figure in the main text block. For two panels with a gutter, subtract the gutter before dividing the available width. Choose the canvas height for the content. The conversion is 72.27 TeX pt per inch and 72 PDF pt per inch.

Size TikZ diagrams at their final print width. In the thesis, use the containing `\linewidth` to lay out the picture. For standalone PDFs, set the bounding box to the corresponding target width and include any border in that width. In Matplotlib, pass the target width to `figsize=(width_inches, height_inches)`. Keep the saved PDF bounding box at that size.

## Semantic palette

These are the default thesis-wide roles. Both shared styles use these colors, and the Matplotlib cycle follows the order below. Use explicit styles for named roles when plotting a subset or changing series order.

| Role | Hex | TikZ color | Use |
|---|---|---|---|
| Vision | `#0072B2` | `ThesisVision` | Visible-light photographs, RGB video and derived visual features |
| Sensor / telemetry | `#009E73` | `ThesisSensor` | Aggregate telemetry, robot state, and other numerical machine channels |
| Context / metadata | `#56B4E9` | `ThesisContext` | Process settings, action type and other contextual inputs |
| Fusion / proposed component | `#CC79A7` | `ThesisFusion` | The combination stage or method under evaluation where that role is the comparison |
| Baseline / reference | `#595959` | `ThesisBaseline` | Control or comparator where that role is the comparison |
| Highlight | `#E69F00` | `ThesisHighlight` | A selected region, event or condition that needs a callout |
| Audio / acoustics | `#882255` | `ThesisAudio` | Microphone waveforms and their acoustic features or timing cues |
| Thermal imagery | `#D55E00` | `ThesisThermal` | Thermal-camera frames and their image-derived features |
| Depth / geometry | `#332288` | `ThesisDepth` | Depth maps, point clouds and features derived from geometric measurements |
| Vibration | `#117733` | `ThesisVibration` | Accelerometer traces and vibration-derived RMS, spectra or summary features |
| Force / torque | `#999933` | `ThesisWrench` | Separately identified force, torque or wrench measurements |

Use the most specific role the figure shows. For example, color a PHM vibration feature `ThesisVibration` and a combined machine-sensor branch `ThesisSensor`. Use `ThesisContext` for a speed setpoint and `ThesisSensor` for a measured speed or scalar temperature. Label the role of audio in the study, such as a timing cue or excluded input. For depth and derived geometry, label shared acquisition sources.

Use modality colors for input branches and modality comparisons. In method comparisons, use the method roles and label each method. Pair colors with labels and line styles, markers, hatching or borders so the figure remains intelligible in grayscale. Use `#222222` for label text and arrows on a white background. Use lighter palette colors for marks or tinted fills with dark text. The colors draw from the [Okabe–Ito palette](https://jfly.uni-koeln.de/color/) and [Paul Tol’s muted palette](https://sronpersonalpages.nl/~pault/).

## Type and drawing

- The thesis body uses 12 TeX pt Latin Modern Roman from `fontspec`. TikZ inherits the document's roman family and math fonts, including optical sizes appropriate to smaller labels. For Matplotlib here, use the smoke script's `--tex-fonts` option: the PGF backend exports through the existing XeLaTeX toolchain with native Latin Modern text and TeX math. It converts the shared PDF-point text sizes to TeX points. The direct PDF backend remains available with registered TrueType Latin Modern faces via `--font-dir`; it uses Computer Modern mathtext. The listed Computer Modern Roman and DejaVu Serif fallbacks do not constitute a thesis-font match.
- Set panel headings at 11 PDF pt bold, axis and node labels at 10 PDF pt, and ticks, legends and secondary annotations at 9 PDF pt minimum at final placement. Use `thesis panel label`, `thesis label` and `thesis annotation` in TikZ. Keep thesis captions in LaTeX.
- Use a 3 PDF pt corner radius, at least 6 PDF pt horizontal and 4 PDF pt vertical node padding, and 8 PDF pt padding for grouped content. Use 0.8 PDF pt for ordinary outlines, arrows and plot axes, 1.2 PDF pt for the fusion outline and 1.4 PDF pt for plot series. Use the `arrow` style with the PGF `stealth` tip.
- Export new diagrams and plots as vector PDF. Keep fonts embedded; the direct Matplotlib PDF backend uses `pdf.fonttype: 42`, while PGF/XeLaTeX embeds native TeX fonts independently of that setting. Place photos or source frames at suitable raster resolution inside the PDF when needed. Use the PNG preview for inspection. Keep `bbox_inches` at its standard setting so the export preserves the authored width.

## Smoke check

Run from the thesis root with the existing XeLaTeX tools on `PATH` and the project Python environment selected. The TikZ example verifies diagram widths in an A4 thesis-size page; its PDF page is not a cropped 159.20 mm figure. The Matplotlib example checks all eleven palette roles and writes individual full- and half-width PDFs with illustrative values, not scientific results. Use a new output directory for each verification pass; the Python smoke check refuses to overwrite its PDFs.

```sh
figure_run=build/figures/smoke_YYYYMMDD_01
mkdir -p "$figure_run"
latexmk -xelatex -halt-on-error -outdir="$figure_run/tikz" figures/smoke/style_smoke.tex
python figures/smoke/style_smoke.py --tex-fonts --outdir "$figure_run/matplotlib"
pdftoppm -r 150 -png -singlefile "$figure_run/tikz/style_smoke.pdf" "$figure_run/style_smoke-preview"
pdftoppm -r 150 -png -singlefile "$figure_run/matplotlib/style_smoke_full.pdf" "$figure_run/style_smoke_full-preview"
pdftoppm -r 150 -png -singlefile "$figure_run/matplotlib/style_smoke_half.pdf" "$figure_run/style_smoke_half-preview"
pdffonts "$figure_run/tikz/style_smoke.pdf"
pdffonts "$figure_run/matplotlib/style_smoke_full.pdf"
pdffonts "$figure_run/matplotlib/style_smoke_half.pdf"
```

The native-font route needs XeLaTeX, `kpsewhich`, PGF/TikZ, `fontspec`, Latin Modern and Matplotlib; the canvas check uses `pypdf` to read compressed PDF page objects. These are available in the existing local toolchain; its environment setup is recorded in the verification report. No new dependency or font installation was needed. The width tolerance is 0.01 PDF pt (less than 0.004 mm), accommodating XeLaTeX's PDF dimension rounding. As an alternative, pass `--font-dir` with verified `lmroman12-regular.ttf` and `lmroman12-bold.ttf` faces. This environment has only the native OTF faces, so the direct TrueType route was not used for the accepted font check. Do not silently treat fallback output as matching the thesis typography.

Open the PNGs and check the content at its inclusion width, as specified in [AGENTS.md](../AGENTS.md).
