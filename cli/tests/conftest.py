# ABOUTME: Test configuration for running Chug tests from the source tree.
# ABOUTME: Adds cli/src to sys.path so tests import the local package.

import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
