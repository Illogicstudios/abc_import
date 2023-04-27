import importlib
from common import utils

utils.unload_packages(silent=True, package="abc_import")
importlib.import_module("abc_import")
from abc_import.ABCImport import ABCImport
try:
    abc_import.close()
except:
    pass
abc_import = ABCImport()
abc_import.show()
