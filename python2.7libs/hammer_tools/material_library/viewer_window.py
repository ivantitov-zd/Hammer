try:
    from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QSpacerItem,
                                 QSizePolicy, QPushButton, QSlider, QSplitter, QAction, QMenu, QAbstractItemView)
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtGui import QIcon, QCursor
except ImportError:
    from PySide2.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QSpacerItem,
                                   QSizePolicy, QPushButton, QSlider, QSplitter, QAction, QMenu, QAbstractItemView)
    from PySide2.QtCore import Qt, QSize
    from PySide2.QtGui import QIcon, QCursor

import hou

from ..utils import openLocation
from .data_roles import InternalDataRole
from .engine_connector import EngineConnector
from .library_list import LibraryListBrowser
from .library_browser import LibraryBrowser
from .add_library_window import AddLibraryDialog
from .add_materials_window import AddMaterialsDialog
from .texture_list import TextureListBrowser
from .remove_library_window import RemoveLibraryWindow
from .remove_material_window import RemoveMaterialWindow

FAVORITE_ENABLED_ICON = hou.qt.Icon('BUTTONS_favorites', 16, 16)
FAVORITE_DISABLED_ICON = hou.qt.Icon('BUTTONS_not_favorites', 16, 16)
FAVORITE_ICON = QIcon()
FAVORITE_ICON.addPixmap(FAVORITE_ENABLED_ICON.pixmap(16, 16), QIcon.Normal, QIcon.On)
FAVORITE_ICON.addPixmap(FAVORITE_DISABLED_ICON.pixmap(16, 16), QIcon.Normal, QIcon.Off)


