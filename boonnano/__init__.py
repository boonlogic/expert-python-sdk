from .management import NanoHandle
from .management import BoonException
from .management import open_nano
from .management import close_nano
from .management import nano_list
from .management import save_nano
from .management import restore_nano
from .management import json_msg

from .configure import get_config
from .configure import generate_config
from .configure import configure_nano
from .configure import autotune_config

from .cluster import load_data
from .cluster import load_file
from .cluster import run_nano

from .results import get_version
from .results import get_buffer_status
from .results import get_nano_status
from .results import get_nano_results

setattr(NanoHandle, "open_nano", open_nano)
setattr(NanoHandle, "close_nano", close_nano)
setattr(NanoHandle, "nano_list", nano_list)
setattr(NanoHandle, "save_nano", save_nano)
setattr(NanoHandle, "restore_nano", restore_nano)

setattr(NanoHandle, "get_config", get_config)
setattr(NanoHandle, "configure_nano", configure_nano)
setattr(NanoHandle, "generate_config", generate_config)
setattr(NanoHandle, "autotune_config", autotune_config)

setattr(NanoHandle, "load_data", load_data)
setattr(NanoHandle, "load_file", load_file)
setattr(NanoHandle, "run_nano", run_nano)

setattr(NanoHandle, "get_version", get_version)
setattr(NanoHandle, "get_buffer_status", get_buffer_status)
setattr(NanoHandle, "get_nano_status", get_nano_status)
setattr(NanoHandle, "get_nano_results", get_nano_results)
