from PyQt5.QtWidgets import QMainWindow, QTabWidget
from src.state_manager import StateManager
from src.viewer.viewer_panel import ViewerPanel
from src.functions.functions_panel import FunctionsPanel

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = StateManager()
        self.setWindowTitle("3D Integrations Visualizer")
        self.setMinimumSize(1200, 800)
        self.build_ui()

    def build_ui(self):
        tabs = QTabWidget()
        tabs.addTab(ViewerPanel(self.state), "Viewer")
        tabs.addTab(FunctionsPanel(self.state), "Functions")
        self.setCentralWidget(tabs)