from qtpy.QtWidgets import QTabWidget

# from .samplelist import QtSampleView
from .widgets.queueControlTab import QueueControlTab
from .widgets.monitorTab import MonitorTab
from .widgets.planTab import PlanTabWidget
from .widgets.samplelist import SampleTab
from .widgets.motorTab import MotorTab
from .widgets.consoleTab import IPythonConsoleTab


class QtViewer(QTabWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        self.setTabPosition(QTabWidget.North)

        # self._re_manager_monitor = QtRunEngineManager_Monitor(model.run_engine)
        # self.addTab(self._re_manager_monitor, "Monitor Queue")
        # print("Added RE Monitor")
        # self._re_manager_editor = QtRunEngineManager_Editor(model.run_engine)
        # self.addTab(self._re_manager_editor, "Edit and Control Queue")
        self._queue_control = QueueControlTab(model.run_engine)
        self.addTab(self._queue_control, "QueueServer Control")
        print("Added RE Manager")
        self._bl_status_monitor = MonitorTab(model)
        self.addTab(self._bl_status_monitor, "Beamline Status")
        print("Added MonitorTab")
        self._plan_editor = PlanTabWidget(model)
        self.addTab(self._plan_editor, "Plan Editor")
        print("Added PlanEditor")
        self._motor_control = MotorTab(model)
        self.addTab(self._motor_control, "Motor Control")

        """
        self._bl_interactive = InteractiveTab(model)
        self.addTab(self._bl_interactive, "Beamline Control")
    _   """
        self._bl_sample_monitor = SampleTab(model)
        self.addTab(self._bl_sample_monitor, "Samples")
        self._ipython_console = IPythonConsoleTab(model)
        self.addTab(self._ipython_console, "IPython Console")
        print("Added IPython Console")
