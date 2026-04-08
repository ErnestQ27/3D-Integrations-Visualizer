from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTabWidget
from src.viewer.tabs.cross_section import CrossSectionTab
from src.viewer.tabs.xy_plane import XYTab
from src.viewer.tabs.shape import ShapeTab

class ViewerPanel(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state

        self.cross_section_tab = CrossSectionTab(state)
        self.xy_tab = XYTab(state)
        self.shape_tab = ShapeTab(state)

        layout = QHBoxLayout()
        layout.addWidget(self.cross_section_tab, stretch = 1)
        layout.addWidget(self.xy_tab, stretch = 1)
        layout.addWidget(self.shape_tab, stretch = 1)
        self.setLayout(layout)

        self.build_ui()

    def build_ui(self):
        tabs  = QTabWidget()
        tabs.addTab(self.cross_section_tab, "Cross Section Shape")
        tabs.addTab(self.xy_tab, "XY Plot")
        tabs.addTab(self.shape_tab, "3D Shape")
        tabs.setTabPosition(QTabWidget.South)
        self.layout().addWidget(tabs)

