from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QListWidget, QSplitter
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
import sympy as sp
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from math_engine import parse_xpr

x = sp.Symbol('x', real=True)


class FunctionsPanel(QWidget):
    def __init__(self, state):
        super().__init__()
        self.state = state

        # Instance variables — like private fields in Java
        # This list stores tuples of (name_string, sympy_expression)
        # e.g. [("f(x)", x**2 + 5), ("g(x)", x + 1)]
        self.functions = []

        self._build_ui()

    def _build_ui(self):
        # Outer layout splits left list from right canvas
        outer = QHBoxLayout()

        # --- Left side: input + function list ---
        left = QVBoxLayout()

        # Input row: text box + button side by side
        input_row = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("f(x) = x**2 + 5")

        # Pressing Enter also triggers add — quality of life
        self.input_field.returnPressed.connect(self._on_add)

        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self._on_add)

        input_row.addWidget(self.input_field)
        input_row.addWidget(self.add_btn)
        left.addLayout(input_row)

        # Function list — shows all added functions as text
        # QListWidget is like a JList in Java Swing
        self.function_list = QListWidget()
        self.function_list.itemClicked.connect(self._on_function_selected)
        left.addWidget(self.function_list)

        # Remove button — removes selected function from list
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self._on_remove)
        left.addWidget(self.remove_btn)

        # Error label — shows parsing errors to user
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 11px;")
        left.addWidget(self.error_label)

        left.addStretch()

        # Wrap left layout in a QWidget so QSplitter can hold it
        left_widget = QWidget()
        left_widget.setLayout(left)

        # --- Right side: matplotlib canvas ---
        # This canvas shows both the LaTeX display and the plot
        right_widget = QWidget()
        right = QVBoxLayout()

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        right.addWidget(self.canvas)

        right_widget.setLayout(right)

        # QSplitter lets user drag the divider between left and right
        # Same idea as JSplitPane in Java Swing
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])   # initial pixel widths

        outer.addWidget(splitter)
        self.setLayout(outer)

    # -----------------------------------------------------------
    # Slot methods
    # -----------------------------------------------------------

    def _on_add(self):
        raw = self.input_field.text().strip()
        if not raw:
            return

        # Parse the input — handle both "f(x) = x**2" and just "x**2"
        # Split on "=" if present, take the right side as the expression
        if "=" in raw:
            parts = raw.split("=", 1)   # split on first "=" only
            name = parts[0].strip()     # e.g. "f(x)"
            expr_str = parts[1].strip() # e.g. "x**2 + 5"
        else:
            name = f"f{len(self.functions) + 1}(x)"
            expr_str = raw

        # Try to parse with math_engine
        try:
            expr = parse_xpr(expr_str)
            self.error_label.setText("")                # clear any old error

            # Store and display
            self.functions.append((name, expr))
            self.function_list.addItem(f"{name} = {expr_str}")
            self.input_field.clear()

            # Redraw everything
            self._redraw()

        except Exception as e:
            self.error_label.setText(f"Parse error: {str(e)}")

    def _on_remove(self):
        selected = self.function_list.currentRow()
        if selected >= 0:
            self.functions.pop(selected)
            self.function_list.takeItem(selected)
            self._redraw()

    def _on_function_selected(self, item):
        # Future: highlight the selected function on the plot
        pass

    # -----------------------------------------------------------
    # Drawing
    # -----------------------------------------------------------

    def _redraw(self):
        self.figure.clear()

        if not self.functions:
            self.canvas.draw()
            return

        # Split figure into two rows:
        # Top: LaTeX display of all functions
        # Bottom: 2D plot of all functions
        ax_latex = self.figure.add_subplot(2, 1, 1)
        ax_plot  = self.figure.add_subplot(2, 1, 2)

        self._draw_latex(ax_latex)
        self._draw_plot(ax_plot)

        self.figure.tight_layout()
        self.canvas.draw()

    def _draw_latex(self, ax):
        # Turn off axes — this panel is just a text display
        ax.axis('off')

        # Build one LaTeX string showing all functions stacked
        # sympy.latex() converts a sympy expression to LaTeX notation
        lines = []
        for name, expr in self.functions:
            latex_expr = sp.latex(expr)
            lines.append(f"${name} = {latex_expr}$")

        combined = "\n".join(lines)

        # matplotlib renders LaTeX math notation natively
        # ha and va center the text in the axes
        ax.text(
            0.05, 0.5, combined,
            transform=ax.transAxes,
            fontsize=14,
            va='center',
            ha='left'
        )

    def _draw_plot(self, ax):
        xs = np.linspace(-10, 10, 500)

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

        for i, (name, expr) in enumerate(self.functions):
            try:
                # lambdify converts sympy expression to fast numpy function
                # Much faster than calling .subs() in a loop
                f_numpy = sp.lambdify(x, expr, 'numpy')
                ys = f_numpy(xs)

                # Clip extreme values so the plot doesn't go wild
                ys = np.clip(ys, -100, 100)

                color = colors[i % len(colors)]
                ax.plot(xs, ys, label=name, color=color, linewidth=1.5)

            except Exception:
                pass    # skip functions that can't be evaluated numerically

        ax.axhline(0, color='black', linewidth=0.5)
        ax.axvline(0, color='black', linewidth=0.5)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')
        ax.set_xlim(-10, 10)