"""Independent asset checks and final package; writes only within this asset root."""
import ast,csv,hashlib,json,os,subprocess,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
import numpy as np,pandas as pd
from PIL import Image
OUT=Path(__file__).resolve().parent;REPO=OUT.parents[3]

def write(name,obj):
    with (OUT/name).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def load(name):return json.loads((OUT/name).read_text())
def csvread(name):return pd.read_csv(OUT/name,dtype={'recording_id':str,'segment_id':str})
assert (OUT/'figure_presentation_notes.json').exists(),'Polish must complete before finalization'
e=csvread('selected_examples.csv');fs=csvread('frame_selection.csv');sm=csvread('sensor_shapes.csv');am=csvread('audio_metadata.csv');vm=csvread('video_metadata.csv');schema=csvread('sensor_channel_schema.csv');stats=csvread('statistics_insert_failure.csv')
cfg=load('config_snapshot.json');cohort_path=REPO/'runs/reassemble/20260927T154732Z-section1/cohort.parquet';f=pd.read_parquet(cohort_path);f.recording_id=f.recording_id.astype(str);f.segment_id=f.segment_id.astype(str)
assert (len(f),int(f.failure.sum()),f.recording_id.nunique())==(4530,509,148)
assert len(e)==8 and e.groupby(['action','failure']).size().eq(1).all()
for r in e.itertuples():
    g=f[(f.action==r.action)&(f.failure==r.failure)].copy();g['duration']=g.end-g.start;g['distance']=(g.duration-g.duration.median()).abs();winner=g.sort_values(['distance','recording_id','segment_id'],kind='stable').iloc[0]
    assert (winner.recording_id,winner.segment_id)==(r.recording_id,r.segment_id)
    for typ,n in [('display5',5),('model16',16)]:
        rows=fs[(fs.example_id==r.example_id)&(fs.selection_type==typ)];assert len(rows)==n and rows.inside_interval.all();assert rows.frame_timestamp.between(r.start,r.end,inclusive='both').all()
        with Image.open(OUT/'contact_sheets'/f'{r.example_id}_{n}frame.png') as im:im.verify()
    x=np.load(OUT/'sensors'/f'{r.example_id}_512x22.npy',allow_pickle=False);assert x.shape==(512,22) and x.dtype==np.float32
    assert np.isclose(np.isfinite(x).mean(),sm.set_index('example_id').loc[r.example_id,'finite_fraction'])
assert len(fs)==168 and len(stats)==220 and stats.groupby('channel_name').size().eq(10).all() and stats.channel_name.nunique()==22
assert np.isfinite(stats.value.to_numpy()).all()
assert len(schema)==22 and schema.groupby('stream_name').component_index.count().sum()==22
assert len(am)==24 and am.decoded_successfully.all() and not am.independently_verified_annotation_offset.any() and not am.independently_verified_drift.any() and am.independently_verified_action_intervals.eq(0).all()
assert len(vm)==8 and vm.frame_count_matches_timestamp_count.all()
assert load('audio_alignment_status.json')['audio_alignment_status']=='unverified'
assert load('sample_alignment_timeline.json')['audio_alignment_status']=='unverified'
assert load('sample_alignment_timeline.json')['action_aligned_audio_samples'] is None
# Check exact statistics again, executing only the source pure function definition.
feature_path=REPO/'src/reassemble/section1_features.py';tree=ast.parse(feature_path.read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='statistics');ns={'np':np};exec(compile(ast.Module(body=[node],type_ignores=[]),str(feature_path),'exec'),ns)
values=ns['statistics'](np.load(OUT/'sensors/insert_failure_512x22.npy',allow_pickle=False));assert np.array_equal(values,stats.value.to_numpy().astype('float32'))
# Read only frame indices, sensor arrays and engineered statistics from retained caches.
cache_inputs=[]
for r in e.itertuples():
    p=REPO/'runs/reassemble/20260927T154732Z-section1/features'/f'{r.recording_id}.npz';cache_inputs.append({'path':os.path.relpath(p,REPO),'sha256':sha(p),'size_bytes':p.stat().st_size,'arrays_read':['row_index','frame_indices','sensor']+(['statistics'] if r.example_id=='insert_failure' else [])})
    with np.load(p,allow_pickle=False) as z:
        index=int(f.index[(f.recording_id==r.recording_id)&(f.segment_id==r.segment_id)][0]);j=int(np.flatnonzero(z['row_index']==index)[0]);assert np.array_equal(z['frame_indices'][j],fs[(fs.example_id==r.example_id)&(fs.selection_type=='model16')].frame_index.to_numpy())
        assert np.array_equal(z['sensor'][j],np.load(OUT/'sensors'/f'{r.example_id}_512x22.npy',allow_pickle=False),equal_nan=True)
        if r.example_id=='insert_failure':assert np.array_equal(z['statistics'][j],values,equal_nan=True)
