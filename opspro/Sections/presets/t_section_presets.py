from dataclasses import dataclass
from .section_properties import SectionProperties, _ensure_quantity, _ureg
from PyMpc import MpcSectionExtrusionBeamData


@dataclass
class TSectionPreset:
    name: str
    h: object
    b: object
    tw: object
    tf: object

    def __post_init__(self):
        _ensure_quantity(self, ['h', 'b', 'tw', 'tf'], 'mm')

PRESETS = [
    TSectionPreset("WT 2x6.5", 52.8, 103.0, 7.11, 8.76),
    TSectionPreset("WT 2.5x9.5", 65.5, 128.0, 6.86, 10.9),
    TSectionPreset("WT 2.5x8", 63.8, 127.0, 6.1, 9.14),
    TSectionPreset("WT 3x12.5", 81.0, 154.0, 8.13, 11.6),
    TSectionPreset("WT 3x10", 78.7, 153.0, 6.6, 9.27),
    TSectionPreset("WT 3x7.5", 76.2, 152.0, 5.84, 6.6),
    TSectionPreset("WT 3x8", 79.8, 102.0, 6.6, 10.3),
    TSectionPreset("WT 3x6", 76.7, 102.0, 5.84, 7.11),
    TSectionPreset("WT 3x4.5", 74.9, 100.0, 4.32, 5.46),
    TSectionPreset("WT 3x4.25", 74.2, 100.0, 4.32, 4.95),
    TSectionPreset("WT 4x33.5", 114.0, 210.0, 14.5, 23.7),
    TSectionPreset("WT 4x29", 111.0, 209.0, 13.0, 20.6),
    TSectionPreset("WT 4x24", 108.0, 206.0, 10.2, 17.4),
    TSectionPreset("WT 4x20", 105.0, 205.0, 9.14, 14.2),
    TSectionPreset("WT 4x17.5", 103.0, 204.0, 7.87, 12.6),
    TSectionPreset("WT 4x15.5", 102.0, 203.0, 7.24, 11.0),
    TSectionPreset("WT 4x14", 102.0, 166.0, 7.24, 11.8),
    TSectionPreset("WT 4x12", 101.0, 165.0, 6.22, 10.2),
    TSectionPreset("WT 4x10.5", 105.0, 134.0, 6.35, 10.2),
    TSectionPreset("WT 4x9", 103.0, 133.0, 5.84, 8.38),
    TSectionPreset("WT 4x7.5", 103.0, 102.0, 6.22, 8.0),
    TSectionPreset("WT 4x6.5", 102.0, 102.0, 5.84, 6.48),
    TSectionPreset("WT 4x5", 100.0, 100.0, 4.32, 5.21),
    TSectionPreset("WT 5x56", 144.0, 264.0, 19.2, 31.8),
    TSectionPreset("WT 5x50", 141.0, 262.0, 17.3, 28.4),
    TSectionPreset("WT 5x44", 138.0, 262.0, 15.4, 25.1),
    TSectionPreset("WT 5x38.5", 135.0, 259.0, 13.5, 22.1),
    TSectionPreset("WT 5x34", 132.0, 257.0, 11.9, 19.6),
    TSectionPreset("WT 5x30", 130.0, 257.0, 10.7, 17.3),
    TSectionPreset("WT 5x27", 128.0, 254.0, 9.4, 15.6),
    TSectionPreset("WT 5x24.5", 127.0, 254.0, 8.64, 14.2),
    TSectionPreset("WT 5x22.5", 128.0, 204.0, 8.89, 15.7),
    TSectionPreset("WT 5x19.5", 126.0, 203.0, 8.0, 13.5),
    TSectionPreset("WT 5x16.5", 124.0, 202.0, 7.37, 11.0),
    TSectionPreset("WT 5x15", 133.0, 148.0, 7.62, 13.0),
    TSectionPreset("WT 5x13", 131.0, 147.0, 6.6, 11.2),
    TSectionPreset("WT 5x11", 129.0, 146.0, 6.1, 9.14),
    TSectionPreset("WT 5x9.5", 130.0, 102.0, 6.35, 10.0),
    TSectionPreset("WT 5x8.5", 129.0, 102.0, 6.1, 8.38),
    TSectionPreset("WT 5x7.5", 127.0, 102.0, 5.84, 6.86),
    TSectionPreset("WT 5x6", 125.0, 101.0, 4.83, 5.33),
    TSectionPreset("WT 6x168", 214.0, 340.0, 45.2, 75.2),
    TSectionPreset("WT 6x152.5", 207.0, 335.0, 41.4, 68.8),
    TSectionPreset("WT 6x139.5", 201.0, 333.0, 38.9, 62.7),
    TSectionPreset("WT 6x126", 196.0, 330.0, 35.6, 57.2),
    TSectionPreset("WT 6x115", 191.0, 328.0, 32.8, 52.6),
]

