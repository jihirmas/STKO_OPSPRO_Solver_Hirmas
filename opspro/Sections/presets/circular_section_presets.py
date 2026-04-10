from dataclasses import dataclass
from .section_properties import SectionProperties, _ensure_quantity, _ureg
from PyMpc import MpcSectionExtrusionBeamData
import math


@dataclass
class CircularSectionPreset:
    name: str
    d: object  # diameter

    def __post_init__(self):
        _ensure_quantity(self, ['d'], 'mm')

PRESETS = []

CUSTOM = CircularSectionPreset(name="user", d=100.0)

PARAM_NAMES = ['d']
PARAM_DESCRIPTIONS = ['Diameter']

def calculate_section_properties(params: dict) -> SectionProperties:
    D = params['d']
    area = math.pi * (D**2) / 4.0
    Iyy = math.pi * (D**4) / 64.0
    Izz = Iyy
    J = Iyy + Izz
    alphaY = 0.9 * _ureg.dimensionless
    alphaZ = 0.9 * _ureg.dimensionless
    centroidY = D / 2.0
    centroidZ = D / 2.0
    return SectionProperties(
        area=area, Iyy=Iyy, Izz=Izz, J=J,
        alphaY=alphaY, alphaZ=alphaZ,
        centroidY=centroidY, centroidZ=centroidZ,
    )

def calculate_extrusion_data(params: dict) -> MpcSectionExtrusionBeamData:
    D = float(params['d'])
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
