from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class CanvasPanel(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.build_ui()
    
    def build_ui(self):
        layout = QVBoxLayout()

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def redraw(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.canvas.draw()