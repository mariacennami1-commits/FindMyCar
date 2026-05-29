import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_ERROR_LOG = os.path.join(
    os.environ.get("EXTERNAL_STORAGE", "/sdcard"),
    "findmycar_error.txt",
)

def _log_error(exc_info):
    try:
        with open(_ERROR_LOG, "w") as f:
            traceback.print_exception(*exc_info, file=f)
    except Exception:
        pass

if __name__ == "__main__":
    try:
        from findmycar.app import FindMyCarApp
        FindMyCarApp().run()
    except Exception:
        _log_error(sys.exc_info())
        raise
