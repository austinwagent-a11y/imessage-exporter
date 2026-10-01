"""Install portable skills into one explicitly selected Git checkout. Preview by default."""
import argparse, shutil, re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MARKER='<!-- austin-shared-skills-v1 -->'
def plan(repo):
    repo=Path(repo).resolve()
    if not (repo/'.git').exists(): raise ValueError('Target must be a Git checkout')
    operations=[]
    for base in ['.agents/skills','.github/skills']:
        for src in sorted((ROOT/'skills').rglob('*')):
            if src.is_file(): operations.append((src,repo/base/src.relative_to(ROOT/'skills')))
    operations.append((ROOT/'scripts/rezen_organizer.py',repo/'scripts/austin-skills/rezen_organizer.py'))
    for src in sorted((ROOT/'integrations').glob('*')):
        if src.is_file(): operations.append((src,repo/'integrations/austin-skills'/src.name))
    # Full preflight before writing. Never replace different existing content.
    for src,dst in operations:
        if dst.exists() and (not dst.is_file() or dst.read_bytes()!=src.read_bytes()):
            raise FileExistsError(f'Existing content differs: {dst}')
    return repo,operations

def install(repo,apply=False):
    repo,ops=plan(repo)
    routes='\n'.join(f'- {p.parent.name}: {p.relative_to(ROOT)}' for p in sorted((ROOT/'skills').glob('*/SKILL.md')))
    docs=[]
    for target,base in [('AGENTS.md','.agents/skills'),('.github/copilot-instructions.md','.github/skills')]:
        p=repo/target
        old=p.read_text() if p.exists() else ''
        block=f'\n\n{MARKER}\n## Austin shared skills\nSelect the narrowest relevant skill below and read it before acting. Current user instructions, platform rules, and applicable repository instructions govern. No skill grants external-action permissions. Preserve evidence and distinguish drafted, tested, installed, and deployed work. Resolve the reZEN helper at scripts/austin-skills/rezen_organizer.py and integration references at integrations/austin-skills/.\n'+routes.replace('skills/',base+'/')+'\n<!-- /austin-shared-skills-v1 -->\n'
        if MARKER in old:
            updated=re.sub(r'<!-- austin-shared-skills-v1 -->.*?<!-- /austin-shared-skills-v1 -->', lambda _: block.strip(), old, flags=re.S)
            if updated != old: docs.append((p,updated))
        else: docs.append((p,old+block))
    print(f'{"APPLY" if apply else "PREVIEW"}: {len(ops)} skill/helper files, {len(docs)} instruction updates in {repo}')
    if apply:
        for src,dst in ops:
            if not dst.exists():
                dst.parent.mkdir(parents=True,exist_ok=True)
                with dst.open('xb') as f: f.write(src.read_bytes())
        for p,content in docs:
            p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content)
    return ops
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('repo'); p.add_argument('--apply',action='store_true'); a=p.parse_args(); install(a.repo,a.apply)
