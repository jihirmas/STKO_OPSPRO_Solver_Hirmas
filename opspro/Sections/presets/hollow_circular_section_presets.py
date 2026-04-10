from dataclasses import dataclass
from .section_properties import SectionProperties, _ensure_quantity, _ureg
from PyMpc import MpcSectionExtrusionBeamData
import math


@dataclass
class HollowCircularSectionPreset:
    name: str
    d: object  # outer diameter
    t: object  # thickness

    def __post_init__(self):
        _ensure_quantity(self, ['d', 't'], 'mm')

PRESETS = []

CUSTOM = HollowCircularSectionPreset(name="user", d=100.0, t=5.0)

PARAM_NAMES = ['d', 't']
PARAM_DESCRIPTIONS = ['Outer diameter', 'Wall thickness']

def calculate_section_properties(params: dict) -> SectionProperties:
    D = params['d']
    t = params['t']
    d = D - 2.0 * t
    if float(d.magnitude) < 0.0:
        raise ValueError('Inner diameter negative: thickness too large')
    area = math.pi * (D**2) / 4.0 - math.pi * (d**2) / 4.0
    Iyy = math.pi * (D**4) / 64.0 - math.pi * (d**4) / 64.0
    Izz = Iyy
    J = Iyy + Izz
    alphaY = 1.0 * _ureg.dimensionless
    alphaZ = 1.0 * _ureg.dimensionless
    centroidY = D / 2.0
    centroidZ = D / 2.0
    return SectionProperties(
        area=area, Iyy=Iyy, Izz=Izz, J=J,
        alphaY=alphaY, alphaZ=alphaZ,
        centroidY=centroidY, centroidZ=centroidZ,
    )

def calculate_extrusion_data(params: dict) -> MpcSectionExtrusionBeamData:
    D = float(params['d'])
    t = float(params['t'])
    d = D - 2.0 * t
    n = 16
    ed = MpcSectionExtrusionBeamData()
    for i in range(n):
        angle = 2.0 * math.pi * i / n
        ed.addPoint((D / 2.0) * math.cos(angle), (D / 2.0) * math.sin(angle))
    for i in range(n):
        angle = 2.0 * math.pi * i / n
        ed.addPoint((d / 2.0) * math.cos(angle), (d / 2.0) * math.sin(angle))
    for i in range(n):
        j = (i + 1) % n
        ed.addTriangle(i, n + j, n + i)
        ed.addTriangle(i, j, n + j)
    ed.addEdge(list(range(n)) + [0])
    ed.addEdge([n] + [n + n - 1 - k for k in range(n - 1)] + [n])
    ed.addSweep(0)
    ed.addSweep(n)
    return ed
