from __future__ import annotations
import sys
from pathlib import Path
from branding_config import APP_VERSION, WINDOW_TITLE
import License
def _ensure_project_root() -> None:
    # Chen thu muc goc du an vao sys.path de import hoat dong chinh xac
    root = Path(__file__).resolve().parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
def main() -> None:
    _ensure_project_root()
    print(f'[RUNNER] Start launcher for {WINDOW_TITLE} - {APP_VERSION}')
    License.main()
if __name__ == '__main__':
    main()