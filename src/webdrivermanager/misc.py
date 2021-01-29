import logging
import subprocess
import sys

LOGGER = logging.getLogger(__name__)


def _inside_virtualenv():
    return hasattr(sys, "real_prefix") or hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix


def raise_runtime_error(msg):
    LOGGER.error(msg)
    raise RuntimeError(msg)


def versiontuple(v):
    return tuple(map(int, (v.split("."))))


def get_output(cmd, **kwargs):
    try:
        output = subprocess.check_output(cmd, **kwargs)
        return output.decode().strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as err:
        LOGGER.debug("Command failed: %s", err)
        return None
