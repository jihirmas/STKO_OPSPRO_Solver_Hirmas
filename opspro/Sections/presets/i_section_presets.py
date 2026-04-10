from dataclasses import dataclass
from typing import List
from .section_properties import SectionProperties, _ensure_quantity, _ureg
from PyMpc import MpcSectionExtrusionBeamData
import math


@dataclass
class ISectionPreset:
    name: str
    h: object
    b: object
    tw: object
    tf: object

    def __post_init__(self):
        _ensure_quantity(self, ['h', 'b', 'tw', 'tf'], 'mm')

PRESETS: List[ISectionPreset] = [
    ISectionPreset("IPE AA 80", 78.0, 46.0, 3.2, 4.2),
    ISectionPreset("IPE A 80", 78.0, 46.0, 3.3, 4.2),
    ISectionPreset("IPE 80", 80.0, 46.0, 3.8, 5.2),
    ISectionPreset("IPE AA 100", 97.6, 55.0, 3.6, 4.5),
    ISectionPreset("IPE A 100", 98.0, 55.0, 3.6, 4.7),
    ISectionPreset("IPE 100", 100.0, 55.0, 4.1, 5.7),
    ISectionPreset("IPE AA 120", 117.0, 64.0, 3.8, 4.8),
    ISectionPreset("IPE A 120", 117.6, 64.0, 3.8, 5.1),
    ISectionPreset("IPE 120", 120.0, 64.0, 4.4, 6.3),
    ISectionPreset("IPE AA 140", 136.6, 73.0, 3.8, 5.2),
    ISectionPreset("IPE A 140", 137.4, 73.0, 3.8, 5.6),
    ISectionPreset("IPE 140", 140.0, 73.0, 4.7, 6.9),
    ISectionPreset("IPE AA 160", 156.4, 82.0, 4.0, 5.6),
    ISectionPreset("IPE A 160", 157.0, 82.0, 4.0, 5.9),
    ISectionPreset("IPE 160", 160.0, 82.0, 5.0, 7.4),
    ISectionPreset("IPE AA 180", 176.4, 91.0, 4.3, 6.2),
    ISectionPreset("IPE A 180", 177.0, 91.0, 4.3, 6.5),
    ISectionPreset("IPE 180", 180.0, 91.0, 5.3, 8.0),
    ISectionPreset("IPE O 180", 182.0, 92.0, 6.0, 9.0),
    ISectionPreset("IPE AA 200", 196.4, 100.0, 4.5, 6.7),
    ISectionPreset("IPE A 200", 197.0, 100.0, 4.5, 7.0),
    ISectionPreset("IPE 200", 200.0, 100.0, 5.6, 8.5),
    ISectionPreset("IPE O 200", 202.0, 102.0, 6.2, 9.5),
    ISectionPreset("IPE AA 220", 216.4, 110.0, 4.7, 7.4),
    ISectionPreset("IPE A 220", 217.0, 110.0, 5.0, 7.7),
    ISectionPreset("IPE 220", 220.0, 110.0, 5.9, 9.2),
    ISectionPreset("IPE O 220", 222.0, 112.0, 6.6, 10.2),
    ISectionPreset("IPE AA 240", 236.4, 120.0, 4.8, 8.0),
    ISectionPreset("IPE A 240", 237.0, 120.0, 5.2, 8.3),
    ISectionPreset("IPE 240", 240.0, 120.0, 6.2, 9.8),
    ISectionPreset("IPE O 240", 242.0, 122.0, 7.0, 10.8),
    ISectionPreset("IPE A 270", 267.0, 135.0, 5.5, 8.7),
    ISectionPreset("IPE 270", 270.0, 135.0, 6.6, 10.2),
    ISectionPreset("IPE O 270", 274.0, 136.0, 7.5, 12.2),
    ISectionPreset("IPE A 300", 297.0, 150.0, 6.1, 9.2),
    ISectionPreset("IPE 300", 300.0, 150.0, 7.1, 10.7),
    ISectionPreset("IPE O 300", 304.0, 152.0, 8.0, 12.7),
    ISectionPreset("IPE A 330", 327.0, 160.0, 6.5, 10.0),
    ISectionPreset("IPE 330", 330.0, 160.0, 7.5, 11.5),
    ISectionPreset("IPE O 330", 334.0, 162.0, 8.5, 13.5),
    ISectionPreset("IPE A 360", 357.6, 170.0, 6.6, 11.5),
    ISectionPreset("IPE 360", 360.0, 170.0, 8.0, 12.7),
    ISectionPreset("IPE O 360", 364.0, 172.0, 9.2, 14.7),
    ISectionPreset("IPE A 400", 397.0, 180.0, 7.0, 12.0),
    ISectionPreset("IPE 400", 400.0, 180.0, 8.6, 13.5),
    ISectionPreset("IPE O 400", 404.0, 182.0, 9.7, 15.5),
    ISectionPreset("IPE V 400", 408.0, 182.0, 10.6, 17.5),
    ISectionPreset("IPE A 450", 447.0, 190.0, 7.6, 13.1),
    ISectionPreset("IPE 450", 450.0, 190.0, 9.4, 14.6),
    ISectionPreset("IPE O 450", 456.0, 192.0, 11.0, 17.6),
    ISectionPreset("IPE V 450", 460.0, 194.0, 12.4, 19.6),
    ISectionPreset("IPE A 500", 497.0, 200.0, 8.4, 14.5),
    ISectionPreset("IPE 500", 500.0, 200.0, 10.2, 16.0),
    ISectionPreset("IPE O 500", 506.0, 202.0, 12.0, 19.0),
    ISectionPreset("IPE V 500", 514.0, 204.0, 14.2, 23.0),
    ISectionPreset("IPE A 550", 547.0, 210.0, 9.0, 15.7),
    ISectionPreset("IPE 550", 550.0, 210.0, 11.1, 17.2),
    ISectionPreset("IPE O 550", 556.0, 212.0, 12.7, 20.2),
    ISectionPreset("IPE V 550", 566.0, 216.0, 17.1, 25.2),
    ISectionPreset("IPE A 600", 597.0, 220.0, 9.8, 17.5),
    ISectionPreset("IPE 600", 600.0, 220.0, 12.0, 19.0),
    ISectionPreset("IPE O 600", 610.0, 224.0, 15.0, 24.0),
    ISectionPreset("IPE V 600", 618.0, 228.0, 18.0, 28.0),
    ISectionPreset("IPE 750 x 134", 750.0, 264.0, 12.0, 15.5),
    ISectionPreset("IPE 750 x 147", 753.0, 265.0, 13.2, 17.0),
    ISectionPreset("IPE 750 x 173", 762.0, 267.0, 14.4, 21.6),
    ISectionPreset("IPE 750 x 196", 770.0, 268.0, 15.6, 25.4),
    ISectionPreset("IPE 750 x 220", 779.0, 266.0, 16.5, 30.0),
]

