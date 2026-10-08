"""Seal a completed audit after its finalization process and log have closed.

Preserve the initial manifest and document the observed log-only discrepancy.
Run with stdout outside the audit tree; never redirect into a hashed audit file.
"""
import argparse
import os
import shutil
from pathlib import Path

from .common import (check_fingerprints, digest, fingerprint, freeze_revision,
                     now, read, write)


def seal(run):
    root = Path(run)
    out = root / '05_final_review'
    manifest_path = out / 'output_manifest.json'
    archive = out / 'output_manifest.initial.json'
    if archive.exists():
        raise FileExistsError('Initial manifest already archived; do not reseal silently.')
    stdout = Path(os.readlink('/proc/self/fd/1'))
    if stdout.is_absolute() and stdout.is_relative_to(root.resolve()):
        raise ValueError('Do not write sealing stdout into the audit tree.')
    initial = read(manifest_path)
    changed = [e['path'] for e in initial['files']
               if not Path(e['path']).is_file()
               or Path(e['path']).stat().st_size != e['bytes']
               or digest(e['path']) != e['sha256']]
    expected = str(out / 'finalization.log')
    if changed != [expected]:
        raise ValueError('Unexpected initial-manifest differences: ' + repr(changed))
    protected = check_fingerprints(read(root / '00_protocol/source_manifest.json'))
    for path, sha256 in read(root / '00_protocol/protocol_freeze.json')['sha256'].items():
        if digest(path) != sha256:
            raise ValueError('Frozen protocol changed: ' + path)
    for section in ['external_blind_files', 'restricted_external_key_identity']:
        check_fingerprints(initial[section])
    required = [
        'FINAL_VALIDITY_AUDIT_HANDOFF.md', 'VALIDITY_STORYLINE_ADDENDUM.md',
        'CLAIM_IMPACT_MATRIX.csv', 'AUDIT_STATUS.json', 'validation.json',
    ]
    for name in required:
        if not (out / name).is_file():
            raise FileNotFoundError(name)
    status = read(out / 'AUDIT_STATUS.json')
    if status['headline_status'] != 'AUTOMATED VALIDITY AUDIT COMPLETE — HUMAN REVIEW PENDING':
        raise ValueError('Unexpected audit status')
    if status['actual_human_ratings_received'] != 0:
        raise ValueError('Review state changed; inspect before sealing.')

    shutil.copyfile(manifest_path, archive)
    correction = (
        '\n3. Final packaging verification found exactly one initial manifest '
        'mismatch: finalization.log received the final status line after the '
        'manifest was written. The completed log is now stable. Preserved the '
        'original manifest byte-for-byte as 05_final_review/output_manifest.initial.json '
        'and resealed with the separate seal.py after finalization exited. '
        'All other initially listed audit outputs and external exports matched; '
        f'all {protected} protected source hashes and frozen protocol hashes '
        'were checked again unchanged. No source prediction, metric, historical '
        'output, or active queue was modified. This is an audit packaging '
        'correction, not a research numerical discrepancy. Final sealing stdout '
        'is not redirected into a hashed file. See manifest_validation.json.\n'
    )
    with (root / '00_protocol/CORRECTIONS.md').open('a') as handle:
        handle.write(correction)
    freeze_revision(root, 'final_manifest_seal')
    source = Path('scripts/thesis/final_validity_audit/seal.py')
    snapshot = root / '00_protocol/audit_source' / source
    with source.open('rb') as src, snapshot.open('xb') as dst:
        shutil.copyfileobj(src, dst)
    write(out / 'manifest_validation.json', {
        'timestamp_UTC': now(), 'passed': True,
        'initial_manifest_sha256': digest(archive),
        'initial_manifest_files_checked': len(initial['files']),
        'initial_manifest_mismatches': changed,
        'correction': 'Post-process sealing; initial manifest preserved unchanged.',
        'protected_source_hashes_unchanged': protected,
        'frozen_protocol_hashes_unchanged': True,
        'external_export_hashes_unchanged': True,
        'status': status['headline_status'],
        'sealing_command': (
            'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=. '
            'ma_thesis_env/bin/python -B -m scripts.thesis.final_validity_audit.seal '
            '--run ' + str(root)
        ),
        'exclusion': 'Only final output_manifest.json excludes its own hash.',
    })
    final = {
        'timestamp_UTC': now(), 'audit_run': str(root),
        'supersedes_preserved_manifest': str(archive),
        'files': fingerprint(p for p in root.rglob('*')
                             if p.is_file() and p != manifest_path),
        'external_blind_files': initial['external_blind_files'],
        'restricted_external_key_identity': initial['restricted_external_key_identity'],
        'exclusions': 'Only this final manifest excludes itself; initial manifest is included. '
                      'Restricted annotation keys are identified, never copied into Git.',
    }
    pending = out / 'output_manifest.pending.json'
    write(pending, final)
    os.replace(pending, manifest_path)
    for section in ['files', 'external_blind_files', 'restricted_external_key_identity']:
        check_fingerprints(read(manifest_path)[section])
    print(f"Final manifest verified: {len(final['files'])} audit files; "
          f'{protected} protected source hashes unchanged.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True)
    seal(parser.parse_args().run)
