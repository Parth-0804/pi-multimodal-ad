#!/usr/bin/env python3
"""Conservative lexical diff for LaTeX. Flags changes; never certifies scientific meaning.
Compare two .tex files or two source directories. Exit 0: no detected differences;
1: review required; 2: input/check error. Standard library only.
"""
import argparse
from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
# Common LaTeX syntax. Exact spelling and counts are intentionally protected.
NUMBER = re.compile(r'[+−-]?(?:\d+(?:,\d{3})*(?:\.\d+)?|\.\d+)(?:[eE][+−-]?\d+)?')
UNIT = re.compile(NUMBER.pattern + r'(?:[ \t~]*)(?:\\%|%|percentage points?|dB|kHz|MHz|Hz|ms|µs|ns|s|mm|cm|kg|MPa|Pa|rpm|°C|\\degree)(?!\w)')
COMMAND = re.compile(r'(?<!\\)\\(?:[A-Za-z]*cite[A-Za-z]*|[A-Za-z]*ref|label)\*?(?![A-Za-z])', re.I)
ENV = r'equation|align|alignat|gather|multline|flalign|eqnarray|math|displaymath'
MATH = re.compile(r'\\begin\{(?P<env>(?:'+ENV+r')\*?)\}.*?\\end\{(?P=env)\}|(?<!\\)\$\$.*?(?<!\\)\$\$|(?<![\\$])\$(?!\$).*?(?<![\\$])\$(?!\$)|\\\(.*?\\\)|\\\[.*?\\\]', re.S)
BLOCK = re.compile(r'\\begin\{(?P<env>(?:table|tabular|tabularx|longtable|figure)\*?)\}.*?\\end\{(?P=env)\}', re.S)
UNUSUAL = re.compile(r'\\(?:verb\*?|catcode|csname|newcommand|renewcommand|def|input|include|bibliography|addbibresource)\b|\\begin\{(?:verbatim\*?|lstlisting|minted)\}')

def uncomment(text):
    # Ordinary TeX comments, not a catcode-aware parser. Preserve escaped percent signs.
    out = []
    for line in text.splitlines(keepends=True):
        end = len(line)
        for m in re.finditer('%', line):
            i = m.start(); j = i - 1
            while j >= 0 and line[j] == '\\': j -= 1
            if (i-j-1) % 2 == 0:
                end = i; break
        out.append(line[:end] + ('\n' if end < len(line) and line.endswith('\n') else ''))
    return ''.join(out)

def argument_end(text, start):
    """Find the end of a balanced [] or {} argument, allowing nested braces."""
    stack = [text[start]]; closing = {'[': ']', '{': '}'}; i = start + 1
    while i < len(text):
        c = text[i]
        if c == '\\': i += 2; continue
        if c == closing[stack[-1]]:
            stack.pop()
            if not stack: return i+1
        elif c == '{' or (c == '[' and stack[-1] == '['): stack.append(c)
        i += 1
    raise ValueError('Unclosed citation/reference/label argument near ' + repr(text[start:start+60]))

def commands(text):
    result=[]
    for m in COMMAND.finditer(text):
        end=m.end(); last=end
        # Preserve optional notes and all consecutive braced arguments (including multicites).
        while True:
            pos=end
            while pos<len(text) and text[pos].isspace(): pos+=1
            if pos==len(text) or text[pos] not in '[{': break
            end=argument_end(text,pos); last=end
        result.append(text[m.start():last])
    return result

def load_terms(extra):
    sheet=(ROOT/'00_THESIS_CANON.md').read_text(encoding='utf-8')
    m=re.search(r'<!-- BEGIN LOCKED TERMS -->\s*```text\s*\n(.*?)\n```\s*<!-- END LOCKED TERMS -->',sheet,re.S)
    if not m: raise ValueError('Locked-term block missing from 00_THESIS_CANON.md')
    return sorted(set([line.strip() for line in m[1].splitlines() if line.strip()]+extra))

def snapshot(text, terms):
    text=uncomment(text)
    return {
        'numeric tokens': Counter(NUMBER.findall(text)),
        'common number-unit tokens': Counter(UNIT.findall(text)),
        'citation/reference/label commands': Counter(commands(text)),
        'math blocks': Counter(m.group(0) for m in MATH.finditer(text)),
        'table/figure blocks': Counter(m.group(0) for m in BLOCK.finditer(text)),
        'locked terms': Counter({term:len(re.findall(r'(?<!\w)'+re.escape(term)+r'(?!\w)',text)) for term in terms}),
        'custom/input/verbatim syntax markers': Counter(m.group(0) for m in UNUSUAL.finditer(text)),
    }

def compare(name, original, candidate, terms):
    a,b=snapshot(original,terms),snapshot(candidate,terms)
    changed=False
    for kind in a:
        removed=a[kind]-b[kind]; added=b[kind]-a[kind]
        if removed or added:
            changed=True; print(f'REVIEW {name}: {kind}')
            for sign, counts in [('-', removed), ('+', added)]:
                for token,n in sorted(counts.items()):
                    # Keep the report readable; exact comparison uses the entire value.
                    short=repr(token[:220])+(' ...' if len(token)>220 else '')
                    print(f'  {sign} {n} × {short}')
    if a['custom/input/verbatim syntax markers'] or b['custom/input/verbatim syntax markers']:
        print(f'NOTE {name}: custom/input/verbatim syntax present; inspect manually and compile.')
    return changed

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original',type=Path); p.add_argument('candidate',type=Path)
    p.add_argument('--term',action='append',default=[],help='Additional exact source spelling to protect; repeat as needed.')
    args=p.parse_args()
    try:
        terms=load_terms(args.term)
        a,b=args.original,args.candidate
        if a.is_file() and b.is_file() and a.suffix.lower()==b.suffix.lower()=='.tex':
            pairs=[(a.name,a,b)]; changed=False
        elif a.is_dir() and b.is_dir():
            x={f.relative_to(a):f for f in a.rglob('*.tex')}; y={f.relative_to(b):f for f in b.rglob('*.tex')}
            if not x or not y: raise ValueError('Both directories must contain .tex files.')
            changed=bool(x.keys()^y.keys())
            for rel in sorted(x.keys()-y.keys()): print('REVIEW missing candidate file:',rel)
            for rel in sorted(y.keys()-x.keys()): print('REVIEW new candidate file:',rel)
            pairs=[(str(rel),x[rel],y[rel]) for rel in sorted(x.keys()&y.keys())]
        else: raise ValueError('Supply two existing .tex files or two source directories, not PDFs.')
        for name, before, after in pairs:
            changed=compare(name,before.read_text(encoding='utf-8'),after.read_text(encoding='utf-8'),terms) or changed
        print(f'Compared {len(pairs)} matching file(s). '+('Review required.' if changed else 'No protected-token differences detected.'))
        print('Manual semantic/primary-evidence review and source compilation remain required. Only common TeX syntax is checked.')
        return int(changed)
    except (OSError,ValueError,UnicodeError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr); return 2

if __name__=='__main__': sys.exit(main())
