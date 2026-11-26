# Thesis project instructions

This supplement applies to the working LaTeX project rooted at `main.tex`.
Repository-level instructions remain applicable.

## Figure verification

- Follow the dimensions, typography and color roles in [figures/VISUAL_STYLE.md](figures/VISUAL_STYLE.md). Import the shared TikZ or Matplotlib style in every new diagram or plot.
- Each time you create or edit a TikZ figure source or a Matplotlib figure script, build its vector PDF and render a PNG preview before finishing the change. When editing either shared style, run the smoke examples and rebuild figures that use the changed style.
- Run builds from the thesis root. Use XeLaTeX for TikZ, for example `latexmk -xelatex -halt-on-error -outdir=build/figures figures/example.tex`. For a TikZ fragment, compile the document that inputs it. Run the Matplotlib script with the project's Python environment and have it save its PDF at the intended print dimensions.
- For a one-page output, run `pdftoppm -r 150 -png -singlefile build/figures/example.pdf build/figures/example-preview`. For a multipage document, specify the figure page with `-f N -l N`, or omit `-singlefile` and open every affected page. Put previews and build logs in `build/figures/`.
- Open the PNG and check the labels, legends, plot limits, arrows, margins and panel boundaries for clipping, overlap and readability at the final inclusion width. Confirm the PDF page dimensions for a standalone figure. Fix issues and rebuild both outputs. Report any build or visual check you could not complete.
