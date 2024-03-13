from qtpy.QtWidgets import QApplication, QVBoxLayout, QWidget, QMainWindow
from .models import BeamlineModel
from .widgets.gatevalve import GVControlBox
from .widgets.monitors import PVMonitorVBoxLayout
from .widgets.manipulator_monitor import RealManipulatorMonitor
from .widgets.energy import EnergyMonitor
from .widgets.views import AutoMonitorBox, AutoMonitor, AutoControl, AutoControlBox
from .tabs.newPlanTab import PlanTabWidget


def main():
    app = QApplication([])
    # beamline = BeamlineModel(
    #    "/home/jamie/work/visualization/sst_gui/sst_gui/test_config.yaml"
    # )

    layout = QVBoxLayout()
    # layout.addWidget(QLabel("Testing"))
    layout.addWidget(PlanTabWidget(None))

    main_window = QMainWindow()
    central_widget = QWidget()
    central_widget.setLayout(layout)
    main_window.setCentralWidget(central_widget)

    main_window.show()

    app.exec_()


if __name__ == "__main__":
    main()
