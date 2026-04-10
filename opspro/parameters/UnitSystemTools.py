import pint
import itertools
from typing import List, Dict

_OPUNIT_FUN_NAME = '_OPUNIT'
_OPUNIT_FUN_MATCH_1 = '* _OPUNIT("'
_OPUNIT_FUN_MATCH_2 = '")'

def preprocess_units(expr: str) -> str:
    """
    Preprocesses a unit expression string by replacing square brackets with a function call,
    stripping whitespace, and removing a leading asterisk if present.

    Args:
        expr (str): The unit expression string to preprocess.

    Returns:
        str: The preprocessed unit expression string.
    """
    # Step 1 + 2: blunt replacement
    expr = expr.replace('[', _OPUNIT_FUN_MATCH_1).replace(']', _OPUNIT_FUN_MATCH_2)
    # Step 3: strip leading/trailing spaces
    expr = expr.strip()
    # Step 4: if it starts with '*', drop it
    if expr.startswith('*'):
        expr = expr[1:].lstrip()
    return expr

def build_common_unit_symbols(ureg : pint.UnitRegistry) -> List[str]:
    """
    Build a list of common unit symbols for various physical quantities.
    This function defines and aggregates commonly used unit symbols,
    including both SI and non-SI units (such as Imperial, US customary, and other widely used units).
    It is intended to provide a comprehensive set of unit abbreviations for use with a Pint UnitRegistry.
    Parameters:
        ureg (pint.UnitRegistry): The Pint UnitRegistry instance used to validate or process unit symbols.
    Returns:
        List[str]: A list of unit symbol strings representing common units for length, mass, time, force, pressure etc... .
    """

    LENGTH = [
        # SI (restricted to 1e-9 .. 1e+9 m)
        'nm',   # nanometer (1e-9 m)
        'um',   # micrometer (1e-6 m)
        'mm',   # millimeter (1e-3 m)
        'cm',   # centimeter (1e-2 m)
        'dm',   # decimeter (1e-1 m)
        'm',    # meter (base)
        'dam',  # decameter (1e1 m)
        'hm',   # hectometer (1e2 m)
        'km',   # kilometer (1e3 m)
        'Mm',   # megameter (1e6 m)
        'Gm',   # gigameter (1e9 m)

        # Imperial / US customary
        'in',   # inch
        'ft',   # foot
        'yd',   # yard
        'mi',   # mile

        # Nautical
        'nmi',  # nautical mile

        # Astronomical
        'au',   # astronomical unit
        'ly',   # light-year
        'pc',   # parsec
    ]

    MASS = [
        # SI (restricted to 1e-9 g .. 1e+9 g)
        'ng',   # nanogram (1e-9 g)
        'ug',   # microgram (1e-6 g)
        'mg',   # milligram (1e-3 g)
        'cg',   # centigram (1e-2 g)
        'dg',   # decigram (1e-1 g)
        'g',    # gram (base for prefixes, even though SI base is kg)
        'dag',  # decagram (1e1 g)
        'hg',   # hectogram (1e2 g)
        'kg',   # kilogram (1e3 g, official SI base)
        'Mg',   # megagram (1e6 g) = metric ton (t)
        'Gg',   # gigagram (1e9 g)

        # SI alias
        't',    # tonne (metric ton, 1e3 kg = 1 Mg)

        # Imperial / US customary
        'oz',    # ounce
        'lb',    # pound
        'stone', # stone
        'cwt',   # hundredweight (UK/US differ, but commonly known)
        'ton',   # short ton (US customary)
    ]
    
    TIME = [
        # SI (restricted to 1e-9 .. 1e+9 s)
        'ns',   # nanosecond (1e-9 s)
        'us',   # microsecond (1e-6 s)
        'ms',   # millisecond (1e-3 s)
        'cs',   # centisecond (1e-2 s)
        'ds',   # decisecond (1e-1 s)
        's',    # second (base)
        'das',  # decasecond (1e1 s)
        'hs',   # hectosecond (1e2 s)
        'ks',   # kilosecond (1e3 s)
        'Ms',   # megasecond (1e6 s)
        'Gs',   # gigasecond (1e9 s)

        # Common multiples (non-SI but widely used)
        'min',  # minute
        'h',    # hour
        'd',    # day
        'week', # week
        'yr',   # year
    ]

    FORCE = [
        # SI (restricted to 1e-9 .. 1e+9 N)
        'nN',   # nanonewton (1e-9 N)
        'uN',   # micronewton (1e-6 N)
        'mN',   # millinewton (1e-3 N)
        'cN',   # centinewton (1e-2 N)
        'dN',   # decinewton (1e-1 N)
        'N',    # newton (base)
        'daN',  # decanewton (1e1 N)
        'hN',   # hectonewton (1e2 N)
        'kN',   # kilonewton (1e3 N)
        'MN',   # meganewton (1e6 N)
        'GN',   # giganewton (1e9 N)

        # Non-SI but used
        'kpond',   # kilopond (aka kilogram-force, obsolete but still seen)

        # Imperial / US customary
        'lbf',  # pound-force
        'ozf',  # ounce-force
        'tf', # ton-force (short ton-force, sometimes kip for 1000 lbf)
        'ton_force', # metric ton-force (t)
        'kip',  # kip (1000 lbf, common in structural engineering)
    ]
    
    PRESSURE = [
        # SI (restricted to 1e-9 .. 1e+9 Pa)
        'nPa',  # nanopascal (1e-9 Pa)
        'uPa',  # micropascal (1e-6 Pa)
        'mPa',  # millipascal (1e-3 Pa)
        'cPa',  # centipascal (1e-2 Pa)
        'dPa',  # decipascal (1e-1 Pa)
        'Pa',   # pascal (base)
        'daPa', # decapascal (1e1 Pa)
        'hPa',  # hectopascal (1e2 Pa) = millibar, common in meteorology
        'kPa',  # kilopascal (1e3 Pa)
        'MPa',  # megapascal (1e6 Pa)
        'GPa',  # gigapascal (1e9 Pa)

        # Common non-SI
        'bar',   # bar (1e5 Pa)
        'mbar',  # millibar (100 Pa), meteorology
        'atm',   # standard atmosphere (101325 Pa)
        'torr',  # 1/760 atm ≈ 133.3 Pa
        'mmHg',  # millimeter of mercury
        'inHg',  # inch of mercury
        'psi',   # pounds per square inch
    ]

    TEMPERATURE = [
        'K',    # kelvin (base)
        'degC', # degree Celsius
        'degF', # degree Fahrenheit
        'degR', # degree Rankine
    ]

    ANGLE = [
        'rad',  # radian (base)
        'deg', '°',  # degree
        'grad', # gradian
        'arcmin', # arcminute
        'arcsec', # arcsecond
    ]

    return list(itertools.chain(
        LENGTH,
        MASS,
        TIME,
        FORCE,
        PRESSURE,
        TEMPERATURE,
        ANGLE
    ))

