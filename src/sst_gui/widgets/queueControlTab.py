from bluesky_widgets.qt.run_engine_client import (
    QtReEnvironmentControls,
    QtReManagerConnection,
    QtReQueueControls,
    QtReExecutionControls,
    QtReStatusMonitor,
    QtRePlanQueue,
    QtRePlanHistory,
    QtReRunningPlan,
    QtRePlanEditor,
    QtReConsoleMonitor,
)
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QTabWidget,
    QFrame,
    QSplitter,
)


class QueueControlTab(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(QtReManagerConnection(model))
        hbox.addWidget(QtReEnvironmentControls(model))
        hbox.addWidget(QtReQueueControls(model))
        hbox.addWidget(QtReExecutionControls(model))
        hbox.addWidget(QtReStatusMonitor(model))

        hbox.addStretch()
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        vbox1 = QVBoxLayout()

        # Register plan editor (opening plans in the editor by double-clicking the plan in the table)
        pe = QtRePlanEditor(model)
        pq = QtRePlanQueue(model)
        pq.registered_item_editors.append(pe.edit_queue_item)

        vbox1.addWidget(pe, stretch=1)
        vbox1.addWidget(pq, stretch=1)
        hbox.addLayout(vbox1)
        vbox2 = QVBoxLayout()
        vbox2.addWidget(QtReRunningPlan(model), stretch=1)
        vbox2.addWidget(QtRePlanHistory(model), stretch=2)
        hbox.addLayout(vbox2)
        vbox.addLayout(hbox)
        vbox.addWidget(QtReConsoleMonitor(model))
        self.setLayout(vbox)
