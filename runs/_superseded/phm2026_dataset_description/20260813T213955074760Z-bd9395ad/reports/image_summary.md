# Gear-tooth image structure and quality profile

Mode: `header`

## Coverage

- Profiled images: 4
- Readable headers: 4
- Unreadable headers: 0
- Pixel-quality coverage: 0 / 4

## Structure

- H × W × C shapes: `{"[1440,2560,3]": 4}`
- Pillow modes: `{"RGB": 4}`
- Dtypes: `{"uint8": 4}`
- Bit depths: `{"8": 4}`
- Formats: `{"JPEG": 4}`

## Annotations and duplicate evidence

- Annotation evidence: `{"no_discovered_annotation": 4}`
- Exact duplicate groups within hash-covered rows: 0
- Perceptual near-duplicate candidate pairs: 0

## Timestamp evidence

- Status counts: `{"missing": 4}`
- Local-naive camera filename timestamps are retained as timezone-unknown; they are not coerced to UTC.

## Limitations

- Header success does not prove that the complete pixel stream is readable.
- Sampled quality metrics cover only a deterministic archive-stratified subset.
- Brightness, darkness, overexposure, and Laplacian variance are acquisition-quality proxies, not damage labels.
- CRC32/size, SHA-256, and dHash evidence have distinct coverage and must not be conflated.
- No discovered sidecar annotation means none was found in the D1.1 archive listing; it is not a claim about undocumented external labels.
