#!/usr/bin/env python3
"""Export pilot chapter copies as readable text without invoking TeX or a PDF tool."""
from pathlib import Path
import collections
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/text_export'))
from pylatexenc.latex2text import LatexNodes2Text

DECODER = LatexNodes2Text(math_mode='text', strict_latex_spaces=False)
STATS = collections.Counter()
FALLBACKS = set()
UNRESOLVED = set()


def group(text, pos, opening='{', closing='}'):
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos >= len(text) or text[pos] != opening:
        raise ValueError(f'Expected {opening} at {pos}: {text[pos:pos+60]!r}')
    start = pos + 1
    depth = 1
    pos += 1
    while pos < len(text):
        if text[pos] == '\\':
            pos += 2
            continue
        if text[pos] == opening:
            depth += 1
        elif text[pos] == closing:
            depth -= 1
            if depth == 0:
                return text[start:pos], pos + 1
        pos += 1
    raise ValueError(f'Unclosed group at {start}')


def calls(text, name, count):
    for match in re.finditer(r'\\' + re.escape(name) + r'(?![A-Za-z@])', text):
        pos = match.end()
        args = []
        try:
            for _ in range(count):
                value, pos = group(text, pos)
                args.append(value)
        except ValueError:
            continue
        yield match.start(), pos, args


def replace_calls(text, name, count, callback):
    for start, end, args in reversed(list(calls(text, name, count))):
        text = text[:start] + callback(args) + text[end:]
    return text


def decode(text):
    return DECODER.latex_to_text(text).replace('\u00a0', ' ').strip()


preview = (ROOT / 'support/chapter-preview.tex').read_text()
citations = {tuple(a[:4]): a[4] for _, _, a in calls(preview, 'PreviewCitation', 5)}
labels = {a[0]: (a[1], a[2]) for _, _, a in calls(preview, 'PreviewLabel', 3)}
aux = ROOT / 'support/last_compiled_main.aux'
if aux.exists():
    for _, _, a in calls(aux.read_text(), 'newlabel', 2):
        try:
            number, end = group(a[1], 0)
            page, end = group(a[1], end)
            labels[a[0]] = (number, page)
        except ValueError:
            pass

# Bibliographic fallback is only used when the exact preview cache lacks a citation.
bib = {}
for path in sorted((ROOT / 'support').glob('references*.bib')):
    text = path.read_text()
    for match in re.finditer(r'@\w+\s*\{([^,]+),', text):
        try:
            body, end = group(text, text.index('{', match.start()))
        except ValueError:
            continue
        fields = {}
        for field in re.finditer(r'\b(author|editor|year|date)\s*=\s*', body):
            if body[field.end():].startswith('{'):
                value, _ = group(body, field.end())
            else:
                value = re.split(r'[,\n]', body[field.end():], 1)[0].strip('" ')
            fields[field[1]] = value
        bib[match[1].strip()] = fields


def single_citation(key):
    for name in ('parencite', 'citep'):
        exact = citations.get((name, '', '', key))
        if exact:
            return exact.strip().strip('()')
    fields = bib.get(key)
    if not fields:
        UNRESOLVED.add('citation:' + key)
        return '[citation: ' + key + ']'
    authors = re.split(r'\s+and\s+', fields.get('author', fields.get('editor', key)))
    surnames = [a.strip('{} ').split(',', 1)[0] if ',' in a else a.strip('{} ').split()[-1] for a in authors]
    author = surnames[0] + (' et al.' if len(authors) > 2 else (r' \& ' + surnames[1] if len(authors) == 2 else ''))
    FALLBACKS.add(key)
    return author + ', ' + fields.get('year', fields.get('date', 'n.d.')[:4])


def citation(name, options, keys):
    pre, post = ('', options[0]) if len(options) == 1 else ((options + ['', ''])[:2])
    exact = citations.get((name, pre, post, keys))
    if not exact and name == 'textcite':
        exact = citations.get(('citet', pre, post, keys))
    if exact:
        STATS['exact_cached_citations'] += 1
        return exact
    STATS['assembled_citations'] += 1
    items = [single_citation(k.strip()) for k in keys.split(',')]
    if name in ('textcite', 'citet') and len(items) == 1 and ', ' in items[0]:
        author, year = items[0].rsplit(', ', 1)
        return pre + author + ' (' + year + (', ' + post if post else '') + ')'
    return '(' + (pre + ' ' if pre else '') + '; '.join(items) + (', ' + post if post else '') + ')'


