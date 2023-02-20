import os
import re
from abc import *

from pymel.core import *

from utils import *


class ABCImportAsset(ABC):
    def __init__(self, name, versions, current_project_dir):
        self._name = name
        self.__versions = sorted(versions, reverse=True)
        self._current_project_dir = current_project_dir
        self._import_version = self.__versions[0] if len(self.__versions) > 0 else None
        self._actual_version = None
        self._actual_standin = None

    def get_name(self):
        return self._name

    def get_versions(self):
        return self.__versions

    def set_import_version(self, version_path):
        self._import_version = version_path

    def get_import_version(self):
        return self._import_version

    def set_actual_version(self, version_path):
        self._actual_version = version_path

    def has_uv_shaders_up_to_date(self):
        pass

    def set_actual_standin(self, standin):
        self._actual_standin = standin

    def get_actual_version(self):
        return self._actual_version

    @abstractmethod
    def import_update_abc(self, do_update_uvs_shaders):
        pass

    def update(self):
        pass

    @abstractmethod
    def check_up_to_date(self):
        pass

    def _get_operator_files(self):
        abc_char_name = self._name[:-len(self._name.split("_")[-1]) - 1]
        assets_folder = os.path.join(self._current_project_dir, "assets")
        operator_folder = assets_folder + "\\" + abc_char_name + "\\publish"
        operator_files = []
        for file in os.listdir(operator_folder):
            file_path = os.path.join(operator_folder, file)
            if os.path.isfile(file_path) and re.match(r".*operator(?:\.v[0-9]+)?\.ass", file, re.IGNORECASE):
                operator_files.append(file_path)
        operator_files = sorted(operator_files, reverse=True)
        return operator_files

    def _check_operator_up_to_date(self):
        # Test if operator is up to date
        operator_files = self._get_operator_files()
        if len(operator_files) == 0:
            return False
        include_graphs = listConnections(self._actual_standin, type="aiIncludeGraph")
        if len(include_graphs) == 0:
            return False
        set_shader = include_graphs[0]
        actual_operator_path = set_shader.filename.get()
        operator_regexp = r".*\.v([0-9]+)\.ass"
        operator_match = re.match(operator_regexp, operator_files[0])
        operator_match_actual = re.match(operator_regexp, actual_operator_path)
        if operator_match and operator_match_actual:
            last_version_num = int(operator_match.group(1))
            actual_version_num = int(operator_match_actual.group(1))
            if last_version_num > actual_version_num:
                return False
        return True

    def _update_operator(self):
        standin_node = listRelatives(self._actual_standin, parent=True)[0]

        # OPERATOR (SHADER)
        try:
            operator_files = self._get_operator_files()
            operator_file_path = operator_files[0]
        except:
            print_warning("No operator files found for " + self._name, char_filler='-')
            return standin_node

        include_graphs = listConnections(self._actual_standin, type="aiIncludeGraph")
        # If include graph exists we retrieve it instead of creating one
        if len(include_graphs) > 0:
            set_shader = include_graphs[0]
        else:
            set_shader = createNode("aiIncludeGraph", n="aiIncludeGraph_" + self._name)
        set_shader.filename.set(operator_file_path)
        set_shader.out >> standin_node.operators[0]
        return standin_node

class ABCImportAnim(ABCImportAsset):
    def __get_mod_files(self):
        abc_char_name = self._name[:-len(self._name.split("_")[-1]) - 1]
        assets_folder = os.path.join(self._current_project_dir, "assets")
        mod_folder = assets_folder + "\\" + abc_char_name + "\\abc\\"
        mod_files = []
        for file in os.listdir(mod_folder):
            file_path = os.path.join(mod_folder, file)
            if os.path.isfile(file_path) and re.match(r".*mod(?:\.v[0-9]+)?\.abc", file, re.IGNORECASE):
                mod_files.append(file_path)
        mod_files = sorted(mod_files, reverse=True)
        return mod_files

    def __check_mod_up_to_date(self):
        # Test if mod is up to date
        mod_files = self.__get_mod_files()
        standin_node = listRelatives(self._actual_standin, parent=True)[0]
        actual_mod_path = standin_node.dso.get()
        if len(mod_files) == 0 or actual_mod_path is None:
            return False
        mod_regexp = r".*mod\.v([0-9]+)\.abc"
        mod_match = re.match(mod_regexp, mod_files[0])
        mod_match_actual = re.match(mod_regexp, actual_mod_path)
        if mod_match and mod_match_actual:
            last_version_num = int(mod_match.group(1))
            actual_version_num = int(mod_match_actual.group(1))
            if last_version_num > actual_version_num:
                return False
        return True

    def __update_mod(self):
        # MOD (UV)
        try:
            mod_files = self.__get_mod_files()
            mod_file_path = mod_files[0]
            standin_node = listRelatives(self._actual_standin, parent=True)[0]
            standin_node.dso.set(mod_file_path)
        except:
            print_warning("No mod files found for " + self._name, char_filler='-')

    def import_update_abc(self, do_update_uvs_shaders):
        is_import = self._actual_standin is None

        # If import we create the standin
        if is_import:
            self._actual_standin = createNode("aiStandIn", n="shape_" + self._name)
            standin_node = listRelatives(self._actual_standin, parent=True)[0]
            standin_node = rename(standin_node, self._name)
        else:
            standin_node = listRelatives(self._actual_standin, parent=True)[0]

        abc_filename = self._name+".abc"
        abc_filepath = os.path.join(self._import_version,abc_filename)
        standin_node.useFrameExtension.set(True)
        standin_node.mode.set(6)
        standin_node.abc_layers.set(abc_filepath)

        if is_import or do_update_uvs_shaders:
            self.update()
        return standin_node

    def check_up_to_date(self):
        # Test if mod is up to date
        mod_up_to_date = self.__check_mod_up_to_date()
        if not mod_up_to_date: return False
        # Test if operator is up to date
        operator_up_to_date = self._check_operator_up_to_date()
        if not operator_up_to_date: return False
        return True

    def update(self):
        self.__update_mod()
        return self._update_operator()


class ABCImportFur(ABCImportAsset):

    def get_name(self):
        return self._name+"_fur"
    def import_update_abc(self, do_update_uvs_shaders):
        is_import = self._actual_standin is None

        # If import we create the standin
        if is_import:
            self._actual_standin = createNode("aiStandIn", n="shape_" + self._name)
            standin_node = listRelatives(self._actual_standin, parent=True)[0]
            standin_node = rename(standin_node, self._name)
        else:
            standin_node = listRelatives(self._actual_standin, parent=True)[0]

        standin_node.useFrameExtension.set(True)
        standin_node.mode.set(6)

        if is_import or do_update_uvs_shaders:
            self.update()
        return standin_node

    def update(self):
        return self._update_operator()

    def check_up_to_date(self):
        # Test if operator is up to date
        return self._check_operator_up_to_date()
