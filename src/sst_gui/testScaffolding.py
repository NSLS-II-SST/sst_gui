from qtpy.QtWidgets import QApplication, QVBoxLayout, QWidget, QMainWindow
from .settings import SETTINGS
from .models import BeamlineModel
from .tabs.motorTab import MotorTab
from os.path import join, exists
import toml


def main():
    app = QApplication([])
    profile_dir = "/usr/local/share/ipython/profile_simulation/startup"
    SETTINGS.object_config_file = join(profile_dir, "devices.toml")
    SETTINGS.gui_config_file = join(profile_dir, "gui_config.toml")
    if exists(SETTINGS.gui_config_file):
        with open(SETTINGS.gui_config_file, "r") as config_file:
            SETTINGS.gui_config = toml.load(config_file)
    else:
        SETTINGS.gui_config = {}
    if exists(SETTINGS.object_config_file):
        with open(SETTINGS.object_config_file, "r") as config_file:
            SETTINGS.object_config = toml.load(config_file)
    else:
        SETTINGS.object_config = {}

    beamline = BeamlineModel()

    class simpleModel:
        beamline = None
        run_engine = None
        user_status = None
        settings = None

    model = simpleModel()
    model.settings = SETTINGS
    model.beamline = beamline
    layout = QVBoxLayout()
    # layout.addWidget(QLabel("Testing"))
    layout.addWidget(MotorTab(model))

    main_window = QMainWindow()
    central_widget = QWidget()
    central_widget.setLayout(layout)
    main_window.setCentralWidget(central_widget)

    main_window.show()

    app.exec_()


if __name__ == "__main__":
    main()
