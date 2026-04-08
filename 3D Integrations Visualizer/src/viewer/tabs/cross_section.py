from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSlider, QLabel, QLineEdit, QVBoxLayout, QRadioButton, QButtonGroup, QPushButton
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import sympy as sp
import sys, os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel)
from PyQt5.QtCore import Qt
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from math_engine import parse_xpr, find_top_bottom

x_sym = sp.Symbol('x', real=True)

class CrossSectionTab(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state

        layout = QHBoxLayout()
        self.input_panel = self.InputPanel()
        self.figure_panel = self.FigurePanel()

        # Give FigurePanel a reference so it can read inputs
        self.figure_panel.set_input_ref(self.input_panel)

        # Connect plot button — defined in InputPanel, triggers FigurePanel
        self.input_panel.plot_btn.clicked.connect(self.figure_panel.redraw)

        layout.addWidget(self.input_panel, stretch=1)
        layout.addWidget(self.figure_panel, stretch=2)
        self.setLayout(layout)

    class InputPanel(QWidget):
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout()
            
            self.func1_label = QLabel("Function 1:")
            self.func1_input = QLineEdit()
            self.func1_input.setPlaceholderText("e.g. x**3 - 5*x**2 + 6*x - 1")
            self.func2_label = QLabel("Function 2:")
            self.func2_input = QLineEdit()
            self.func2_input.setPlaceholderText("e.g. (sqrt(x)) + 5")
            self.z_label = QLabel("Z Cross Section:")
            self.z_input = QLineEdit()
            self.z_input.setPlaceholderText("e.g. isosceles_triangle(width)")
            self.slider_label = QLabel("Subdivisions:")
            self.slider = QSlider()
            self.slider.setOrientation(Qt.Horizontal)
            self.slider.setRange(0, 1000)
            self.slider.setValue(20)
            self.respect_var_label = QLabel("Variable of Integration:")
            self.x_radio = QRadioButton("dx")
            self.y_radio = QRadioButton("dy")
            self.var_button_group = QButtonGroup()
            self.var_button_group.addButton(self.x_radio)
            self.var_button_group.addButton(self.y_radio)
            self.plot_btn = QPushButton("Plot")


            layout.addWidget(self.func1_label)
            layout.addWidget(self.func1_input)
            layout.addWidget(self.func2_label)
            layout.addWidget(self.func2_input)
            layout.addWidget(self.z_label)
            layout.addWidget(self.z_input)
            layout.addWidget(self.slider_label)
            layout.addWidget(self.slider)
            layout.addWidget(self.respect_var_label)
            layout.addWidget(self.x_radio)
            layout.addWidget(self.y_radio)
            layout.addWidget(self.plot_btn)

            layout.setAlignment(Qt.AlignTop)
            self.setLayout(layout)

    class FigurePanel(QWidget):
        def __init__(self):
            super().__init__()
            self.input_ref = None       # set by CrossSectionTab after construction
            self._build_ui()

        def _build_ui(self):
            layout = QVBoxLayout()

            # Create the matplotlib figure — square aspect
            self.figure = Figure(figsize=(6, 6))
            self.canvas = FigureCanvasQTAgg(self.figure)

            # Toolbar gives you zoom/pan/rotate/save for free
            self.toolbar = NavigationToolbar2QT(self.canvas, self)

            # Stats label below the canvas
            self.stats_label = QLabel("Volume: —    Width range: —")
            self.stats_label.setAlignment(Qt.AlignCenter)

            layout.addWidget(self.toolbar)
            layout.addWidget(self.canvas)
            layout.addWidget(self.stats_label)
            self.setLayout(layout)

        def set_input_ref(self, input_panel):
            # Called by CrossSectionTab so FigurePanel can read inputs
            self.input_ref = input_panel

        def redraw(self):
            if self.input_ref is None:
                return

            # Read all values from the InputPanel
            expr1_str    = self.input_ref.func1_input.text()
            expr2_str    = self.input_ref.func2_input.text()
            z_str        = self.input_ref.z_input.text()
            subdivisions = self.input_ref.slider.value()
            use_dx       = self.input_ref.x_radio.isChecked()

            if not expr1_str or not expr2_str:
                return

            try:
                # Parse expressions
                xpr1 = parse_xpr(expr1_str)
                xpr2 = parse_xpr(expr2_str)

                # Convert to fast numpy functions for plotting
                f1 = sp.lambdify(x_sym, xpr1, 'numpy')
                f2 = sp.lambdify(x_sym, xpr2, 'numpy')

                # Determine plot range — use state bounds if available
                a = float(self.input_ref.a_input.text()) if hasattr(self.input_ref, 'a_input') else -5
                b = float(self.input_ref.b_input.text()) if hasattr(self.input_ref, 'b_input') else  5

                # Clear and create 3D axes
                self.figure.clear()
                ax = self.figure.add_subplot(111, projection='3d')

                # --- Draw f(x) and g(x) on the XY plane (Z=0) ---
                xs_dense = np.linspace(a, b, 300)
                ys1 = f1(xs_dense)
                ys2 = f2(xs_dense)

                ax.plot(xs_dense, ys1, zs=0, zdir='z', color='blue',
                        linewidth=2, label='f(x)')
                ax.plot(xs_dense, ys2, zs=0, zdir='z', color='red',
                        linewidth=2, label='g(x)')

                # Shade the region between curves on XY plane
                ax.plot_surface(
                    np.array([xs_dense, xs_dense]),
                    np.array([ys2, ys1]),
                    np.zeros((2, len(xs_dense))),
                    alpha=0.15, color='purple'
                )

                # --- Draw cross sections at each subdivision ---
                xs_sub = np.linspace(a, b, subdivisions + 1)
                total_volume = 0.0
                widths = []

                # Determine cross section shape from z_input or default square
                shape = self._parse_shape(z_str)

                faces = []
                for xi in xs_sub:
                    y_top = float(f1(xi))
                    y_bot = float(f2(xi))
                    width = y_top - y_bot

                    if width <= 0:
                        continue

                    widths.append(width)
                    height = self._shape_height(shape, width)
                    dx_step = (b - a) / subdivisions
                    total_volume += self._shape_area(shape, width) * dx_step

                    # Build the 4 vertices of this cross section face
                    # Each face is a quadrilateral standing upright at xi
                    verts = [
                        (xi, y_bot, 0),
                        (xi, y_top, 0),
                        (xi, y_top, height),
                        (xi, y_bot, height)
                    ]
                    faces.append(verts)

                # Poly3DCollection draws all faces at once — much faster than looping plot()
                if faces:
                    poly = Poly3DCollection(
                        faces,
                        alpha=0.4,
                        facecolor='cyan',
                        edgecolor='steelblue',
                        linewidth=0.5
                    )
                    ax.add_collection3d(poly)

                # --- Axis labels and formatting ---
                ax.set_xlabel('X')
                ax.set_ylabel('Y')
                ax.set_zlabel('Z')
                ax.legend()

                # Initial camera angle — user can rotate from here
                ax.view_init(elev=25, azim=-60)

                # --- Update stats label ---
                if widths:
                    self.stats_label.setText(
                        f"Volume ≈ {total_volume:.4f}    "
                        f"Subdivisions: {subdivisions}    "
                        f"Width range: [{min(widths):.3f}, {max(widths):.3f}]    "
                        f"Shape: {shape}"
                    )

                self.canvas.draw()

            except Exception as e:
                self.stats_label.setText(f"Error: {str(e)}")

        def _parse_shape(self, z_str):
            # Match user input to a known shape name
            # Checks if the z_input contains a shape keyword
            z_lower = z_str.lower()
            if 'semi'       in z_lower: return 'semicircle'
            if 'equilateral' in z_lower: return 'equilateral_triangle'
            if 'isosceles'  in z_lower: return 'isosceles_triangle'
            if 'square'     in z_lower: return 'square'
            return 'square'             # default

        def _shape_area(self, shape, w):
            # Cross sectional area — same as math_engine.standard_xsects_area
            # but returns a float directly for volume calculation
            if shape == 'square':               return w**2
            if shape == 'semicircle':           return (np.pi / 8) * w**2
            if shape == 'isosceles_triangle':   return 0.5 * w**2
            if shape == 'equilateral_triangle': return (np.sqrt(3) / 4) * w**2
            return w**2

        def _shape_height(self, shape, w):
            # Maximum Z height of the cross section shape
            if shape == 'square':               return w
            if shape == 'semicircle':           return w / 2
            if shape == 'isosceles_triangle':   return w / 2
            if shape == 'equilateral_triangle': return (np.sqrt(3) / 2) * w
            return w