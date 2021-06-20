try:
    from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QSpacerItem,
                                 QSizePolicy, QPushButton, QSlider, QSplitter, QAction, QMenu, QAbstractItemView,
                                 QToolBar, QApplication, QFileDialog)
    from PyQt5.QtCore import Qt, QSize, QEvent
    from PyQt5.QtGui import QIcon, QCursor, QKeySequence
except ImportError:
    from PySide2.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QSpacerItem,
                                   QSizePolicy, QPushButton, QSlider, QSplitter, QAction, QMenu, QAbstractItemView,
                                   QToolBar, QApplication, QFileDialog)
    from PySide2.QtCore import Qt, QSize, QEvent
    from PySide2.QtGui import QIcon, QCursor, QKeySequence

import hou

from ..utils import openLocation
from ..widgets import Slider, InputField, ComboBox
from ..menu import Menu
from .db import connect
from .data_roles import InternalDataRole
from .engine_connector import EngineConnector
from .library_list_browser import LibraryListBrowser
from .library_browser import LibraryBrowser
from .add_library_window import AddLibraryDialog
from .add_folder_content_window import AddFolderContentDialog, Target
from .texture_list import TextureListBrowser
from .remove_library_options_window import RemoveLibraryOptionsWindow
from .remove_material_options_window import RemoveMaterialOptionsWindow
from .remove_texture_options_window import RemoveTextureOptionsWindow
from .thumbnail import updateMaterialThumbnails, updateTextureThumbnails
from .library import Library
from .material import Material
from .texture import TextureMap
from .build_options_window import BuildOptionsWindow
from .edit_library_window import EditLibraryWindow

FAVORITE_ENABLED_ICON = hou.qt.Icon('BUTTONS_favorites', 16, 16)
FAVORITE_DISABLED_ICON = hou.qt.Icon('BUTTONS_not_favorites', 16, 16)
FAVORITE_ICON = QIcon()
FAVORITE_ICON.addPixmap(FAVORITE_ENABLED_ICON.pixmap(16, 16), QIcon.Normal, QIcon.On)
FAVORITE_ICON.addPixmap(FAVORITE_DISABLED_ICON.pixmap(16, 16), QIcon.Normal, QIcon.Off)

MATERIAL_ICON = hou.qt.Icon('SOP_material', 16, 16)
TEXTURE_ICON = hou.qt.Icon('BUTTONS_parmmenu_texture', 16, 16)


class MaterialLibraryViewerWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MaterialLibraryViewerWindow, self).__init__(parent)

        self.setWindowTitle('Hammer: Material Library')
        self.setWindowIcon(hou.qt.Icon('SOP_material', 32, 32))

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)

        toolbar = QToolBar()
        toolbar.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        toolbar.setFloatable(False)
        toolbar.setContentsMargins(2, 4, 6, 0)
        toolbar.setStyleSheet('QToolBar { spacing: 2px; }')
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        self.target_engine_combo = ComboBox()
        self.target_engine_combo.view().setMinimumWidth(self.target_engine_combo.minimumSizeHint().width())
        self.target_engine_combo.setMinimumWidth(100)
        self.target_engine_combo.addItem(EngineConnector.icon(), 'Auto', None)
        for engine in EngineConnector.engines():
            if engine.isAvailable() and engine.builders():
                self.target_engine_combo.addItem(engine.icon(), engine.name(), engine)
        self.target_engine_combo.setToolTip('Target rendering engine')
        self.target_engine_combo.currentIndexChanged.connect(self.onCurrentEngineChanged)
        toolbar.addWidget(self.target_engine_combo)

        self.target_builder_combo = ComboBox()
        self.target_builder_combo.setMinimumWidth(100)
        self.target_builder_combo.setMaximumWidth(150)
        self.target_builder_combo.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Ignored)
        self.target_builder_combo.view().setMinimumWidth(200)
        self.target_builder_combo.setToolTip('Target builder')
        self.target_builder_combo.currentTextChanged.connect(
            lambda name: self.target_builder_combo.setToolTip('Target builder\n' + name)
        )
        self.updateEngineBuilderList()
        toolbar.addWidget(self.target_builder_combo)

        self.target_network_combo = ComboBox()
        self.target_network_combo.setMinimumWidth(100)
        self.target_network_combo.setMaximumWidth(200)
        self.target_network_combo.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Ignored)
        self.target_network_combo.view().setMinimumWidth(350)
        self.target_network_combo.setToolTip('Target network')
        self.target_network_combo.currentTextChanged.connect(
            lambda path: self.target_network_combo.setToolTip('Target network\n' + path)
        )
        self.target_network_combo.installEventFilter(self)
        toolbar.addWidget(self.target_network_combo)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        toolbar.addWidget(spacer)

        self.show_materials_toggle = QPushButton()
        self.show_materials_toggle.setFixedWidth(24)
        self.show_materials_toggle.setCheckable(True)
        self.show_materials_toggle.setChecked(True)
        self.show_materials_toggle.setToolTip('Show materials')
        self.show_materials_toggle.setIcon(MATERIAL_ICON)
        toolbar.addWidget(self.show_materials_toggle)

        self.show_textures_toggle = QPushButton()
        self.show_textures_toggle.setFixedWidth(24)
        self.show_textures_toggle.setCheckable(True)
        self.show_textures_toggle.setChecked(True)
        self.show_textures_toggle.setToolTip('Show textures')
        self.show_textures_toggle.setIcon(TEXTURE_ICON)
        toolbar.addWidget(self.show_textures_toggle)

        self.search_field = InputField()
        self.search_field.setMinimumWidth(80)
        self.search_field.setMaximumWidth(140)
        self.search_field.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Ignored)
        self.search_field.setPlaceholderText('Search...')
        toolbar.addWidget(self.search_field)

        self.favorite_toggle = QPushButton()
        self.favorite_toggle.setFixedWidth(24)
        self.favorite_toggle.setCheckable(True)
        self.favorite_toggle.setToolTip('Show favorite only')
        self.favorite_toggle.setIcon(FAVORITE_ICON)
        toolbar.addWidget(self.favorite_toggle)

        self.thumbnail_size_slider = Slider(Qt.Horizontal)
        self.thumbnail_size_slider.setFixedWidth(80)
        self.thumbnail_size_slider.setRange(48, 256)
        self.thumbnail_size_slider.setValue(96)
        toolbar.addWidget(self.thumbnail_size_slider)

        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)

        self.library_list_browser = LibraryListBrowser()
        self.splitter.addWidget(self.library_list_browser)

        self.library_browser = LibraryBrowser()
        self.library_browser.installEventFilter(self)
        self.library_list_browser.currentLibraryChanged.connect(self.library_browser.setLibrary)
        selection_model = self.library_browser.view.selectionModel()
        selection_model.selectionChanged.connect(self.updateStatusBar)
        self.show_materials_toggle.toggled.connect(self.library_browser.proxy_model.showMaterials)
        self.show_textures_toggle.toggled.connect(self.library_browser.proxy_model.showTextures)
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
        self.add_texture_action = None
        self.add_from_folder_action = None
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
        self.mark_library_as_favorite_action = None
        self.edit_library_action = None
        self.remove_library_action = None
        self.library_menu = None

        self.create_material_action = None
        self.create_material_and_assign_action = None
        self.generate_material_thumbnail_action = None
        self.save_item_thumbnail_action = None
        self.set_custom_material_thumbnail_action = None
        self.copy_item_path_action = None
        self.open_item_location_action = None
        self.show_material_textures_action = None
        self.mark_item_as_favorite_action = None
        self.edit_item_action = None
        self.remove_item_action = None
        self.material_menu = None
        self.texture_menu = None

        self.createActions()
        self.createMainMenu()
        self.createLibraryContextMenu()
        self.library_list_browser.view.customContextMenuRequested.connect(self.onLibraryContextMenuRequested)

        self.createMaterialContextMenu()
        self.createTextureContextMenu()
        self.library_browser.view.customContextMenuRequested.connect(self.onLibraryBrowserContextMenuRequested)

        self.updateTargetNetworkList()
        self.reloadContent()

        self.statusBar().setSizeGripEnabled(False)

    def createActions(self):
        self.open_settings_action = QAction(hou.qt.Icon('LOP_rendersettings', 16, 16), 'Settings...', self)

        self.reload_action = QAction(hou.qt.Icon('NETVIEW_reload', 16, 16), 'Reload', self)
        self.reload_action.triggered.connect(self.reloadContent)

        self.add_material_action = QAction(hou.qt.Icon('LOP_materiallibrary', 16, 16), 'Add material...', self)
        self.add_material_action.triggered.connect(self.onAddMaterial)

        self.add_texture_action = QAction(hou.qt.Icon('SOP_texture', 16, 16), 'Add texture...', self)
        self.add_texture_action.triggered.connect(self.onAddTexture)

        self.add_from_folder_action = QAction(hou.qt.Icon('BUTTONS_import_library', 16, 16), 'Add from folder...', self)
        self.add_from_folder_action.triggered.connect(self.onAddFromFolder)

        self.add_library_action = QAction(hou.qt.Icon('DATATYPES_styles_folder', 16, 16), 'Add library...', self)
        self.add_library_action.triggered.connect(self.onAddLibrary)

        self.update_thumbnails_action = QAction(hou.qt.Icon('NODEFLAGS_render', 16, 16), 'Update thumbnails', self)

        self.edit_tags_action = QAction(hou.qt.Icon('BUTTONS_tag', 16, 16), 'Edit tags', self)

        self.generate_library_thumbnails_action = QAction('Generate thumbnails...', self)
        self.generate_library_thumbnails_action.triggered.connect(self.generateLibraryThumbnails)

        self.open_library_location_action = QAction('Open location...', self)
        self.open_library_location_action.triggered.connect(self.openCurrentLibraryLocation)
        self.open_library_location_action.setShortcut(QKeySequence('Ctrl+L'))
        self.open_library_location_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.library_list_browser.addAction(self.open_library_location_action)

        self.assemble_library_action = QAction('Assemble...', self)

        self.mark_library_as_favorite_action = QAction('Mark as favorite', self)
        self.mark_library_as_favorite_action.triggered.connect(self.onMarkLibraryAsFavorite)

        self.edit_library_action = QAction('Edit...', self)
        self.edit_library_action.triggered.connect(self.editLibrary)
        self.edit_library_action.setShortcut(QKeySequence('Ctrl+E'))
        self.edit_library_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.library_list_browser.addAction(self.edit_library_action)

        self.remove_library_action = QAction('Remove...', self)
        self.remove_library_action.triggered.connect(self.onRemoveLibrary)
        self.remove_library_action.setShortcut(QKeySequence.Delete)
        self.remove_library_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.library_list_browser.addAction(self.remove_library_action)

        self.create_material_action = QAction('Create material\t[Ctrl]', self)
        self.create_material_action.triggered.connect(self.createMaterial)

        self.create_material_and_assign_action = QAction('Create material and assign\t[Ctrl]', self)
        self.create_material_and_assign_action.triggered.connect(self.createMaterialAndAssign)

        self.generate_material_thumbnail_action = QAction('Generate thumbnail', self)
        self.generate_material_thumbnail_action.triggered.connect(self.generateItemThumbnails)

        self.save_item_thumbnail_action = QAction('Save thumbnail...', self)
        self.save_item_thumbnail_action.triggered.connect(self.saveItemThumbnail)

        self.set_custom_material_thumbnail_action = QAction('Set custom thumbnail...', self)

        self.copy_item_path_action = QAction('Copy path', self)
        self.copy_item_path_action.triggered.connect(self.copyCurrentItemPath)
        self.copy_item_path_action.setShortcut(QKeySequence.Copy)
        self.copy_item_path_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.library_browser.addAction(self.copy_item_path_action)

        self.open_item_location_action = QAction('Open location...', self)
        self.open_item_location_action.triggered.connect(self.openCurrentItemLocation)
        self.open_item_location_action.setShortcut(QKeySequence('Ctrl+L'))
        self.open_item_location_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.library_browser.addAction(self.open_item_location_action)

        self.show_material_textures_action = QAction('Textures...', self)
        self.show_material_textures_action.triggered.connect(self.onShowMaterialTextures)

        self.mark_item_as_favorite_action = QAction('Mark as favorite', self)
        self.mark_item_as_favorite_action.triggered.connect(self.onMarkItemsAsFavorite)

        self.edit_item_action = QAction('Edit...', self)
        self.edit_item_action.setShortcut(QKeySequence('Ctrl+E'))
        self.edit_item_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.library_browser.addAction(self.edit_item_action)

        self.remove_item_action = QAction('Remove...', self)
        self.remove_item_action.triggered.connect(self.onRemoveItems)
        self.remove_item_action.setShortcut(QKeySequence.Delete)
        self.remove_item_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.library_browser.addAction(self.remove_item_action)

    def createMainMenu(self):
        # self.main_menu = Menu('Main', self)
        # self.menuBar().addMenu(self.main_menu)
        #
        # self.main_menu.addAction(self.open_settings_action)

        self.content_menu = Menu('Content', self)
        self.menuBar().addMenu(self.content_menu)

        self.content_menu.addAction(self.add_library_action)
        self.content_menu.addSeparator()
        # self.content_menu.addAction(self.add_material_action)
        self.content_menu.addAction(self.add_texture_action)
        self.content_menu.addAction(self.add_from_folder_action)
        self.content_menu.addSeparator()
        # self.content_menu.addAction(self.update_thumbnails_action)
        self.content_menu.addAction(self.reload_action)

        # self.tags_menu = Menu('Tags', self)
        # self.menuBar().addMenu(self.tags_menu)
        #
        # self.tags_menu.addAction(self.edit_tags_action)

    def createLibraryContextMenu(self):
        self.library_menu = Menu(self.library_list_browser.view)
        self.library_list_browser.view.setContextMenuPolicy(Qt.CustomContextMenu)

        self.library_menu.addAction(self.generate_library_thumbnails_action)
        self.library_menu.addSeparator()
        self.library_menu.addAction(self.open_library_location_action)
        # self.library_menu.addAction(self.assemble_library_action)
        self.library_menu.addSeparator()
        # self.library_menu.addAction(self.mark_library_as_favorite_action)
        self.library_menu.addAction(self.edit_library_action)
        self.library_menu.addAction(self.remove_library_action)

    def updateLibraryContextMenu(self):
        pass

    def onLibraryContextMenuRequested(self):
        if not self.library_list_browser.hasSelection():
            return

        self.updateLibraryContextMenu()
        self.library_menu.exec_(QCursor.pos())

    def createMaterialContextMenu(self):
        self.material_menu = Menu(self.library_browser.view)
        self.library_browser.view.setContextMenuPolicy(Qt.CustomContextMenu)

        self.material_menu.addAction(self.create_material_action)
        self.material_menu.addAction(self.create_material_and_assign_action)
        self.material_menu.addSeparator()
        self.material_menu.addAction(self.generate_material_thumbnail_action)
        self.material_menu.addAction(self.save_item_thumbnail_action)
        # self.material_menu.addAction(self.set_custom_material_thumbnail_action)
        self.material_menu.addSeparator()
        self.material_menu.addAction(self.show_material_textures_action)
        self.material_menu.addAction(self.open_item_location_action)
        self.material_menu.addAction(self.copy_item_path_action)
        self.material_menu.addSeparator()
        self.material_menu.addAction(self.mark_item_as_favorite_action)
        # self.material_menu.addAction(self.edit_material_action)
        self.material_menu.addAction(self.remove_item_action)

    def updateMaterialContextMenu(self):
        pass

    def showMaterialContextMenu(self):
        self.updateMaterialContextMenu()
        self.material_menu.exec_(QCursor.pos())

    def createTextureContextMenu(self):
        self.texture_menu = Menu(self.library_browser.view)
        self.library_browser.view.setContextMenuPolicy(Qt.CustomContextMenu)

        self.texture_menu.addAction(self.generate_material_thumbnail_action)
        self.texture_menu.addAction(self.save_item_thumbnail_action)
        # self.texture_menu.addAction(self.set_custom_material_thumbnail_action)
        self.texture_menu.addSeparator()
        self.texture_menu.addAction(self.open_item_location_action)
        self.texture_menu.addAction(self.copy_item_path_action)
        self.texture_menu.addSeparator()
        self.texture_menu.addAction(self.mark_item_as_favorite_action)
        # self.texture_menu.addAction(self.edit_material_action)
        self.texture_menu.addAction(self.remove_item_action)

    def updateTextureContextMenu(self):
        pass

    def showTextureContextMenu(self):
        self.updateTextureContextMenu()
        self.texture_menu.exec_(QCursor.pos())

    def onLibraryBrowserContextMenuRequested(self):
        if not self.library_browser.hasSelection():
            return

        item = self.library_browser.currentItem()
        if isinstance(item, Material):
            self.showMaterialContextMenu()
        elif isinstance(item, TextureMap):
            self.showTextureContextMenu()

    def updateEngineBuilderList(self):
        self.target_builder_combo.clear()

        engine = EngineConnector.currentEngine()
        if not engine:
            self.target_builder_combo.addItem('Auto', None)
            return

        for builder in engine.builders():
            self.target_builder_combo.addItem(builder.name(), builder)

    def onCurrentEngineChanged(self, index):
        EngineConnector.setCurrentEngine(self.target_engine_combo.itemData(index, Qt.UserRole))
        self.updateEngineBuilderList()
        self.library_browser.updateThumbnails()

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

    def reloadContent(self):
        self.library_list_browser.reloadContent()
        self.library_browser.reloadContent()

    def onAddLibrary(self):
        window = AddLibraryDialog(hou.qt.mainWindow())
        try:
            if window.exec_():
                Library.addLibrary(window.options())
                self.library_list_browser.reloadContent()
        finally:
            window.deleteLater()

    def onAddMaterial(self):
        raise NotImplementedError

    def onAddTexture(self):
        pass

    def onAddFromFolder(self):
        window = AddFolderContentDialog(hou.qt.mainWindow())
        if window.exec_():
            options = window.options()
            if options['add_to'] == Target.NoLibrary:
                library = None
            elif options['add_to'] == Target.NewLibrary:
                library = Library.fromData({'name': window.library_name_field.text()})
                Library.addLibrary(library)
            elif options['add_to'] == Target.ExistingLibrary:
                library = options['existing_library']

            if options['add_materials']:
                materials = Material.addMaterialsFromFolder(options['path'],
                                                            None,
                                                            library,
                                                            options['mark_materials_as_favorite'])
            if options['add_textures']:
                textures = TextureMap.addTexturesFromFolder(options['path'],
                                                            None,
                                                            library,
                                                            options['mark_textures_as_favorite'])
            if options['add_materials'] and options['material_thumbnails']:
                updateMaterialThumbnails(materials)
            if options['add_textures'] and options['texture_thumbnails']:
                updateTextureThumbnails(textures)
            self.reloadContent()
        window.deleteLater()

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
        builder = self.target_builder_combo.currentData()
        if builder is None:
            engine = EngineConnector.currentEngine()
            if engine:
                builders = engine.builders()
                if builders:
                    builder = builders[0]  # Todo: Take it by options

        root = self.target_network_combo.currentData()
        if root is None:
            selected_nodes = hou.selectedNodes()
            if selected_nodes:
                node = selected_nodes[0]
                if node.childTypeCategory() == hou.vopNodeTypeCategory():
                    root = node
        if root is None:
            root = hou.root().node('mat')

        options = None
        if QApplication.queryKeyboardModifiers() == Qt.ControlModifier or not builder:
            window = BuildOptionsWindow(builder, self)
            if not window.exec_():
                return

            options = window.options()
            builder = options['builder']

        nodes = []
        for material in self.library_browser.selectedMaterials():
            material_node = builder.build(material, root, options=options)
            material_node.moveToGoodPosition()
            nodes.append(material_node)

        if len(nodes) == 1:
            QApplication.clipboard().setText(nodes[0].path())
        return tuple(nodes)

    def createMaterialAndAssign(self):
        material_nodes = self.createMaterial()
        if not material_nodes:
            return
        selected_nodes = hou.selectedNodes()
        for mat_node, obj_node in zip(material_nodes, selected_nodes):
            obj_node.parm('shop_materialpath').set(mat_node.path())

    def generateLibraryThumbnails(self):
        materials = (mat for lib in self.library_list_browser.selectedLibraries() for mat in lib.materials())
        updateMaterialThumbnails(materials)
        textures = (tex for lib in self.library_list_browser.selectedLibraries() for tex in lib.textures())
        updateTextureThumbnails(textures)
        self.library_browser.reloadContent(True)

    def generateItemThumbnails(self):
        updateMaterialThumbnails(self.library_browser.selectedMaterials())
        updateTextureThumbnails(self.library_browser.selectedTextures())
        self.library_browser.reloadContent(True)

    def generateTextureThumbnail(self):
        texture = self.library_browser.currentItem()
        window = GenerateTextureThumbnailWindow(texture)
        window.exec_()

    def saveItemThumbnail(self):
        item = self.library_browser.currentItem()
        if not item.thumbnail():
            return

        if isinstance(item, Material):
            path = item.path() + '/' + item.name()
        else:
            path = item.path()
        path, _ = QFileDialog.getSaveFileName(self, 'Save thumbnail', path, 'Image (*.png *.jpg);; Any (*.*)')
        if not path:
            return
        item.thumbnail().pixmap(256).save(path)

    def copyCurrentItemPath(self):
        item = self.library_browser.currentItem()
        if isinstance(item, TextureMap):
            path = item.path(engine=EngineConnector.currentEngine())
        else:
            path = item.path()
        if path:
            QApplication.clipboard().setText(path)

    def openCurrentItemLocation(self):
        item = self.library_browser.currentItem()
        if isinstance(item, Material) and item.source().path():
            openLocation(item.source().path())
        elif isinstance(item, TextureMap):
            openLocation(item.path(), select=True)

    def onShowMaterialTextures(self):
        material = self.library_browser.currentItem()
        window = TextureListBrowser(self)
        window.model.setTextureList(material.textureMaps())
        window.show()

    def onMarkLibraryAsFavorite(self):
        connection = connect()
        connection.execute('BEGIN')

        for library in self.library_list_browser.selectedLibraries():
            library.markAsFavorite(not library.isFavorite(), external_connection=connection)

        connection.commit()
        connection.close()
        self.library_list_browser.reloadContent()

    def editLibrary(self):
        library = self.library_list_browser.currentLibrary()
        if not library:
            return

        window = EditLibraryWindow(self)
        window.setOptions(library.asData())

        if not window.exec_():
            return

        # Todo

    def onMarkItemsAsFavorite(self):
        connection = connect()
        connection.execute('BEGIN')

        state = not self.library_browser.currentItem().isFavorite()
        for item in self.library_browser.selectedItems():
            item.markAsFavorite(state, external_connection=connection)

        connection.commit()
        connection.close()
        self.library_browser.reloadContent()

    def onRemoveLibrary(self):
        connection = connect()
        connection.execute('BEGIN')

        libraries = self.library_list_browser.selectedLibraries()

        window = RemoveLibraryOptionsWindow(libraries)
        try:
            if not window.exec_():
                return
            options = window.options()
        finally:
            window.deleteLater()

        for library in libraries:
            library.remove(remove_materials=options['remove_materials'],
                           only_single_bound_materials=options['only_single_bound_materials'],
                           remove_textures=options['remove_textures'],
                           only_single_bound_textures=options['only_single_bound_textures'],
                           external_connection=connection)

        connection.commit()
        connection.close()
        self.reloadContent()

    def onRemoveItems(self):
        items = self.library_browser.selectedItems()
        library = self.library_browser.library()

        current_item = self.library_browser.currentItem()
        if isinstance(current_item, Material):
            window = RemoveMaterialOptionsWindow(items, library)
        elif isinstance(current_item, TextureMap):
            window = RemoveTextureOptionsWindow(items, library)
        else:
            raise TypeError

        try:
            if not window.exec_():
                return
            else:
                options = window.options()
        finally:
            window.deleteLater()

        connection = connect()
        connection.execute('BEGIN')

        if options['only_from_this_library']:
            for item in items:
                library.removeItem(item, external_connection=connection)
        else:
            for item in items:
                item.remove(external_connection=connection)

        connection.commit()
        connection.close()
        self.library_browser.reloadContent()
        window.deleteLater()

    def eventFilter(self, watched, event):
        if watched == self.target_network_combo:
            if event.type() == QEvent.MouseButtonPress:
                self.updateTargetNetworkList()
        elif watched == self.library_browser:
            if event.type() == QEvent.KeyPress:
                if event.matches(QKeySequence.Find) or event.matches(QKeySequence.FindNext):
                    self.search_field.setFocus()
                    self.search_field.selectAll()
                    return True
                elif event.matches(QKeySequence.ZoomIn):
                    self.library_browser.view.zoomIn()
                    return True
                elif event.matches(QKeySequence.ZoomOut):
                    self.library_browser.view.zoomOut()
                    return True
                elif event.matches(QKeySequence.Refresh):
                    self.library_browser.reloadContent()
                    return True
        return False
