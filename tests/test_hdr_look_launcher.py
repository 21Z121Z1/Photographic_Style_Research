"""Exercise the actual zsh launcher without requiring private Apple frameworks."""
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest


LAUNCHER = Path(__file__).resolve().parents[1] / "tools/hdr-look.command"


class HDRLookLauncherTests(unittest.TestCase):
    def test_argv_finder_paths_and_shell_literals_are_not_executed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake = root / "fake-cli"
            log = root / "argv.json"
            fake.write_text("#!/usr/bin/env python3\nimport json,os,sys\n"
                            "open(os.environ['HDR_TEST_LOG'],'w').write(json.dumps(sys.argv[1:]))\n"
                            "sys.exit(1 if '--injected-failure' in sys.argv else 0)\n")
            fake.chmod(0o755)
            env = dict(os.environ, XDREMUX_CLI=str(fake), HDR_TEST_LOG=str(log))
            paths = [root / '中文 a.HEIC', root / '$(touch INJECTED)`touch OTHER` "b".heic']
            for path in paths:
                path.touch()
            prefix = ['--lang', 'zh-CN', 'hdr-look', '--recursive']
            for supplied, stdin, expected in [
                ([str(p) for p in paths], None, prefix + [str(p) for p in paths]),
                ([], str(paths[0]) + '\n', prefix + ['--', str(paths[0])]),
                ([], ' '.join(shlex.quote(str(p)) for p in paths) + '\n',
                 prefix + ['--'] + [str(p) for p in paths]),
            ]:
                result = subprocess.run(['/bin/zsh', str(LAUNCHER), *supplied], input=stdin,
                                        text=True, env=env, cwd=root, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(log.read_text()), expected)
                self.assertFalse((root / 'INJECTED').exists())
                self.assertFalse((root / 'OTHER').exists())
            result = subprocess.run(['/bin/zsh', str(LAUNCHER), '--injected-failure'],
                                    env=env, capture_output=True)
            self.assertEqual(result.returncode, 1, 'partial batch failure must reach the caller')


if __name__ == '__main__':
    unittest.main()