CUSTOM = ISectionPreset(name="user", h=200.0, b=100.0, tw=5.6, tf=8.5)

PARAM_NAMES = ['h', 'b', 'tw', 'tf']
PARAM_DESCRIPTIONS = ['Total height', 'Flange width', 'Web thickness', 'Flange thickness']

def calculate_section_properties(params: dict) -> SectionProperties:
    """Compute section properties for an I section matching MpcBeamSection::compute() logic.
    Expects params with keys: h, b, tw, tf (matching PRESET field names: h, b, tw, tf).
    """
    h = params['h']
    B = params['b']
    b_web = params['tw']
    h_flange = params['tf']
    H = h - 2.0 * h_flange

    area = 2.0 * B * h_flange + b_web * H
    Iyy = (H**3) * (b_web / 12.0) + 2.0 * ((h_flange**3) * B / 12.0 + h_flange * B * ((H + h_flange)**2) / 4.0)
    Izz = (b_web**3) * H / 12.0 + 2.0 * (B**3 * h_flange / 12.0)
    J = (1.0 / 3.0) * (((H + h_flange) * (h_flange**3)) + 2.0 * B * (b_web**3))

    alphaY = 5.0 / 6.0 * _ureg.dimensionless
    alphaZ = 1.0 * _ureg.dimensionless
    centroidY = B / 2.0
    centroidZ = H / 2.0 + h_flange

    return SectionProperties(
        area=area, Iyy=Iyy, Izz=Izz, J=J,
        alphaY=alphaY, alphaZ=alphaZ,
        centroidY=centroidY, centroidZ=centroidZ,
    )

def calculate_extrusion_data(params: dict) -> MpcSectionExtrusionBeamData:
    h = float(params['h'])
    B = float(params['b'])
    b = float(params['tw'])
    hf = float(params['tf'])
    H = h - 2.0 * hf
    cx = B / 2.0
    cy = H / 2.0 + hf
    ed = MpcSectionExtrusionBeamData()
    ed.addPoint(0.0 - cx, 0.0 - cy)            # 0
    ed.addPoint(B - cx, 0.0 - cy)              # 1
    ed.addPoint(B - cx, hf - cy)               # 2
    ed.addPoint((B + b) / 2.0 - cx, hf - cy)  # 3
    ed.addPoint((B + b) / 2.0 - cx, H + hf - cy)  # 4
    ed.addPoint(B - cx, H + hf - cy)          # 5
    ed.addPoint(B - cx, H + 2.0 * hf - cy)    # 6
    ed.addPoint(0.0 - cx, H + 2.0 * hf - cy)  # 7
    ed.addPoint(0.0 - cx, H + hf - cy)        # 8
    ed.addPoint((B - b) / 2.0 - cx, H + hf - cy)  # 9
    ed.addPoint((B - b) / 2.0 - cx, hf - cy)  # 10
    ed.addPoint(0.0 - cx, hf - cy)            # 11
    # triangles
    ed.addTriangle(0, 1, 3)
    ed.addTriangle(1, 2, 3)
    ed.addTriangle(0, 3, 10)
    ed.addTriangle(10, 3, 4)
    ed.addTriangle(10, 4, 9)
    ed.addTriangle(4, 5, 6)
    ed.addTriangle(9, 4, 6)
    ed.addTriangle(9, 6, 7)
    ed.addTriangle(8, 9, 7)
    ed.addTriangle(0, 10, 11)
    # edges
    for i in range(12):
        ed.addEdge([i, (i + 1) % 12])
    # sweeps
    for i in range(12):
        ed.addSweep(i)
    return ed
