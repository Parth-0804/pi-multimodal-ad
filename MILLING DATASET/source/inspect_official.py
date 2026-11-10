#!/usr/bin/env python3
"""Snapshot public Kaggle metadata and every file-list page; no payload download."""
import argparse
import collections
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def fetch(url):
    with urllib.request.urlopen(url, timeout=45) as response:
        body = response.read(4_000_001)
        if len(body) > 4_000_000:
            raise ValueError("Metadata response exceeded 4 MB limit")
        return body, response.url, response.headers.get("Content-Type")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads((args.run / "config/resolved_config.json").read_text())
    handle = cfg["handle"].split("/versions/")[0]
    sources = []
    for name, url in (
        ("dataset_doi.html", "https://doi.org/" + cfg["dataset_doi"]),
        ("datacite.json", "https://api.datacite.org/dois/" + cfg["dataset_doi"]),
        ("kaggle_page.html", "https://www.kaggle.com/datasets/" + handle),
        ("publication.html", "https://www.nature.com/articles/" + cfg["paper_doi"].split("/")[1]),
        ("kaggle_metadata.json", "https://www.kaggle.com/api/v1/datasets/view/" + handle),
    ):
        body, resolved, content_type = fetch(url)
        # Do not persist cookie/session redirects or query parameters.
        resolved = urllib.parse.urlunsplit(urllib.parse.urlsplit(resolved)._replace(query="", fragment=""))
        (args.run / "evidence" / name).write_bytes(body)
        sources.append({"source": url, "resolved": resolved, "bytes": len(body), "content_type": content_type})
    metadata = json.loads((args.run / "evidence/kaggle_metadata.json").read_text())
    if metadata["id"] != cfg["dataset_id"] or metadata["ref"] != handle:
        raise ValueError("Official dataset identity mismatch")
    if cfg["version"] not in [v["versionNumber"] for v in metadata["versions"]]:
        raise ValueError("Requested version is not in official metadata")
    files, pages, seen_tokens = [], 0, set()
    token = None
    while True:
        params = {"datasetVersionNumber": cfg["version"], "pageSize": 200}
        if token:
            params["pageToken"] = token
        url = "https://www.kaggle.com/api/v1/datasets/list/" + handle + "?" + urllib.parse.urlencode(params)
        body, _, _ = fetch(url)
        page = json.loads(body)
        if page.get("errorMessage"):
            raise ValueError(page["errorMessage"])
        files.extend(page["datasetFiles"])
        pages += 1
        token = page.get("nextPageToken")
        if not token:
            break
        if token in seen_tokens:
            raise ValueError("Repeated pagination cursor")
        seen_tokens.add(token)
    names = [f["name"] for f in files]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate file names across inventory pages")
    inventory = {
        "dataset_id": cfg["dataset_id"], "handle": cfg["handle"], "version": cfg["version"],
        "retrieved_utc": datetime.now(timezone.utc).isoformat(), "pages": pages,
        "listing_endpoint": "https://www.kaggle.com/api/v1/datasets/list/" + handle,
        "listing_parameters": {"datasetVersionNumber": cfg["version"], "pageSize": 200},
        "files": [{"name": f["name"], "bytes": f["totalBytes"], "creation_date": f["creationDate"]} for f in files],
    }
    (args.run / "manifests/official_file_inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")
    (args.run / "evidence/source_access.json").write_text(json.dumps(sources, indent=2) + "\n")
    groups = collections.defaultdict(set)
    for name in names:
        parts = name.split("/")
        if len(parts) >= 3:
            groups[parts[0]].add(parts[1])
    print(json.dumps({"version": cfg["version"], "files": len(files), "pages": pages,
                      "bytes": sum(f["bytes"] for f in inventory["files"]),
                      "experiments": {k: len(v) for k, v in groups.items()},
                      "file_types": dict(collections.Counter(Path(n).suffix for n in names)),
                      "label_files": sum(n.endswith("/label.csv") for n in names)}, indent=2))


if __name__ == "__main__":
    main()
