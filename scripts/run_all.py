"""Rebuild notebooks, models, SQL exports, and the deployable dashboard."""
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
for script in ('run_notebooks.py', 'modeling.py', 'run_sql.py', 'build_dashboard.py'):
    subprocess.run([sys.executable, str(ROOT / 'scripts' / script)], cwd=ROOT, check=True)
