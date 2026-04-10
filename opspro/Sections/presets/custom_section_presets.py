from dataclasses import dataclass
from .section_properties import SectionProperties, _ensure_quantity, _ureg
from PyMpc import MpcSectionExtrusionBeamData
import math


@dataclass
class CustomSectionPreset:
    name: str
    area: object
    Iyy: object
    Izz: object
    J: object
    alphaY: object
    alphaZ: object
    centroidY: object
    centroidZ: object

    def __post_init__(self):
        _ensure_quantity(self, ['area'], 'mm^2')
        _ensure_quantity(self, ['Iyy', 'Izz', 'J'], 'mm^4')
        _ensure_quantity(self, ['alphaY', 'alphaZ'], 'dimensionless')
        _ensure_quantity(self, ['centroidY', 'centroidZ'], 'mm')

PRESETS = []

CUSTOM = CustomSectionPreset(
    name="user", area=1000.0, Iyy=1e6, Izz=1e6,
    J=1e6, alphaY=5.0/6.0, alphaZ=5.0/6.0,
    centroidY=0.0, centroidZ=0.0,
)

# only for custom section we cannot assume mm for all parameters, 
# so we use the units of the provided values directly without conversion
PARAM_UNITS = ['mm^2', 'mm^4', 'mm^4', 'mm^4', 'dimensionless', 'dimensionless', 'mm', 'mm']

PARAM_NAMES = ['area', 'Iyy', 'Izz', 'J', 'alphaY', 'alphaZ', 'centroidY', 'centroidZ']
PARAM_DESCRIPTIONS = [
    'Cross-section area',
    'Moment of inertia Iyy',
    'Moment of inertia Izz',
    'Torsional constant J',
    'Shear correction factor alphaY',
    'Shear correction factor alphaZ',
    'Centroid Y',
    'Centroid Z',
]

def calculate_section_properties(params: dict) -> SectionProperties:
    """For custom sections, the user provides all properties directly."""
    return SectionProperties(
        area=params['area'],
        Iyy=params['Iyy'],
        Izz=params['Izz'],
        J=params['J'],
        alphaY=params['alphaY'],
        alphaZ=params['alphaZ'],
        centroidY=params['centroidY'],
        centroidZ=params['centroidZ'],
    )

def calculate_extrusion_data(params: dict) -> MpcSectionExtrusionBeamData:
    area = float(params['area'])
    D = (area / math.pi) ** 0.5
    n = 16
    ed = MpcSectionExtrusionBeamData()
    for i in range(n):
        angle = 2.0 * math.pi * i / n
        ed.addPoint((D / 2.0) * math.cos(angle), (D / 2.0) * math.sin(angle))
    for i in range(1, n - 1):
        ed.addTriangle(0, i, i + 1)
    ed.addEdge(list(range(n)) + [0])
    ed.addSweep(0)
    return ed
