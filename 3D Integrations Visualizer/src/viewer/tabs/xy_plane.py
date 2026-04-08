from PyQt5.QtWidgets import QWidget, QHBoxLayout

class XYTab(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def build_input_ui(self):
        layout = QHBoxLayout()
        # Add input widgets for 3D shape parameters here
        self.setLayout(layout)
    
    def build_figure_ui(self):
        # Add code to create and display the 3D shape figure here
        pass