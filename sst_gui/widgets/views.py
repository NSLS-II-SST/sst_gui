from .motor import MotorControl, MotorMonitor
from .monitors import PVMonitor, PVMonitorHBoxLayout, PVMonitorVBoxLayout
from .energy import EnergyControl, EnergyMonitor
from .gatevalve import GVControl, GVControlBox, GVMonitor
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox, QMenu, QAction


def AutoMonitor(model, orientation="h"):
    mtype = model.default_monitor
    if mtype == "PVMonitor":
        return PVMonitor(model, orientation)
    elif mtype == "MotorMonitor":
        return MotorMonitor(model, orientation)
    elif mtype == "GVMonitor":
        return GVMonitor(model)


def AutoControl(model, orientation="h"):
    mtype = model.default_controller
    if mtype == "MotorControl":
        return MotorControl(model, orientation)
    elif mtype == "GVControl":
        return GVControl(model)


class AutoControlBox(QGroupBox):
    """
    GVControlBox is a widget that creates a view around GVModels.
    It takes a dictionary 'shutters' as an argument, where the values are GVModel objects.
    It provides a control interface for each GVModel in the 'shutters' dictionary.
    """

    def __init__(self, modelDict, title, orientation="h"):
        """
        Initializes the GVControlBox widget.
        Args:
            shutters (dict): A dictionary where the values are GVModel objects.
            *args: Variable length argument list passed to the QGroupBox init method.
            **kwargs: Arbitrary keyword arguments passed to the QGroupBox init method.
        """
        super().__init__(title)
        self.widgets = {}
        if orientation == "h":
            self.box = QHBoxLayout()
            widget_orientation = "v"
        else:
            self.box = QVBoxLayout()
            widget_orientation = "h"
        for k, m in modelDict.items():
            widget = AutoControl(m, widget_orientation)
            self.widgets[k] = widget
            self.box.addWidget(widget)
            widget.setVisible(getattr(m, "visible", True))

        self.setLayout(self.box)

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)

        for widget_name, widget in self.widgets.items():
            action = QAction(widget_name, self)
            action.setCheckable(True)
            action.setChecked(widget.isVisible())
            action.triggered.connect(lambda checked, w=widget: w.setVisible(checked))
            contextMenu.addAction(action)

        # show the context menu at the event's position
        contextMenu.exec_(event.globalPos())


class AutoMonitorBox(QGroupBox):
    """
    GVControlBox is a widget that creates a view around GVModels.
    It takes a dictionary 'shutters' as an argument, where the values are GVModel objects.
    It provides a control interface for each GVModel in the 'shutters' dictionary.
    """

    def __init__(self, modelDict, title, orientation="h"):
        """
        Initializes the GVControlBox widget.
        Args:
            shutters (dict): A dictionary where the values are GVModel objects.
            *args: Variable length argument list passed to the QGroupBox init method.
            **kwargs: Arbitrary keyword arguments passed to the QGroupBox init method.
        """
        super().__init__(title)
        self.widgets = {}
        if orientation == "h":
            self.box = QHBoxLayout()
            widget_orientation = "v"
        else:
            self.box = QVBoxLayout()
            widget_orientation = "h"
        for k, m in modelDict.items():
            widget = AutoMonitor(m, widget_orientation)
            self.widgets[k] = widget
            self.box.addWidget(widget)
            widget.setVisible(getattr(m, "visible", True))
        self.setLayout(self.box)

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)

        for widget_name, widget in self.widgets.items():
            action = QAction(widget_name, self)
            action.setCheckable(True)
            action.setChecked(widget.isVisible())
            action.triggered.connect(lambda checked, w=widget: w.setVisible(checked))
            contextMenu.addAction(action)

        # show the context menu at the event's position
        contextMenu.exec_(event.globalPos())
