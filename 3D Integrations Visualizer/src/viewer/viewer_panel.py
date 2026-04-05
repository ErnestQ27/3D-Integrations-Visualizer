from PyQt5.QtWidgets import QWidget, QHBoxLayout
from src.viewer.input_panel import InputPanel
from src.viewer.canvas_panel import CanvasPanel

class ViewerPanel(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state

        layout = QHBoxLayout()
        self.inputs = InputPanel(state)
        self.canvas = CanvasPanel(state)
        layout.addWidget(self.inputs, stretch = 1)
        layout.addWidget(self.canvas, stretch = 2)
        self.setLayout(layout)

