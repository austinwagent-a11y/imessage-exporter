from pathlib import Path
import json,re
root=Path(__file__).resolve().parent
count=0
for p in sorted((root/'skills').glob('*/SKILL.md')):
    s=p.read_text(); name=p.parent.name
    assert s.startswith('---\n') and f'name: {name}\n' in s
    desc=re.search(r'description: "(.*)"',s).group(1)
    assert len(desc)<=1024 and 'Use when' in desc and 'Do NOT use' in desc
    assert len(s.splitlines())<500
    for section in ['## Map','## Operating contract','## Method','## Workflow','## Output','## Verification seam','## Do not rationalize']: assert section in s,(name,section)
    assert not re.search(r'(sk-[A-Za-z0-9]{20,}|/home/|/Users/)',s)
    e=json.loads((p.parent/'evals.json').read_text())
    assert len(e['positive'])>=2 and len(e['negative'])>=2 and len(e['behavior'])>=2
    assert all(x.strip() for x in e['positive']+e['negative'])
    count+=len(e['positive'])+len(e['negative'])+len(e['behavior'])
assert len(list((root/'skills').glob('*/SKILL.md')))==10
assert (root/'scripts/rezen_organizer.py').is_file()
print(f'PASS: 10 skills; {count} authored routing/behavior fixtures; structural checks. Live agent evals not run.')
