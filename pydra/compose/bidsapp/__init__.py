"""
This is a basic doctest demonstrating that the package and pydra can both be successfully
imported.

>>> import pydra.compose.bidsapp
"""

try:
    from ._version import __version__
except ImportError:
    raise RuntimeError(
        "Pydra package 'pydra-compose-bidsapp' has not been installed, please use "
        "`pip install -e <path-to-repo>` to install development version"
    )

from .builder import define
from .fields import arg, out
from .task import BidsAppTask as Task, BidsAppOutputs as Outputs

__all__ = ["arg", "out", "define", "Task", "Outputs", "__version__"]
