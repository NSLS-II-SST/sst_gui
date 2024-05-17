from qtpy.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QVBoxLayout,
)

from ..widgets.views import AutoControlBox, AutoControlCombo, AutoControl
import time


class MotorTab(QWidget):
    name = "Motor Control"

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # run_engine = model.run_engine
        # user_status = model.user_status
        beamline = model.beamline
        print("Initializing Motor Control Tab")
        vbox = QVBoxLayout()
        vbox.addWidget(AutoControlBox(beamline.shutters, "Shutters", model))
        vbox.addWidget(AutoControlCombo(beamline.motors, "Choose a Motor", model))
        vbox.addWidget(AutoControl(beamline.energy, model))
        hbox = QHBoxLayout()
        print("Real Manipulator")
        hbox.addWidget(
            AutoControlBox(
                beamline.primary_manipulator.real_axes_models, "Real Axes", model, "v"
            )
        )
        print("Pseudo Manipulator")
        time.sleep(2.0)
        print("Sleep Done")
        hbox.addWidget(
            AutoControlBox(
                beamline.primary_manipulator.pseudo_axes_models,
                "Pseudo Axes",
                model,
                "v",
            )
        )
        vbox.addLayout(hbox)
        vbox.addStretch()
        self.setLayout(vbox)
