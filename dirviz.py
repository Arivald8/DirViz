"""
Directory Tree Generator (DirViz)
==================================

A Qt-based GUI application for generating 
and visualizing directory tree structures.

Requirements:
------------
- Python 3.6+
- PySide6

Usage:
-----
Run the script directly:
    python dirviz.py

The application will open a window where you can:
1. Click "Browse" to select a directory
2. Use the tree view to select/deselect files and directories
3. Click "Generate Tree" to create the text representation
4. Use "Copy to Clipboard" to copy the result

Author: Arivald8
License: MIT
Version: 1.0.0
"""

import sys
import os

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QLabel, QSizePolicy, QHeaderView, QMessageBox,
    QStyle, QTreeWidgetItemIterator, QMenuBar
)
from PySide6.QtGui import QColor, QPalette, QAction
from PySide6.QtCore import Qt, QDir, QSettings

# Tree structure characters
BRANCH_MID = "├── "
BRANCH_END = "└── "
BRANCH_VERT = "│   "
BRANCH_SPACE = "    "


class DirectoryTreeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Directory Tree Generator")
        self.setGeometry(100, 100, 850, 750)
        self.current_dir = ""
        self.settings = QSettings("MyCompany", "DirVizApp")

        # Theme Setup
        self.light_palette = QPalette()
        self.dark_palette = QPalette()
        self.setup_light_palette()
        self.setup_dark_palette()
        self.current_theme = "light"  # Default theme

        # Menu Bar
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        view_menu = self.menu_bar.addMenu("&View")
        self.theme_action = QAction("Switch to Dark Mode", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)

        # Main Widget and Layout
        main_widget = QWidget(self)
        main_widget.setObjectName("mainWidget")
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Directory Selection Section
        dir_select_layout = QHBoxLayout()
        self.dir_label = QLabel("Selected Directory:")
        self.dir_path_edit = QLineEdit()
        self.dir_path_edit.setPlaceholderText(
            "Select a directory using the 'Browse' button")
        self.dir_path_edit.setReadOnly(True)
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.select_directory)

        dir_select_layout.addWidget(self.dir_label)
        dir_select_layout.addWidget(self.dir_path_edit, 1)
        dir_select_layout.addWidget(self.browse_button)
        main_layout.addLayout(dir_select_layout)

        # Tree View Section
        tree_label = QLabel("Select Files and Directories:")
        main_layout.addWidget(tree_label)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(1)
        self.tree_widget.setHeaderLabels(["Name"])
        self.tree_widget.header().setSectionResizeMode(QHeaderView.Stretch)
        self.tree_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.itemChanged.connect(self.handle_item_change)
        main_layout.addWidget(self.tree_widget, 1)

        # Select/Deselect All Buttons
        select_buttons_layout = QHBoxLayout()
        select_buttons_layout.addStretch()
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(
            lambda: self.toggle_all_items(Qt.Checked))
        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.clicked.connect(
            lambda: self.toggle_all_items(Qt.Unchecked))
        select_buttons_layout.addWidget(self.select_all_button)
        select_buttons_layout.addWidget(self.deselect_all_button)
        main_layout.addLayout(select_buttons_layout)

        # Results Section
        results_label = QLabel("Generated Tree Structure:")
        main_layout.addWidget(results_label)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(200)
        self.results_text.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.results_text.setFontFamily("monospace")
        main_layout.addWidget(self.results_text)

        # Action Buttons Section
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.addStretch()
        self.generate_button = QPushButton("Generate Tree")
        self.copy_button = QPushButton("Copy to Clipboard")

        self.generate_button.clicked.connect(self.generate_tree_text)
        self.copy_button.clicked.connect(self.copy_to_clipboard)

        action_buttons_layout.addWidget(self.generate_button)
        action_buttons_layout.addWidget(self.copy_button)
        main_layout.addLayout(action_buttons_layout)

        self.statusBar().showMessage("Ready")

        self.load_settings()
        self.update_button_states()

    # Theme Methods
    def setup_light_palette(self):
        """Configures the light QPalette explicitly."""
        self.light_palette.setColor(QPalette.Window, QColor(240, 240, 240))
        self.light_palette.setColor(QPalette.WindowText, Qt.black)
        self.light_palette.setColor(QPalette.Base, Qt.white)
        self.light_palette.setColor(
            QPalette.AlternateBase, QColor(233, 233, 233))
        self.light_palette.setColor(QPalette.ToolTipBase, Qt.white)
        self.light_palette.setColor(QPalette.ToolTipText, Qt.black)
        self.light_palette.setColor(QPalette.Text, Qt.black)
        self.light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
        self.light_palette.setColor(QPalette.ButtonText, Qt.black)
        self.light_palette.setColor(QPalette.BrightText, Qt.red)
        self.light_palette.setColor(QPalette.Link, QColor(0, 0, 255))
        self.light_palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        self.light_palette.setColor(QPalette.HighlightedText, Qt.white)

        # Disabled states for light theme
        disabled_text = QColor(160, 160, 160)
        # Slightly different background for disabled button
        disabled_button = QColor(200, 200, 200)
        self.light_palette.setColor(
            QPalette.Disabled, QPalette.Text, disabled_text)
        self.light_palette.setColor(
            QPalette.Disabled, QPalette.WindowText, disabled_text)
        self.light_palette.setColor(
            QPalette.Disabled, QPalette.ButtonText, disabled_text)
        self.light_palette.setColor(
            QPalette.Disabled, QPalette.Button, disabled_button)

    def setup_dark_palette(self):
        """Configures the dark QPalette."""
        self.dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.WindowText, Qt.white)
        self.dark_palette.setColor(QPalette.Base, QColor(42, 42, 42))
        self.dark_palette.setColor(QPalette.AlternateBase, QColor(60, 60, 60))
        self.dark_palette.setColor(
            QPalette.ToolTipBase, QColor(53, 53, 53))  # Dark tooltip
        self.dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        self.dark_palette.setColor(QPalette.Text, Qt.white)
        self.dark_palette.setColor(QPalette.Button, QColor(65, 65, 65))
        self.dark_palette.setColor(QPalette.ButtonText, Qt.white)
        self.dark_palette.setColor(
            QPalette.BrightText, QColor(255, 100, 100))  # Lighter red
        self.dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        self.dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        self.dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        # Disabled states for dark theme
        disabled_color = QColor(127, 127, 127)
        self.dark_palette.setColor(
            QPalette.Disabled, QPalette.Text, disabled_color)
        self.dark_palette.setColor(
            QPalette.Disabled, QPalette.WindowText, disabled_color)
        self.dark_palette.setColor(
            QPalette.Disabled, QPalette.ButtonText, disabled_color)
        self.dark_palette.setColor(QPalette.Disabled, QPalette.Base, QColor(
            48, 48, 48))  # Slightly diff disabled bg
        self.dark_palette.setColor(
            QPalette.Disabled, QPalette.Button, QColor(53, 53, 53))

    def apply_theme(self, theme_name):
        """Applies the specified *defined* theme ('light' or 'dark')."""
        if theme_name == "dark":
            palette_to_apply = self.dark_palette
            self.current_theme = "dark"
            self.theme_action.setText("Switch to Light Mode")
        else:  # Default to defined light theme
            palette_to_apply = self.light_palette
            self.current_theme = "light"
            self.theme_action.setText("Switch to Dark Mode")

        app = QApplication.instance()
        app.setPalette(palette_to_apply)

        if hasattr(self, 'menu_bar'):  # Check if menu_bar has been initialized
            self.menu_bar.setPalette(palette_to_apply)

        self.settings.setValue("theme", self.current_theme)  # Save preference

    def toggle_theme(self):
        """Switches between the defined light and dark themes."""
        if self.current_theme == "light":
            self.apply_theme("dark")
        else:
            self.apply_theme("light")

    def load_settings(self):
        """Loads saved settings, including the theme."""
        saved_theme = self.settings.value(
            "theme", "light")  # Default preference is light
        self.apply_theme(saved_theme)  # Apply the loaded (or default) theme

    def update_button_states(self):
        """Enable/disable buttons based on context."""
        has_dir = bool(self.current_dir)
        has_items = self.tree_widget.topLevelItemCount() > 0
        has_results = bool(self.results_text.toPlainText())
        is_any_selected = False
        if has_items:
            iterator = QTreeWidgetItemIterator(
                self.tree_widget, QTreeWidgetItemIterator.All)
            while iterator.value():
                item = iterator.value()
                state = item.checkState(0)
                if state == Qt.Checked or state == Qt.PartiallyChecked:
                    is_any_selected = True
                    break
                iterator += 1

        self.select_all_button.setEnabled(has_items)
        self.deselect_all_button.setEnabled(has_items)
        self.generate_button.setEnabled(has_items and is_any_selected)
        self.copy_button.setEnabled(has_results)
        self.tree_widget.setEnabled(has_dir)

    def select_directory(self):
        """Opens a dialog to select a directory and populates the tree."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Root Directory",
            self.current_dir or QDir.homePath()
        )
        if directory:
            if directory == self.current_dir and self.tree_widget.topLevelItemCount() > 0:
                return

            self.current_dir = directory
            self.dir_path_edit.setText(directory)
            self.results_text.clear()
            self.statusBar().showMessage(f"Loading directory: {directory}...")
            QApplication.processEvents()
            self.populate_tree(directory)
            self.statusBar().showMessage("Directory loaded.", 3000)
            self.update_button_states()

    def populate_tree(self, root_path):
        """Clears and populates the QTreeWidget with directory contents."""
        self.tree_widget.clear()
        self.tree_widget.setUpdatesEnabled(False)
        try:
            self.add_items_recursive(
                self.tree_widget.invisibleRootItem(), root_path)
        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Could not read directory:\n{e}")
            self.current_dir = ""
            self.dir_path_edit.clear()
        finally:
            self.tree_widget.setUpdatesEnabled(True)
            self.tree_widget.expandToDepth(0)
            self.update_button_states()

    def add_items_recursive(self, parent_item, dir_path):
        """Recursively adds items from a directory to the tree."""
        try:
            qdir = QDir(dir_path)
            qdir.setFilter(QDir.Files | QDir.Dirs | QDir.NoDotAndDotDot)
            qdir.setSorting(QDir.DirsFirst | QDir.Name | QDir.IgnoreCase)
            entries = qdir.entryInfoList()

        except Exception as e:
            error_item = QTreeWidgetItem(
                parent_item, [f"Error Accessing: {os.path.basename(dir_path)}"])
            error_item.setData(0, Qt.UserRole, dir_path)
            error_item.setFlags(Qt.ItemIsEnabled)
            error_color = QApplication.palette().color(QPalette.BrightText)
            error_item.setForeground(0, error_color)
            error_item.setToolTip(0, f"Could not read directory: {e}")
            return

        for entry_info in entries:
            full_path = entry_info.absoluteFilePath()
            entry_name = entry_info.fileName()

            item = QTreeWidgetItem(parent_item, [entry_name])
            item.setData(0, Qt.UserRole, full_path)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable |
                          Qt.ItemIsUserCheckable | Qt.ItemIsAutoTristate)
            item.setCheckState(0, Qt.Checked)

            if entry_info.isDir():
                item.setIcon(0, QApplication.style(
                ).standardIcon(QStyle.SP_DirIcon))
                self.add_items_recursive(item, full_path)
            else:
                item.setIcon(0, QApplication.style(
                ).standardIcon(QStyle.SP_FileIcon))

    def handle_item_change(self, item, column):
        """Update button states when an item's check state changes."""
        if column == 0:
            QApplication.instance().processEvents()
            self.update_button_states()

    def toggle_all_items(self, check_state):
        """Checks or unchecks all items in the tree."""
        try:
            self.tree_widget.itemChanged.disconnect(self.handle_item_change)
        except RuntimeError:
            pass

        iterator = QTreeWidgetItemIterator(
            self.tree_widget, QTreeWidgetItemIterator.All)
        self.tree_widget.setUpdatesEnabled(False)
        while iterator.value():
            item = iterator.value()
            if item.flags() & Qt.ItemIsEnabled and item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(0, check_state)
            iterator += 1
        self.tree_widget.setUpdatesEnabled(True)

        self.tree_widget.itemChanged.connect(self.handle_item_change)
        self.update_button_states()

    def generate_tree_text(self):
        """Generates the text representation of the checked items."""
        self.results_text.clear()
        tree_lines = []
        root_item = self.tree_widget.invisibleRootItem()

        def build_tree_string(item, prefix=""):
            visible_children = []
            for i in range(item.childCount()):
                child = item.child(i)
                if child.checkState(0) != Qt.Unchecked:
                    visible_children.append(child)

            child_count = len(visible_children)

            for i, child in enumerate(visible_children):
                is_last = (i == child_count - 1)
                connector = BRANCH_END if is_last else BRANCH_MID
                line = f"{prefix}{connector}{child.text(0)}"
                tree_lines.append(line)

                if child.childCount() > 0:
                    new_prefix = prefix + \
                        (BRANCH_SPACE if is_last else BRANCH_VERT)
                    build_tree_string(child, new_prefix)

        root_name = os.path.basename(
            self.current_dir) if self.current_dir else "Selected_Items"
        if self.tree_widget.topLevelItemCount() > 0:  # Only add root if tree is populated
            tree_lines.append(f"{root_name}/")
            build_tree_string(root_item)  # Start recursion from invisible root

        if len(tree_lines) > 1:  # More than just the root name line
            self.results_text.setPlainText("\n".join(tree_lines))
        elif len(tree_lines) == 1 and self.current_dir:  # Only root line exists
            # Check if anything was actually selected
            any_selected = False
            iterator = QTreeWidgetItemIterator(
                self.tree_widget, QTreeWidgetItemIterator.Checked | QTreeWidgetItemIterator.PartiallyChecked)
            if iterator.value():
                any_selected = True

            if not any_selected:
                self.results_text.setPlainText(
                    f"{root_name}/\n(No items selected within)")
            else:
                # Only root selected (e.g., empty dir, or all children unchecked)
                self.results_text.setPlainText(
                    tree_lines[0])  # Show just root name
        else:  # No directory loaded or tree is empty
            self.results_text.setPlainText(
                "(No directory loaded or no items selected)")

        self.update_button_states()

    def copy_to_clipboard(self):
        """Copies the content of the results text edit to the clipboard."""
        clipboard = QApplication.clipboard()
        text_to_copy = self.results_text.toPlainText()
        placeholder_messages = [
            "(No items selected)",
            "(No directory loaded or no items selected)",
            f"{os.path.basename(self.current_dir)}/\n(No items selected within)" if self.current_dir else ""
        ]
        # Remove empty strings from placeholder list if current_dir is empty
        placeholder_messages = [msg for msg in placeholder_messages if msg]

        if text_to_copy and text_to_copy not in placeholder_messages:
            clipboard.setText(text_to_copy)
            self.statusBar().showMessage("Tree copied to clipboard!", 2500)
        else:
            self.statusBar().showMessage("Nothing to copy.", 2500)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DirectoryTreeApp()
    window.show()
    sys.exit(app.exec())
