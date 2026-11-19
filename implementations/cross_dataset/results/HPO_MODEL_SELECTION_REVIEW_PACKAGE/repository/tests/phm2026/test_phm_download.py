"""Synthetic offline downloader tests; live NAS checks are separate CLI runs."""
from contextlib import contextmanager
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import socket
import threading
from types import SimpleNamespace
import pytest
from phm2026.acquisition import phm_download as d

BODY = b'PK' + bytes(range(256)) * 4096


def item(body=BODY, path='high_frequency/EXP A/a.zip', exp='A', component='high_frequency'):
    return {'relative_path': path, 'experiment': exp, 'component': component,
            'size_bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest(),
            'source_kind': 'official_share', 'source_path': '/train/high-frequency/EXP-A/a.zip'}


@contextmanager
def server(body=BODY, mode='normal'):
    requests = []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass
        def do_GET(self):
            range_header = self.headers.get('Range'); requests.append(range_header)
            start = int(range_header.split('=')[1].split('-')[0]) if range_header else 0
            code = 206 if range_header and mode != 'no_range' else 200
            if mode == 'no_range': start = 0
            self.send_response(code)
            self.send_header('Content-Type', 'application/octet-stream')
            if code == 206:
                reported = start + 1 if mode == 'bad_range' else start
                self.send_header('Content-Range', f'bytes {reported}-{len(body)-1}/{len(body)}')
            self.send_header('Content-Length', str(len(body)-start)); self.end_headers()
            data = body[start:]
            if mode == 'interrupt': data = data[:8192]
            try:
                self.wfile.write(data); self.wfile.flush()
                if mode == 'interrupt': self.connection.shutdown(socket.SHUT_RDWR)
            except (BrokenPipeError, ConnectionResetError): pass
    http = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=http.serve_forever, daemon=True);thread.start()
    try: yield f'http://127.0.0.1:{http.server_port}/synthetic.zip', requests
    finally: http.shutdown(); http.server_close(); thread.join()


def test_experiment_and_component_parsing():
    a = d.parser().parse_args(['--experiments', 'A', 'B', 'F', '--components', 'photos'])
    assert a.experiments == ['A', 'B', 'F'] and a.components == ['photos']
    with pytest.raises(SystemExit): d.parser().parse_args(['--experiments', 'G'])
    with pytest.raises(SystemExit): d.parser().parse_args(['--components', 'secrets'])


def test_component_filtering():
    files=[item(),item(path='ci.zip',component='condition_indicators'),item(path='lf.zip',component='oil_environment'),item(path='b.zip',exp='B',component='photos')]
    assert len(d.select_files({'files':files}, ['A'], ['low_frequency'])) == 2
    assert len(d.select_files({'files':files}, ['A','B','F'], ['all'])) == 4
    with pytest.raises(d.RecoveryError): d.select_files({'files':files}, ['G'], ['all'])


def test_manifest_validation(tmp_path):
    p=tmp_path/'manifest.json';p.write_text(json.dumps({'schema_version':1,'files':[item()]}))
    assert len(d.load_manifest(p)['files'])==1
    for bad in [dict(item(),sha256='bad'),dict(item(),relative_path='../outside'),dict(item(),size_bytes=-1)]:
        p.write_text(json.dumps({'schema_version':1,'files':[bad]}))
        with pytest.raises(d.RecoveryError):d.load_manifest(p)
    p.write_text(json.dumps({'schema_version':1,'files':[item(),item()]}))
    with pytest.raises(d.RecoveryError):d.load_manifest(p)


def test_safe_destination_and_symlinks(tmp_path):
    root=tmp_path/'data'
    for bad in ['../outside','/absolute','x/../z','x//y','x\\y']:
        with pytest.raises(d.RecoveryError):d.destination(root,bad)
    assert d.destination(root,'a/b.zip')==root/'a/b.zip'
    root.mkdir(); (root/'link').symlink_to(tmp_path,target_is_directory=True)
    with pytest.raises(d.RecoveryError):d.destination(root,'link/b.zip')
    with pytest.raises(d.RecoveryError):d.destination(root/'link','b.zip')


def test_existing_valid_skip_without_http(tmp_path):
    p=tmp_path/'a.zip';p.write_bytes(BODY)
    class Never:
        def open(self,*args):raise AssertionError('network must not be called')
    assert d.download_one(item(),p,Never(),'unused')['status']=='skipped'


