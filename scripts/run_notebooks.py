"""Execute the existing notebook pipeline in order from any working directory."""
from pathlib import Path
import os
import sys

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

ROOT = Path(__file__).resolve().parents[1]


def main(names=None):
    # Keep kernel runtime files inside the project and plots noninteractive.
    runtime = ROOT / '.work' / 'jupyter'
    runtime.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('JUPYTER_RUNTIME_DIR', str(runtime))
    os.environ.setdefault('IPYTHONDIR', str(ROOT / '.work' / 'ipython'))
    os.environ.setdefault('MPLBACKEND', 'module://matplotlib_inline.backend_inline')
    for directory in ('data/processed', 'reports/charts'):
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    if not (ROOT / 'data/raw/vehicles.xlsx').is_file():
        raise FileNotFoundError('Missing data/raw/vehicles.xlsx; see data/README.md.')
    paths = sorted((ROOT / 'notebooks').glob('[0-9][0-9]_*.ipynb'))
    if names:
        unknown = set(names) - {path.stem for path in paths}
        if unknown:
            raise ValueError(f'Unknown notebooks: {sorted(unknown)}')
        paths = [path for path in paths if path.stem in names]
    for path in paths:
        print(f'Executing {path.name}', flush=True)
        notebook = nbformat.read(path, as_version=4)
        # Use this interpreter rather than a potentially unrelated global kernel.
        notebook.metadata.kernelspec = {
            'display_name': 'Python 3', 'language': 'python', 'name': 'python3'
        }
        manager = KernelManager(kernel_name='python3')
        manager.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
        client = NotebookClient(
            notebook, timeout=600, kernel_name='python3', km=manager,
            resources={'metadata': {'path': str(ROOT / 'notebooks')}},
        )
        try:
            client.execute()
        finally:
            if manager.has_kernel:
                manager.shutdown_kernel(now=True)
        nbformat.write(notebook, path)
        print(f'Saved {path.name}', flush=True)


if __name__ == '__main__':
    main(sys.argv[1:])
