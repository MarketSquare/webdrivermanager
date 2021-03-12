import logging
import subprocess
import sys

LOGGER = logging.getLogger(__name__)
LOG_LEVELS = {
    "notset": logging.NOTSET,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def _inside_virtualenv():
    return hasattr(sys, "real_prefix") or hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix


def raise_runtime_error(msg):
    LOGGER.error(msg)
    raise RuntimeError(msg)


def versiontuple(v):
    return tuple(map(int, (v.split("."))))


def get_output(cmd, **kwargs):
    try:
        output = subprocess.check_output(cmd, **kwargs, stderr=subprocess.STDOUT)
        return output.decode().strip()
    except subprocess.CalledProcessError as err:
        error = err.output.decode().strip()
        LOGGER.debug("Command failed:\n%s", error)
        return None
    except FileNotFoundError as err:
        LOGGER.debug("Command not found: %s", err)
        return None
