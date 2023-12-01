from qtpy.QtWidgets import QApplication, QVBoxLayout, QWidget, QMainWindow
from .loaders import motorFromOphyd
from .widgets.motor import MotorControl


def main():
    app = QApplication([])

    motormodel = motorFromOphyd("tesz")

    layout = QVBoxLayout()
    # layout.addWidget(QLabel("Testing"))
    layout.addWidget(MotorControl(motormodel))

    main_window = QMainWindow()
    central_widget = QWidget()
    central_widget.setLayout(layout)
    main_window.setCentralWidget(central_widget)

    main_window.show()

    app.exec_()


if __name__ == "__main__":
    main()
