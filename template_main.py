import sys
import importlib

if __name__ == '__main__':
    # TODO specify the right path
    install_dir = 'PATH/TO/abc_import'
    if not sys.path.__contains__(install_dir):
        sys.path.append(install_dir)

    modules = [
        "ABCImport",
        "ABCImportAsset"
    ]

    from utils import *
    unload_packages(silent=True, packages=modules)

    for module in modules:
        importlib.import_module(module)

    from ABCImport import *

    try:
        abc_import.close()
    except:
        pass
    abc_import = ABCImport()
    abc_import.show()
