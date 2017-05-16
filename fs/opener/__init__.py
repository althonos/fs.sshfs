import pkgutil
import importlib

__path__ = pkgutil.extend_path(__path__, __name__)
print(__path__)

from ._registry import registry
from ._utils import manage_fs, parse

for importer, modname, ispkg in pkgutil.iter_modules(__path__):
    print("Found submodule", modname, "(is a package:", ispkg, ")")
    importlib.import_module('.'.join([__name__, modname]), package=__name__)

open_fs = registry.open_fs
open = registry.open
