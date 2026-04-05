from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QSlider, QPushButton)
from PyQt5.QtCore import Qt

class InputPanel(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.build_ui()
    
    def build_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("f(x) ="))
        self.xy1_input = QLineEdit()
        self.xy1_input.setPlaceholderText("e.g sqrt(x) + 5")
        self.xy1_input.textChanged.connect(self.on_xy1_changed)
        layout.addWidget(self.xy1_input)

        layout.addWidget(QLabel("g(x) ="))
        self.xy2_input = QLineEdit()
        self.xy2_input.setPlaceholderText("x**3 - 5*x**2 + 6*x - 1")
        self.xy2_input.textChanged.connect(self.on_xy2_changed)
        layout.addWidget(self.xy2_input)

        layout.addWidget(QLabel("Subdivisions: "))
        self.subdivisions_slider = QSlider(Qt.Horizontal)
        self.subdivisions_slider.setMinimum(1)
        self.subdivisions_slider.setMaximum(1000)
        self.subdivisions_slider.setValue(10)
        self.subdivisions_slider.valueChanged.connect(self.on_subdivisions_changed)
        layout.addWidget(self.subdivisions_slider)

        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.on_plot)
        layout.addWidget(self.plot_button)

        layout.addStretch()
        self.setLayout(layout)

    def on_xy1_changed(self, text):
        self.state.xy1 = text
    def on_xy2_changed(self, text):
        self.state.xy2 = text
    def on_subdivisions_changed(self, value):
        self.state.subdivisions = value
    def on_plot(self):
        pass