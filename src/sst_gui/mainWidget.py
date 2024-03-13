from qtpy.QtWidgets import QTabWidget
import pkg_resources
import toml
from os.path import exists
from .settings import SETTINGS


class QtViewer(QTabWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        self.setTabPosition(QTabWidget.North)

        if exists(SETTINGS.gui_config):
            with open(SETTINGS.gui_config, "r") as config_file:
                config = toml.load(config_file)
        else:
            config = {}
        tabs_to_include = config.get("gui", {}).get("tabs", {}).get("include", [])
        tabs_to_exclude = config.get("gui", {}).get("tabs", {}).get("exclude", [])

        explicit_inclusion = len(tabs_to_include) > 0
        self.tab_dict = {}
        tabs = pkg_resources.iter_entry_points("sst_gui.tabs")
        for tab_entry_point in tabs:
            tab = tab_entry_point.load()  # Load the modifier function
            if callable(tab):
                # Call the modifier function with model and self (as parent) to get the QWidget
                tab_widget = tab(model)
                if explicit_inclusion and tab_entry_point.name in tabs_to_include:
                    self.tab_dict[tab_entry_point.name] = tab_widget
                elif tab_entry_point.name not in tabs_to_exclude:
                    self.tab_dict[tab_entry_point.name] = tab_widget
                    tabs_to_include.append(tab_entry_point.name)

        for tab_name in tabs_to_include:
            if tab_name in self.tab_dict:
                tab_widget = self.tab_dict[tab_name]
                self.addTab(tab_widget, tab_widget.name)

        """
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
        self._plan_editor2 = PlanTabWidget2(model)
        self.addTab(self._plan_editor2, "Plan Editor2")
        self._motor_control = MotorTab(model)
        self.addTab(self._motor_control, "Motor Control")


        self._bl_interactive = InteractiveTab(model)
        self.addTab(self._bl_interactive, "Beamline Control")

        self._bl_sample_monitor = SampleTab(model)
        self.addTab(self._bl_sample_monitor, "Samples")
        self._ipython_console = IPythonConsoleTab(model)
        self.addTab(self._ipython_console, "IPython Console")
        print("Added IPython Console")
        """
