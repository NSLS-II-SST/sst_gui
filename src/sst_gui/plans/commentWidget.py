from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QDialog,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QSizePolicy,
    QListWidget,
    QListWidgetItem,
)

from qtpy.QtCore import Signal, Qt


class CommentWidget(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.label = QLabel("Scan Comment")
        self.comment = QLineEdit()
        layout.addWidget(self.label)
        layout.addWidget(self.comment)
        self.setLayout(layout)

    def getComment(self):
        return self.comment.getText()
