from bluesky_widgets.apps.queue_monitor.widgets import (
    QtRunEngineManager_Editor,
    QtRunEngineManager_Monitor,
)
from qtpy.QtWidgets import QTabWidget
from .tabs.monitorTab import MonitorTab


class QtViewer(QTabWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        self.setTabPosition(QTabWidget.North)

        self._re_manager_monitor = QtRunEngineManager_Monitor(model.run_engine)
        self.addTab(self._re_manager_monitor, "Monitor Queue")

        self._re_manager_editor = QtRunEngineManager_Editor(model.run_engine)
        self.addTab(self._re_manager_editor, "Edit and Control Queue")

        self._bl_status_monitor = MonitorTab(model)
        self.addTab(self._bl_status_monitor, "Beamline Status")

        # self._bl_interactive = InteractiveTab(model)
        # self.addTab(self._bl_interactive, "Beamline Control")

        # self._bl_sample_monitor = QtSampleView(model.user_status)
        # self.addTab(self._bl_sample_monitor, "Samples")
