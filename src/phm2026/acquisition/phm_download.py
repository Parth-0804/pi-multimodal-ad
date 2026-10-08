"""PHM public-share recovery with bounded discovery and verified streaming.

Only standard-library dependencies. Never reads a local credential/cookie file.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import http.client
import http.cookiejar
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

REPO = Path(__file__).resolve().parents[3]
OFFICIAL_PAGE = 'https://data.phmsociety.org/phm-north-america-2026-conference-data-challenge/'
DEFAULT_SHARE = 'https://gtc-data.synology.me:51111/sharing/uIrAvzqEh'
COMPONENTS = ('all', 'high_frequency', 'low_frequency', 'condition_indicators', 'oil_environment', 'photos', 'other')
CHUNK = 1024 * 1024


class RecoveryError(RuntimeError):
    """A failed recovery precondition; callers must not delete source data."""


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8 * CHUNK), b''):
            h.update(block)
    return h.hexdigest()


def destination(root, relative):
    """Reject traversal and symlinks including missing-root ancestors."""
    if not isinstance(relative, str) or '\\' in relative:
        raise RecoveryError('Invalid destination path')
    parts = relative.split('/')
    if not parts or any(p in ('', '.', '..') for p in parts) or PurePosixPath(relative).is_absolute():
        raise RecoveryError('Unsafe relative destination')
    root = Path(root).expanduser().absolute()
    for node in [root, *root.parents]:
        if node.is_symlink():
            raise RecoveryError('Symlink data-root ancestor refused')
    target = root.joinpath(*parts)
    for node in [target, *target.parents]:
        if node.is_symlink():
            raise RecoveryError('Symlink destination refused')
        if node == root:
            break
    if not target.resolve().is_relative_to(root.resolve()):
        raise RecoveryError('Destination escapes data root')
    return target


def load_manifest(path):
    manifest = json.loads(Path(path).read_text())
    if manifest.get('schema_version') != 1 or not isinstance(manifest.get('files'), list) or not manifest['files']:
        raise RecoveryError('Unsupported/empty recovery manifest')
    seen = set()
    for item in manifest['files']:
        rel = item['relative_path']
        destination(Path('/tmp/phm-manifest-validation'), rel)
        if rel in seen or rel + '.part' in seen or (rel.endswith('.part') and rel[:-5] in seen):
            raise RecoveryError('Duplicate/colliding manifest destination')
        seen.add(rel)
        if item['experiment'] not in ('A', 'B', 'F', 'shared/unknown') or item['component'] not in COMPONENTS[1:]:
            raise RecoveryError('Unsupported experiment/component in manifest')
        size = item.get('size_bytes')
        if size is not None and (type(size) is not int or size < 0):
            raise RecoveryError('Invalid expected size')
        if not re.fullmatch(r'[0-9a-f]{64}', item.get('sha256', '')):
            raise RecoveryError('Expected SHA256 required')
        if item.get('source_kind') not in ('official_share', 'repository_code'):
            raise RecoveryError('Unsupported source kind')
        if item['source_kind'] == 'repository_code' and item.get('repository_source') != 'scripts/phm2026/legacy_inspect_dataset.py':
            raise RecoveryError('Unapproved repository recovery asset')
        if item['source_kind'] == 'official_share' and not item.get('source_path', '').startswith('/train/'):
            raise RecoveryError('Official source path must be inventoried under /train/')
    return manifest


def select_files(manifest, experiments, components):
    if not set(experiments) <= {'A', 'B', 'F'} or not experiments:
        raise RecoveryError('Only experiments A, B and F are supported')
    if not components or not set(components) <= set(COMPONENTS):
        raise RecoveryError('Unsupported component')
    wanted = set(components)
    if 'low_frequency' in wanted:
        wanted.update(('condition_indicators', 'oil_environment'))
    return [dict(item) for item in manifest['files']
            if item['experiment'] in set(experiments) | {'shared/unknown'}
            and ('all' in wanted or item['component'] in wanted)]


class TrainingLinkParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.href = None; self.text = []; self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.href = dict(attrs).get('href'); self.text = []

    def handle_data(self, data):
        if self.href:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == 'a' and self.href:
            if re.search(r'\btraining\s+data\b', ' '.join(self.text), re.I):
                self.links.append(self.href)
            self.href = None


def training_link(html):
    parser = TrainingLinkParser(); parser.feed(html)
    links = list(dict.fromkeys(parser.links))
    if len(links) != 1:
        raise RecoveryError('Official training link is missing or ambiguous; use reviewed --share-url')
    validate_share(links[0])
    return links[0]


def validate_share(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.query or p.fragment:
        raise RecoveryError('Share must be a public HTTPS URL without credentials/query/fragment')
    if not re.fullmatch(r'/sharing/[A-Za-z0-9]+/?', p.path):
        raise RecoveryError('Expected a public /sharing/<id> URL')
    return p


class TLSRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(req.full_url).scheme == 'https' and urllib.parse.urlsplit(newurl).scheme != 'https':
            raise RecoveryError('HTTPS downgrade refused')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Transport:
    def __init__(self, timeout=30, retries=3):
        self.timeout = timeout; self.retries = retries
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ssl.create_default_context()),
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), TLSRedirect())
        self.opener.addheaders = [('User-Agent', 'PHM2026-Recovery/1.0'), ('Accept-Encoding', 'identity')]

    def open(self, url, headers=None):
        for attempt in range(self.retries + 1):
            try:
                return self.opener.open(urllib.request.Request(url, headers=headers or {}), timeout=self.timeout)
            except urllib.error.HTTPError as exc:
                code = exc.code; exc.close()
                if code not in (408, 429, 500, 502, 503, 504) or attempt == self.retries:
                    raise RecoveryError(f'HTTP {code}; request failed (no credentials logged)') from None
            except (urllib.error.URLError, TimeoutError, socket.timeout, OSError):
                if attempt == self.retries:
                    raise RecoveryError('Network/TLS request failed after bounded retries') from None
            time.sleep(min(2 ** attempt, 8))

    def small(self, url, headers=None, limit=4 * CHUNK):
        with self.open(url, headers) as r:
            data = r.read(limit + 1)
            if len(data) > limit:
                raise RecoveryError('Metadata response exceeds bounded size')
            return data


class SynologyResolver:
    """API names discovered in official FileBrowser.js; paths never guessed per file."""
    def __init__(self, transport, share_url):
        p = validate_share(share_url)
        self.transport = transport; self.share_url = share_url
        self.host = f'{p.scheme}://{p.netloc}'; self.share_id = p.path.rstrip('/').split('/')[-1]

    def initialize(self):
        self.transport.small(self.share_url)
        # The page advertises this bootstrap. Cookies stay in the in-memory jar.
        url = self.host + '/sharing/webapi/entry.cgi?' + urllib.parse.urlencode({
            'api': 'SYNO.Core.Sharing.Session', 'version': 1, 'method': 'get',
            'sharing_id': json.dumps(self.share_id), 'sharing_status': json.dumps('none')})
        self.transport.small(url)

    def api(self, params):
        params = dict(params, _sharing_id=json.dumps(self.share_id))
        url = self.host + '/fsdownload/webapi/entry.cgi?' + urllib.parse.urlencode(params)
        response = json.loads(self.transport.small(url, {'X-SYNO-SHARING': self.share_id}))
        if response.get('success') is not True:
            raise RecoveryError(f"Public sharing API refused request; code {response.get('error', {}).get('code', 'unknown')}")
        return response['data']

    def list_directory(self, path=None, offset=0):
        params = {'api': 'SYNO.FolderSharing.List', 'version': 2, 'method': 'list',
                  'offset': offset, 'limit': 1000, 'additional': json.dumps(['size'])}
        if path is not None:
            params['folder_path'] = json.dumps(path)
        return self.api(params)

    def discover(self):
        self.initialize(); pending = ['/train']; seen = set(); files = []
        while pending:
            path = pending.pop()
            if path in seen:
                continue
            seen.add(path)
            if len(seen) > 100:
                raise RecoveryError('Unexpected public share depth/size')
            offset = 0
            while True:
                data = self.list_directory(path, offset)
                entries = data.get('files')
                if not isinstance(entries, list):
                    raise RecoveryError('Unexpected public-share listing schema')
                for entry in entries:
                    remote = entry['path']
                    if not isinstance(remote, str) or not remote.startswith('/train') or '..' in PurePosixPath(remote).parts:
                        raise RecoveryError('Unexpected remote training path')
                    if entry.get('isdir'):
                        pending.append(remote)
                    else:
                        size = entry.get('additional', {}).get('size', entry.get('size'))
                        files.append({'source_path': remote, 'filename': entry['name'], 'size_bytes': size})
                total = data.get('total', len(entries))
                offset += len(entries)
                if offset >= total:
                    break
                if not entries or offset > 10000:
                    raise RecoveryError('Invalid listing pagination')
        return files

    def download_url(self, source_path):
        # Existing repository protocol, supplied with an API-discovered path.
        params = {'dlink': json.dumps(source_path.encode().hex()), '_sharing_id': json.dumps(self.share_id),
                  'api': 'SYNO.FolderSharing.Download', 'version': 2, 'method': 'download',
                  'mode': 'download', 'stdhtml': 'false'}
        return self.host + '/fsdownload/webapi/file_download.cgi/' + urllib.parse.quote(PurePosixPath(source_path).name, safe='') + '?' + urllib.parse.urlencode(params)


def resolve_files(items, discovered):
    bypath = {}
    for row in discovered:
        if row['source_path'] in bypath:
            raise RecoveryError('Duplicate remote identity')
        bypath[row['source_path']] = row
    result = []
    for item in items:
        if item['source_kind'] == 'official_share':
            remote = bypath.get(item['source_path'])
            if remote is None:
                raise RecoveryError('Required official file missing: ' + item['relative_path'])
            if item.get('size_bytes') is not None and remote['size_bytes'] != item['size_bytes']:
                raise RecoveryError('Official size differs from historical manifest: ' + item['relative_path'])
        else:
            source = REPO / item['repository_source']
            if not valid_file(source, item):
                raise RecoveryError('Preserved research-code asset changed or missing')
        result.append(item)
    return result


def valid_file(path, item):
    path = Path(path)
    return (path.is_file() and not path.is_symlink()
            and (item.get('size_bytes') is None or path.stat().st_size == item['size_bytes'])
            and sha256(path) == item['sha256'])


def nearest_existing(path):
    path = Path(path)
    while not path.exists():
        path = path.parent
    return path


def preflight(items, root, overwrite=False, allow_unknown=False):
    plan = []; required = {}
    for item in items:
        target = destination(root, item['relative_path']); part = destination(root, item['relative_path'] + '.part')
        if target.exists() and not target.is_file():
            raise RecoveryError('Destination is not a regular file')
        if part.exists() and (not part.is_file() or part.stat().st_nlink != 1):
            raise RecoveryError('Unsafe partial file')
        if valid_file(target, item):
            plan.append((item, target, 'SKIP')); continue
        if target.exists() and not overwrite:
            raise RecoveryError('Corrupt existing file refused; use --overwrite-corrupt after review')
        size = item.get('size_bytes')
        if size is None and not allow_unknown:
            raise RecoveryError('Unknown size; --allow-unknown-size required')
        offset = part.stat().st_size if part.exists() else 0
        if size is not None and offset > size:
            raise RecoveryError('Partial file exceeds expected size; explicit recovery review required')
        parent = nearest_existing(target.parent); device = parent.stat().st_dev
        required.setdefault(device, [parent, 0])
        required[device][1] += max(0, (size or 0) - offset)
        plan.append((item, target, 'DOWNLOAD'))
    for parent, remaining in required.values():
        if shutil.disk_usage(parent).free < math.ceil(remaining * 1.05):
            raise RecoveryError('Insufficient disk: remaining bytes plus 5% margin required')
    return plan


def parse_content_range(value):
    m = re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)', value or '')
    if not m:
        raise RecoveryError('Missing/invalid Content-Range')
    start, end, total = map(int, m.groups())
    if end < start or end >= total:
        raise RecoveryError('Inconsistent Content-Range')
    return start, end, total


def download_one(item, target, transport, url, overwrite=False, retries=3, progress=print, on_bytes=None):
    target = Path(target); part = target.with_name(target.name + '.part')
    if target.is_symlink() or part.is_symlink():
        raise RecoveryError('Symlink refused')
    if valid_file(target, item):
        return {'status': 'skipped', 'bytes_downloaded': 0, 'checksum': 'pass'}
    if target.exists() and not overwrite:
        raise RecoveryError('Corrupt existing file refused')
    if part.exists() and (not part.is_file() or part.stat().st_nlink != 1):
        raise RecoveryError('Unsafe partial file')
    target.parent.mkdir(parents=True, exist_ok=True)
    expected = item.get('size_bytes'); received = 0
    for attempt in range(retries + 1):
        offset = part.stat().st_size if part.exists() else 0
        if expected is not None and offset > expected:
            raise RecoveryError('Oversized partial file; preserved for review')
        if expected is not None and offset == expected and part.exists():
            break
        headers = {'Accept-Encoding': 'identity'}
        if offset:
            headers['Range'] = f'bytes={offset}-'
        try:
            with transport.open(url, headers) as response:
                status = response.status
                if offset and status != 206:
                    raise RecoveryError('Resume unsupported; restart required. Partial preserved; no automatic truncation.')
                if status == 206:
                    start, end, total = parse_content_range(response.headers.get('Content-Range'))
                    if start != offset or end != total - 1 or (expected is not None and total != expected):
                        raise RecoveryError('Incorrect resumed byte range/total')
                    expected = total
                elif status != 200:
                    raise RecoveryError('Unexpected download HTTP status')
                mime = response.headers.get('Content-Type', '').lower()
                if 'json' in mime or 'html' in mime:
                    raise RecoveryError('Server returned metadata/error instead of archive')
                if response.headers.get('Content-Encoding', 'identity') != 'identity':
                    raise RecoveryError('Unexpected content encoding')
                length = response.headers.get('Content-Length')
                if length and expected is not None and int(length) != expected - offset:
                    raise RecoveryError('Unexpected Content-Length')
                # O_NOFOLLOW prevents a replaced .part symlink from being followed.
                fd = os.open(part, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
                with os.fdopen(fd, 'ab') as output:
                    if os.fstat(output.fileno()).st_size != offset:
                        raise RecoveryError('Concurrent partial modification')
                    last = time.monotonic()
                    while True:
                        block = response.read1(CHUNK) if hasattr(response, 'read1') else response.read(CHUNK)
                        if not block:
                            break
                        if expected is not None and output.tell() + len(block) > expected:
                            raise RecoveryError('Response exceeds expected size')
                        if shutil.disk_usage(target.parent).free < len(block) + 64 * CHUNK:
                            raise RecoveryError('Low disk space during transfer; partial retained')
                        output.write(block); received += len(block)
                        if on_bytes is not None:
                            on_bytes(len(block))
                        if time.monotonic() - last > 5:
                            progress(f'{target.name}: {output.tell():,}/{expected or "unknown"} bytes')
                            last = time.monotonic()
                    output.flush(); os.fsync(output.fileno())
            if expected is not None and part.stat().st_size != expected:
                raise EOFError('Interrupted transfer')
            break
        except (EOFError, http.client.IncompleteRead, http.client.RemoteDisconnected, TimeoutError, socket.timeout, ConnectionError, urllib.error.URLError):
            if attempt == retries:
                raise RecoveryError('Interrupted transfer; .part retained for resume') from None
            time.sleep(min(2 ** attempt, 8))
    if expected is not None and part.stat().st_size != expected:
        raise RecoveryError('Final size mismatch; .part preserved')
    if sha256(part) != item['sha256']:
        raise RecoveryError('SHA256 mismatch; .part preserved, final untouched')
    if target.exists() and not overwrite:
        raise RecoveryError('Final file appeared concurrently; refusing overwrite')
    os.replace(part, target)
    return {'status': 'completed', 'bytes_downloaded': received, 'checksum': 'pass'}


def parser():
    p = argparse.ArgumentParser(description='Restore exact PHM A/B/F training inputs from the official public share.')
    p.add_argument('--experiments', nargs='+', choices=['A', 'B', 'F'], default=['A', 'B', 'F'])
    p.add_argument('--components', nargs='+', choices=COMPONENTS, default=['all'])
    p.add_argument('--data-root', type=Path, default=Path('gtc-data-experiment'))
    p.add_argument('--manifest', type=Path, default=REPO / 'configs/phm2026/download_manifest.json')
    p.add_argument('--share-url', help='Reviewed public HTTPS sharing URL override; otherwise resolve official page')
    p.add_argument('--list', action='store_true'); p.add_argument('--dry-run', action='store_true')
    p.add_argument('--overwrite-corrupt', action='store_true')
    p.add_argument('--allow-unknown-size', action='store_true')
    p.add_argument('--transfer-test', action='store_true', help='Transfer only a 1-MiB range; never restore full archives')
    return p


def main(argv=None):
    log = {'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'completed': [], 'skipped': [], 'failed': [],
           'bytes_downloaded': 0, 'resolved_files': [], 'checksum_status': {}, 'mode': 'parse'}
    status = 1
    try:
        args = parser().parse_args(argv)
        log.update(experiments=args.experiments, components=args.components,
                   mode='list' if args.list else 'dry-run' if args.dry_run else 'transfer-test' if args.transfer_test else 'download')
        manifest = load_manifest(args.manifest)
        log['manifest_sha256'] = sha256(args.manifest)
        log['python'] = sys.version
        import subprocess
        log['git_commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip() if (REPO / '.git').exists() else None
        items = select_files(manifest, args.experiments, args.components)
        if not items:
            raise RecoveryError('No files selected')
        transport = Transport()
        share = args.share_url or training_link(transport.small(OFFICIAL_PAGE).decode())
        validate_share(share); log['official_share_url'] = share
        resolver = SynologyResolver(transport, share); log['share_id'] = resolver.share_id
        discovered = resolver.discover()
        log['discovered_files'] = discovered
        items = resolve_files(items, discovered)
        log['coverage'] = {'required': len(items), 'resolved': len(items)}
        for item in items:
            target = destination(args.data_root, item['relative_path'])
            part = destination(args.data_root, item['relative_path'] + '.part')
            state = ('SIZE_MATCH_CHECKSUM_NOT_CHECKED' if target.is_file() and target.stat().st_size == item.get('size_bytes') else
                     'EXISTING_REQUIRES_VERIFICATION' if target.exists() else 'PARTIAL' if part.exists() else 'MISSING / AVAILABLE FOR DOWNLOAD')
            record = {k: item.get(k) for k in ['experiment', 'component', 'source_path', 'relative_path', 'size_bytes', 'source_kind']}
            record['current_state'] = state; log['resolved_files'].append(record)
            print(f"{item['experiment']}\t{item['component']}\t{item.get('source_path', item.get('repository_source'))}\t{target}\t{item.get('size_bytes')}\t{state}")
        if args.list or args.dry_run:
            status = 0; return status
        if args.transfer_test:
            item = next(i for i in items if i['source_kind'] == 'official_share' and i['component'] == 'high_frequency')
            count = CHUNK
            with transport.open(resolver.download_url(item['source_path']), {'Range': f'bytes=0-{count-1}', 'Referer': share}) as response:
                if response.status != 206:
                    raise RecoveryError('Range test unsupported; no large body read. Test a small required archive separately.')
                start, end, total = parse_content_range(response.headers.get('Content-Range'))
                if (start, end, total) != (0, count - 1, item['size_bytes']):
                    raise RecoveryError('Transfer-test range differs from historical manifest')
                body = response.read(count + 1)
            if len(body) != count or not body.startswith(b'PK'):
                raise RecoveryError('Transfer test did not return the requested ZIP bytes')
            log['bytes_downloaded'] = len(body)
            log['transfer_test'] = {'source_path': item['source_path'], 'bytes': count, 'sha256': hashlib.sha256(body).hexdigest(), 'range_total': total, 'http_status': 206}
            local = destination(args.data_root, item['relative_path'])
            if local.is_file():
                with local.open('rb') as f:
                    if f.read(count) != body:
                        raise RecoveryError('Transferred range differs from retained raw bytes')
                log['transfer_test']['matches_local_prefix'] = True
            # Bounded memory only: no connectivity-test artifact is written to disk.
            status = 0; return status
        if any(i.get('size_bytes') is None for i in items):
            print('WARNING: unknown size; capacity cannot be guaranteed', file=sys.stderr)
        plan = preflight(items, args.data_root, args.overwrite_corrupt, args.allow_unknown_size)
        for item, target, action in plan:
            if action == 'SKIP':
                log['skipped'].append(item['relative_path']); log['checksum_status'][item['relative_path']] = 'pass'; continue
            if item['source_kind'] == 'repository_code':
                # Local source code recovery is also verified before atomic installation.
                part = destination(args.data_root, item['relative_path'] + '.part')
                if part.exists():
                    raise RecoveryError('Local-code partial exists; review before retry')
                target.parent.mkdir(parents=True, exist_ok=True)
                with part.open('xb') as f:
                    f.write((REPO / item['repository_source']).read_bytes()); f.flush(); os.fsync(f.fileno())
                if not valid_file(part, item):
                    raise RecoveryError('Preserved code checksum failed')
                os.replace(part, target)
                result = {'bytes_downloaded': 0}
            else:
                def account_bytes(count):
                    log['bytes_downloaded'] += count
                log['checksum_status'][item['relative_path']] = 'pending'
                result = download_one(item, target, transport, resolver.download_url(item['source_path']), args.overwrite_corrupt, on_bytes=account_bytes)
            log['completed'].append(item['relative_path'])
            log['checksum_status'][item['relative_path']] = 'pass'
        status = 0; return status
    except SystemExit as exc:
        status = exc.code; raise
    except KeyboardInterrupt:
        log['failed'].append('Interrupted; completed files intact, .part files preserved'); status = 130; return status
    except (RecoveryError, OSError, ValueError, KeyError) as exc:
        # Never dump server headers, response bodies, cookies or URL-query state.
        msg = str(exc) if isinstance(exc, RecoveryError) else type(exc).__name__
        log['failed'].append(msg); print('ERROR: ' + msg, file=sys.stderr); return 1
    finally:
        log['exit_code'] = status
        if status != 0:
            for path, check in list(log['checksum_status'].items()):
                if check == 'pending':
                    log['checksum_status'][path] = 'not_verified_transfer_failed'
        folder = REPO / 'artifacts/phm2026/downloads'; folder.mkdir(parents=True, exist_ok=True)
        name = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid.uuid4().hex[:8] + '.json'
        with (folder / name).open('x') as f:
            json.dump(log, f, indent=2)
        print('Provenance: ' + str((folder / name).relative_to(REPO)), file=sys.stderr)
