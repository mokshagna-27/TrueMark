import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
for path in (root, root / "backend"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from main import app  # noqa: E402,F401
