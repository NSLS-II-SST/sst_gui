from bluesky_widgets.models.run_engine_client import RunEngineClient
from bluesky_widgets.qt import Window
from bluesky_widgets.qt.threading import wait_for_workers_to_quit, active_thread_count
from .models import UserStatus
from .confEdit import ConfigEditor

from .settings import SETTINGS
from .mainWidget import QtViewer

from qtpy.QtWidgets import QAction, QApplication

from .models import BeamlineModel


class CustomWindow(Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("CustomWindow created")

    def update_widget(self, new_qt_widget):
        # Remove the old widget from the layout
        self._qt_center.layout().removeWidget(self.qt_widget)
        self.qt_widget.setParent(None)  # Ensure the old widget is not visible
        self.qt_widget.deleteLater()
        QApplication.processEvents()
        # Add the new widget to the layout
        self._qt_center.layout().addWidget(new_qt_widget)

        # Update the reference
        self.qt_widget = new_qt_widget


class ViewerModel:
    """
    This encapsulates on the models in the application.
    """

    def __init__(self):
        print("Initializing ViewerModel")
        self.init_beamline()

    def init_beamline(self):
        print("Initializing Beamline")
        self.run_engine = RunEngineClient(
            zmq_control_addr=SETTINGS.zmq_re_manager_control_addr,
            zmq_info_addr=SETTINGS.zmq_re_manager_info_addr,
            http_server_uri=SETTINGS.http_server_uri,
            http_server_api_key=SETTINGS.http_server_api_key,
        )
        self.user_status = UserStatus(self.run_engine)
        self.beamline = BeamlineModel()


class Viewer(ViewerModel):
    """
    This extends the model by attaching a Qt Window as its view.

    This object is meant to be exposed to the user in an interactive console.
    """

    def __init__(self, *, show=True):
        super().__init__()
        self.init_ui(show)

    def init_ui(self, show):
        print("Initializing UI")
        self._widget = QtViewer(self)
        self._window = CustomWindow(self._widget, show=show)
        # self._window._qt_window.setWindowTitle(title)

        menu_bar = self._window._qt_window.menuBar()
        menu_item_control = menu_bar.addMenu("Control Actions")
        self.action_activate_env_destroy = QAction(
            "Activate 'Destroy Environment'", self._window._qt_window
        )
        self.action_activate_env_destroy.setCheckable(True)
        self._update_action_env_destroy_state()
        self.action_activate_env_destroy.triggered.connect(
            self._activate_env_destroy_triggered
        )
        menu_item_control.addAction(self.action_activate_env_destroy)

        menu_item_config = self._window._qt_window.menuBar().addMenu("Config")
        self.action_edit_config = QAction("Edit Config", self._window._qt_window)
        self.action_edit_config.triggered.connect(self.editConfig)
        menu_item_config.addAction(self.action_edit_config)

        self.action_reload_config = QAction("Reload Config", self._window._qt_window)
        self.action_reload_config.triggered.connect(self.reloadConfig)
        menu_item_config.addAction(self.action_reload_config)

        self._widget.model.run_engine.events.status_changed.connect(
            self.on_update_widgets
        )

    def editConfig(self):
        self.config_editor = ConfigEditor(SETTINGS.config)
        self.config_editor.show()

    def reloadConfig(self):
        # Close the current viewer
        self.init_beamline()
        new_widget = QtViewer(self)
        self._window.update_widget(new_widget)
        self._widget = new_widget

    def _update_action_env_destroy_state(self):
        env_destroy_activated = self._widget.model.run_engine.env_destroy_activated
        self.action_activate_env_destroy.setChecked(env_destroy_activated)

    def _activate_env_destroy_triggered(self):
        env_destroy_activated = self._widget.model.run_engine.env_destroy_activated
        self._widget.model.run_engine.activate_env_destroy(not env_destroy_activated)

    def on_update_widgets(self, event):
        self._update_action_env_destroy_state()

    @property
    def window(self):
        return self._window

    def show(self):
        """Resize, show, and raise the window."""
        self._window.show()

    def close(self):
        """Close the window."""
        print("In close method")
        self._window.close()
        print("After window close in close method")
