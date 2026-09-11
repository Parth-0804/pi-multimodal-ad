# Gear-tooth image structure and quality profile

Mode: `sampled`

## Coverage

- Profiled images: 12
- Readable headers: 12
- Unreadable headers: 0
- Pixel-quality coverage: 4 / 12

## Structure

- H × W × C shapes: `{"[1440,2560,3]": 12}`
- Pillow modes: `{"RGB": 12}`
- Dtypes: `{"uint8": 12}`
- Bit depths: `{"8": 12}`
- Formats: `{"JPEG": 12}`

## Annotations and duplicate evidence

- Annotation evidence: `{"none_discovered_in_archive_listing": 12}`
- Exact duplicate groups within hash-covered rows: 0
- Perceptual near-duplicate candidate pairs: 0

## Timestamp evidence

- Status counts: `{"missing": 12}`
- Local-naive camera filename timestamps are retained as timezone-unknown; they are not coerced to UTC.

## Limitations

- Header success does not prove that the complete pixel stream is readable.
- Sampled quality metrics cover only a deterministic archive-stratified subset.
- Brightness, darkness, overexposure, and Laplacian variance are acquisition-quality proxies, not damage labels.
- CRC32/size, SHA-256, and dHash evidence have distinct coverage and must not be conflated.
- No discovered sidecar annotation means none was found in the D1.1 archive listing; it is not a claim about undocumented external labels.