def convert_citations(text):
    pattern = re.compile(r'\\(parencites|parencite|textcite|citep|citet)\b')
    matches = list(pattern.finditer(text))
    for match in reversed(matches):
        pos = match.end()
        chunks = []
        while True:
            options = []
            while True:
                pos = pos + len(text[pos:]) - len(text[pos:].lstrip())
                if pos < len(text) and text[pos] == '[':
                    arg, pos = group(text, pos, '[', ']')
                    options.append(arg)
                else:
                    break
            if pos >= len(text) or text[pos] != '{':
                break
            keys, pos = group(text, pos)
            chunks.append(citation('parencite' if match[1] == 'parencites' else match[1], options, keys))
            if match[1] != 'parencites':
                break
            probe = pos + len(text[pos:]) - len(text[pos:].lstrip())
            if probe >= len(text) or text[probe] not in '[{':
                break
        if not chunks:
            raise ValueError('Cannot parse citation near ' + text[match.start():match.start()+100])
        replacement = ('(' + '; '.join(x.strip('()') for x in chunks) + ')') if len(chunks) > 1 else chunks[0]
        text = text[:match.start()] + replacement + text[pos:]
    return text


def reference(a, page=False):
    if a[0] not in labels:
        UNRESOLVED.add('reference:' + a[0])
        return '[' + a[0] + ']'
    return labels[a[0]][int(page)]


def expanded_review():
    source = (ROOT / 'support/figures/review_figure_table.tex').read_text()
    source = re.sub(r'(?<!\\)%[^\n]*', '', source)
    rows = re.findall(r'#1\{([^}]+)\}\{([^}]+)\}\{(\d+)\}\{(\d+)\}\{(\d+)\}\{(\d+)\}', source)
    assert len(rows) == 7 and all(sum(map(int, r[2:])) == 94 for r in rows)
    _, _, figure_args = next(x for x in calls(source, 'newcommand', 2) if x[2][0] == r'\ReviewDepthFigure')
    fig = figure_args[1]
    caption = next(calls(fig, 'caption', 1))[2][0]
    note = next(calls(fig, 'ReviewNote', 1))[2][0]
    body = '\n\nFigure ' + reference(['fig:review-depth']) + '. ' + caption + '\n\n'
    body += 'Topic | Direct test recorded | Used or discussed only | No treatment recorded | Unclear from appraisal\n\n'
    body += '\n\n'.join(' | '.join(r[1:]) for r in rows)
    body += '\n\nNote. ' + note + '\n\n'
    findings = {a[0]: (a[1], a[2]) for _, _, a in calls(source, 'ReviewText', 3)}
    _, _, table_args = next(x for x in calls(source, 'newcommand', 2) if x[2][0] == r'\ReviewFollowupTable')
    title = next(calls(table_args[1], 'caption', 1))[2][0]
    table = '\n\nTable ' + reference(['tab:literature-synthesis']) + '. ' + title + '\n\n'
    for key, topic, *_ in rows + [('credibility', 'How credible is the estimate?')]:
        finding, question = findings[key]
        table += topic + '\n\nPublished finding and its limit: ' + finding + '\n\nFollow-up question: ' + question + '\n\n'
    return body, table


review_figure, review_table = expanded_review()


