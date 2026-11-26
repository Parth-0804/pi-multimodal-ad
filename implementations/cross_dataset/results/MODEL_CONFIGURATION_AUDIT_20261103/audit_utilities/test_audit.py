"""CPU-only tests of audit computations, isolation and literal metadata parsing."""
from pathlib import Path
import json
import math
import numpy as np
import pytest
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss,log_loss
from audit_common import OUT,CONFIG_FIELDS,write,read
from metrics_check import metrics
from discover import sensitive
from static_optimizer_metadata import optimizer_literals


@pytest.mark.parametrize('seed',range(12))
def test_tied_metrics_match_independent_library(seed):
    rng=np.random.default_rng(seed);y=rng.integers(0,2,127);p=rng.integers(1,10,127)/10
    result=metrics(y,p)
    assert result['AP']==pytest.approx(average_precision_score(y,p),abs=1e-14)
    assert result['AUROC']==pytest.approx(roc_auc_score(y,p),abs=1e-14)
    assert result['Brier']==pytest.approx(brier_score_loss(y,p),abs=1e-14)
    assert result['log_loss']==pytest.approx(log_loss(y,p),abs=1e-14)
    assert result['TN']+result['FP']+result['FN']+result['TP']==len(y)


def test_constant_probability_ap_is_prevalence():
    y=np.array([1,0,0,1,0]);r=metrics(y,np.repeat(.23,len(y)))
    assert r['AP']==pytest.approx(.4);assert r['AUROC']==.5


def test_scope_write_guard_fails_before_mutation():
    forbidden=OUT.parent/'THIS_FILE_MUST_NOT_BE_CREATED_BY_AUDIT.json'
    assert not forbidden.exists()
    with pytest.raises(AssertionError,match='AUDIT_WRITE_OUTSIDE_NEW_FOLDER'):write(forbidden,{'no_write':True})
    assert not forbidden.exists()


@pytest.mark.parametrize('name',['.env','.env.local','synology_cookies.txt','credentials','id_rsa','id_ed25519','secret.pem','secret.key','access_token.json','session_cookie.txt'])
def test_credential_names_excluded(name):assert sensitive(name)


@pytest.mark.parametrize('p',[[-.01,.5],[.4,1.01],[float('nan'),.7]])
def test_invalid_saved_probabilities_rejected(p):
    with pytest.raises(AssertionError):metrics([0,1],p)


def test_static_optimizer_parser_requires_no_pickle_execution(tmp_path):
    import torch
    p=tmp_path/'synthetic_literal_checkpoint.pt'
    torch.save({'optimizer':{'state':{},'param_groups':[{'lr':.001,'betas':(.9,.999),'eps':1e-8,'weight_decay':.001,'params':[0]}]},'model':{'weight':torch.tensor([1.])}},p)
    got=optimizer_literals(p)
    assert got['betas']==[.9,.999];assert got['eps']==1e-8;assert got['lr']==.001


def test_config_count_and_required_unknown_markers():
    rows=json.loads((OUT/'03_hyperparameter_configuration/EFFECTIVE_CONFIGURATIONS.json').read_text())
    assert len(rows)==7969;assert len({r['run_id'] for r in rows})==7969
    assert sum(r['training_status']=='REUSED' for r in rows)==40
    assert all(set(CONFIG_FIELDS)<=set(r['effective_configuration']) for r in rows)
    assert any('NOT RECORDED' in r['effective_configuration'].values() for r in rows)


def test_official_validation_is_not_oof():
    import csv
    p=OUT/'06_dataset_specific/HANDOVER/COMPLETE_RESULTS.csv'
    with p.open() as f:rows=list(csv.DictReader(f))
    assert any(r['evaluation_scope']=='VALIDATION OFFICIAL' for r in rows)
    assert not any(r['evaluation_scope']=='INNER-OOF ASSESSMENT' for r in rows)


def test_compressed_audit_scratch_remains_readable(tmp_path):
    import gzip
    p=tmp_path/'audit_state.json'
    with gzip.open(p.with_suffix('.json.gz'),'wt') as f:json.dump({'roundtrip':'exact','value':13},f)
    assert read(p)=={'roundtrip':'exact','value':13}
