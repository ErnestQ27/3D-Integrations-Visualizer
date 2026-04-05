import sympy as sp
import scipy
import numpy as np

x = sp.Symbol('x', real=True)

def parse_xpr(expression):
    try:
        if isinstance(expression, sp.Expr):
            return expression
        return sp.sympify(expression, locals={'x': x})
    except:
        raise sp.SympifyError("Expression could not be parsed.")
    
def find_ints(expression1, expression2, search_min=-50, search_max=50):
    try:
        xpr1 = parse_xpr(expression1)
        xpr2 = parse_xpr(expression2)
        difference = xpr1 - xpr2

        symbolicInts = sp.solve(difference, x)
        if symbolicInts:
            return symbolicInts
        
        difference_func = sp.lambdify(x, difference, 'numpy')
        xs = np.linspace(search_min, search_max, 5000)

        with np.errstate(invalid='ignore'):
            ys = difference_func(xs)        
        valid = np.isfinite(ys)
        xs = xs[valid]
        ys = ys[valid]

        roots = []
        for i in range(len(ys) - 1):
            if np.sign(ys[i]) != np.sign(ys[i + 1]):
                try:
                    root = scipy.optimize.brentq(difference_func, xs[i], xs[i + 1])
                    roots.append(root)
                except:
                    pass
        return roots
    
    except Exception as e:
        raise e

def integrate_symbolically(expression,a=None, b=None):
    try:
        xpr = parse_xpr(expression)
        if a is not None and b is not None:
            return sp.integrate(xpr, (x, a, b))
        elif a is not None:
            return sp.integrate(xpr, (x, a))
        return sp.integrate(xpr, x)
    except Exception as e:
        raise e
    
def standard_zxsects_area(shape, width):
    areas = {
        "semicircle": lambda w: w**2 * (sp.pi/8),
        "isosceles_triangle": lambda w: w**2 * (1/2),
        "square": lambda w: w**2,
        "equilateral_triangle": lambda w: w**2 * (sp.sqrt(3)/4)
    }
    return areas[shape](width)

def find_top_bottom(expression1, expression2, a, b):
    try:
        xpr1 = parse_xpr(expression1)
        xpr2 = parse_xpr(expression2)
        midpoint = (a + b) / 2
        val1 = float(xpr1.subs(x, midpoint).evalf())
        val2 = float(xpr2.subs(x, midpoint))
        if val1 > val2:
            return xpr1, xpr2
        else:
            return xpr2, xpr1
    except Exception as e:
        raise e

def integrate_xsect(expression1, expression2, a, b):
    try:
        xpr1, xpr2 = find_top_bottom(expression1, expression2, a, b)
        return integrate_symbolically(xpr1 - xpr2, a, b)
    except Exception as e:
        raise e

