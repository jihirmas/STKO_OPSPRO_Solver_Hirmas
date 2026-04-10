# flexparser, flexcache, pint
import opspro.parameters.UnitSystemTools as UnitSystemTools
from asteval import Interpreter
import pint
import math
import numpy as np
import itertools

class _silent_writer:
    @staticmethod
    def write(msg):
        ...

def _make_protected_dict() -> dict:
    """
    Creates and returns a dictionary of safe functions and constants for use in user expressions.

    The returned dictionary includes:
        - All public functions and constants from the `math` module.
        - Mathematical constants `pi` and `e`.
        - The `numpy` module as `np`.
        - A helper function `_OPUNIT` for handling units via `ParameterManager.ureg`.

    Returns:
        dict: A dictionary containing safe math functions, constants, numpy as `np`, and a unit helper function.
    """
    # add safe math functions for user expressions
    safe_dict = {name: getattr(math, name) for name in dir(math) if not name.startswith("_")}
    safe_dict.update({"pi": math.pi, "e": math.e})
    # add numpy as np
    safe_dict['np'] = np
    # add helper function to handle units
    safe_dict[UnitSystemTools._OPUNIT_FUN_NAME] = lambda u: ParameterManager._unit_registry(u)
    # done
    return safe_dict

# a global singleton to manage parameters
class ParameterManager:

    # ----------------------------------------------- Private static class members:

    # the unit registry
    _unit_registry = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)

    # a set of common unit symbols for autocompletion and parsing; built from the unit registry
    _unit_common_symbols = UnitSystemTools.build_common_unit_symbols(_unit_registry)

    # a mapping from dimensionality strings to common quantity names; built from the unit registry
    _unit_common_quantity_map = UnitSystemTools.build_common_quantity_map(_unit_registry)

    # SI unit system used as fallback when no unit system is configured
    _si_fallback = UnitSystemTools.UnitSystem('SI', 'm', 'kg', 's')

    # the currently active unit system; None → fall back to SI base units
    _current_unit_system: 'UnitSystemTools.UnitSystem' = None

    # a default dictionary of safe math functions for user expressions
    _safe_math_dict = _make_protected_dict()

    # a global asteval interpreter, built with the default safe_dict
    _evaluator = Interpreter(symtable=_safe_math_dict, writer=_silent_writer, err_writer=_silent_writer) 

    # ----------------------------------------------- Public static members:

    all_symbols = sorted(itertools.chain(
        _safe_math_dict.keys(),
        _unit_common_symbols
    ))

    # prevent instantiation
    def __new__(cls, *args, **kwargs):
        raise RuntimeError("Cannot instantiate ParameterManager, use class methods only")

    @staticmethod
    def evaluate(expr: str) -> pint.Quantity:
        expr_processed = UnitSystemTools.preprocess_units(expr)
        retval = ParameterManager._evaluator(expr_processed)
        if isinstance(retval, (int, float, np.ndarray)):
            return retval * ParameterManager._unit_registry.dimensionless
        elif isinstance(retval, pint.Quantity):
            return retval
        else:
            extra = ''
            if len(ParameterManager._evaluator.error) > 0:
                extra = '<br>' + '<br>'.join(['{}:{}'.format(*err.get_error()) for err in ParameterManager._evaluator.error])
                ParameterManager._evaluator.error = []
            raise ValueError(f"Expression \"{expr}\" did not evaluate to a number or quantity.{extra}")

    # ------------------------------------------------------------------ unit system

    @classmethod
    def set_unit_system(cls, system: 'UnitSystemTools.UnitSystem'):
        """
        Set the active unit system.  Pass *None* to revert to SI base units.

        Example::

            from opspro.parameters.UnitSystemTools import PREDEFINED_UNIT_SYSTEMS
            ParameterManager.set_unit_system(PREDEFINED_UNIT_SYSTEMS['mm-t-s'])
        """
        cls._current_unit_system = system

    @classmethod
    def get_unit_system(cls) -> 'UnitSystemTools.UnitSystem':
        """Return the active unit system, or *None* if using SI base units."""
        return cls._current_unit_system

    @staticmethod
    def to_internal(qty: pint.Quantity) -> pint.Quantity:
        """
        Convert *qty* to the active unit system.

        Falls back to SI base units when no unit system is configured.
        Dimensionless quantities are returned unchanged.
        """
        us = ParameterManager._current_unit_system
        if us is None:
            return qty.to_base_units()
        return us.to_internal(qty, ParameterManager._unit_registry)

    @staticmethod
    def evaluate_to_internal(expr: str) -> pint.Quantity:
        """Evaluate *expr* and convert the result to the active unit system."""
        return ParameterManager.to_internal(ParameterManager.evaluate(expr))

    @staticmethod
    def to_internal_like(qty: pint.Quantity) -> pint.Quantity:
        """
        Like :meth:`to_internal` but rewrites the result in terms of **force**
        instead of the raw ``mass × acceleration`` base-unit decomposition.

        The simplification applies whenever all [time] exponents in the
        dimensionality are consumed by extracting ``n`` forces
        (condition: ``c + 2·a == 0``, where ``a`` = [mass] exp and
        ``c`` = [time] exp).  The target unit is then ``F^a · L^(b-a)``,
        built from the force unit and length unit of the active unit system.

        Quantities whose dimensionality does not satisfy this condition
        (e.g. density ``[M/L³]``) are returned unchanged from
        :meth:`to_internal`.

        Examples (active unit system = mm-t-s, F = N, L = mm)::

            # force
            to_internal_like(1 kN)       → 1000 N          # F¹·L⁰
            # pressure / stress
            to_internal_like(200 GPa)    → 200000 N/mm²    # F¹·L⁻²
            to_internal_like(30 MPa)     → 30 N/mm²
            # stiffness / fracture energy (N/m = J/m²)
            to_internal_like(100 J/m²)   → 0.1 N/mm        # F¹·L⁻¹
            # self-weight
            to_internal_like(1 N/mm³)    → 1 N/mm³         # F¹·L⁻³
            # density → unchanged (c + 2a = 0 + 2·1 = 2 ≠ 0)
            to_internal_like(7850 kg/m³) → 7.85e-9 t/mm³
        """
        ureg     = ParameterManager._unit_registry
        internal = ParameterManager.to_internal(qty)

        dims  = dict(internal.dimensionality)
        a = dims.get('[mass]',   0)
        b = dims.get('[length]', 0)
        c = dims.get('[time]',   0)
        other = {k: v for k, v in dims.items()
                 if k not in ('[mass]', '[length]', '[time]')}

        # Integer check (pint stores exponents as int or float)
        a_int = int(round(a))
        b_int = int(round(b))
        c_int = int(round(c))

        # Simplify only when:
        #  • mass exponent is a positive integer
        #  • all time exponents vanish after extracting a_int forces (c + 2a == 0)
        #  • no extra exotic dimensions (temperature, current, …)
        if (
            a_int > 0
            and a_int == a and b_int == b and c_int == c
            and c_int + 2 * a_int == 0
            and not other
        ):
            us     = ParameterManager._current_unit_system or ParameterManager._si_fallback
            # ── Named force unit (N, kN, MN, …) for this unit system ──
            # get_unit_for returns the *base-unit* expression of 1 force unit;
            # convert it to N to find the right SI prefix.
            F_base = us.get_unit_for((ureg.N).dimensionality, ureg)
            try:
                force_scale = float((1.0 * F_base).to(ureg.N).magnitude)
            except Exception:
                return internal
            _SI_PREFIXES = [
                (-12,'p'),(-9,'n'),(-6,'u'),(-3,'m'),(0,''),(3,'k'),(6,'M'),(9,'G'),(12,'T'),
            ]
            F_named = 'N'
            for log_exp, prefix in _SI_PREFIXES:
                if abs(math.log10(force_scale) - log_exp) < 0.01:
                    F_named = f'{prefix}N'
                    break

            L_unit = ureg.parse_expression(us.length).units
            l_exp  = b_int - a_int   # length exponent after force extraction

            def _upow(unit_str, exp):
                return unit_str if exp == 1 else f'({unit_str})**{exp}'

            parts = [_upow(F_named, a_int)]
            if l_exp != 0:
                parts.append(_upow(format(L_unit, '~'), l_exp))

            try:
                target = ureg.parse_expression(' * '.join(parts)).units
                return internal.to(target)
            except Exception:
                pass

        return internal
    @staticmethod
    def get_common_quantity_name(q : pint.Quantity) -> str:
        """
        Return the common quantity name for the dimensions of *q*.

        For example, a quantity with dimensions of length would return "length".
        Returns *None* if no common quantity is found.
        """
        return ParameterManager._unit_common_quantity_map.get(str(q.units.dimensionality), None)

    @staticmethod
    def get_unit_for(dimensionality) -> pint.Unit:
        """
        Return the pint Unit for *dimensionality* in the active unit system.

        Falls back to SI base units when no unit system is configured.
        """
        us = ParameterManager._current_unit_system or ParameterManager._si_fallback
        return us.get_unit_for(dimensionality, ParameterManager._unit_registry)