write('retained_feature_comparison_sources.json',cache_inputs)
# Final preservation check after layout and audio display adjustments.
preserved=load('source_preservation_before.json')
for group in ['raw_files','selected_encoded_videos']:
    for item in preserved[group]:
        s=(REPO/item['path']).stat();assert (s.st_size,s.st_mtime_ns)==(item['size_bytes'],item['mtime_ns']),item['path']
for item in load('input_manifest.json'):assert sha(REPO/item['path'])==item['sha256']
images=sorted(OUT.rglob('*.png'))
for p in images:
    with Image.open(p) as im:im.verify()
assert len(images)==39
write('redactions.json',{'reviewed_utc':datetime.now(timezone.utc).isoformat(),'review_method':'Visual inspection of all eight 5-frame and all eight 16-frame contact sheets; same frame indices retained during layout adjustment.','contact_sheets_reviewed':[str(p.relative_to(OUT)) for p in sorted((OUT/'contact_sheets').glob('*.png'))],'result':'No identifiable faces, badges, screens, or private text observed in selected frames. Robot gripper, assembly fixtures, parts, cables, floor and background are visible.','redactions':[],'source_media_modified':False,'presentation_edits':'Thumbnail resize and layout only; no crop, blur, generated content, or altered pixels within the original media.'})
env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
checks=[]
for command in [['git','diff','--check'],['git','diff','--stat'],['git','status','--short','--branch','--untracked-files=all'],['ma_thesis_env/bin/python','-B','-m','pip','check']]:
    p=subprocess.run(command,cwd=REPO,env=env,text=True,capture_output=True);checks.append({'command':' '.join(command),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0
status=checks[2]['stdout'];assert all(line.startswith('##') or line==' D src/shared/README.md' or line.startswith('?? artifacts/presentation/reassemble_dataset_assets/'+OUT.name+'/') for line in status.splitlines()),'Unexpected worktree change'
write('repository_checks.json',checks)
validation=load('validation_pending.json');validation.update({'privacy_review':'Complete; no sensitive regions observed; no redactions required','independent_reselection_matches':True,'persisted_sensor_arrays_validated':True,'statistics_match_current_function_and_retained_cache':True,'all_pngs_readable':True,'png_count':len(images),'audio_stream_rows':len(am),'video_metadata_rows':len(vm),'source_preservation_rechecked_after_polish':True,'repository_checks_passed':True,'all_requested_assets_present':True,'overall_status':'PASS','package_integrity_report':'package_integrity.json (created after ZIP verification; outside ZIP)'})
assert not validation['missing_assets'] and not validation['warnings'];write('validation.json',validation)
zipname=f'REASSEMBLE_DATASET_PPT_ASSETS_{OUT.name}.zip';zip_path=OUT/zipname
excluded_names={'manifest.csv','checksums.sha256','package_integrity.json',zipname}
# The pre-finalization report and font cache remain in this run for transparency,
# but are not presentation payload and do not enter the ZIP.
def packageable(p):return p.name not in {'validation_pending.json'} and 'plot_cache' not in p.relative_to(OUT).parts
existing=[p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file()]
all_paths=sorted(set(existing+['README.md','redactions.json','validation.json','manifest.csv','checksums.sha256','package_integrity.json',zipname]))
readme=f'''# REASSEMBLE dataset presentation assets

Frozen cohort: **4,530 completed actions**, **4,021 successes**, **509 failures**, **148 recordings**. The raw inventory contains **149 recordings**. The pack contains **39 PNG figures**, eight exact **512 × 22** sensor arrays, label cards, tables and provenance.

Use `contact_sheets/*_5frame.png` for slides, `*_16frame.png` to explain actual frame selection, `sensors/*_heatmap.png` and `*_grouped_lines.png` for sensor examples, and `statistics_insert_failure.png` for the 22 × 10 = 220 engineered statistics. `recording_contents.json` describes a recording; `sample_label_cards.json` exposes the actual selected annotation fields; `sample_alignment_timeline.json` supplies the insert/failure diagram data.

No model training or inference was run. No labels or cohort files were changed. No raw files were modified. No Task 4 execution occurred. No models or dependencies were downloaded or installed. No commits, pushes or Git index/branch changes were made. The pre-existing deletion of `src/shared/README.md` was left untouched. All new writes are under this timestamped asset directory. Full recordings, audio payloads and private human-review mappings are not exported.

Examples were selected without prediction outcomes, scores, correctness, or human-review outcomes. Within each action/failure stratum, duration is end minus start; select the first row sorted by absolute distance from that stratum's median duration, then recording_id and segment_id as strings. CSV readers should explicitly preserve recording_id and segment_id as strings. The exact identities and median distances are in `selected_examples.csv` and `selection_details.json`.

The eight selected IDs are: {', '.join(e.example_id)}.

Frame positions are uniformly spaced ranks in the inclusive in-interval index set, using NumPy rounding; they are not a claim of an exact frame at the annotation boundary. The 5 display positions are 0%, 25%, 50%, 75%, 100%. The 16 indices use the unmodified expression from the current Section 1 extractor. Every selected frame is inside its action interval and matches the retained extractor indices. Actual encoded videos are H.264, **640 × 480 at 30 fps**. Their frame counts equal timestamp counts. Container duration is frame_count/fps, which can differ from timestamp-span duration; config image_size=640 is not a raw-resolution declaration.

Sensor groups, in concatenation order: measured_force **3**, measured_torque **3**, gripper_positions **2**, joint_efforts **7**, joint_velocities **7** = **22 scalar channels**. The schema uses component indices, not invented axis names. `scalar_channel_count` is the group's width repeated on each component row; count the 22 rows or sum one width per group. Units were absent from the inspected sensor dataset attributes and are recorded as `NOT_AVAILABLE`.

Resampling calls the existing `interval_indices` and `resample_progress` functions with 512 positions and gap_multiple=5, then concatenates groups and casts to float32 exactly as Section 1. No population statistics, standardization, or imputation are applied to saved arrays. All eight arrays exactly match retained Section 1 sensor arrays, including NaNs. Finite fractions range from {sm.finite_fraction.min():.4%} to {sm.finite_fraction.max():.4%}; no channels are entirely missing. Boundary/gap NaNs are retained. Heatmap colors use per-channel within-example z-scores only (clipped to ±3), labelled “per-channel visualization scaling only — not model preprocessing”; line plots use source values.

Statistics execute the unmodified pure function definition from `src/reassemble/section1_features.py::statistics`, without importing or calling its model-loading/extraction entry points. Output is statistic-major: mean, population standard deviation, median, minimum, maximum, q25, q75, range, RMS, and slope per normalized progress. Exactly 220 values match retained Section 1 statistics. The compact statistics plot divides each channel's ten values by its maximum absolute value for display; the CSV retains the original values.

Audio figures are **illustrative full-recording excerpts, not action-aligned evidence**. The recording is the lexicographically first selected recording (`{sorted(e.recording_id.unique())[0]}`); each excerpt is its own stream's central ten seconds. Action labels and action intervals do not select these excerpts. Hama1/Hama2 are stereo MP3 at 16 kHz; hand_audio is mono MP3 at 48 kHz. All three are encoded byte values stored in int64 HDF5 arrays, not raw int64 PCM samples. No audio files are exported.

Sample counts are decoded sample frames per channel, not byte counts or total interleaved scalar samples. For the illustrated recording, decoded counts were recounted blockwise to EOF. For the other seven selected recordings, counts and durations retain the existing full-decode inventory after confirming raw size/mtime; current headers and beginning/central probes were decoded. These evidence types and header-versus-decoded counts are explicit in `audio_decode_evidence.json` and `audio_metadata.csv`. `decoded_successfully` records successful current probes; it does not claim a fresh full decode of all 24 streams. Header counts may overestimate duration. Waveforms show min/max envelopes; spectrograms show actual PSD with an excerpt-specific 80 dB display range, detailed in `figure_presentation_notes.json`.

Annotations supply absolute Unix-style start/end timestamps. Video and sensors use their HDF5 timestamp arrays. The nominal audio origin is the inventory's minimum first non-audio timestamp, following the established inventory convention. It is not an independently measured mapping from decoded audio time to the annotation clock. No verified offset, drift calibration, or segment anchor is available. Nominal overlap therefore does not establish label-safe action extraction. Audio was excluded by this prerequisite, not by a finding that it has no predictive signal. No audio samples are assigned to the displayed action.

Retained gate coverage matches the requested rounded values: hama1_audio **97.31% nominal / 96.46% failures**, hama2_audio **96.20% / 95.48%**, hand_audio **100.00% / 100.00%**; each has **148 nominally valid recordings and zero verified action intervals**. Exact source values, paths and SHA256 hashes are preserved in `audio_alignment_status.json`.

Visual inspection of all 16 contact sheets found no identifiable faces, badges, screens or private text; no redactions were needed (`redactions.json`).

`validation.json` is the final asset validation. `validation_pending.json` is the retained intermediate report, superseded by it and excluded from the ZIP. `repository_checks.json` records successful git diff --check, Git status/diff inspection and pip check. Existing repository implementation and historical outputs were not edited. This is an asset task, not a restructuring phase.

Raw size/mtime checks cover all **149 inventoried raw HDF5 files** plus eight selected encoded videos, before/after generation and after final presentation adjustments. Cohort, config, code and audit input hashes are checked unchanged. These are preservation metadata checks, not a fresh whole-dataset payload hash scan. Retained raw SHA256 identities come from the authoritative inventory.

The scripts `build_assets.py`, `polish_figures.py`, and `finalize_package.py` record the generation and verification process. Run with the existing repository Python and `-B`. These files are tied to this run; build/finalization use exclusive creation and intentionally refuse to overwrite completed outputs. To reproduce, place the scripts in a **new authorized timestamp directory** under the same root and execute in that order, including visual review. No clean second extraction run is claimed. Reproduction dependencies and software versions are in `provenance.json`.

Package: `{zipname}`. It contains the timestamp-named asset directory, excluding the ZIP itself, its post-package integrity record, the intermediate validation report and the Matplotlib font cache. `manifest.csv` inventories the pre-package files (including excluded intermediates); its own hash is covered by `checksums.sha256`. Checksums cover all packaged files except checksums.sha256 itself. The ZIP SHA256 and post-write CRC/content verification are in `package_integrity.json` beside the ZIP. These exclusions avoid circular/self hashes. All paths below are relative to `artifacts/presentation/reassemble_dataset_assets/{OUT.name}/`:

'''+ '\n'.join('- `'+p+'`' for p in all_paths)+'\n'
with (OUT/'README.md').open('x') as fp:fp.write(readme)
files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name not in excluded_names)
rows=[]
for p in files:rows.append({'path':p.relative_to(OUT).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p),'included_in_package':packageable(p),'role':'figure' if p.suffix=='.png' else 'bounded_resampled_example' if p.suffix=='.npy' else 'table' if p.suffix=='.csv' else 'provenance_or_documentation'})
with (OUT/'manifest.csv').open('x',newline='') as fp:
    writer=csv.DictWriter(fp,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
payload=[p for p in files if packageable(p)]+[OUT/'manifest.csv']
with (OUT/'checksums.sha256').open('x') as fp:
    for p in payload:fp.write(f'{sha(p)}  {p.relative_to(OUT).as_posix()}\n')
payload.append(OUT/'checksums.sha256')
with zipfile.ZipFile(zip_path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in payload:z.write(p,arcname=OUT.name+'/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(zip_path,'r') as z:
    assert z.testzip() is None
    assert len(z.infolist())==len(payload)
    for p in payload:assert hashlib.sha256(z.read(OUT.name+'/'+p.relative_to(OUT).as_posix())).hexdigest()==sha(p)
write('package_integrity.json',{'package':zipname,'size_bytes':zip_path.stat().st_size,'sha256':sha(zip_path),'zip_crc_check':'PASS','archived_file_hashes_match_disk':True,'archived_file_count':len(payload),'verified_utc':datetime.now(timezone.utc).isoformat(),'missing_assets':[]})
print(json.dumps({'package':str(zip_path),'MiB':zip_path.stat().st_size/2**20,'files':len(payload),'pngs':len(images),'validation':'PASS','examples':e.example_id.tolist(),'no_training_inference_task4_or_label_changes':True},indent=2))
