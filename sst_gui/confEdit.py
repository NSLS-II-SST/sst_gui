from qtpy.QtWidgets import (
    QApplication,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QAction,
    QFileDialog,
    QMenu,
    QInputDialog,
    QMessageBox,
)
from qtpy.QtCore import Qt
import yaml
import argparse


class ConfigEditor(QMainWindow):
    def __init__(self, config_file):
        super().__init__()

        self.config_file = config_file
        self.config_changed = False

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Key", "Value"])
        self.tree.itemChanged.connect(self.handleItemChanged)
        self.tree.itemChanged.connect(self.setConfigChanged)

        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.loadConfig()

        # Create a top menu bar
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Add save action
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.saveConfig)
        self.file_menu.addAction(save_action)

        # Add save as action
        save_as_action = QAction("Save As", self)
        save_as_action.triggered.connect(self.saveConfigAs)
        self.file_menu.addAction(save_as_action)

    def setConfigChanged(self, item, column):
        self.config_changed = True

    def closeEvent(self, event):
        if self.config_changed:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)
        items = self.tree.selectedItems()
        item = items[0]
        keys = self.get_keys(item)
        depth = len(keys)

        if depth <= 1:
            # Add new key/value action
            new_section = QAction("New Section", self)
            new_section.triggered.connect(self.newSection)
            new_device = QAction("New Device", self)
            new_device.triggered.connect(lambda: self.newDevice(item, keys))
            contextMenu.addAction(new_section)
            contextMenu.addAction(new_device)
        elif depth == 2:
            new_device = QAction("New Device", self)
            new_device.triggered.connect(
                lambda: self.newDevice(item.parent(), keys[:-1])
            )
            new_action = QAction("New Key/Value", self)
            new_action.triggered.connect(lambda: self.newKeyValue(item, keys))
            contextMenu.addAction(new_device)
            contextMenu.addAction(new_action)
        elif depth == 3:
            new_action = QAction("New Key/Value", self)
            new_action.triggered.connect(
                lambda: self.newKeyValue(item.parent(), keys[:-1])
            )
            contextMenu.addAction(new_action)
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.deleteItem(item, keys))
        contextMenu.addAction(delete_action)
        contextMenu.exec_(event.globalPos())

    def loadConfig(self):
        with open(self.config_file, "r") as file:
            self.config = yaml.safe_load(file)

        self.fillTree(self.config)

    def fillTree(self, parent, item=None):
        if item is None:
            item = self.tree.invisibleRootItem()

        for key, value in parent.items():
            child = QTreeWidgetItem()
            child.setText(0, str(key))
            child.setFlags(child.flags() | Qt.ItemIsEditable)

            if isinstance(value, dict):
                self.fillTree(value, child)
            else:
                child.setText(1, str(value))

            item.addChild(child)

    def get_keys(self, item):
        keys = []
        while item is not None:
            keys.append(str(item.text(0)))
            item = item.parent()
        return keys[::-1]

    def deleteItem(self, item, keys):
        reply = QMessageBox.question(
            self,
            "Delete Item",
            "Are you sure you want to delete this item and all its children?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Remove the item from the tree
            parent = item.parent()
            if parent is not None:
                parent.removeChild(item)
            else:
                # The item is a top-level item
                self.tree.invisibleRootItem().removeChild(item)

            # Remove the corresponding key/value pair from the config
            config = self.config
            for key in keys[:-1]:
                config = config[key]
            del config[keys[-1]]

            self.config_changed = True

    def newSection(self):
        newkey, ok = QInputDialog.getText(self, "New Section", "Enter section name:")
        if ok:
            root = self.tree.invisibleRootItem()
            child = QTreeWidgetItem()
            child.setText(0, newkey)
            child.setFlags(child.flags() | Qt.ItemIsEditable)
            root.addChild(child)
            self.config[newkey] = {}
            self.config_changed = True

    def newDevice(self, item, keys):
        newkey, ok = QInputDialog.getText(self, "New Device", "Enter device name:")
        if ok:
            child = QTreeWidgetItem()
            child.setText(0, newkey)
            child.setFlags(child.flags() | Qt.ItemIsEditable)
            item.addChild(child)
            config = self.config
            for key in keys:
                config = self.config[key]
            config[newkey] = {}
            self.config_changed = True

    def newKeyValue(self, item, keys):
        # Get the item at the position

        newkey, ok = QInputDialog.getText(self, "New Key", "Enter key:")
        if ok:
            value, ok = QInputDialog.getText(self, "New Value", "Enter value:")
            if ok:
                # Add the new key/value pair to the item's value in the config
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                config = self.config
                for key in keys:
                    config = config[key]
                try:
                    config[newkey] = value

                    # Add the new key/value pair to the item in the tree
                    child = QTreeWidgetItem()
                    child.setText(0, newkey)
                    child.setText(1, value)
                    item.addChild(child)
                    self.config_changed = True
                except TypeError:
                    QMessageBox.warning(
                        self,
                        "Invalid Operation",
                        "New keys can only be added to dictionaries",
                    )

    def handleItemChanged(self, item, column):
        keys = self.get_keys(item)
        value = item.text(1)
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False

        if column == 0:
            # Key was changed
            pass  # Implement key change logic here
        elif column == 1:
            # Value was changed
            # Update the value in the config dictionary
            config = self.config
            for key in keys[:-1]:  # Traverse to the correct level in the config
                config = config[key]
            config[keys[-1]] = value  # Set the new value

    def saveConfig(self):
        with open(self.config_file, "w") as file:
            yaml.safe_dump(self.config, file)
        self.config_changed = False

    def saveConfigAs(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            "QFileDialog.getSaveFileName()",
            "",
            "All Files (*);;Text Files (*.txt)",
            options=options,
        )
        if fileName:
            with open(fileName, "w") as file:
                yaml.safe_dump(self.config, file)
        self.config_changed = False


def main():
    parser = argparse.ArgumentParser(description="Config file editor.")
    parser.add_argument("config_file", type=str, help="Path to the config file")

    args = parser.parse_args()

    app = QApplication([])

    editor = ConfigEditor(args.config_file)
    editor.show()

    app.exec_()


if __name__ == "__main__":
    main()
