from dataclasses import dataclass
from .section_properties import SectionProperties, _ensure_quantity, _ureg
from PyMpc import MpcSectionExtrusionBeamData


@dataclass
class LUSectionPreset:
    name: str
    h: object
    b: object
    tw: object
    tf: object

    def __post_init__(self):
        _ensure_quantity(self, ['h', 'b', 'tw', 'tf'], 'mm')

PRESETS = []

CUSTOM = LUSectionPreset(name="user", h=100.0, b=75.0, tw=6.0, tf=8.0)

PARAM_NAMES = ['h', 'b', 'tw', 'tf']
PARAM_DESCRIPTIONS = ['Total height', 'Total width', 'Web thickness', 'Flange thickness']

def calculate_section_properties(params: dict) -> SectionProperties:
    # Implement the LU-section calculation following MpcBeamSection::compute() logic.
    # Parameters expected: h (total height), b (total width), tw (web thickness), tf (flange thickness)
    H = params['h']
    B = params['b']
    tw = params['tw']
    tf = params['tf']

    H = H - tf
    Af = B * tf
    Aw = tw * H
    area = Af + Aw

    alphaY = 5.0 / 6.0 * _ureg.dimensionless
    alphaZ = 5.0 / 6.0 * _ureg.dimensionless

    Sy = Af * (B / 2.0) + Aw * (tw / 2.0)
    Sz = Af * (H + tf / 2.0) + Aw * (H / 2.0)
    centroidY = Sy / area
    centroidZ = Sz / area

    Iyy = (B * tf**3 / 12.0) + (Af * (H + tf / 2.0 - centroidZ)**2) + (tw * H**3 / 12.0) + (Aw * (H / 2.0 - centroidZ)**2)
    Izz = (H * tw**3 / 12.0) + (Aw * (tw / 2.0 - centroidY)**2) + (tf * B**3 / 12.0) + (Af * (B / 2.0 - centroidY)**2)
    J = (1.0 / 3.0) * ((H + tf / 2.0) * tw**3 + (B - tf / 2.0) * tf**3)

    return SectionProperties(
        area=area, Iyy=Iyy, Izz=Izz, J=J,
        alphaY=alphaY, alphaZ=alphaZ,
        centroidY=centroidY, centroidZ=centroidZ,
    )

def calculate_extrusion_data(params: dict) -> MpcSectionExtrusionBeamData:
    H = float(params['h'])
    B = float(params['b'])
    tw = float(params['tw'])
    tf = float(params['tf'])
    H -= tf
    Af = B * tf
    Aw = tw * H
    area = Af + Aw
    cy = (Af * (B / 2.0) + Aw * (tw / 2.0)) / area
    cz = (Af * (H + tf / 2.0) + Aw * (H / 2.0)) / area
    ed = MpcSectionExtrusionBeamData()
    ed.addPoint(0.0 - cy, 0.0 - cz)      # 0
    ed.addPoint(tw - cy, 0.0 - cz)        # 1
    ed.addPoint(tw - cy, H - cz)          # 2
    ed.addPoint(B - cy, H - cz)           # 3
    ed.addPoint(B - cy, H + tf - cz)      # 4
    ed.addPoint(0.0 - cy, H + tf - cz)    # 5
    # triangles
    ed.addTriangle(0, 1, 2)
    ed.addTriangle(0, 2, 5)
    ed.addTriangle(2, 3, 4)
    ed.addTriangle(2, 4, 5)
    # edges
    for i in range(6):
        ed.addEdge([i, (i + 1) % 6])
    # sweeps
    for i in range(6):
        ed.addSweep(i)
    return ed
