from qtpy.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
    QPushButton,
    QLineEdit,
)
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.manager import QtKernelManager
import sys
import argparse
import subprocess
import os


def get_jupyter_runtime_dir():
    """Get the Jupyter runtime directory."""
    return subprocess.check_output(["jupyter", "--runtime-dir"]).decode("utf-8").strip()


class IPythonConsoleTab(QWidget):
    """
    A QWidget that contains an embedded IPython console.

    Attributes
    ----------
    console : RichJupyterWidget
        The embedded IPython console widget.
    kernel_manager : QtKernelManager
        Manager for the IPython kernel.
    kernel_client : QtKernelClient
        Client for interacting with the kernel.
    """

    name = "IPython Console"

    def __init__(self, kernel_file=None):
        """
        Initializes the IPythonConsoleTab widget, setting up the IPython console,
        kernel manager, and kernel client, and connecting them together.
        """
        super().__init__()
        self.kernel_file = kernel_file

        vbox = QVBoxLayout(self)

        # Create the IPython console widget but do not initialize it yet
        self.console = RichJupyterWidget()
        self.console.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        vbox.addWidget(self.console)

        # Create a QLineEdit for inputting a file path
        self.filePathLineEdit = QLineEdit()
        self.filePathLineEdit.setPlaceholderText("Enter kernel connection file path")
        vbox.addWidget(self.filePathLineEdit)

        # Create a button to connect to the kernel
        self.connectButton = QPushButton("Connect to Kernel")
        vbox.addWidget(self.connectButton)
        self.connectButton.clicked.connect(self.connect_to_kernel)

        self.runCodeButton = QPushButton("Run Hello World")
        self.runCodeButton.clicked.connect(self.run_hello_world)
        vbox.addWidget(self.runCodeButton)
        self.setLayout(vbox)

    def connect_to_kernel(self):
        """
        Connects to the IPython kernel when the button is pressed.
        Prioritizes the file path from the QLineEdit if provided.
        """
        # Use the file path from the QLineEdit if provided, otherwise use the initial kernel_file
        kernel_file = self.filePathLineEdit.text().strip() or self.kernel_file

        if kernel_file:
            self.kernel_manager = QtKernelManager(connection_file=kernel_file)
            self.kernel_manager.load_connection_file()
        else:
            # Start a new kernel if no connection file was provided
            self.kernel_manager = QtKernelManager()
            self.kernel_manager.start_kernel()

        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()

        # Connect the console widget to the kernel
        self.console.kernel_manager = self.kernel_manager
        self.console.kernel_client = self.kernel_client

        # Optionally, disable the button after connecting
        self.connectButton.setEnabled(False)

    def run_hello_world(self):
        """
        Executes the code `print("hello world")` in the IPython console.
        """
        code = 'print("hello world")'
        # Execute the code in the IPython kernel
        self.console.execute(code)


class MainApplicationWindow(QMainWindow):
    """
    The main application window that hosts the IPythonConsoleTab widget.
    """

    def __init__(self, kernel_file=None):
        """
        Initializes the main application window, setting up the central widget
        as an instance of IPythonConsoleTab.
        """
        super().__init__()
        self.setWindowTitle("IPython Console Tab")
        self.setCentralWidget(IPythonConsoleTab(kernel_file=kernel_file))
        self.resize(800, 600)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IPython Console Application")
    parser.add_argument("--kernel", type=str, help="Path to the kernel connection file")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    mainWin = MainApplicationWindow(kernel_file=args.kernel)
    mainWin.show()
    sys.exit(app.exec_())
