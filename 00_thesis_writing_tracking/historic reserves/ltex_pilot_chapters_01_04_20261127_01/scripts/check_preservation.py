"""Check pilot source preservation without compiling LaTeX."""
from pathlib import Path
import hashlib, json, re, subprocess, difflib
PILOT = Path(__file__).resolve().parents[1]
REPO = PILOT.parents[1]
SOURCE_MANIFEST = json.loads((PILOT/'reports/source_manifest.json').read_text())

def protected(text):
    return {
        'numbers': re.findall(r'\d+(?:[.,]\d+)*', text),
        'citations': re.findall(r'\\(?:cite|citep|parencite|textcite|citet)\*?(?:\[[^\]]*\]){0,2}\{[^}]*\}', text),
        'references_labels': re.findall(r'\\(?:ref|pageref|label|EvidenceRef)\{[^}]*\}', text),
        'headings': re.findall(r'\\(?:chapter|section|subsection|subsubsection)\*?\{[^}]*\}', text),
        'environment_sequence': re.findall(r'\\(?:begin|end)\{[^}]*\}', text),
        'math': re.findall(r'\\\(.*?\\\)|\\\[.*?\\\]|(?<!\\)\$(?:\\.|[^$])*\$', text, re.S),
        'tables_diagrams_equations': re.findall(r'\\begin\{(table\*?|longtable|tabularx|tabular\*?|tikzpicture|equation\*?|align\*?)\}.*?\\end\{\1\}', text, re.S),
        'graphic_calls': re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{[^}]*\}', text),
        'review_macro_calls': re.findall(r'\\Review(?:DepthFigure|FollowupTable)\b', text),
    }

def whole_protected_blocks(text):
    # Include full matched text, not just the environment capture.
    pattern = r'\\begin\{(table\*?|longtable|tabularx|tabular\*?|tikzpicture|equation\*?|align\*?)\}.*?\\end\{\1\}'
    return [m.group(0) for m in re.finditer(pattern,text,re.S)]

report = {'chapters': {}, 'active_sources_unchanged': {}, 'pilot_tracked_paths': []}
patches = []
for original in sorted((PILOT/'original/tex').glob('*.tex')):
    edited = PILOT/'reworked/tex'/original.name
    a,b=original.read_text(),edited.read_text()
    pa,pb=protected(a),protected(b)
    checks={key:pa[key]==pb[key] for key in pa}
    checks['full_tables_diagrams_equations']=whole_protected_blocks(a)==whole_protected_blocks(b)
    report['chapters'][original.name]={'changed':a!=b,'checks':checks,
        'original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
        'reworked_sha256':hashlib.sha256(edited.read_bytes()).hexdigest()}
    patches.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),
        fromfile='original/tex/'+original.name,tofile='reworked/tex/'+original.name))
for relative,meta in SOURCE_MANIFEST.items():
    report['active_sources_unchanged'][relative]=hashlib.sha256((REPO/relative).read_bytes()).hexdigest()==meta['sha256']
relative_pilot=str(PILOT.relative_to(REPO))
report['pilot_tracked_paths']=subprocess.check_output(['git','ls-files','--',relative_pilot],cwd=REPO,text=True).splitlines()
report['pilot_ignore_rule']=subprocess.check_output(['git','check-ignore','-v',relative_pilot+'/reworked/tex/03_foundations.tex'],cwd=REPO,text=True).strip()
report['passed']=all(all(c['checks'].values()) for c in report['chapters'].values()) and all(report['active_sources_unchanged'].values()) and not report['pilot_tracked_paths']
(PILOT/'reports/preservation_checks.json').write_text(json.dumps(report,indent=2)+'\n')
(PILOT/'reports/source_changes.diff').write_text(''.join(patches))
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['passed'] else 1)
