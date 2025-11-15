from pathlib import Path

from dicer import functions as fn
from dicer import io_ops as io

DCR_PY_HOME: Path = Path(__file__).parent

# Find shared dir
_path_var = DCR_PY_HOME
while not _path_var.joinpath('commons').exists():
    if _path_var == Path().home():
        raise LookupError("Unable to find data directory commons")
    _path_var = _path_var.parent

DCR_DATA_SHARED: Path = _path_var