def test_corrupt_existing_refused(tmp_path):
    p=tmp_path/'a.zip';p.write_bytes(b'bad')
    with pytest.raises(d.RecoveryError,match='Corrupt existing'):
        d.download_one(item(),p,None,'unused')
    assert p.read_bytes()==b'bad'


def test_stream_checksum_and_atomic_rename(tmp_path,monkeypatch):
    p=tmp_path/'a.zip';real=d.os.replace;calls=[]
    def verified_replace(source,target):
        assert d.sha256(source)==item()['sha256']
        assert not p.exists();calls.append((source,target));real(source,target)
    monkeypatch.setattr(d.os,'replace',verified_replace)
    with server() as (url,requests):
        result=d.download_one(item(),p,d.Transport(retries=0),url)
    assert p.read_bytes()==BODY and not Path(str(p)+'.part').exists()
    assert result['checksum']=='pass' and result['bytes_downloaded']==len(BODY) and len(calls)==1


def test_resume_existing_part(tmp_path):
    p=tmp_path/'a.zip';part=tmp_path/'a.zip.part';part.write_bytes(BODY[:8192])
    with server() as (url,requests):result=d.download_one(item(),p,d.Transport(retries=0),url)
    assert requests==['bytes=8192-'] and result['bytes_downloaded']==len(BODY)-8192
    assert p.read_bytes()==BODY and not part.exists()


def test_no_range_preserves_partial(tmp_path):
    p=tmp_path/'a.zip';part=tmp_path/'a.zip.part';part.write_bytes(BODY[:8192])
    with server(mode='no_range') as (url,_):
        with pytest.raises(d.RecoveryError,match='restart required'):d.download_one(item(),p,d.Transport(retries=0),url)
    assert part.read_bytes()==BODY[:8192] and not p.exists()


def test_bad_range_refused(tmp_path):
    p=tmp_path/'a.zip';part=tmp_path/'a.zip.part';part.write_bytes(BODY[:8192])
    with server(mode='bad_range') as (url,_):
        with pytest.raises(d.RecoveryError,match='Incorrect resumed'):d.download_one(item(),p,d.Transport(retries=0),url)
    assert part.read_bytes()==BODY[:8192]


def test_checksum_failure_retains_part_and_old_final(tmp_path):
    p=tmp_path/'a.zip';p.write_bytes(b'old')
    bad=dict(item(),sha256='0'*64)
    with server() as (url,_):
        with pytest.raises(d.RecoveryError,match='SHA256 mismatch'):
            d.download_one(bad,p,d.Transport(retries=0),url,overwrite=True)
    assert p.read_bytes()==b'old' and (tmp_path/'a.zip.part').read_bytes()==BODY


def test_overwrite_corrupt_only_after_verification(tmp_path):
    p=tmp_path/'a.zip';p.write_bytes(b'old')
    with server() as (url,_):d.download_one(item(),p,d.Transport(retries=0),url,overwrite=True)
    assert p.read_bytes()==BODY


def test_interrupted_transfer_retained_then_resumed(tmp_path):
    p=tmp_path/'a.zip'
    with server(mode='interrupt') as (url,_):
        with pytest.raises(d.RecoveryError,match='Interrupted transfer'):
            d.download_one(item(),p,d.Transport(retries=0),url,retries=0)
    part=tmp_path/'a.zip.part';assert part.read_bytes()==BODY[:8192] and not p.exists()
    with server() as (url,requests):d.download_one(item(),p,d.Transport(retries=0),url)
    assert requests==['bytes=8192-'] and p.read_bytes()==BODY


def test_complete_partial_verified_without_network(tmp_path):
    p=tmp_path/'a.zip';(tmp_path/'a.zip.part').write_bytes(BODY)
    assert d.download_one(item(),p,None,'unused')['bytes_downloaded']==0
    assert p.read_bytes()==BODY


