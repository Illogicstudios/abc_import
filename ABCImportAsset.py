import os
import re
from abc import *

from pymel.core import *

from utils import *


class ABCImportAsset(ABC):
    def __init__(self, name, versions):
        self._name = name
        self.__versions = sorted(versions, reverse=True)
        self._import_version = self.__versions[0] if len(self.__versions)>0 else None
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

    def set_actual_standin(self, standin):
        self._actual_standin = standin

    def get_actual_version(self):
        return self._actual_version

    @abstractmethod
    def import_update_abc(self, current_project_dir, do_update_uvs_shaders):
        pass

    @abstractmethod
    def update_uvs_shaders(self, current_project_dir):
        pass


class ABCImportAnim(ABCImportAsset):
    def __init__(self, name, versions):
        super(ABCImportAnim, self).__init__(name, versions)

    def import_update_abc(self, current_project_dir, do_update_uvs_shaders):
        is_import = self._actual_standin is None

        abc_filename = self._name+".abc"
        abc_filepath = os.path.join(self._import_version,abc_filename)

        # If import we create the standin
        if is_import:
            self._actual_standin = createNode("aiStandIn", n="shape_"+self._name)
            standin_node = listRelatives(self._actual_standin, parent=True)[0]
            standin_node = rename(standin_node, self._name)
        else:
            standin_node = listRelatives(self._actual_standin, parent=True)[0]

        standin_node.useFrameExtension.set(True)
        standin_node.abc_layers.set(abc_filepath)

        if is_import or do_update_uvs_shaders:
            self.update_uvs_shaders(current_project_dir)

        return standin_node

    def update_uvs_shaders(self, current_project_dir):
        standin_node = listRelatives(self._actual_standin, parent=True)[0]
        abc_char_name = self._name[:-len(self._name.split("_")[-1]) - 1]
        assets_folder = os.path.join(current_project_dir, "assets")

        # MOD (UV)
        mod_folder = assets_folder + "\\" + abc_char_name + "\\abc\\"
        mod_files = []
        for file in os.listdir(mod_folder):
            file_path = os.path.join(mod_folder, file)
            if os.path.isfile(file_path) and re.match(r".*mod(\.v[0-9]+)?\.abc", file, re.IGNORECASE):
                mod_files.append(file_path)
        mod_files = sorted(mod_files, reverse=True)
        if len(mod_files) == 0:
            raise Exception("No mod file found in " + mod_folder)
        mod_file_path = mod_files[0]
        standin_node.dso.set(mod_file_path)

        # OPERATOR (SHADER)
        operator_folder = assets_folder + "\\" + abc_char_name + "\\publish"
        operator_files = []
        for file in os.listdir(operator_folder):
            file_path = os.path.join(operator_folder, file)
            if os.path.isfile(file_path) and re.match(r".*\.ass", file, re.IGNORECASE):
                operator_files.append(file_path)
        operator_files = sorted(operator_files, reverse=True)
        if len(operator_files) == 0:
            raise Exception("No operator file found in " + operator_folder)
        operator_file_path = operator_files[0]

        ai_standin = listRelatives(standin_node)
        include_graphs = listConnections(ai_standin, type="aiIncludeGraph")
        # If includ graph exists we retrieve it instead of creating one
        if len(include_graphs) > 0:
            set_shader = include_graphs[0]
        else:
            set_shader = createNode("aiIncludeGraph", n="aiIncludeGraph_" + self._name)
        set_shader.filename.set(operator_file_path)
        set_shader.out >> standin_node.operators[0]
        return standin_node


class ABCImportFur(ABCImportAsset):
    def __init__(self, name, versions):
        super(ABCImportFur, self).__init__(name, versions)

    def import_update_abc(self, current_project_dir, do_update_uvs_shaders):
        pass

    def update_uvs_shaders(self, current_project_dir):
        pass