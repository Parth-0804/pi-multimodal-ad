# Portable independent-review export

Created on 2026-10-28 UTC from the existing ViFailback verification evidence.

| Archive | Exact bytes | Approximate size | Intended recipient |
| --- | ---: | ---: | --- |
| VIFAILBACK_BLINDED_REVIEW.zip | 268,114,337 | 255.69 MiB | Independent blinded reviewer |
| VIFAILBACK_RESEARCH_REPORTS.zip | 196,278 | 191.68 KiB | Research reviewer after visual judgments are saved |
| VIFAILBACK_UNBLINDING.zip | 6,484 | 6.33 KiB | Researcher; withhold until independent judgments are saved |

Give ChatGPT only the blinded archive for the initial examination. Extract the
whole archive and open `index.html` for interactive offline viewing. It contains
20 cases, 960 native-resolution camera frames, 60 complete-view sheets, 60 enlarged
region sheets, 20 three-camera overviews, 20 measured sensor timelines, a blank
20-row review form, frame timestamps, instructions and a source/output hash
manifest. The three cameras share each case's 16 existing selected timepoints.
The enlarged region is the same fixed central crop for every case; full camera
views remain available at their original 640-by-480 resolution.

The documentation ZIP contains the five requested research audits and the final
decision, plus the existing README, researcher handoff, source provenance,
configuration, compact supporting checks and a file manifest. All original
reports are byte-identical. Narrative references to raw data and full original
source trees remain provenance references; those large inputs are not bundled.

The additional unblinding ZIP preserves both original key files and the previous
analyst screen unchanged. Neither the key nor that screen is included in the
visual-review archive. The existing source key directory remains untouched.

Blinding controls use a strict file allowlist. Native annotation files,
per-example outcomes/categories, source episode identities, pairing assignments,
previous observations and decode logs are excluded. The index's key link is
removed only in the exported copy. PNG text/time/EXIF chunks are removed
losslessly from the 20 plots; decoded pixels are identical. Other image bytes
are identical. ZIP timestamps/permissions are uniform and comments are empty.
Manifest source hashes identify neutral existing gallery assets, without mapping
them to original episode IDs. Task instructions, physical scenes, recording
durations, source frame indices and measured signals remain available to review.

Validation passed:

- All three ZIPs pass CRC, archive SHA-256 and all payload manifest hash checks.
- All 1,120 image files decode and pass metadata checks.
- All 264 explicit HTML resource/link references resolve within the export.
- Offline Chromium 156.0.8078.4 opens the independently extracted `file://`
  gallery, without a server or the original source directory. All 20 cases and
  320 slider positions display the correct three source frames, timestamps and
  crop-drawing coordinates: 960 full-frame/crop checks. All 140 static full/
  enlarged sheets and sensor plots load. No network attempts, failed requests,
  source-folder requests or JavaScript exceptions occur. Enlarged canvas
  screenshots also contain rendered image content.
- All 1,275 previously registered evidence files, including the original output
  manifest, match their pre-export hashes.
- Git whitespace checks and repository-environment `pip check` pass. Tracked
  modifications match the initial baseline. The archives are ignored by Git;
  no files were staged or committed.

No video frame extraction, sensor plot regeneration, training, or new scientific
inference was performed. Browser tooling and missing runtime libraries were
downloaded/extracted privately under `/tmp`; no project or system packages were
installed or changed. GPU rendering was disabled during verification.

`EXPORT_PROVENANCE.json`, `PACKAGE_VALIDATION.json`,
`REPOSITORY_VALIDATION.json`, and `SHA256SUMS.txt` record the commands, environment,
checks, source preservation and exact archive checksums. The two PNG browser
screenshots document the tested rendering. Packaging source is preserved beside
the archives; the first partial staging attempt is retained separately. The
successful build uses `staging_attempt_02/`. These working trees and verification
records are outside all three archives.