def build_common_quantity_map(ureg : pint.UnitRegistry) -> Dict[str, str]:
    """
    Builds a mapping from dimensionality strings (as produced by Pint's UnitRegistry)
    to common physical quantity names.
    Args:
        ureg (pint.UnitRegistry): The unit registry instance from Pint, used to generate dimensionalities.
    Returns:
        Dict[str, str]: A dictionary mapping the string representation of dimensionalities
                        to human-readable names of physical quantities (e.g., 'Length', 'Force', 'Energy').
    Notes:
        - The mapping covers basic, derived, force-related, energy, density, and cross-sectional quantities.
        - Multiple physical quantities may share the same dimensionality and are separated by semicolons in the values.
    """
    return {
        # Basics
        str((ureg.m).dimensionality): 'Length',
        str((ureg.kg).dimensionality): 'Mass',
        str((ureg.s).dimensionality): 'Time',
        str((ureg.K).dimensionality): 'Temperature',

        # Derived
        str((ureg.m / ureg.s).dimensionality): 'Velocity',
        str((ureg.m / ureg.s**2).dimensionality): 'Acceleration',

        # Force-related
        str((ureg.N).dimensionality): 'Force; Moment-Per-Unit-Length',
        str((ureg.N*ureg.m).dimensionality): 'Moment; Work; Energy',
        str((ureg.N/ureg.m).dimensionality): 'Stiffness; Force-Per-Unit-Length',
        str((ureg.N/ureg.m**2).dimensionality): 'Pressure; Stress; Material-Modulus(E, G, K); Energy-Density',

        # energy
        str((ureg.J).dimensionality): 'Energy; Work; Moment',
        str((ureg.W).dimensionality): 'Power',

        # Densities
        str((ureg.kg/ureg.m**3).dimensionality): 'Mass-Density',
        str((ureg.N/ureg.m**3).dimensionality): 'Weight-Density',

        # Cross-Sectional-related
        str((ureg.m**2).dimensionality): 'Area',
        str((ureg.m**3).dimensionality): 'Volume; First-Moment-Area; Static-Moment',
        str((ureg.m**4).dimensionality): 'Second-Moment-Area; Area-Moment-of-Inertia',

    }


