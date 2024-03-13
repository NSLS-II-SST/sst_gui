from qtpy.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QMenu,
    QAction,
    QWidget,
    QLabel,
    QComboBox,
    QStackedWidget,
)


def AutoMonitor(model, parent_model, orientation="h"):
    """
    Takes a model, and automatically creates and returns a widget to monitor the model.

    Parameters
    ----------
    model : object
        Any model class that wraps a device.
    parent_model : object
        The full GUI model.
    """
    Monitor = model.default_monitor
    return Monitor(model, parent_model, orientation=orientation)


def AutoControl(model, parent_model, orientation="h"):
    """
    Takes a model, and automatically creates and returns a widget to control the model.

    Parameters
    ----------
    model : object
        Any model class that wraps a device.
    parent_model : object
        The full GUI model.
    """
    Controller = model.default_controller
    return Controller(model, parent_model, orientation=orientation)


class AutoControlBox(QGroupBox):
    """
    A widget that automatically generates control interfaces for a given set of models.
    """

    def __init__(self, models, title, parent_model, orientation="h"):
        """
        Initializes the AutoControlBox widget with a set of models, a title, a parent model, and an orientation.

        Parameters
        ----------
        models : dict, list
            A container with model objects for which control interfaces are to be generated.
        title : str
            The title of the group box.
        parent_model : object
            The parent model for the GUI.
        orientation : str, optional
            The orientation of the control interface box. Can be 'h' for horizontal or 'v' for vertical. Default is 'h'.
        """
        super().__init__(title)
        self.widgets = {}
        if orientation == "h":
            self.box = QHBoxLayout()
            widget_orientation = "v"
        else:
            self.box = QVBoxLayout()
            widget_orientation = "h"
        if isinstance(models, dict):
            for k, m in models.items():
                widget = AutoControl(m, parent_model, widget_orientation)
                self.widgets[k] = widget
                self.box.addWidget(widget)
                widget.setVisible(getattr(m, "visible", True))
        elif isinstance(models, list):
            for m in models:
                widget = AutoControl(m, parent_model, widget_orientation)
                self.widgets[m.label] = widget
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
    A widget that automatically generates a monitor interface for a given set of models.
    """

    def __init__(self, models, title, parent_model, orientation="h"):
        """
        Initializes the AutoMonitorBox widget with a set of models, a title, a parent model, and an orientation.

        Parameters
        ----------
        modelDict : dict
            A dictionary where keys are identifiers and values are model objects to be monitored.
        title : str
            The title of the group box.
        parent_model : object
            The parent model for the GUI.
        orientation : str, optional
            The orientation of the monitor box. Can be 'h' for horizontal or 'v' for vertical. Default is 'h'.
        """
        super().__init__(title)
        self.widgets = {}
        if orientation == "h":
            self.box = QHBoxLayout()
            widget_orientation = "v"
        else:
            self.box = QVBoxLayout()
            widget_orientation = "h"
        if isinstance(models, dict):
            for k, m in models.items():
                widget = AutoMonitor(m, parent_model, widget_orientation)
                self.widgets[k] = widget
                self.box.addWidget(widget)
                widget.setVisible(getattr(m, "visible", True))
        elif isinstance(models, list):
            for m in models:
                widget = AutoMonitor(m, parent_model, widget_orientation)
                self.widgets[m.label] = widget
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


class AutoControlCombo(QWidget):
    def __init__(
        self, modelDict, title, parent_model, *args, orientation="h", **kwargs
    ):
        """
        Initializes an AutoControlCombo widget with a dropdown to select between different models.

        Parameters
        ----------
        modelDict : dict
            A dictionary mapping model names to model instances. These models are used to populate the dropdown and the stacked widget.
        title : str
            The title label for the combo box.
        parent_model : object
            The parent model associated with the GUI. Used for creating AutoControl instances.
        *args
            Variable length argument list for QWidget.
        orientation : str, optional
            The orientation for the AutoControl widgets. Can be 'h' for horizontal or 'v' for vertical. Defaults to 'h'.
        **kwargs
            Arbitrary keyword arguments for QWidget.
        """
        super().__init__(*args, **kwargs)
        controlBox = QHBoxLayout()
        label = QLabel(title)
        dropdown = QComboBox()
        widgetStack = QStackedWidget()
        for key, model in modelDict.items():
            dropdown.addItem(key)
            widgetStack.addWidget(
                AutoControl(model, parent_model, orientation=orientation)
            )
        dropdown.currentIndexChanged.connect(widgetStack.setCurrentIndex)
        controlBox.addWidget(label)
        controlBox.addWidget(dropdown)
        controlBox.addWidget(widgetStack)
        self.setLayout(controlBox)