def test_space_preflight_counts_remaining_and_margin(tmp_path,monkeypatch):
    i=item(path='a.zip');(tmp_path/'a.zip.part').write_bytes(BODY[:8192])
    remaining=len(BODY)-8192
    monkeypatch.setattr(d.shutil,'disk_usage',lambda _:SimpleNamespace(free=remaining))
    with pytest.raises(d.RecoveryError,match='Insufficient disk'):d.preflight([i],tmp_path)
    monkeypatch.setattr(d.shutil,'disk_usage',lambda _:SimpleNamespace(free=d.math.ceil(remaining*1.05)))
    assert d.preflight([i],tmp_path)[0][2]=='DOWNLOAD'


def test_unknown_size_requires_explicit_flag(tmp_path):
    i=dict(item(path='a.zip'),size_bytes=None)
    with pytest.raises(d.RecoveryError,match='Unknown size'):d.preflight([i],tmp_path)
    assert d.preflight([i],tmp_path,allow_unknown=True)


def test_resolver_official_page_fixture():
    fixture=Path(__file__).parents[1]/'fixtures/phm_recovery/official_page.html'
    assert d.training_link(fixture.read_text())==d.DEFAULT_SHARE
    with pytest.raises(d.RecoveryError):d.training_link('<a href="https://example.invalid">Nothing</a>')
    for url in ['http://example.org/sharing/a','https://name:password@example.org/sharing/a','https://example.org/sharing/a?token=x']:
        with pytest.raises(d.RecoveryError):d.validate_share(url)


def test_exact_source_coverage_and_size():
    i=item();rows=[{'source_path':i['source_path'],'size_bytes':i['size_bytes']}]
    assert d.resolve_files([i],rows)==[i]
    with pytest.raises(d.RecoveryError,match='missing'):d.resolve_files([i],[])
    with pytest.raises(d.RecoveryError,match='size differs'):d.resolve_files([i],[dict(rows[0],size_bytes=1)])


def test_dry_run_does_not_create_raw_root(tmp_path,monkeypatch):
    monkeypatch.setattr(d,'REPO',tmp_path)
    i=item();manifest=tmp_path/'manifest.json';manifest.write_text(json.dumps({'schema_version':1,'files':[i]}))
    monkeypatch.setattr(d.Transport,'small',lambda *a,**k: f'<a href="{d.DEFAULT_SHARE}">Training Data</a>'.encode())
    monkeypatch.setattr(d.SynologyResolver,'discover',lambda self:[{'source_path':i['source_path'],'size_bytes':i['size_bytes']}])
    raw=tmp_path/'missing-raw'
    assert d.main(['--dry-run','--manifest',str(manifest),'--data-root',str(raw)])==0
    assert not raw.exists()
    logs=list((tmp_path/'artifacts/phm2026/downloads').glob('*.json'))
    assert len(logs)==1 and json.loads(logs[0].read_text())['bytes_downloaded']==0


def test_discovery_uses_server_paths_and_folder_parameter():
    class SyntheticTransport:
        def __init__(self):self.requests=[]
        def small(self,url,headers=None):
            self.requests.append(url)
            query=d.urllib.parse.parse_qs(d.urllib.parse.urlsplit(url).query)
            if query.get('api')==['SYNO.FolderSharing.List']:
                assert 'folder_path' in query and 'file_path' not in query
                folder=json.loads(query['folder_path'][0])
                entries=[{'name':'high-frequency','path':'/train/high-frequency','isdir':True}] if folder=='/train' else [{'name':'a.zip','path':'/train/high-frequency/a.zip','isdir':False,'additional':{'size':5}}]
                return json.dumps({'success':True,'data':{'files':entries,'total':1}}).encode()
            return b''
    t=SyntheticTransport();r=d.SynologyResolver(t,d.DEFAULT_SHARE)
    assert r.discover()==[{'source_path':'/train/high-frequency/a.zip','filename':'a.zip','size_bytes':5}]


def test_transfer_byte_accounting_on_interruption(tmp_path):
    counts=[]
    with server(mode='interrupt') as (url,_):
        with pytest.raises(d.RecoveryError):d.download_one(item(),tmp_path/'a.zip',d.Transport(retries=0),url,retries=0,on_bytes=counts.append)
    assert sum(counts)==8192


def test_empty_file_verified(tmp_path):
    i=item(body=b'');p=tmp_path/'empty.zip'
    with server(body=b'') as (url,_):d.download_one(i,p,d.Transport(retries=0),url)
    assert p.is_file() and p.stat().st_size==0
