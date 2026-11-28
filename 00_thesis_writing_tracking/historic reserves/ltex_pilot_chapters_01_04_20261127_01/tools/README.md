# Isolated LTeX+ pilot tools

The official Linux x64 LTeX+ LS 19.0.0 release is unpacked here, with its bundled Java 21.0.10 runtime and LanguageTool 6.8. Nothing was installed globally or added to VS Code. The downloaded archive is retained; its SHA-256 matches the digest in the official GitHub release metadata. See `../reports/ltex_installation.json`.

Checks run locally on chapter copies. `ltex-client-configuration.json` selects British English, adds a small scientific vocabulary, and leaves the external HTTP checker URL empty. The same frozen settings and vocabulary are used before and after editing. No thesis text is sent to a checking service.

From the pilot directory:

```sh
python3 scripts/run_ltex.py original
python3 scripts/run_ltex.py reworked
```

These commands do not compile LaTeX and do not edit the checked files. Completed reports are protected against overwrite. An exit code of 3 in the saved tool record means grammar or spelling suggestions were found; it does not mean the checker failed. CLI output is preserved verbatim in `reports/ltex_original.raw.txt` and `reports/ltex_reworked.raw.txt`. Matching JSON files structure those raw records without filtering. A suggestion list includes only replacements printed by the CLI, not an exhaustive list of alternatives that an editor might offer.

Official documentation: https://ltex-plus.github.io/ltex-plus/ltex-ls-plus/cli-usage.html
Release: https://github.com/ltex-plus/ltex-ls-plus/releases/tag/19.0.0
