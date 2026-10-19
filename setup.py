"""Build-time asset inclusion; this module is never imported by the auditor."""
from pathlib import Path
import shutil
from setuptools import setup
from setuptools.command.build_py import build_py


class BuildPy(build_py):
    def run(self):
        super().run()
        root = Path(__file__).parent
        target = Path(self.build_lib)/'cursorrace'
        shutil.copy2(root/'README.md', target/'README.md')
        shutil.copytree(root/'schemas', target/'schemas', dirs_exist_ok=True)


setup(cmdclass={'build_py': BuildPy})