def export(tex):
    # Drop comments, review-only evidence annotations, and layout commands.
    text = re.sub(r'(?<!\\)%[^\n]*', '', tex)
    text = text.replace(r'\ReviewDepthFigure', review_figure).replace(r'\ReviewFollowupTable', review_table)
    text = re.sub(r'\\Review(?:WorkCount|AppraisalN)\b(?:\{\})?', '94', text)
    text = replace_calls(text, 'ReviewCite', 2, lambda a: r'\parencite{' + a[0] + '}')
    text = convert_citations(text)
    for name in ('ref', 'pageref'):
        text = replace_calls(text, name, 1, lambda a, name=name: reference(a, name == 'pageref'))
    text = replace_calls(text, 'ev', 2, lambda a: '')
    text = replace_calls(text, 'EvidenceRef', 2, lambda a: '')
    text = replace_calls(text, 'label', 1, lambda a: '')
    text = replace_calls(text, 'texttt', 1, lambda a: a[0])
    text = replace_calls(text, 'setlength', 2, lambda a: '')
    text = replace_calls(text, 'renewcommand', 2, lambda a: '')
    text = replace_calls(text, 'addcontentsline', 3, lambda a: '')
    # Use headings as text, and explicit sentence boundaries for display notes.
    text = re.sub(r'\\(chapter|section|subsection|subsubsection)\*', r'\\\1', text)
    for name in ('chapter', 'section', 'subsection', 'subsubsection'):
        text = replace_calls(text, name, 1, lambda a: '\n\n' + a[0] + '\n\n')
    text = replace_calls(text, 'displaynote', 1, lambda a: '\n\nNote. ' + a[0] + '\n\n')
    text = replace_calls(text, 'caption', 1, lambda a: '\n\n' + a[0] + '\n\n')
    # Graphics have no editable prose here: retain their source captions and notes.
    text = re.sub(r'\\includegraphics(?:\[[^\]]*\])?\{[^}]*\}', '', text)
    # Remove tabular declarations while preserving cells and row boundaries.
    for match in reversed(list(re.finditer(r'\\begin\{tabularx\}', text))):
        _, pos = group(text, match.end())
        _, pos = group(text, pos)
        text = text[:match.start()] + '\n\n' + text[pos:]
    text = re.sub(r'\\end\{tabularx\}', '\n\n', text)
    text = re.sub(r'\\(?:toprule|midrule|bottomrule)\b', '\n\n', text)
    text = re.sub(r'(?<!\\)&', ' | ', text)
    text = re.sub(r'\\\\(?:\[[^\]]*\])?', '\n\n', text)
    # Preserve SQ numbering rather than losing it as generic list bullets.
    def numbered(match):
        n = 0
        def item(_):
            nonlocal n
            n += 1
            return '\n\nSQ' + str(n) + '. '
        return re.sub(r'\\item\b', item, match[1])
    text = re.sub(r'\\begin\{enumerate\}\[[^\]]*\](.*?)\\end\{enumerate\}', numbered, text, flags=re.S)
    # Parentheses around numerator/denominator avoid ambiguous plain-text division.
    text = replace_calls(text, 'frac', 2, lambda a: '(' + a[0] + ')/(' + a[1] + ')')
    text = re.sub(r'(?<!\\)\\(exp|alpha)\b', r' \\\1', text)
    text = decode(text)
    text = re.sub(r'∑_([A-Za-z])', r'∑_(\1) ', text)
    # Evidence-only inline labels have no content after dropping trace references.
    text = re.sub(r'(?:Implementation (?:and decision )?|Provenance )records?:[\s,.;]*', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    # Paragraphs are reflowed into one line for copy/paste into checking tools.
    paragraphs = []
    for paragraph in re.split(r'\n\s*\n', text):
        paragraph = re.sub(r'\s+', ' ', paragraph).strip()
        if paragraph and re.search(r'[\wα-ωΑ-Ω]', paragraph):
            paragraphs.append(paragraph)
    return '\n\n'.join(paragraphs).strip() + '\n'


def main():
    report = {'converter': 'pylatexenc 2.10 with project-specific preprocessing', 'compilation': False, 'files': [], 'combined_files': []}
    checks = {}
    for variant in ('original', 'reworked'):
        out = ROOT / variant / 'txt'
        out.mkdir(parents=True, exist_ok=True)
        chapter_results = []
        for source in sorted((ROOT / variant / 'tex').glob('*.tex')):
            result = export(source.read_text())
            target = out / (source.stem + '.txt')
            target.write_text(result)
            chapter_results.append((source.stem, result))
            report['files'].append({'source': str(source.relative_to(ROOT)), 'output': str(target.relative_to(ROOT)), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'output_sha256': hashlib.sha256(result.encode()).hexdigest(), 'words': len(result.split())})
        combined = '\n\n\n'.join(text.rstrip() for _, text in chapter_results) + '\n'
        combined_path = out / 'Chapters_01_04.txt'
        combined_path.write_text(combined)
        report['combined_files'].append({'output': str(combined_path.relative_to(ROOT)), 'chapters_in_order': [stem for stem, _ in chapter_results], 'sha256': hashlib.sha256(combined.encode()).hexdigest(), 'words': len(combined.split())})
        texts = dict(chapter_results)
        ch2 = texts['02_literature_review']
        checks[variant] = {
            'chapter_files': len(texts),
            'combined_files': 1,
            'no_unprocessed_latex_commands': all(not re.search(r'\\[A-Za-z]+', t) for t in texts.values()),
            'review_count_rows': sum(row in ch2 for row in ['Adding an input | 46 | 15 | 30 | 3', 'Choice of fusion rule | 37 | 28 | 29 | 0', 'Training strategy | 28 | 60 | 4 | 2', 'Corrupted inputs at test | 21 | 22 | 50 | 1', 'Input representation | 15 | 67 | 7 | 5', 'Missing inputs at inference | 11 | 15 | 68 | 0', 'Transfer across settings | 11 | 30 | 52 | 1']),
            'followup_questions': ch2.count('Follow-up question:'),
            'figure_before_gap': ch2.index('Figure 2.2. Depth') < ch2.index('Unresolved Questions and Research Gap'),
            'closing_table_after_summary': ch2.index('Final Summary of the Literature Review') < ch2.index('Table 2.1.'),
            'sq_labels_retained': all('SQ' + str(i) + '.' in texts['01_introduction'] for i in range(1, 5)),
            'chapter3_math_and_model_id_retained': all(x in texts['03_foundations'] for x in ('p_F2=sigmoid', 'w_m(u,a)=', 'p_A=sigmoid', 'PekingU/rtdetr_r18vd')),
            'chapter4_code_identifiers_retained': all(x in texts['04_methodology'] for x in ('average_precision_score', 'FULL20', 'FULL100')),
            'combined_exact_concatenation': combined_path.read_text() == '\n\n\n'.join((out / (stem + '.txt')).read_text().rstrip() for stem, _ in chapter_results) + '\n',
            'combined_order': [stem for stem, _ in chapter_results],
        }
    (ROOT / 'reports/text_export_checks.json').write_text(json.dumps(checks, indent=2) + '\n')
    report.update({'citation_processing': dict(STATS), 'bibliography_metadata_fallback_keys': sorted(FALLBACKS), 'unresolved': sorted(UNRESOLVED), 'export_notes': [
        'Both versions use exactly the same source-to-text transformation; no PDF was read or generated.',
        'Headings, prose, captions, display notes, source table cells and equations are retained; diagram graphics are not OCR-transcribed.',
        'ReviewDepthFigure is represented by its caption, seven exact count rows, four category names and note; ReviewFollowupTable retains all eight topic findings and follow-up questions.',
        'LaTeX comments, formatting controls, graphic file paths and evidence trace identifiers/annotation blocks are omitted. Scientific prose, model identifiers and appendix references are retained.',
        'References use the existing last-compiled auxiliary file (preview-cache fallback). Numbering is not newly compiled.',
        'Citations use exact cached author-year forms where available, otherwise assemble cached single-work forms, then fall back to author/year fields in the copied bibliography. No bibliography contents were independently verified.',
        'Equations are readable linear Unicode text, not publication typesetting; numerator and denominator groups are parenthesised.',
    ]})
    (ROOT / 'reports/text_export.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'files': len(report['files']), 'combined_files': len(report['combined_files']), 'unresolved': report['unresolved'], 'bibliography_fallback_keys': report['bibliography_metadata_fallback_keys'], 'citation_processing': report['citation_processing']}, ensure_ascii=False))
    if UNRESOLVED:
        raise SystemExit('Unresolved reference/citation: inspect reports/text_export.json')


if __name__ == '__main__':
    main()
