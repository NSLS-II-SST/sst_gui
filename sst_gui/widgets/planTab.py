from qtpy.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLineEdit, QPushButton


class PlanSubmissionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)

        # Create and add the plan selection combo box
        self.plan_selection = QComboBox(self)
        self.plan_selection.addItems(["plan1", "plan2", "plan3", "plan4", "plan5"])
        self.layout.addWidget(self.plan_selection)

        # Create and add the parameter input field
        self.parameter_input = QLineEdit(self)
        self.layout.addWidget(self.parameter_input)

        # Create and add the submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.submit_plan)
        self.layout.addWidget(self.submit_button)

    def submit_plan(self):
        # Get the selected plan and parameter
        selected_plan = self.plan_selection.currentText()
        parameter = self.parameter_input.text()

        # Wrap the plan with BPlan and send it to the REClientModel
        # This is just a placeholder, replace it with your actual implementation
        print(f"Submitting plan {selected_plan} with parameter {parameter}")
