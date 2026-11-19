# Gear-tooth image structure and quality profile

Mode: `header`

## Coverage

- Profiled images: 1311
- Readable headers: 1311
- Unreadable headers: 0
- Pixel-quality coverage: 0 / 1311
- Images by experiment: `{"EXP-A": 455, "EXP-B": 576, "EXP-F": 280}`
- Inspection groups: 26

## Structure

- H × W × C shapes: `{"[1440,2560,3]": 1311}`
- Pillow modes: `{"RGB": 1311}`
- Dtypes: `{"uint8": 1311}`
- Bit depths: `{"8": 1311}`
- Formats: `{"JPEG": 1311}`
- Aspect ratios: `{"1.77777777778": 1311}`
- Unusual singleton shapes or modes: 0

## Annotations and duplicate evidence

- Annotation evidence: `{"none_discovered_in_archive_listing": 1311}`
- Discovered annotation types: `{}`
- Exact-hash coverage: 0 / 1311
- Exact duplicate groups within hash-covered rows: 0
- Perceptual-hash coverage: 0 / 1311
- Perceptual near-duplicate candidate pairs: 0

## Timestamp evidence

- Status counts: `{"missing": 671, "timezone_unknown": 640}`
- Local-naive camera filename timestamps are retained as timezone-unknown; they are not coerced to UTC.

## Limitations

- Header success does not prove that the complete pixel stream is readable.
- Sampled quality metrics cover only a deterministic archive-stratified subset.
- Brightness, darkness, overexposure, and Laplacian variance are acquisition-quality proxies, not damage labels.
- CRC32/size, SHA-256, and dHash evidence have distinct coverage and must not be conflated.
- No discovered sidecar annotation means none was found in the D1.1 archive listing; it is not a claim about undocumented external labels.