class UnitSystem:
    """
    Defines a coherent set of base units for a physical modeling context.

    All derived quantities (force, pressure, energy, density, etc.) are
    automatically expressed in terms of the four fundamental base units:
    length (L), mass (M), time (T), and temperature (Θ).

    Examples
    --------
    SI      : L=m,  M=kg,   T=s  → F=N,    σ=Pa
    mm-t-s  : L=mm, M=t,    T=s  → F=N,    σ=MPa   (Abaqus default, structural)
    m-t-s   : L=m,  M=t,    T=s  → F=kN,   σ=kPa   (large structural models)
    mm-kg-ms: L=mm, M=kg,   T=ms → F=kN,   σ=GPa   (explicit dynamics)
    """

    def __init__(self, name: str, length: str, mass: str, time: str, temperature: str = 'K'):
        self.name = name
        self.length = length
        self.mass = mass
        self.time = time
        self.temperature = temperature

    def get_unit_for(self, dimensionality, ureg: pint.UnitRegistry):
        """
        Return the pint Unit corresponding to *dimensionality* expressed in
        this unit system.

        Pint base dimensions ([length], [mass], [time], [temperature]) are
        mapped individually to the user-chosen base units and combined via
        multiplication / exponentiation.
        """
        dims = dict(dimensionality)
        L = dims.get('[length]', 0)
        M = dims.get('[mass]', 0)
        T = dims.get('[time]', 0)
        Θ = dims.get('[temperature]', 0)

        parts = []
        for exp, sym in [(L, self.length), (M, self.mass), (T, self.time), (Θ, self.temperature)]:
            if exp == 0:
                continue
            parts.append(f'({sym})**{int(exp)}' if exp != 1 else sym)

        if not parts:
            return ureg.dimensionless

        return ureg.parse_expression(' * '.join(parts)).units

    def to_internal(self, qty, ureg: pint.UnitRegistry):
        """Convert *qty* to its representation in this unit system."""
        return qty.to(self.get_unit_for(qty.dimensionality, ureg))

    def describe(self, ureg: pint.UnitRegistry) -> str:
        """Human-readable summary with the key derived units."""
        F = self.get_unit_for((ureg.N).dimensionality, ureg)
        σ = self.get_unit_for((ureg.Pa).dimensionality, ureg)
        return (
            f"{self.name}:  L={self.length}, M={self.mass}, T={self.time}, "
            f"Θ={self.temperature}  →  F={F:~P}, σ={σ:~P}"
        )

    def __repr__(self):
        return (
            f"UnitSystem('{self.name}', "
            f"L={self.length}, M={self.mass}, T={self.time}, Θ={self.temperature})"
        )


def build_predefined_unit_systems() -> Dict[str, UnitSystem]:
    """
    Return a dict of ready-to-use unit systems commonly used in structural
    and mechanical FEA.

    All systems are mass-based (L, M, T, Θ). Derived force/pressure units
    follow automatically:  F = M·L/T²,  σ = M/(L·T²).

    ============  =====  =====  ====  =======  =======
    name          L      M      T     F        σ
    ============  =====  =====  ====  =======  =======
    SI            m      kg     s     N        Pa
    mm-t-s        mm     t      s     N        MPa
    m-t-s         m      t      s     kN       kPa
    mm-kg-ms      mm     kg     ms    kN       GPa
    cm-g-s        cm     g      s     dyn      Ba
    in-lb-s       in     lb     s     pdl      pdl/in²
    ft-slug-s     ft     slug   s     lbf      psf
    ============  =====  =====  ====  =======  =======
    """
    systems = [
        UnitSystem('SI',         'm',  'kg',   's',  'K'),
        UnitSystem('mm-t-s',     'mm', 't',    's',  'K'),
        UnitSystem('m-t-s',      'm',  't',    's',  'K'),
        UnitSystem('mm-kg-ms',   'mm', 'kg',   'ms', 'K'),
        UnitSystem('cm-g-s',     'cm', 'g',    's',  'K'),
        UnitSystem('in-lb-s',    'in', 'lb',   's',  'K'),
        UnitSystem('ft-slug-s',  'ft', 'slug', 's',  'K'),
    ]
    return {s.name: s for s in systems}


#: Ready-to-use predefined unit systems — import and use directly.
PREDEFINED_UNIT_SYSTEMS: Dict[str, UnitSystem] = build_predefined_unit_systems()
