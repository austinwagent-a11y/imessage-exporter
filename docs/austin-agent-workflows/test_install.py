import tempfile,unittest
from pathlib import Path
from install import install
class InstallerTests(unittest.TestCase):
 def test_preview_apply_repeat(self):
  with tempfile.TemporaryDirectory() as t:
   r=Path(t);(r/'.git').mkdir();(r/'AGENTS.md').write_text('Keep these rules.\n')
   install(r);self.assertFalse((r/'.agents').exists())
   install(r,True);self.assertTrue((r/'.agents/skills/austin-drive-evidence/SKILL.md').exists())
   self.assertTrue((r/'AGENTS.md').read_text().startswith('Keep these rules.'))
   first=(r/'AGENTS.md').read_text();install(r,True);self.assertEqual(first,(r/'AGENTS.md').read_text())
 def test_collision_before_mutation(self):
  with tempfile.TemporaryDirectory() as t:
   r=Path(t);(r/'.git').mkdir();p=r/'.github/skills/austin-agent-handoff/SKILL.md';p.parent.mkdir(parents=True);p.write_text('custom')
   with self.assertRaises(FileExistsError):install(r,True)
   self.assertFalse((r/'.agents').exists());self.assertEqual(p.read_text(),'custom')
 def test_requires_checkout(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaises(ValueError):install(t,True)
if __name__=='__main__':unittest.main()
