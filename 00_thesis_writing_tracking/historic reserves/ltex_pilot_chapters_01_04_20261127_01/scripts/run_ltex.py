#!/usr/bin/env python3
"""Run the bundled local LTeX+ CLI and preserve its unfiltered output.

Raw CLI diagnostics are the authority. JSON is a lossless structured rendering
of each CLI record (including the original record); suggestions are those the
CLI prints, not an asserted exhaustive LSP replacement list.
"""
import argparse,datetime,hashlib,json,re,subprocess,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CLI=ROOT/'tools/ltex-ls-plus-19.0.0/bin/ltex-cli-plus'
SERVER=CLI.with_name('ltex-ls-plus')
CONFIG=ROOT/'tools/ltex-client-configuration.json'
HEADER=re.compile(r'^(.*\.tex):(\d+):(\d+): (\w+): (.*) \[([^\]]+)\]$')

def parse(text):
    records=[]
    for line in text.splitlines():
        match=HEADER.match(line)
        if match:
            filename,row,col,severity,message,rule=match.groups()
            records.append({'filename':str(Path(filename).relative_to(ROOT)),'line':int(row),'column':int(col),'severity':severity,'rule_id':rule,'message':message,'source_line':'','suggestions':[],'raw_lines':[line]})
        elif records:
            r=records[-1]
            r['raw_lines'].append(line)
            if not r['source_line']:r['source_line']=line
            elif line.lstrip().startswith('Use '):r['suggestions'].append(line.lstrip()[4:])
    return records

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('variant',choices=['original','reworked'])
    args=parser.parse_args()
    prefix=ROOT/'reports'/('ltex_'+args.variant)
    if prefix.with_suffix('.json').exists():raise SystemExit('Refusing to overwrite completed diagnostics')
    if args.variant=='reworked':
        baseline=json.loads((ROOT/'reports/ltex_original.json').read_text())
        if hashlib.sha256(CONFIG.read_bytes()).hexdigest()!=baseline['configuration_sha256']:
            raise SystemExit('Configuration differs from frozen baseline')
    files=sorted((ROOT/args.variant/'tex').glob('*.tex'))
    version=subprocess.run([str(SERVER),'--version'],capture_output=True,text=True,check=True).stdout
    command=[str(CLI),'--verbose','--client-configuration='+str(CONFIG),*[str(f) for f in files]]
    before={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    started=datetime.datetime.now().astimezone().isoformat()
    t=time.monotonic()
    with prefix.with_suffix('.raw.txt').open('w') as out,prefix.with_suffix('.stderr.txt').open('w') as err:
        run=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err)
    text=prefix.with_suffix('.raw.txt').read_text()
    diagnostics=parse(text)
    after={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    if before!=after:raise SystemExit('Input files changed during run')
    payload={'tool':'LTeX+ CLI','versions':json.loads(version),'language':'en-GB','network_checker':False,'configuration_sha256':hashlib.sha256(CONFIG.read_bytes()).hexdigest(),'configuration':str(CONFIG.relative_to(ROOT)),'input_sha256':before,'command':command,'started':started,'finished':datetime.datetime.now().astimezone().isoformat(),'elapsed_seconds':round(time.monotonic()-t,3),'exit_code':run.returncode,'note':'Exit code 3 means diagnostics found; 0 means none. JSON is parsed from preserved raw CLI output; suggestions lists contain only replacements printed by the CLI. No automatic fixes or diagnostic filtering.','diagnostics':diagnostics}
    prefix.with_suffix('.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    counts={f.name:sum(Path(d['filename']).name==f.name for d in diagnostics) for f in files}
    print(json.dumps({'variant':args.variant,'exit_code':run.returncode,'counts':counts,'reports':str(prefix)},indent=2),flush=True)
    if run.returncode not in (0,3):return run.returncode
    if not all(f.name in prefix.with_suffix('.stderr.txt').read_text() for f in files):raise SystemExit('Missing per-file check log')
    return 0
if __name__=='__main__':sys.exit(main())
