import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)

from . import _loader
from ._registry import registry, Registry
from ._utils import manage_fs, parse, ParseResult
from ._errors import OpenerError, ParseError, Unsupported

open_fs = registry.open_fs
open = registry.open
