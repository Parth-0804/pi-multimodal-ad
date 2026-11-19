"""Scoped local-only result commits; never touch unrelated staged work or branches."""
from collections import Counter
import subprocess
from .common import PROJECT,REPO,config,read,sha,utc,write

INITIAL='94f61529116ebdc966bcf87704a93e4d02fa5e89'


def capture(c=None,commit=False):
    c=c or config()
    def git(*args,check=True):return subprocess.run(['git',*args],cwd=REPO,text=True,capture_output=True,check=check)
    note='No automatic commit requested.'
    if commit:
        provenance=read(PROJECT/'logs'/c['run_id']/'EXECUTION_PROVENANCE.json')
        branch=git('branch','--show-current').stdout.strip()
        if branch!=provenance['git_branch']:note='Skipped result commit: branch changed externally; preserved.'
        elif git('diff','--cached','--quiet',check=False).returncode!=0:note='Skipped result commit: index contains staged work; preserved.'
        else:
            root=PROJECT/'10_final_research_reports';publication=read(root/'LATEST_PUBLICATION.json')
            snapshot=REPO/publication['snapshot'];candidates=[]
            expected={**{str((root/name).relative_to(REPO)):identity for name,identity in publication['reports'].items()},
                      **{str((snapshot/name).relative_to(REPO)):identity for name,identity in publication['reports'].items()},
                      **publication['auxiliary'],
                      'VIFAILBACK/RESEARCH_COMPLETION_STATUS.md':publication['completion_status_sha256']}
            for relative,identity in expected.items():
                p=REPO/relative
                assert p.resolve().is_relative_to(PROJECT.resolve()) and not p.is_symlink()
                assert sha(p)==identity,'EXTERNALLY_CHANGED_REPORT_PRESERVED_NO_COMMIT'
                if p.stat().st_size<=1024**2:candidates.append(relative)
            candidates.append('VIFAILBACK/10_final_research_reports/LATEST_PUBLICATION.json')
            if candidates:
                git('add','-f','--',*candidates)
                git('diff','--cached','--check')
                if git('diff','--cached','--quiet',check=False).returncode==1:
                    git('commit','-m','docs(vifailback): consolidate independently checked experimental evidence')
                    note='Created scoped local evidence commit; nothing pushed.'
                else:note='No new scoped evidence content to commit.'
    status=git('status','--porcelain=v1','-z','--untracked-files=all').stdout.split('\0')
    untracked=[s[3:] for s in status if s.startswith('?? ')];tracked=[s for s in status if s and not s.startswith('?? ')]
    commits=git('log','--format=%H%x09%s',INITIAL+'..HEAD').stdout.splitlines()
    result={'utc':utc(),'initial_HEAD':INITIAL,'current_HEAD':git('rev-parse','HEAD').stdout.strip(),
            'commits':[{'hash':s.split('\t',1)[0],'message':s.split('\t',1)[1]} for s in commits],
            'tracked_changes_remaining':tracked,'untracked_count':len(untracked),
            'untracked_by_root':dict(Counter(p.split('/')[0] for p in untracked)),
            'preserved_unrelated_initial_changes':['README.md','REPO_MAP.md','docs/thesis_research_direction/THESIS_EVIDENCE_GAPS.md'],
            'push_performed':False,'PR_created':False,'local_result_commit_note':note,
            'bulk_artifacts':'Raw videos, feature banks, all checkpoints and large generated galleries remain ignored; preserved on disk.'}
    write(PROJECT/'10_final_research_reports/researcher_handoff/GIT_HANDOFF.json',result)
    return result
