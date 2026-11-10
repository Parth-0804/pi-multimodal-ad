"""Read filesystem metadata and produce a condensed, measured project map."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import time
from zoneinfo import ZoneInfo

OUTPUT = Path(__file__).resolve().parents[1]
ROOT = OUTPUT.parents[1]
OUTPUT_REL = OUTPUT.relative_to(ROOT).as_posix()
DESCRIPTIONS = {
    '.cache': 'Preserved local caches',
    '.git': 'Git history and repository metadata',
    '.github': 'Repository contribution instructions',
    '.pytest_cache': 'Pytest cache',
    '.vscode': 'Editor configuration',
    '00_experiments': 'REASSEMBLE follow-up studies and comparisons',
    '26.10.2026_feedback_experiments': 'CNN benchmarks, fine-tuning and seed-stability studies',
    'archive': 'Preserved legacy code and research records',
    'artifacts': 'Curated figures, reports and thesis evidence',
    'configs': 'Dataset and experiment configurations',
    'CROSS_DATASET_COMPARISON': 'Cross-dataset evaluation, synthesis and review export',
    'data': 'Supplementary datasets currently stored here',
    'DATASET_RESEARCH': 'Dataset navigation links and registry',
    'docs': 'Policies, methodology, research notes and indexes',
    'experiments': 'Historical EDA and numbered experiment walkthroughs',
    'HANDOVER': 'Handover raw inputs, evaluation and research evidence',
    'ma_thesis_env': 'Installed Python environment and libraries',
    'MILLING DATASET': 'Historical MSM acquisition, pilots and source data',
    'MSM': 'Final MSM evaluation and research evidence',
    'parth_ws_bootstrap': 'Original REASSEMBLE workspace and experiment history',
    'REBOOT': 'REBOOT feasibility audit and blinded visual-review pilot',
    'runs': 'Versioned PHM, REASSEMBLE, Intel and thesis outputs',
    'scratch': 'Existing scratch and exploratory inspection outputs',
    'scripts': 'Command-line research and maintenance scripts',
    'src': 'Domain-owned implementation and compatibility wrappers',
    'STORAGE_AUDIT': 'Dated storage and directory-map snapshots',
    'tests': 'Validation code and synthetic fixtures',
    'tutorials': 'Tutorials, baseline demonstrations and presentations',
}
LEAF_LABELS = {
    '01_raw_dataset': 'Raw dataset files and source metadata',
    'official_dataset': 'Original dataset files',
    'official_release': 'Pinned REBOOT dataset files',
    'remote_range_evidence': 'Original byte-range acquisition evidence',
    '02_labels_and_alignment': 'Labels, sample manifests and alignment evidence',
    '02_labels_and_annotations': 'Native annotations and label audits',
    '03_processed_model_inputs': 'Derived features, model inputs and split manifests',
    '03_video_sensor_alignment': 'Numerical projections and video alignment evidence',
    '04_experiment_protocol': 'Experiment configuration and methodology',
    '04_visual_failure_review': 'Real frames, video previews and blinded review materials',
    '05_trained_models': 'Fitted models, scalers and training histories',
    '05_architecture_compatibility': 'Architecture compatibility evidence',
    '06_evaluation_results': 'Predictions, metrics and evaluation figures',
    '06_evaluation_feasibility': 'Grouping, duplicate and evaluation feasibility evidence',
    '07_robustness_experiments': 'Corruption policies and robustness results',
    '07_research_decision': 'Research decision and researcher handoff',
    '08_visual_examples_and_eda': 'Representative inputs and exploratory figures',
    '09_final_reports': 'Final scientific reports',
    '99_preserved_previous_work': 'Links or records preserving earlier work',
    'INDEPENDENT_REVIEW_PACKAGE': 'Complete independent-review evidence and ZIP archive',
    'code': 'Study source code', 'source': 'Study source code',
    'src': 'Source code', 'tests': 'Validation code and fixtures',
    'results': 'Saved experiment results', 'logs': 'Run logs',
    'configs': 'Configuration files', 'config': 'Configuration snapshots',
    'data_manifests': 'Dataset and sample identities',
    'provenance': 'Source and execution provenance',
    'shared_cache': 'Shared feature caches and cache-retention records',
}


def purpose(path: str) -> str:
    if path == '.':
        return 'Project root'
    if path in DESCRIPTIONS:
        return DESCRIPTIONS[path]
    name = path.rsplit('/', 1)[-1]
    if name in LEAF_LABELS:
        return LEAF_LABELS[name]
    if name == '__pycache__':
        return 'Python bytecode cache'
    if path.startswith('runs/reassemble'):
        return 'REASSEMBLE experiment files'
    if path.startswith('runs/phm2026'):
        return 'PHM 2026 ' + name.removeprefix('phm2026').strip('_').replace('_', ' ') + ' outputs'
    if path.startswith('00_experiments/') and path.count('/') == 1:
        return 'REASSEMBLE ' + name.replace('_', ' ') + ' study'
    if path.startswith('CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/'):
        return 'Exported ' + name.replace('_', ' ') + ' evidence'
    if path.startswith('data/'):
        return name.replace('_', ' ') + ' dataset files'
    if name == 'reassemble':
        return 'REASSEMBLE ' + path.split('/')[0] + ' files'
    if name in {'phm2026', 'intel_welding', 'thesis'}:
        return name.replace('_', ' ') + ' ' + path.split('/')[0] + ' files'
    if name == 'runs':
        return 'Versioned study runs and provenance'
    return name.replace('_', ' ') + ' files'


def size(value: int) -> str:
    for unit, divisor in [('TiB', 1024**4), ('GiB', 1024**3), ('MiB', 1024**2), ('KiB', 1024)]:
        if value >= divisor:
            return f'{value/divisor:,.2f} {unit}'
    return f'{value:,} B'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    started = datetime.now(timezone.utc)
    start_clock = time.monotonic()
    directories = {}
    symlinks = []
    warnings = []
    inode_sizes = {}
    unique_bytes = 0
    unique_allocated = 0
    hardlink_repeats = 0
    special = 0

    def scan(relative: str):
        nonlocal unique_bytes, unique_allocated, hardlink_repeats, special
        folder = ROOT if relative == '.' else ROOT / relative
        record = {'path': relative, 'files': 0, 'file_bytes': 0, 'subdirectories': 0,
                  'symlinks': 0, 'direct_files': 0, 'direct_file_bytes': 0,
                  'direct_symlinks': 0, 'direct_allocated_bytes': 0,
                  'unique_file_bytes': 0, 'unique_allocated_bytes': 0,
                  'children': [], 'purpose': purpose(relative)}
        local_inodes = set()
        direct_inodes = set()
        try:
            with os.scandir(folder) as iterator:
                entries = sorted(iterator, key=lambda entry: entry.name.casefold())
        except OSError as error:
            warnings.append({'path': relative, 'operation': 'scandir', 'error_type': type(error).__name__})
            directories[relative] = record
            return record, local_inodes
        for entry in entries:
            child = entry.name if relative == '.' else relative + '/' + entry.name
            if child == OUTPUT_REL:
                continue  # This new audit excludes itself from its own snapshot.
            try:
                info = entry.stat(follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode):
                    record['symlinks'] += 1
                    record['direct_symlinks'] += 1
                    target = os.readlink(entry.path)
                    resolved = Path(entry.path).resolve(strict=False)
                    inside = resolved.is_relative_to(ROOT)
                    # Do not expose unrelated external home-directory identities.
                    target_display = (os.path.relpath(resolved, Path(entry.path).parent)
                                      if inside else '[outside project]/' + resolved.name)
                    symlinks.append({'path': child, 'target': target_display,
                                     'target_within_project': inside,
                                     'target_is_directory': resolved.is_dir(),
                                     'exists_at_scan': resolved.exists()})
                elif stat.S_ISDIR(info.st_mode):
                    below, child_inodes = scan(child)
                    local_inodes.update(child_inodes)
                    record['children'].append(child)
                    for key in ['files', 'file_bytes', 'symlinks']:
                        record[key] += below[key]
                    record['subdirectories'] += below['subdirectories'] + 1
                elif stat.S_ISREG(info.st_mode):
                    record['files'] += 1
                    record['direct_files'] += 1
                    record['file_bytes'] += info.st_size
                    record['direct_file_bytes'] += info.st_size
                    identity = (info.st_dev, info.st_ino)
                    local_inodes.add(identity)
                    direct_inodes.add(identity)
                    if identity not in inode_sizes:
                        inode_sizes[identity] = (info.st_size, info.st_blocks * 512)
                        unique_bytes += info.st_size
                        unique_allocated += info.st_blocks * 512
                    else:
                        hardlink_repeats += 1
                else:
                    special += 1
            except OSError as error:
                warnings.append({'path': child, 'operation': 'metadata', 'error_type': type(error).__name__})
        directories[relative] = record
        record['unique_file_bytes'] = sum(inode_sizes[k][0] for k in local_inodes)
        record['unique_allocated_bytes'] = sum(inode_sizes[k][1] for k in local_inodes)
        record['direct_allocated_bytes'] = sum(inode_sizes[k][1] for k in direct_inodes)
        return record, local_inodes

    total, _ = scan('.')
    finished = datetime.now(timezone.utc)
    top = [directories[path] for path in total['children']]
    assert total['files'] == total['direct_files'] + sum(row['files'] for row in top)
    assert total['file_bytes'] == total['direct_file_bytes'] + sum(row['file_bytes'] for row in top)
    assert len(directories) - 1 == total['subdirectories']
    assert total['symlinks'] == len(symlinks)
    assert total['unique_file_bytes'] == unique_bytes
    assert total['unique_allocated_bytes'] == unique_allocated
    usage = shutil.disk_usage(ROOT)
    rows = [{k: v for k, v in directories[p].items() if k != 'children'} for p in sorted(directories)]
    with (OUTPUT / 'DIRECTORY_INVENTORY.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUTPUT / 'SYMLINK_INVENTORY.json').write_text(json.dumps(symlinks, indent=2) + '\n')

    displayed = set()

    def collapse(path: str) -> bool:
        parts = path.split('/')
        depth = len(parts)
        first = parts[0]
        if first in {'.git', '.cache', '.pytest_cache', '.vscode', '.github', 'ma_thesis_env'}:
            return True
        if any(p in {'__pycache__', '.tools', 'official_release', 'official_dataset',
                     'remote_range_evidence', 'galleries', 'numerical_projections'} for p in parts):
            return True
        if path in {'MILLING DATASET/runs', 'MILLING DATASET/data/raw',
                    'parth_ws_bootstrap/00_Experimentaitons'}:
            return True
        if first in {'runs', 'data', 'docs', 'artifacts', 'scripts', 'src', 'tests',
                     'configs', 'archive', 'STORAGE_AUDIT', 'scratch', 'tutorials'}:
            return depth >= 2
        if first == 'experiments':
            return depth >= (3 if path.startswith(('experiments/reassemble', 'experiments/phm2026')) else 2)
        return depth >= 3

    def line(record):
        links = f"; {record['symlinks']:,} links" if record['symlinks'] else ''
        noun = 'file' if record['files'] == 1 else 'files'
        return f"{record['files']:,} {noun}; {size(record['unique_allocated_bytes'])} on disk{links}"

    def tree(path: str, prefix: str, last: bool):
        row = directories[path]
        displayed.add(path)
        stop = collapse(path)
        suffix = ' [grouped]' if stop and row['subdirectories'] else ''
        lines.append(prefix + ('└── ' if last else '├── ') + path.rsplit('/', 1)[-1] + '/  '
                     + line(row) + ' — ' + row['purpose'] + suffix)
        if stop:
            return
        items = [('directory', p) for p in row['children']]
        items += [('link', r) for r in symlinks if r['path'].rsplit('/', 1)[0] == path]
        if row['direct_files']:
            items.append(('files', None))
        indent = prefix + ('    ' if last else '│   ')
        for index, (kind, value) in enumerate(items):
            final = index == len(items) - 1
            branch = '└── ' if final else '├── '
            if kind == 'directory':
                tree(value, indent, final)
            elif kind == 'link':
                lines.append(indent + branch + value['path'].rsplit('/', 1)[-1] + '@ → '
                             + value['target'] + ' [link; target files not counted again]')
            else:
                lines.append(indent + branch + f"[files directly here: {row['direct_files']:,}; {size(row['direct_allocated_bytes'])} on disk]")

    local_time = finished.astimezone(ZoneInfo('Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S %Z')
    text = ['# Current project directory map', '',
            f'Measured {local_time}. Project root: `pi-multimodal-ad/`.', '',
            f"**{total['files']:,} regular file paths · {total['subdirectories']:,} directories · "
            f"{size(unique_allocated)} of file storage · {len(symlinks):,} symbolic links.**", '',
            'Counts include all descendants, hidden files and ignored files. Sizes use binary units '
            '(1 GiB = 1,073,741,824 bytes). The tree shows allocated regular-file blocks, with '
            'hard links counted once within each folder. The table also shows logical file bytes '
            '(the sum of file lengths, counting every path). Directory and symlink metadata blocks are excluded. '
            'Parent values already include children: do not add parent and child rows. '
            'Shared hard links can also overlap between sibling folders. '
            'Symlinks are listed without following their targets; their target files are not counted again. '
            'Private-file contents were never opened; this report lists groups instead of individual file names.', '',
            f'The scan read directory entries and file metadata only. It did not open datasets, archives, checkpoints '
            f'or credentials. The new report directory `{OUTPUT_REL}/` is excluded from its own snapshot. '
            'Concurrent jobs may change file counts or sizes after this scan.', '',
            '## Top-level folders', '',
            '| Folder | Content | Files, recursive | File storage on disk | Logical size |',
            '|---|---|---:|---:|---:|']
    for row in top:
        text.append(f"| `{row['path']}/` | {row['purpose']} | {row['files']:,} | {size(row['unique_allocated_bytes'])} | {size(row['file_bytes'])} |")
    text += [f"| Files directly in project root | Root documents, scripts, configuration, model and local files | {total['direct_files']:,} | {size(total['direct_allocated_bytes'])} | {size(total['direct_file_bytes'])} |", '',
             '## Condensed directory tree', '',
             'Each `[grouped]` branch represents every descendant beneath that folder. '
             'Repeated sessions, model outputs, raw files and installed packages are summarized by their complete counts and sizes. '
             'The CSV inventory contains a measurement for every scanned directory if a deeper lookup is needed.', '', '```text']
    lines = [f"pi-multimodal-ad/  {line(total)}"]
    root_items = total['children']
    for path in root_items:
        tree(path, '', False)
    lines.append(f"└── [files directly in project root: {total['direct_files']:,}; {size(total['direct_allocated_bytes'])} on disk]")
    text += lines + ['```', '', '## Where the dataset work lives', '',
                     '| Study | Main locations | Interpretation |', '|---|---|---|',
                     '| REASSEMBLE | `src/reassemble/`, `scripts/reassemble/`, `configs/reassemble/`, `runs/reassemble/`, `artifacts/reassemble/`, `experiments/reassemble/`, `00_experiments/`, `parth_ws_bootstrap/`, `26.10.2026_feedback_experiments/` | Implementation, walkthroughs, original experiments and later CNN/fusion studies; raw inputs may be referenced outside this project. |',
                     '| MSM / Milling | `MSM/`, `MILLING DATASET/` | Current MSM evaluation plus preserved acquisition and pilot evidence for the same dataset. |',
                     '| Handover | `HANDOVER/` | Native inputs, labels, evaluation, robustness and reports. |',
                     '| REBOOT | `REBOOT/` | Independent feasibility pilot, source audit and blinded visual review. |',
                     '| PHM 2026 | `src/phm2026/`, `scripts/phm2026/`, `configs/`, `runs/phm2026*/`, `artifacts/phm2026/`, `experiments/` | PHM implementations and historical/current research outputs. |',
                     '| Intel welding | `src/intel_welding/`, `scripts/intel_welding/`, `runs/intel_welding/`, `artifacts/intel_welding/`, `archive/` | Implementation, audit evidence and historical work. Folder existence does not imply raw data are present. |',
                     '| Shared navigation | `DATASET_RESEARCH/` | Links to MSM, Milling, Handover and REBOOT; no extra copies of those datasets. |',
                     '| Cross-dataset review | `CROSS_DATASET_COMPARISON/` | Shared external evaluation and the independent-review export. |', '',
                     '## Relevant links and external inputs', '',
                     'Links below retain their original locations. External targets are named only by their final component; '
                     'their contents were not traversed or included in project totals.', '',
                     '| Link | Target | Target location | Exists at scan |', '|---|---|---|---|']
    relevant_links = [r for r in symlinks if r['target_is_directory']
                      and r['path'].split('/')[0] not in {'.git', 'ma_thesis_env', '.cache', 'runs'}]
    for row in relevant_links:
        text.append(f"| `{row['path']}` | `{row['target']}` | {'Inside project' if row['target_within_project'] else 'Outside project'} | {'Yes' if row['exists_at_scan'] else 'No'} |")
    text += ['', '## Snapshot checks', '',
             f"- All {len(directories):,} scanned directory records reconcile with the root file and byte totals.",
             f"- {len(displayed):,} directory branches are printed; other descendants are covered by their grouped parent and the complete CSV.",
             f"- {len(warnings):,} metadata access/change warnings; {special:,} special filesystem entries.",
             f'- Hard-link repeats: {hardlink_repeats:,}. Unique regular-file content is {size(unique_bytes)}; '
             f'unique regular-file allocated blocks occupy {size(unique_allocated)}. These exclude directory blocks and external link targets.',
             f'- Whole filesystem at scan: {size(usage.free)} free of {size(usage.total)}. '
             'This is filesystem capacity, not this project’s size.',
             '- Existing files, experiments and running jobs were left unchanged. No training or cleanup was run.', '',
             'Companion files: `DIRECTORY_INVENTORY.csv` (every scanned directory), '
             '`SYMLINK_INVENTORY.json`, `PROVENANCE.json`, `config/resolved_config.json`, '
             '`validation.json` and `source/build_directory_map.py`.', '']
    (OUTPUT / 'PROJECT_DIRECTORY_MAP.md').write_text('\n'.join(text))
    (OUTPUT / 'DIRECTORY_TREE.txt').write_text('\n'.join([
        f'Measured {local_time}; allocated file sizes, hard links counted once per subtree; symlinks not followed; current audit output excluded.',
        'Parent counts include descendants. [grouped] means descendants are summarized.', '', *lines, '']))
    config = {'project_root': '.', 'output_root': OUTPUT_REL, 'follow_symlinks': False,
              'read_file_payloads': False,
              'tree_size_basis': 'allocated regular-file blocks with hard links counted once per subtree',
              'additional_table_size_basis': 'logical regular-file bytes per path',
              'excluded_from_snapshot': [OUTPUT_REL], 'directory_display_maximum_depth': 3,
              'full_directory_measurements_retained': True, 'private_file_names_listed': False}
    (OUTPUT / 'config').mkdir(exist_ok=True)
    (OUTPUT / 'config/resolved_config.json').write_text(json.dumps(config, indent=2) + '\n')
    provenance = {'scan_started_utc': started.isoformat(), 'scan_finished_utc': finished.isoformat(),
                  'scan_finished_Europe_Berlin': finished.astimezone(ZoneInfo('Europe/Berlin')).isoformat(),
                  'scan_elapsed_seconds': time.monotonic() - start_clock,
                  'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  'tracked_dirty_paths': subprocess.check_output(['git', 'status', '--short', '--untracked-files=no'], cwd=ROOT, text=True).splitlines(),
                  'command': f'ma_thesis_env/bin/python -B {OUTPUT_REL}/source/build_directory_map.py',
                  'config': config, 'python': os.sys.version,
                  'method': 'os.scandir + stat(follow_symlinks=False); no payload read, raw hashing or archive traversal',
                  'file_paths_count': total['files'], 'logical_file_bytes_per_path': total['file_bytes'],
                  'directory_count_including_root': len(directories), 'symbolic_link_count': len(symlinks),
                  'hard_link_repeat_paths': hardlink_repeats, 'unique_regular_file_bytes': unique_bytes,
                  'unique_regular_file_allocated_bytes': unique_allocated,
                  'filesystem_free_bytes': usage.free, 'filesystem_total_bytes': usage.total,
                  'warnings': warnings, 'existing_files_modified': False}
    (OUTPUT / 'PROVENANCE.json').write_text(json.dumps(provenance, indent=2) + '\n')
    (OUTPUT / 'validation.json').write_text(json.dumps({
        'passed': not warnings, 'root_file_count_reconciles': True,
        'root_logical_bytes_reconcile': True, 'all_directory_counts_reconcile': True,
        'symlink_count_reconciles': True, 'payloads_read': False, 'metadata_warnings': warnings,
        'printed_directory_branches': len(displayed), 'full_directory_records': len(directories),
        'no_existing_file_modified': True}, indent=2) + '\n')
    outputs = [p for p in OUTPUT.rglob('*') if p.is_file() and p.name != 'OUTPUT_MANIFEST.json']
    (OUTPUT / 'OUTPUT_MANIFEST.json').write_text(json.dumps([
        {'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
        for p in sorted(outputs)], indent=2) + '\n')
    print(json.dumps({'report': (OUTPUT / 'PROJECT_DIRECTORY_MAP.md').relative_to(ROOT).as_posix(),
                      'files': total['files'], 'directories': total['subdirectories'],
                      'logical_size': size(total['file_bytes']), 'free': size(usage.free),
                      'printed_branches': len(displayed), 'symlinks': len(symlinks),
                      'warnings': len(warnings), 'elapsed_seconds': time.monotonic() - start_clock}, indent=2), flush=True)


if __name__ == '__main__':
    main()
