from vifailback import common,reporting


def test_reports_preserve_previous_snapshots_and_do_not_invent_results(tmp_path,monkeypatch):
    c=common.config();monkeypatch.setattr(common,'PROJECT',tmp_path);monkeypatch.setattr(reporting,'PROJECT',tmp_path)
    monkeypatch.setattr(reporting,'REPO',tmp_path.parent)
    a=reporting.publish(c,stage='SYNTHETIC_CHECK')
    first=tmp_path.parent/a['snapshot'];before={p.name:p.read_bytes() for p in first.glob('*.md')}
    assert len(before)==13
    assert a['models_with_saved_outer_predictions']==[]
    assert 'No held-out ViFailback predictions have been completed' in (first/'06_UNIMODAL_BASELINE_RESULTS.md').read_text()
    b=reporting.publish(c,stage='SECOND_SYNTHETIC_CHECK');assert b['snapshot']!=a['snapshot']
    assert before=={p.name:p.read_bytes() for p in first.glob('*.md')}
