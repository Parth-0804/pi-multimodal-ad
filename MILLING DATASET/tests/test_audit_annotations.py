import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("audit_annotations", Path(__file__).parents[1] / "source/audit_annotations.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_native_label_two_is_stable_tool_defect():
    row = module.validate_rows([{"start": "1.1", "end": "2.3", "label": "2"}])[0]
    assert row["label"] == 2
    assert str(row["duration"]) == "1.2"
    assert module.MEANINGS[2] == "defective tool during stable cutting"


def test_invalid_labels_and_times_remain_in_audit():
    rows = [{"start": "0", "end": "1", "label": "3"},
            {"start": "nan", "end": "1", "label": "1"},
            {"start": "2", "end": "1", "label": "0"},
            {"start": "-1", "end": "0", "label": "0"},
            {"start": "0", "end": "inf", "label": "1"},
            {"start": "0", "end": "0", "label": "0"}]
    result = module.validate_rows(rows)
    assert len(result) == len(rows)
    assert all(r["errors"] for r in result)
    assert [r["source_row"] for r in result] == list(range(2, 8))


def test_overlaps_duplicates_and_missing_context_reported_without_deletion():
    rows = [{"start": "0", "end": "2", "label": "0", "Tool": ""},
            {"start": "1", "end": "3", "label": "1", "Tool": "A"},
            {"start": "1", "end": "3", "label": "1", "Tool": "A"}]
    result = module.validate_rows(rows)
    assert len(result) == 3
    assert "missing_context:Tool" in result[0]["warnings"]
    assert "overlaps_earlier_interval" in result[1]["warnings"]
    assert "duplicate_annotation_row" in result[2]["warnings"]
    assert not any(r["errors"] for r in result)
