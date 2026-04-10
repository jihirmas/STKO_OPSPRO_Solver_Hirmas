from dataclasses import dataclass
from .section_properties import SectionProperties, _ensure_quantity, _ureg
from PyMpc import MpcSectionExtrusionBeamData


@dataclass
class BoxSectionPreset:
    name: str
    h: object  # height
    b: object  # width

    def __post_init__(self):
        _ensure_quantity(self, ['h', 'b'], 'mm')

PRESETS = []

CUSTOM = BoxSectionPreset(name="user", h=100.0, b=50.0)

PARAM_NAMES = ['h', 'b']
PARAM_DESCRIPTIONS = ['Height', 'Width']

def calculate_section_properties(params: dict) -> SectionProperties:
    """
    Calculate section properties for a rectangular (box) section.
    params: dict with keys 'b' (width), 'h' (height) as pint.Quantity.
    """
    b = params['b']
    h = params['h']
    area = b * h
    Iyy = (b * h**3) / 12.0
    Izz = (h * b**3) / 12.0
    # Torsion approximation: follow MpcBeamSection::compute() logic
    if h > b:
        J = h * b**3 * (1.0/3.0 - 0.21 * (b / h) * (1.0 - (b**4) / (12.0 * (h**4))))
    else:
        J = b * h**3 * (1.0/3.0 - 0.21 * (h / b) * (1.0 - (h**4) / (12.0 * (b**4))))
    alphaY = 5.0 / 6.0 * _ureg.dimensionless
    alphaZ = 5.0 / 6.0 * _ureg.dimensionless
    centroidY = b / 2.0
    centroidZ = h / 2.0
    return SectionProperties(
        area=area, Iyy=Iyy, Izz=Izz, J=J,
        alphaY=alphaY, alphaZ=alphaZ,
        centroidY=centroidY, centroidZ=centroidZ,
    )

def calculate_extrusion_data(params: dict) -> MpcSectionExtrusionBeamData:
    b = float(params['b'])
    h = float(params['h'])
    cx = b / 2.0
    cy = h / 2.0
    ed = MpcSectionExtrusionBeamData()
    ed.addPoint(-cx, -cy)
    ed.addPoint(b - cx, -cy)
    ed.addPoint(b - cx, h - cy)
    ed.addPoint(-cx, h - cy)
    ed.addTriangle(0, 1, 2)
    ed.addTriangle(0, 2, 3)
    ed.addEdge([0, 1])
    ed.addEdge([1, 2])
    ed.addEdge([2, 3])
    ed.addEdge([3, 0])
    ed.addSweep(0)
    ed.addSweep(1)
    ed.addSweep(2)
    ed.addSweep(3)
    return ed
