"""Tiny synthetic HTTP payloads; no real dataset fixtures."""
import hashlib
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import pytest
from vifailback.acquisition import acquire_one


@pytest.fixture
def source():
    payload = b'synthetic-scientific-fixture-only'
    class Handler(BaseHTTPRequestHandler):
        calls = 0
        def do_GET(self):
            Handler.calls += 1
            self.send_response(200)
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        def log_message(self, *args): pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    yield payload, Handler, f'http://127.0.0.1:{server.server_port}/fixture'
    server.shutdown()
    worker.join()


def test_hash_reuse_and_existing_preservation(tmp_path, source):
    payload, handler, url = source
    item = {'size': len(payload), 'lfs': {'sha256': hashlib.sha256(payload).hexdigest()}}
    path = tmp_path / 'fixture.bin'
    assert acquire_one(item, path, url=url)['status'] == 'ACQUIRED_VERIFIED'
    assert acquire_one(item, path, url=url)['status'] == 'VERIFIED_EXISTING'
    assert handler.calls == 1
    path.write_bytes(b'existing-invalid-fixture')
    with pytest.raises(RuntimeError, match='EXISTING_SOURCE_IDENTITY'):
        acquire_one(item, path, url=url)
    assert path.read_bytes() == b'existing-invalid-fixture'


def test_mismatched_source_never_creates_destination(tmp_path, source):
    payload, _, url = source
    item = {'size': len(payload), 'lfs': {'sha256': '0' * 64}}
    path = tmp_path / 'bad.bin'
    with pytest.raises(RuntimeError, match='IDENTITY_MISMATCH'):
        acquire_one(item, path, url=url)
    assert not path.exists()
