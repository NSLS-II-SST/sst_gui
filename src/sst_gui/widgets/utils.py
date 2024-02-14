from qtpy.QtWidgets import QFrame
from qtpy.QtWidgets import QWidget
from qtpy.QtGui import QPainter, QColor
from qtpy.QtCore import QSize


class HLine(QFrame):
    """
    Creates a horizontal separator line
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class ByteIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = "grey"
        self.setMinimumSize(QSize(15, 15))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(self.color))
        painter.drawRect(self.rect())

    def setColor(self, color):
        self.color = color
        self.update()  # Trigger a repaint

        class PlaceHolder(QWidget):
            """
            Creates a grey placeholder box with specified dimensions.

            Parameters
            ----------
            width : int
                The width of the placeholder box in pixels.
            height : int
                The height of the placeholder box in pixels.
            parent : Optional[QWidget]
                The parent widget. Default is None.
            """

            def __init__(self, width, height, parent=None):
                super().__init__(parent)
                self.setMinimumSize(QSize(width, height))
                self.setMaximumSize(QSize(width, height))
                self.color = "grey"

            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setBrush(QColor(self.color))
                painter.drawRect(self.rect())
