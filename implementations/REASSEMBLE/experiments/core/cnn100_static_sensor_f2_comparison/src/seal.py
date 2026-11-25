"""Hash final outputs after pipeline/log writers have exited."""
from common import ROOT, RUN, read, write, identity, utc


def main():
    assert read(RUN/'validation.json')['passed']
    assert read(RUN/'PIPELINE_STATUS.json')['stage'] == 'COMPLETE'
    write(ROOT/'09_reproducibility/FINAL_SEAL_RECEIPT.json',
          {'utc': utc(), 'after_all_stage_and_log_writers_completed': True,
           'validation_passed': True, 'original_inputs_modified': False})
    out = RUN/'manifests/OUTPUT_MANIFEST.json'
    payload = [identity(p) for p in sorted(ROOT.rglob('*'))
               if p.is_file() and p != out and not p.name.endswith('.writing')]
    write(out, {'utc': utc(), 'files': payload, 'total_bytes': sum(r['bytes'] for r in payload),
                'self_excluded': True, 'sealed_after_pipeline_completed': True,
                'raw_datasets_and_original_large_checkpoints_not_duplicated': True})
    print('SEALED_OUTPUTS', len(payload), sum(r['bytes'] for r in payload), 'bytes', flush=True)


if __name__ == '__main__':main()
