import os
from functools import partial

import sys

from pymel.core import *
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from shiboken2 import wrapInstance

from utils import *

from Prefs import *

import maya.OpenMaya as OpenMaya

from ABCImportAsset import *

# ######################################################################################################################

_FILE_NAME_PREFS = "abc_import"


# ######################################################################################################################


class ABCImport(QDialog):
    # Get the directory parent of the scene
    @staticmethod
    def __get_dir_name():
        scene_name = sceneName()
        if len(scene_name) > 0:
            dirname = os.path.dirname(os.path.dirname(scene_name))
        else:
            dirname = None
        return dirname

    @staticmethod
    def __is_correct_folder(folder):
        if not os.path.exists(folder):
            return False
        if ABCImport.__is_parent_abc_folder(folder):
            return True
        if ABCImport.__is_abc_folder(folder):
            return True
        if ABCImport.__is_abc_fur_folder(folder):
            return True
        return False

    @staticmethod
    def __is_abc_folder(folder):
        return re.match(r".*/abc(?:/|\\)?$", folder)

    @staticmethod
    def __is_abc_fur_folder(folder):
        return re.match(r".*/abc_fur(?:/|\\)?$", folder)

    @staticmethod
    def __is_parent_abc_folder(folder):
        for d in os.listdir(folder):
            if os.path.isdir(os.path.join(folder, d)):
                if d in ["abc", "abc_fur"]:
                    return True
        return False

    def __init__(self, prnt=wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget)):
        super(ABCImport, self).__init__(prnt)

        # Common Preferences (common preferences on all tools)
        self.__common_prefs = Prefs()
        # Preferences for this tool
        self.__prefs = Prefs(_FILE_NAME_PREFS)

        # Model attributes
        self.__folder_path = ""
        self.__update_uvs_shaders = True
        self.__abcs = []
        self.__selected_abcs = []

        self.__retrieve_current_project_dir()
        self.__retrieve_abcs()

        # UI attributes
        self.__ui_width = 600
        self.__ui_height = 400
        self.__ui_min_width = 400
        self.__ui_min_height = 250
        self.__ui_pos = QDesktopWidget().availableGeometry().center() - QPoint(self.__ui_width, self.__ui_height) / 2

        self.__retrieve_prefs()

        # name the window
        self.setWindowTitle("ABC Import")
        # make the window a "tool" in Maya's eyes so that it stays on top when you click off
        self.setWindowFlags(QtCore.Qt.Tool)
        # Makes the object get deleted from memory, not just hidden, when it is closed.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Create the layout, linking it to actions and refresh the display
        self.__create_ui()
        self.__refresh_ui()

    # Save preferences
    def __save_prefs(self):
        size = self.size()
        self.__prefs["window_size"] = {"width": size.width(), "height": size.height()}
        pos = self.pos()
        self.__prefs["window_pos"] = {"x": pos.x(), "y": pos.y()}

    # Retrieve preferences
    def __retrieve_prefs(self):
        if "window_size" in self.__prefs:
            size = self.__prefs["window_size"]
            self.__ui_width = size["width"]
            self.__ui_height = size["height"]

        if "window_pos" in self.__prefs:
            pos = self.__prefs["window_pos"]
            self.__ui_pos = QPoint(pos["x"], pos["y"])

    def showEvent(self, arg__1: QShowEvent) -> None:
        self.__selection_callback = \
            OpenMaya.MEventMessage.addEventCallback("SelectionChanged", self.__on_selection_changed)

    # Remove callbacks
    def hideEvent(self, arg__1: QCloseEvent) -> None:
        OpenMaya.MMessage.removeCallback(self.__selection_callback)
        self.__save_prefs()

    def __retrieve_current_project_dir(self):
        self.__current_project_dir = os.getenv("CURRENT_PROJECT_DIR")
        if self.__current_project_dir is None:
            self.__stop_and_display_error()

    # Delete the window and show an error message
    def __stop_and_display_error(self):
        self.deleteLater()
        msg = QMessageBox()
        msg.setWindowTitle("Error current project directory not found")
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Current project directory not found")
        msg.setInformativeText("Current project directory has not been found. You should use an Illogic Maya Launcher")
        msg.exec_()

    # Create the ui
    def __create_ui(self):
        # Reinit attributes of the UI
        self.setMinimumSize(self.__ui_min_width, self.__ui_min_height)
        self.resize(self.__ui_width, self.__ui_height)
        self.move(self.__ui_pos)

        browse_icon_path = os.path.dirname(__file__) + "/assets/browse.png"

        # Main Layout
        main_lyt = QVBoxLayout()
        main_lyt.setContentsMargins(8, 12, 8, 12)
        main_lyt.setSpacing(7)
        self.setLayout(main_lyt)

        # Folder selection layout
        folder_lyt = QHBoxLayout()
        main_lyt.addLayout(folder_lyt)
        self.__ui_folder_path = QLineEdit(self.__folder_path)
        self.__ui_folder_path.setFixedHeight(27)
        self.__ui_folder_path.textChanged.connect(self.__on_folder_changed)
        folder_lyt.addWidget(self.__ui_folder_path)
        browse_btn = QPushButton()
        browse_btn.setIconSize(QtCore.QSize(18, 18))
        browse_btn.setFixedSize(QtCore.QSize(24, 24))
        browse_btn.setIcon(QIcon(QPixmap(browse_icon_path)))
        browse_btn.clicked.connect(partial(self.__browse_folder))
        folder_lyt.addWidget(browse_btn)

        # Asset Table
        self.__ui_abcs_table = QTableWidget(0, 5)
        self.__ui_abcs_table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.__ui_abcs_table.verticalHeader().hide()
        self.__ui_abcs_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.__ui_abcs_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.__ui_abcs_table.setHorizontalHeaderLabels(
            ["State", "Asset name", "Actual version", "Import version", "Update look"])
        horizontal_header = self.__ui_abcs_table.horizontalHeader()
        horizontal_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(1, QHeaderView.Stretch)
        horizontal_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.__ui_abcs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.__ui_abcs_table.itemSelectionChanged.connect(self.__on_abcs_selection_changed)
        main_lyt.addWidget(self.__ui_abcs_table)

        # Update UV and Shader checkbox
        self.__ui_update_uvs_shaders = QCheckBox("Update UVs and Shaders")
        self.__ui_update_uvs_shaders.setChecked(self.__update_uvs_shaders)
        self.__ui_update_uvs_shaders.stateChanged.connect(self.__on_checked_update_uvs_shaders)
        main_lyt.addWidget(self.__ui_update_uvs_shaders,0 ,Qt.AlignHCenter)

        # Submit Import button
        self.__ui_import_btn = QPushButton("Import or Update selection")
        self.__ui_import_btn.clicked.connect(self.__import_update_selected_abcs)
        main_lyt.addWidget(self.__ui_import_btn)

    # Refresh the ui according to the model attribute
    def __refresh_ui(self):
        self.__refresh_btn()
        self.__refresh_table()

    def __refresh_btn(self):
        nb_abcs_selected = len(self.__selected_abcs)
        enabled = True
        tooltip = ""
        if nb_abcs_selected == 0:
            enabled = False
            tooltip = "Select atleast one abc to import or update"
        elif not self.__is_correct_folder(self.__folder_path):
            enabled = False
            tooltip = "The export folder must be named a parent folder of a folder named \"abc\" or \"abc_fur\""
        self.__ui_import_btn.setEnabled(enabled)
        self.__ui_import_btn.setToolTip(tooltip)

    def __refresh_table(self):
        valid_icon_path = os.path.dirname(__file__) + "/assets/valid.png"
        warning_icon_path = os.path.dirname(__file__) + "/assets/warning.png"
        new_icon_path = os.path.dirname(__file__) + "/assets/new.png"

        selected_abcs = [abc.get_name() for abc in self.__selected_abcs]

        self.__ui_abcs_table.setRowCount(0)
        row_index = 0
        selected_rows = []
        for abc in self.__abcs:
            name = abc.get_name()
            anim_versions = abc.get_versions()
            anim_import_version = abc.get_import_version()
            anim_actual_version = abc.get_actual_version()

            self.__ui_abcs_table.insertRow(row_index)

            if name in selected_abcs:
                selected_rows.append(row_index)

            if anim_actual_version is None:
                state = 2
            else:
                if int(os.path.basename(anim_actual_version)) < int(os.path.basename(anim_versions[0])):
                    state = 1
                else:
                    state = 0

            icon_widget = QLabel()
            icon_widget.setFixedSize(QSize(22, 22))
            icon_widget.setScaledContents(True)

            if state == 0:
                pixmap = QPixmap(valid_icon_path)
                tooltip = "Up to date"
            elif state == 1:
                pixmap = QPixmap(warning_icon_path)
                tooltip = "Not up to date"
            else:
                pixmap = QPixmap(new_icon_path)
                tooltip = "New"
            icon_widget.setPixmap(pixmap)
            icon_widget.setToolTip(tooltip)

            # State
            container_icon_widget = QWidget()
            layout_container_icon_widget = QVBoxLayout(container_icon_widget)
            layout_container_icon_widget.setContentsMargins(0, 0, 0, 0)
            layout_container_icon_widget.addWidget(icon_widget)
            layout_container_icon_widget.setAlignment(Qt.AlignCenter)
            container_icon_widget.setLayout(layout_container_icon_widget)
            self.__ui_abcs_table.setCellWidget(row_index, 0, container_icon_widget)

            # Name
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, abc)
            self.__ui_abcs_table.setItem(row_index, 1, name_item)
            if state == 2:
                self.__ui_abcs_table.setSpan(row_index, 1, 1, 2)

            # Actual version
            if state != 2:
                version_item = QTableWidgetItem(abc.get_actual_version())
                version_item.setData(Qt.UserRole, abc)
                version_item.setTextAlignment(Qt.AlignCenter)
                self.__ui_abcs_table.setItem(row_index, 2, version_item)

            # Import version
            import_version_combobox = QComboBox()
            import_version_combobox.setStyleSheet(".QComboBox{margin:2px; padding:3px}")
            self.__ui_abcs_table.setCellWidget(row_index, 3, import_version_combobox)
            for v in anim_versions:
                import_version_combobox.addItem(os.path.basename(v), v)
            import_version_combobox.currentIndexChanged.connect(partial(self.__on_version_combobox_changed, row_index))
            if anim_import_version is not None:
                import_version_combobox.setCurrentText(os.path.basename(anim_import_version))

            # Action
            if state != 2:
                action_btn = QPushButton("Update")
                action_btn.setStyleSheet("margin:3px")
                action_btn.clicked.connect(partial(self.__on_click_update_uvs_shaders, abc))
                action_btn.setEnabled(not abc.check_up_to_date())
                self.__ui_abcs_table.setCellWidget(row_index, 4, action_btn)

            row_index += 1

        # Select the previous selected rows
        self.__ui_abcs_table.setSelectionMode(QAbstractItemView.MultiSelection)
        for row_index in selected_rows:
            self.__ui_abcs_table.selectRow(row_index)
        self.__ui_abcs_table.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def __browse_folder(self):
        dirname = ABCImport.__get_dir_name()
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select ABC Directory", dirname)
        if ABCImport.__is_correct_folder(folder_path) and folder_path != self.__folder_path:
            self.__ui_folder_path.setText(folder_path)

    def __on_selection_changed(self, *args, **kwarrgs):
        self.__retrieve_assets_in_scene()
        self.__refresh_ui()

    def __on_checked_update_uvs_shaders(self,state):
        self.__update_uvs_shaders = state == 2

    def __on_folder_changed(self):
        retrieved_text = self.__ui_folder_path.text().strip("\\/")
        if self.__folder_path != retrieved_text:
            self.__folder_path = retrieved_text
            self.__retrieve_abcs()
            self.__refresh_ui()

    def __on_abcs_selection_changed(self):
        self.__selected_abcs.clear()
        for selected_row in self.__ui_abcs_table.selectionModel().selectedRows():
            self.__selected_abcs.append(self.__ui_abcs_table.item(selected_row.row(), 1).data(Qt.UserRole))
        self.__refresh_btn()

    def __on_version_combobox_changed(self, row_index, cb_index):
        abc = self.__ui_abcs_table.item(row_index, 1).data(Qt.UserRole)
        version_path = self.__ui_abcs_table.cellWidget(row_index, 3).model().item(cb_index).data(Qt.UserRole)
        abc.set_import_version(version_path)

    def __on_click_update_uvs_shaders(self, abc):
        standin_node = abc.update()
        select(standin_node)

    def __retrieve_abcs(self):
        self.__abcs.clear()
        if os.path.exists(self.__folder_path):
            if ABCImport.__is_parent_abc_folder(self.__folder_path):
                self.__retrieve_assets(os.path.join(self.__folder_path, "abc"), True)
                # self.__retrieve_assets(os.path.join(self.__folder_path, "abc_fur"), False)
            elif ABCImport.__is_abc_folder(self.__folder_path):
                self.__retrieve_assets(self.__folder_path, True)
            elif ABCImport.__is_abc_fur_folder(self.__folder_path):
                pass
                # self.__retrieve_assets(self.__folder_path, False)
        self.__retrieve_assets_in_scene()

    def __retrieve_assets(self, folder_path, is_anim_folder):
        if os.path.isdir(folder_path):
            for asset_folder in os.listdir(folder_path):
                asset_folder_path = os.path.join(folder_path, asset_folder)
                anim_versions = []
                if os.path.isdir(asset_folder_path):
                    for version_folder in os.listdir(asset_folder_path):
                        version_folder_path = os.path.join(asset_folder_path, version_folder)
                        if asset_folder + ".abc" in os.listdir(version_folder_path):
                            anim_versions.append(version_folder_path)
                if is_anim_folder:
                    asset = ABCImportAnim(asset_folder, anim_versions, self.__current_project_dir)
                else:
                    asset = ABCImportFur(asset_folder, anim_versions, self.__current_project_dir)
                self.__abcs.append(asset)

    def __retrieve_assets_in_scene(self):
        standins = ls(type="aiStandIn")
        standins_datas = {}
        for standin in standins:
            standin_node = listRelatives(standin, parent=True)[0]
            abc_layer = standin_node.abc_layers.get()
            if abc_layer is not None:
                abc_layer = abc_layer.replace("\\","/")
                match = re.match(r".*/(.*)/(.*)/([0-9]{4})/.*_[0-9]{2}\.abc", abc_layer, re.IGNORECASE)
                if match:
                    name = match.groups()[1]
                    if match.groups()[0] == "abc_fur":
                        name+="_fur"
                    standins_datas[name] = (standin, match.groups()[2])
        for abc in self.__abcs:
            abc_name = abc.get_name()
            if abc_name in standins_datas.keys():
                abc.set_actual_standin(standins_datas[abc_name][0])
                abc.set_actual_version(standins_datas[abc_name][1])
            else:
                abc.set_actual_standin(None)
                abc.set_actual_version(None)

    def __import_update_selected_abcs(self):
        standin_nodes = []
        for abc in self.__selected_abcs:
            standin_nodes.append(abc.import_update_abc(self.__update_uvs_shaders))
        select(standin_nodes)
        self.__retrieve_assets_in_scene()
        self.__refresh_ui()