CUSTOM = TSectionPreset(name="user", h=100.0, b=100.0, tw=6.0, tf=8.0)

PARAM_NAMES = ['h', 'b', 'tw', 'tf']
PARAM_DESCRIPTIONS = ['Total height', 'Flange width', 'Web thickness', 'Flange thickness']

def calculate_section_properties(params: dict) -> SectionProperties:
    """Compute T-section properties following MpcBeamSection::compute() logic.

    Expects params with keys: h (total height), b (base width B), tw (web thickness), tf (flange height)
    """
    h_total = params['h']
    B = params['b']
    b = params['tw']
    h_flange = params['tf']

    H = h_total - h_flange
    area = B * h_flange + H * b
    ycog = ((H + h_flange / 2.0) * h_flange * B + (H / 2.0) * H * b) / area

    Iyy = b * H * (ycog - H / 2.0) ** 2 + (b * H ** 3) / 12.0 + h_flange * B * (H + h_flange / 2.0 - ycog) ** 2 + (
        h_flange ** 3 * B / 12.0)
    Izz = (b ** 3) * H / 12.0 + (B ** 3) * h_flange / 12.0
    J = (1.0 / 3.0) * (((H + h_flange / 2.0) * (h_flange ** 3)) + B * (b ** 3))

    alphaY = 5.0 / 6.0 * _ureg.dimensionless
    alphaZ = 1.0 * _ureg.dimensionless
    centroidY = B / 2.0
    centroidZ = ycog

    return SectionProperties(
        area=area, Iyy=Iyy, Izz=Izz, J=J,
        alphaY=alphaY, alphaZ=alphaZ,
        centroidY=centroidY, centroidZ=centroidZ,
    )

def calculate_extrusion_data(params: dict) -> MpcSectionExtrusionBeamData:
    h_total = float(params['h'])
    B = float(params['b'])
    b = float(params['tw'])
    h_flange = float(params['tf'])
    H = h_total - h_flange
    # centroid
    area = B * h_flange + H * b
    ycog = ((H + h_flange / 2.0) * h_flange * B + (H / 2.0) * H * b) / area
    cx = B / 2.0
    cy = ycog
    ed = MpcSectionExtrusionBeamData()
    ed.addPoint((B - b) / 2.0 - cx, 0.0 - cy)      # 0
    ed.addPoint((B + b) / 2.0 - cx, 0.0 - cy)      # 1
    ed.addPoint((B + b) / 2.0 - cx, H - cy)         # 2
    ed.addPoint(B - cx, H - cy)                      # 3
    ed.addPoint(B - cx, H + h_flange - cy)           # 4
    ed.addPoint(0.0 - cx, H + h_flange - cy)         # 5
    ed.addPoint(0.0 - cx, H - cy)                    # 6
    ed.addPoint((B - b) / 2.0 - cx, H - cy)         # 7
    # triangles
    ed.addTriangle(0, 1, 2)
    ed.addTriangle(0, 2, 7)
    ed.addTriangle(2, 3, 4)
    ed.addTriangle(2, 4, 7)
    ed.addTriangle(7, 4, 5)
    ed.addTriangle(6, 7, 5)
    # edges
    for i in range(8):
        ed.addEdge([i, (i + 1) % 8])
    # sweeps
    for i in range(8):
        ed.addSweep(i)
    return ed
