from dataclasses import dataclass
import pint
from opspro.parameters.ParameterManager import ParameterManager

_ureg = ParameterManager._unit_registry

def _ensure_quantity(obj, field_names, unit_str):
    """Convert float fields of a dataclass to pint.Quantity in __post_init__."""
    for name in field_names:
        val = getattr(obj, name)
        if not isinstance(val, pint.Quantity):
            object.__setattr__(obj, name, ParameterManager.to_internal_like(val * _ureg(unit_str)))

@dataclass(frozen=True)
class SectionProperties:
    """All fields are pint.Quantity with appropriate units."""
    area: object       # [length^2]
    Iyy: object        # [length^4]
    Izz: object        # [length^4]
    J: object          # [length^4]
    alphaY: object     # dimensionless
    alphaZ: object     # dimensionless
    centroidY: object  # [length]
    centroidZ: object  # [length]

PROP_UNITS = ['mm^2', 'mm^4', 'mm^4', 'mm^4', 'dimensionless', 'dimensionless', 'mm', 'mm']

PROP_NAMES = ['area', 'Iyy', 'Izz', 'J', 'alphaY', 'alphaZ', 'centroidY', 'centroidZ']
PROP_DESCRIPTIONS = [
    'Cross-section area',
    'Moment of inertia Iyy',
    'Moment of inertia Izz',
    'Torsional constant J',
    'Shear correction factor alphaY',
    'Shear correction factor alphaZ',
    'Centroid Y',
    'Centroid Z',
]
