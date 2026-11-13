"""Check the actual installed public API; never load WinDLL on Linux."""
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
OUT = Path.cwd() / 'typing-contract-results'
OUT.mkdir(exist_ok=False)
distribution = importlib.metadata.distribution('pysetupdi')
package = Path(distribution.locate_file('pysetupdi')).resolve()
assert package.is_relative_to(Path(sys.prefix).resolve()), package
assert distribution.version == '2018.10.23+stablekite.1'
assert (package / 'py.typed').is_file()
inputs = OUT / 'inputs'
shutil.copytree(ROOT / 'tests/typing', inputs)
version = f'{sys.version_info.major}.{sys.version_info.minor}'
public = sorted(path for path in package.iterdir() if path.suffix == '.pyi' or (path.suffix == '.py' and not path.with_suffix('.pyi').exists()))
assert len(public) == 6
stages = []


def run(label, command):
    result = subprocess.run([str(x) for x in command], cwd=inputs, capture_output=True)
    (OUT / (label + '.stdout.log')).write_bytes(result.stdout)
    (OUT / (label + '.stderr.log')).write_bytes(result.stderr)
    stages.append({'label': label, 'command': [str(x) for x in command], 'exit_code': result.returncode})
    (OUT / 'STAGES.json').write_text(json.dumps(stages, indent=2) + '\n')
    return result


my = run('mypy-public', [sys.executable, '-I', '-m', 'mypy', '--strict', '--platform', 'win32', '--python-version', version, '--no-incremental', '--cache-dir', OUT / 'my-cache', package, inputs / 'positive.py'])
assert my.returncode == 0, my.stdout.decode(errors='replace')
config = inputs / 'pyright-public.json'
config.write_text(json.dumps({'include': [os.path.relpath(p, inputs) for p in public] + ['positive.py'], 'typeCheckingMode': 'strict', 'pythonVersion': version, 'pythonPlatform': 'Windows'}, indent=2) + '\n')
pr = run('pyright-public', [sys.executable, '-I', '-m', 'pyright', '--project', config, '--pythonpath', sys.executable, '--outputjson'])
parsed = json.loads(pr.stdout)
assert pr.returncode == 0 and parsed['summary']['filesAnalyzed'] == 7 and parsed['summary']['errorCount'] == 0, parsed
negative = inputs / 'negative.py'
expected = [n for n, line in enumerate(negative.read_text().splitlines(), 1) if '# E' in line]
assert len(expected) == 22
my = run('mypy-negative', [sys.executable, '-I', '-m', 'mypy', '--strict', '--platform', 'win32', '--python-version', version, '--no-incremental', '--cache-dir', OUT / 'negative-my-cache', negative])
actual = sorted(set(int(n) for n in re.findall(r'negative\.py:(\d+): error:', my.stdout.decode())))
assert my.returncode == 1 and actual == expected, (actual, expected, my.stdout.decode())
config = inputs / 'pyright-negative.json'
config.write_text(json.dumps({'include': ['negative.py'], 'typeCheckingMode': 'strict', 'pythonVersion': version, 'pythonPlatform': 'Windows'}, indent=2) + '\n')
pr = run('pyright-negative', [sys.executable, '-I', '-m', 'pyright', '--project', config, '--pythonpath', sys.executable, '--outputjson'])
parsed = json.loads(pr.stdout)
errors = [row for row in parsed['generalDiagnostics'] if row['severity'] == 'error']
actual = sorted(set(row['range']['start']['line'] + 1 for row in errors))
assert pr.returncode == 1 and actual == expected and all(row.get('rule') != 'reportUnusedVariable' for row in errors), parsed
if sys.platform == 'win32':
    assert run('real-native-positive', [sys.executable, '-I', inputs / 'positive.py']).returncode == 0
result = {'status': 'PASS_ACTUAL_INSTALLED_PUBLIC_INTERFACE', 'version': distribution.version, 'installed_package': str(package), 'python': sys.version, 'public_module_files': [p.name for p in public], 'negative_exact_lines_each_checker': expected, 'platform_scope': 'Native Windows; Windows-target static analysis on Linux. The ctypes implementation files covered by .pyi are tested natively, not claimed to pass raw implementation strict analysis.'}
(OUT / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
