"""Use the project's optional environment, never install into system Python."""
import importlib.util
import os
import sys
from common import ROOT


def local_runtime():
    if importlib.util.find_spec('fastembed') is not None:
        return
    python = ROOT / '.venv/bin/python'
    if python.exists() and str(ROOT / '.venv') != sys.prefix:
        os.execv(str(python), [str(python), *sys.argv])
