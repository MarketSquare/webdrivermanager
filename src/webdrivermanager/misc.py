import logging
import sys

LOGGER = logging.getLogger(__name__)


def _inside_virtualenv():
    return hasattr(sys, 'real_prefix') or hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix


def raise_runtime_error(msg):
    LOGGER.error(msg)
    raise RuntimeError(msg)


def versiontuple(v):
    return tuple(map(int, (v.split("."))))