class MaterialLibraryViewerDialog(QMainWindow):
    def __init__(self, parent=None):
        super(MaterialLibraryViewerDialog, self).__init__(parent)

        self.setWindowTitle('Hammer: Material Library')
        self.setWindowIcon(hou.qt.Icon('SOP_material', 32, 32))

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(4, 4, 4, 4)
        top_layout.setSpacing(8)
        main_layout.addLayout(top_layout)

        self.target_engine_combo = QComboBox()
        self.target_engine_combo.setMinimumWidth(100)
        self.target_engine_combo.addItem(EngineConnector.icon(), 'Auto', None)
        for engine in EngineConnector.engines():
            if engine.isAvailable() and engine.builders():
                self.target_engine_combo.addItem(engine.icon(), engine.name(), engine)
        self.target_engine_combo.setToolTip('Target rendering engine')
        self.target_engine_combo.currentIndexChanged.connect(
            lambda: EngineConnector.setCurrentEngine(self.target_engine_combo.currentData(Qt.UserRole))
        )
        self.target_engine_combo.currentIndexChanged.connect(self.updateEngineBuilderList)
        top_layout.addWidget(self.target_engine_combo)

        self.target_builder_combo = QComboBox()
        self.target_builder_combo.setMinimumWidth(140)
        self.target_builder_combo.setToolTip('Target builder')
        self.updateEngineBuilderList()
        top_layout.addWidget(self.target_builder_combo)

        self.target_network_combo = QComboBox()
        self.target_network_combo.setToolTip('Target network')
        self.target_network_combo.setMinimumWidth(160)
        top_layout.addWidget(self.target_network_combo)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        top_layout.addSpacerItem(spacer)

        self.search_field = QLineEdit()
        self.search_field.setFixedWidth(140)
        self.search_field.setPlaceholderText('Search...')
        top_layout.addWidget(self.search_field)

        self.favorite_toggle = QPushButton()
        self.favorite_toggle.setFixedWidth(24)
        self.favorite_toggle.setCheckable(True)
        self.favorite_toggle.setToolTip('Show favorite only')
        self.favorite_toggle.setIcon(FAVORITE_ICON)
        top_layout.addWidget(self.favorite_toggle)

        self.thumbnail_size_slider = QSlider(Qt.Horizontal)
        self.thumbnail_size_slider.setFixedWidth(80)
        self.thumbnail_size_slider.setRange(48, 256)
        self.thumbnail_size_slider.setValue(64)
        top_layout.addWidget(self.thumbnail_size_slider)

        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)

        self.library_list_browser = LibraryListBrowser()
        self.splitter.addWidget(self.library_list_browser)

        self.library_browser = LibraryBrowser()
        self.library_list_browser.currentLibraryChanged.connect(self.library_browser.setLibrary)
        selection_model = self.library_browser.view.selectionModel()
        selection_model.selectionChanged.connect(self.updateStatusBar)
        self.favorite_toggle.toggled.connect(self.library_browser.proxy_model.showFavoriteOnly)
        self.search_field.textChanged.connect(self.library_browser.proxy_model.setFilterPattern)
        self.library_browser.view.iconSizeChanged.connect(self.updateThumbnailSizeSlider)
        self.thumbnail_size_slider.valueChanged.connect(self.setThumbnailSize)
        self.splitter.addWidget(self.library_browser)

        self.splitter.setSizes([140, self.splitter.width() - 140])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.open_settings_action = None
        self.add_material_action = None
        self.add_materials_action = None
        self.add_library_action = None
        self.add_library_from_folder_action = None
        self.update_thumbnails_action = None
        self.reload_action = None
        self.edit_tags_action = None
        self.main_menu = None
        self.content_menu = None
        self.tags_menu = None

        self.generate_library_thumbnails_action = None
        self.open_library_location_action = None
        self.assemble_library_action = None
        self.edit_library_action = None
        self.remove_library_action = None
        self.library_menu = None

        self.create_material_action = None
        self.create_material_and_assign_action = None
        self.generate_material_thumbnail_action = None
        self.set_custom_material_thumbnail_action = None
        self.open_material_location_action = None
        self.material_textures_action = None
        self.mark_material_as_favorite_action = None
        self.edit_material_action = None
        self.remove_material_action = None
        self.material_menu = None

        self.createActions()
        self.createMainMenu()
        self.createLibraryContextMenu()
        self.createMaterialContextMenu()

        self.updateTargetNetworkList()
        self.updateContent()

        self.statusBar().setSizeGripEnabled(False)

    def createActions(self):
        self.open_settings_action = QAction(hou.qt.Icon('LOP_rendersettings', 16, 16), 'Settings...', self)

        self.reload_action = QAction(hou.qt.Icon('NETVIEW_reload', 16, 16), 'Reload', self)

        self.add_material_action = QAction(hou.qt.Icon('LOP_materiallibrary', 16, 16), 'Add material...', self)

        self.add_materials_action = QAction(hou.qt.Icon('BUTTONS_import_library', 16, 16), 'Add materials...', self)
        self.add_materials_action.triggered.connect(self.onAddMaterials)

        self.add_library_action = QAction(hou.qt.Icon('DATATYPES_styles_folder', 16, 16), 'Add library...', self)
        self.add_library_action.triggered.connect(self.onAddLibrary)

        self.update_thumbnails_action = QAction(hou.qt.Icon('NODEFLAGS_render', 16, 16), 'Update thumbnails', self)

        self.edit_tags_action = QAction(hou.qt.Icon('BUTTONS_tag', 16, 16), 'Edit tags', self)

        self.generate_library_thumbnails_action = QAction('Generate thumbnails...', self)

        self.open_library_location_action = QAction('Open location...', self)
        self.open_library_location_action.triggered.connect(self.openCurrentLibraryLocation)

        self.assemble_library_action = QAction('Assemble...', self)

        self.edit_library_action = QAction('Edit...', self)

        self.remove_library_action = QAction('Remove...', self)
        self.remove_library_action.triggered.connect(self.onRemoveLibrary)

        self.create_material_action = QAction('Create material', self)
        self.create_material_action.triggered.connect(self.createMaterial)

        self.create_material_and_assign_action = QAction('Create material and assign', self)

        self.generate_material_thumbnail_action = QAction('Generate thumbnail...', self)

        self.set_custom_material_thumbnail_action = QAction('Set custom thumbnail...', self)

        self.open_material_location_action = QAction('Open location...', self)
        self.open_material_location_action.triggered.connect(self.openCurrentMaterialLocation)

        self.material_textures_action = QAction('Textures...', self)
        self.material_textures_action.triggered.connect(self.onMaterialTextures)

        self.mark_material_as_favorite_action = QAction('Mark as favorite', self)
        self.mark_material_as_favorite_action.triggered.connect(self.onMarkMaterialAsFavorite)

        self.edit_material_action = QAction('Edit...', self)

        self.remove_material_action = QAction('Remove...', self)
        self.remove_material_action.triggered.connect(self.onRemoveMaterial)

    def createMainMenu(self):
        self.main_menu = QMenu('Main', self)
        self.menuBar().addMenu(self.main_menu)

        self.main_menu.addAction(self.open_settings_action)

        self.content_menu = QMenu('Content', self)
        self.menuBar().addMenu(self.content_menu)

        self.content_menu.addAction(self.add_library_action)
        self.content_menu.addSeparator()
        self.content_menu.addAction(self.add_material_action)
        self.content_menu.addAction(self.add_materials_action)
        self.content_menu.addSeparator()
        self.content_menu.addAction(self.update_thumbnails_action)
        self.content_menu.addAction(self.reload_action)

        # self.tags_menu = QMenu('Tags', self)
        # self.menuBar().addMenu(self.tags_menu)
        #
        # self.tags_menu.addAction(self.edit_tags_action)

    def createLibraryContextMenu(self):
        self.library_menu = QMenu(self.library_list_browser.view)
        self.library_list_browser.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.library_list_browser.view.customContextMenuRequested.connect(self.onLibraryContextMenuRequested)

        self.library_menu.addAction(self.generate_library_thumbnails_action)
        self.library_menu.addSeparator()
        self.library_menu.addAction(self.open_library_location_action)
        self.library_menu.addAction(self.assemble_library_action)
        self.library_menu.addSeparator()
        self.library_menu.addAction(self.edit_library_action)
        self.library_menu.addAction(self.remove_library_action)

    def updateLibraryContextMenu(self):
        pass

    def onLibraryContextMenuRequested(self):
        if len(self.library_list_browser.view.selectedIndexes()) != 1:
            return

        self.updateLibraryContextMenu()
        self.library_menu.exec_(QCursor.pos())

    def createMaterialContextMenu(self):
        self.material_menu = QMenu(self.library_browser.view)
        self.library_browser.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.library_browser.view.customContextMenuRequested.connect(self.onMaterialContextMenuRequested)

        self.material_menu.addAction(self.create_material_action)
        self.material_menu.addAction(self.create_material_and_assign_action)
        self.material_menu.addSeparator()
        self.material_menu.addAction(self.generate_material_thumbnail_action)
        self.material_menu.addAction(self.set_custom_material_thumbnail_action)
        self.material_menu.addSeparator()
        self.material_menu.addAction(self.open_material_location_action)
        self.material_menu.addAction(self.material_textures_action)
        self.material_menu.addSeparator()
        self.material_menu.addAction(self.mark_material_as_favorite_action)
        self.material_menu.addAction(self.edit_material_action)
        self.material_menu.addAction(self.remove_material_action)

    def updateMaterialContextMenu(self):
        pass

    def onMaterialContextMenuRequested(self):
        if len(self.library_browser.view.selectedIndexes()) != 1:
            return

        self.updateMaterialContextMenu()
        self.material_menu.exec_(QCursor.pos())

    def updateEngineBuilderList(self):
        self.target_builder_combo.clear()

        engine = EngineConnector.currentEngine()
        if not engine:
            self.target_builder_combo.addItem('Auto', None)
            return

        for builder in engine.builders():
            builder = builder()
            if builder.isAvailable():
                self.target_builder_combo.addItem(builder.name(), builder)

    def updateTargetNetworkList(self):
        self.target_network_combo.clear()

        self.target_network_combo.addItem(hou.qt.Icon('NETWORKS_mat', 16, 16), 'Auto', None)

        nodes = []

        # materiallib_node = hou.nodeType(hou.lopNodeTypeCategory(), 'materiallibrary')
        # if materiallib_node is not None:
        #     for node in materiallib_node.instances():
        #         nodes.append(node)

        nodes.append(hou.node('/mat/'))

        for category in hou.nodeTypeCategories().values():
            matnet_type = category.nodeType('matnet')
            if matnet_type is not None:
                for node in matnet_type.instances():
                    nodes.append(node)

        nodes.append(hou.node('/shop/'))

        for category in hou.nodeTypeCategories().values():
            shopnet_type = category.nodeType('shopnet')
            if shopnet_type is not None:
                for node in shopnet_type.instances():
                    nodes.append(node)

        for node in nodes:
            self.target_network_combo.addItem(hou.qt.Icon(node.type().icon(), 16, 16), node.path(), node)

    def updateStatusBar(self):
        self.statusBar().showMessage('Selected: {}'.format(len(self.library_browser.view.selectedIndexes())))

    def updateContent(self):
        self.library_list_browser.updateContent()
        self.library_browser.updateContent()

    def onAddLibrary(self):
        if AddLibraryDialog.addLibrary():
            self.updateContent()

    def onAddMaterials(self):
        if AddMaterialsDialog.addMaterials():
            self.updateContent()

    def updateThumbnailSizeSlider(self, size):
        self.thumbnail_size_slider.blockSignals(True)
        self.thumbnail_size_slider.setValue(size.width())
        self.thumbnail_size_slider.blockSignals(False)

    def setThumbnailSize(self, size):
        self.library_browser.view.setIconSize(QSize(size, size))

    def openCurrentLibraryLocation(self):
        library = self.library_list_browser.view.currentIndex().data(InternalDataRole)
        if library.path():
            openLocation(library.path())

    def createMaterial(self):
        material = self.library_browser.view.currentIndex().data(InternalDataRole)
        builder = self.target_builder_combo.currentData(Qt.UserRole)
        root = self.target_network_combo.currentData(Qt.UserRole)
        material_node = builder.build(material, root)
        material_node.moveToGoodPosition()

    def openCurrentMaterialLocation(self):
        material = self.library_browser.view.currentIndex().data(InternalDataRole)
        if material.source().path():
            openLocation(material.source().path())

    def onMaterialTextures(self):
        material = self.library_browser.view.currentIndex().data(InternalDataRole)
        window = TextureListBrowser(self)
        window.model.setTextureList(material.textures())
        window.show()

    def onRemoveLibrary(self):
        library = self.library_list_browser.view.currentIndex().data(InternalDataRole)

        window = RemoveLibraryWindow(library)

        if not window.exec_():
            return

        library.remove(remove_materials=window.removeMaterials(),
                       only_single_bound_materials=window.onlySingleBoundMaterials())

        self.updateContent()

    def onMarkMaterialAsFavorite(self):
        index = self.library_browser.view.currentIndex()
        material = index.data(InternalDataRole)
        material.markAsFavorite(not material.isFavorite())
        self.updateContent()

    def onRemoveMaterial(self):
        material = self.library_browser.view.currentIndex().data(InternalDataRole)
        library = self.library_browser.library()

        window = RemoveMaterialWindow(material, library)

        if not window.exec_():
            return

        if window.onlyFromLibrary():
            library.removeMaterial(material)
        else:
            material.remove()

        self.updateContent()
