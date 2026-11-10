"""Tiny local download-reuse fixtures; no network or real media fixtures."""
import hashlib
import sys
import pytest
sys.path.insert(0,'CROSS_DATASET_COMPARISON/src')
from external_eval.io import download


def test_existing_official_byte_identity_is_verified_before_reuse(tmp_path):
    data=b'synthetic fixture only';p=tmp_path/'official';p.write_bytes(data)
    item={'key':'fixture','size':len(data),'checksum':'md5:'+hashlib.md5(data).hexdigest()}
    receipt=download(item,p,tmp_path/'receipts')
    assert receipt['status']=='reused_verified' and receipt['sha256']==hashlib.sha256(data).hexdigest()


def test_mismatching_existing_bytes_are_preserved_and_never_replaced(tmp_path):
    p=tmp_path/'official';p.write_bytes(b'wrong')
    item={'key':'fixture','size':4,'checksum':'md5:'+hashlib.md5(b'good').hexdigest()}
    with pytest.raises(ValueError,match='preserved'):download(item,p,tmp_path/'receipts')
    assert p.read_bytes()==b'wrong'
