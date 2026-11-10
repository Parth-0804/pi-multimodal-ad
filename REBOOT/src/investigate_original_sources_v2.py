"""Bounded, anonymous, metadata-only investigation; never changes original data.

Run with --run pointing at a NEW versioned investigation directory.
All fetched bytes and sanitized provenance are retained; signed redirect URLs
and request authentication are deliberately neither requested nor recorded.
"""
import argparse
import concurrent.futures
import hashlib
import io
import json
import pathlib
import re
import shutil
import tarfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
LOCK = threading.Lock()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


class Collector:
    def __init__(self, run):
        self.run = run
        self.receipts = []

    def fetch(self, url, name, cap=3_000_000):
        path = self.run / 'evidence' / name
        if path.exists():
            raise FileExistsError(path)
        rec = {'url': url, 'requested_utc': stamp(), 'cap_bytes': cap}
        try:
            if shutil.disk_usage(ROOT).free < 20_000_000_000 + cap:
                raise RuntimeError('Free-space reserve guard')
            req = urllib.request.Request(url, headers={'User-Agent': 'REBOOT-original-source-blocker-audit/2.0'})
            with urllib.request.urlopen(req, timeout=25) as response:
                data = response.read(cap + 1)
                if len(data) > cap:
                    raise RuntimeError('Bounded response cap exceeded')
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('xb') as f:
                    f.write(data)
                rec.update(status=response.status, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                           path=str(path.relative_to(ROOT)), link=response.headers.get('Link'),
                           etag=response.headers.get('ETag'))
            try:
                value = json.loads(data)
            except (ValueError, UnicodeDecodeError):
                value = data
        except urllib.error.HTTPError as exc:
            rec.update(status=exc.code, error_type=type(exc).__name__)
            value = None
        except Exception as exc:
            rec.update(error_type=type(exc).__name__, error=str(exc)[:160])
            value = None
        with LOCK:
            self.receipts.append(rec)
            with (self.run / 'manifests' / 'source_fetch_receipts.jsonl').open('a') as f:
                f.write(json.dumps(rec) + '\n')
        return value, rec


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True, type=pathlib.Path)
    args = parser.parse_args()
    c = Collector(args.run.resolve())
    inventory = json.loads((ROOT / 'REBOOT/00_dataset_overview/PINNED_DATASET_INVENTORY.json').read_text())
    live, _ = c.fetch('https://huggingface.co/api/datasets?author=REBOOT26&limit=100&full=true', 'hf_author_live.json')
    live_by_id = {x['id']: x for x in live or []}

    def one_repo(entry):
        repo = entry['repo_id']
        slug = repo.split('/')[-1]
        commits, receipt = c.fetch(f'https://huggingface.co/api/datasets/{repo}/commits/main?limit=100', f'history/{slug}/commits.json')
        refs, _ = c.fetch(f'https://huggingface.co/api/datasets/{repo}/refs', f'history/{slug}/refs.json')
        revisions = {entry['revision']}
        if isinstance(commits, list):
            revisions.update(x['id'] for x in commits)
        if isinstance(refs, dict):
            for kind in ('branches', 'tags'):
                revisions.update(x['targetCommit'] for x in refs.get(kind, []))
        summary = {'repo_id': repo, 'old_pin': entry['revision'], 'live_sha': live_by_id.get(repo, {}).get('sha'),
                   'history_count': len(commits) if isinstance(commits, list) else None,
                   'history_link': receipt.get('link'), 'history_response_ok': isinstance(commits, list),
                   'refs': refs, 'revisions': [], 'annotation_files': [], 'metadata_versions': []}
        old_tree = json.loads((ROOT / entry['file_tree']).read_text())
        seen = set()
        for rev in sorted(revisions):
            if rev == entry['revision']:
                tree = old_tree
                tree_origin = entry['file_tree']
            else:
                tree, tr = c.fetch(f'https://huggingface.co/api/datasets/{repo}/tree/{rev}?recursive=true&expand=false&limit=1000',
                                   f'history/{slug}/trees/{rev}.json')
                tree_origin = tr.get('path')
                if tr.get('link'):
                    summary.setdefault('tree_pagination_unresolved', []).append(rev)
            if not isinstance(tree, list):
                summary.setdefault('unavailable_revisions', []).append(rev)
                continue
            summary['revisions'].append({'revision': rev, 'tree': tree_origin, 'entries': len(tree)})
            for file in tree:
                if file.get('type') != 'file':
                    continue
                path = file['path']
                identity = file.get('lfs', {}).get('oid', file.get('oid'))
                is_annotation = bool(re.search(r'phase|annotat|label|session|operator|pair|failure|recovery.*\.json', path, re.I))
                is_meta = path.startswith('meta/') or path.lower().endswith(('.jsonl', '.csv', '.tsv', '.json', '.yaml', '.yml', '.zip'))
                item = {'revision': rev, 'path': path, 'bytes': file['size'], 'identity': identity}
                if is_annotation:
                    summary['annotation_files'].append(item)
                if not is_meta:
                    continue
                key = (path, identity)
                if key in seen:
                    continue
                seen.add(key)
                summary['metadata_versions'].append(item)
                # Existing current metadata is already preserved with byte hashes.
                if rev == entry['revision'] and (ROOT / entry['local_root'] / path).exists():
                    item['reused_path'] = str(pathlib.Path(entry['local_root']) / path)
                elif file['size'] <= 2_000_000 and (is_annotation or path.startswith('meta/episodes/') or path.endswith('info.json')):
                    blob, br = c.fetch(f'https://huggingface.co/datasets/{repo}/resolve/{rev}/{path}',
                                       f'history/{slug}/originals/{rev}/{path}', cap=2_000_000)
                    item['receipt'] = br
        save_json(c.run / 'reports' / 'history' / f'{slug}.json', summary)
        print(slug, summary['history_count'], 'commits;', len(summary['revisions']), 'trees;', len(summary['annotation_files']), 'annotation paths', flush=True)
        return summary

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        summaries = list(pool.map(one_repo, inventory))
    save_json(c.run / 'reports' / 'HF_HISTORY_SUMMARY.json', summaries)
    endpoints = [
        ('github_branches.json', 'https://api.github.com/repos/anon-robo-account/REBOOT/branches?per_page=100'),
        ('github_tags.json', 'https://api.github.com/repos/anon-robo-account/REBOOT/tags?per_page=100'),
        ('github_releases.json', 'https://api.github.com/repos/anon-robo-account/REBOOT/releases?per_page=100'),
        ('project_github_repo.json', 'https://api.github.com/repos/nanayawoa/REBOOT'),
        ('project_github_branches.json', 'https://api.github.com/repos/nanayawoa/REBOOT/branches?per_page=100'),
        ('official_project.html', 'https://nanayawoa.github.io/REBOOT/'),
        ('paper.html', 'https://arxiv.org/html/2609.22591v1'),
        ('paper_abstract.html', 'https://arxiv.org/abs/2609.22591'),
    ]
    for name, url in endpoints:
        c.fetch(url, name)
    branches_path = c.run / 'evidence/github_branches.json'
    if branches_path.exists():
        for branch in json.loads(branches_path.read_text()):
            sha = branch['commit']['sha']
            tree, _ = c.fetch(f'https://api.github.com/repos/anon-robo-account/REBOOT/git/trees/{sha}?recursive=1', f'github_trees/{sha}.json', cap=4_000_000)
            c.fetch(f'https://api.github.com/repos/anon-robo-account/REBOOT/commits?sha={sha}&per_page=100', f'github_commits/{sha}.json', cap=4_000_000)
    # Official arXiv source archive may contain additional author supplementary files.
    bundle, receipt = c.fetch('https://arxiv.org/src/2609.22591v1', 'paper_source.tar', cap=30_000_000)
    if isinstance(bundle, bytes):
        try:
            members = []
            with tarfile.open(fileobj=io.BytesIO(bundle), mode='r:*') as tf:
                for member in tf:
                    rec = {'path': member.name, 'size': member.size, 'type': str(member.type)}
                    if member.isfile() and member.size <= 2_000_000:
                        raw = tf.extractfile(member).read()
                        rec['sha256'] = hashlib.sha256(raw).hexdigest()
                        if member.name.endswith(('.tex', '.bib', '.txt', '.json', '.jsonl', '.csv', '.md')):
                            # Never extract archive paths onto disk; retain source archive + bounded text inventory.
                            rec['text'] = raw.decode('utf-8', 'replace')
                    members.append(rec)
            save_json(c.run / 'reports/PAPER_SOURCE_MEMBER_INVENTORY.json', members)
        except tarfile.TarError as exc:
            save_json(c.run / 'reports/PAPER_SOURCE_ARCHIVE_ERROR.json', {'error': str(exc)})


if __name__ == '__main__':
    main()
