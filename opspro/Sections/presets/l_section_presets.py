from dataclasses import dataclass
from typing import List
from .section_properties import SectionProperties, _ensure_quantity, _ureg
from PyMpc import MpcSectionExtrusionBeamData


@dataclass
class LSectionPreset:
    name: str
    h: object
    b: object
    t: object

    def __post_init__(self):
        _ensure_quantity(self, ['h', 'b', 't'], 'mm')

PRESETS: List[LSectionPreset] = [
    LSectionPreset("L2x2x0.375", 50.8, 50.8, 9.53),
    LSectionPreset("L2x2x0.3125", 50.8, 50.8, 7.94),
    LSectionPreset("L2x2x0.250", 50.8, 50.8, 6.35),
    LSectionPreset("L2x2x0.1875", 50.8, 50.8, 4.76),
    LSectionPreset("L2x2x0.125", 50.8, 50.8, 3.18),
    LSectionPreset("L2.5x2.5x0.500", 63.5, 63.5, 12.7),
    LSectionPreset("L2.5x2.5x0.375", 63.5, 63.5, 9.53),
    LSectionPreset("L2.5x2.5x0.3125", 63.5, 63.5, 7.94),
    LSectionPreset("L2.5x2.5x0.250", 63.5, 63.5, 6.35),
    LSectionPreset("L2.5x2.5x0.1875", 63.5, 63.5, 4.76),
    LSectionPreset("L2.5x2x0.375", 50.8, 63.5, 9.53),
    LSectionPreset("L2.5x2x0.3125", 50.8, 63.5, 7.94),
    LSectionPreset("L2.5x2x0.250", 50.8, 63.5, 6.35),
    LSectionPreset("L2.5x2x0.1875", 50.8, 63.5, 4.76),
    LSectionPreset("L2.5x1.5x0.250", 38.1, 63.5, 6.35),
    LSectionPreset("L2.5x1.5x0.1875", 38.1, 63.5, 4.76),
    LSectionPreset("L3x3x0.500", 76.2, 76.2, 12.7),
    LSectionPreset("L3x3x0.4375", 76.2, 76.2, 11.1),
    LSectionPreset("L3x3x0.375", 76.2, 76.2, 9.53),
    LSectionPreset("L3x3x0.3125", 76.2, 76.2, 7.94),
    LSectionPreset("L3x3x0.250", 76.2, 76.2, 6.35),
    LSectionPreset("L3x3x0.1875", 76.2, 76.2, 4.76),
    LSectionPreset("L3x2.5x0.500", 63.5, 76.2, 12.7),
    LSectionPreset("L3x2.5x0.4375", 63.5, 76.2, 11.1),
    LSectionPreset("L3x2.5x0.375", 63.5, 76.2, 9.53),
    LSectionPreset("L3x2.5x0.3125", 63.5, 76.2, 7.94),
    LSectionPreset("L3x2.5x0.250", 63.5, 76.2, 6.35),
    LSectionPreset("L3x2.5x0.1875", 63.5, 76.2, 4.76),
    LSectionPreset("L3x2x0.500", 50.8, 76.2, 12.7),
    LSectionPreset("L3x2x0.375", 50.8, 76.2, 9.53),
    LSectionPreset("L3x2x0.3125", 50.8, 76.2, 7.94),
    LSectionPreset("L3x2x0.250", 50.8, 76.2, 6.35),
    LSectionPreset("L3x2x0.1875", 50.8, 76.2, 4.76),
    LSectionPreset("L3.5x3.5x0.500", 88.9, 88.9, 12.7),
    LSectionPreset("L3.5x3.5x0.4375", 88.9, 88.9, 11.1),
    LSectionPreset("L3.5x3.5x0.375", 88.9, 88.9, 9.53),
    LSectionPreset("L3.5x3.5x0.3125", 88.9, 88.9, 7.94),
    LSectionPreset("L3.5x3.5x0.250", 88.9, 88.9, 6.35),
    LSectionPreset("L3.5x3x0.500", 76.2, 88.9, 12.7),
    LSectionPreset("L3.5x3x0.4375", 76.2, 88.9, 11.1),
    LSectionPreset("L3.5x3x0.375", 76.2, 88.9, 9.53),
    LSectionPreset("L3.5x3x0.3125", 76.2, 88.9, 7.94),
    LSectionPreset("L3.5x3x0.250", 76.2, 88.9, 6.35),
    LSectionPreset("L3.5x2.5x0.500", 63.5, 88.9, 12.7),
    LSectionPreset("L3.5x2.5x0.375", 63.5, 88.9, 9.53),
    LSectionPreset("L3.5x2.5x0.3125", 63.5, 88.9, 7.94),
    LSectionPreset("L3.5x2.5x0.250", 63.5, 88.9, 6.35),
    LSectionPreset("L4x4x0.750", 102.0, 102.0, 19.1),
    LSectionPreset("L4x4x0.625", 102.0, 102.0, 15.9),
    LSectionPreset("L4x4x0.500", 102.0, 102.0, 12.7),
    LSectionPreset("L4x4x0.4375", 102.0, 102.0, 11.1),
    LSectionPreset("L4x4x0.375", 102.0, 102.0, 9.53),
    LSectionPreset("L4x4x0.3125", 102.0, 102.0, 7.94),
    LSectionPreset("L4x4x0.250", 102.0, 102.0, 6.35),
    LSectionPreset("L4x3.5x0.500", 88.9, 102.0, 12.7),
    LSectionPreset("L4x3.5x0.375", 88.9, 102.0, 9.53),
    LSectionPreset("L4x3.5x0.3125", 88.9, 102.0, 7.94),
    LSectionPreset("L4x3.5x0.250", 88.9, 102.0, 6.35),
    LSectionPreset("L4x3x0.625", 76.2, 102.0, 15.9),
    LSectionPreset("L4x3x0.500", 76.2, 102.0, 12.7),
    LSectionPreset("L4x3x0.375", 76.2, 102.0, 9.53),
    LSectionPreset("L4x3x0.3125", 76.2, 102.0, 7.94),
    LSectionPreset("L4x3x0.250", 76.2, 102.0, 6.35),
    LSectionPreset("L5x5x0.875", 127.0, 127.0, 22.2),
    LSectionPreset("L5x5x0.750", 127.0, 127.0, 19.1),
    LSectionPreset("L5x5x0.625", 127.0, 127.0, 15.9),
    LSectionPreset("L5x5x0.500", 127.0, 127.0, 12.7),
    LSectionPreset("L5x5x0.4375", 127.0, 127.0, 11.1),
    LSectionPreset("L5x5x0.375", 127.0, 127.0, 9.53),
    LSectionPreset("L5x5x0.3125", 127.0, 127.0, 7.94),
    LSectionPreset("L5x3.5x0.750", 88.9, 127.0, 19.1),
    LSectionPreset("L5x3.5x0.625", 88.9, 127.0, 15.9),
    LSectionPreset("L5x3.5x0.500", 88.9, 127.0, 12.7),
    LSectionPreset("L5x3.5x0.375", 88.9, 127.0, 9.53),
    LSectionPreset("L5x3.5x0.3125", 88.9, 127.0, 7.94),
    LSectionPreset("L5x3.5x0.250", 88.9, 127.0, 6.35),
    LSectionPreset("L5x3x0.500", 76.2, 127.0, 12.7),
    LSectionPreset("L5x3x0.4375", 76.2, 127.0, 11.1),
    LSectionPreset("L5x3x0.375", 76.2, 127.0, 9.53),
    LSectionPreset("L5x3x0.3125", 76.2, 127.0, 7.94),
    LSectionPreset("L5x3x0.250", 76.2, 127.0, 6.35),
    LSectionPreset("L6x6x1", 152.0, 152.0, 25.4),
    LSectionPreset("L6x6x0.875", 152.0, 152.0, 22.2),
    LSectionPreset("L6x6x0.750", 152.0, 152.0, 19.1),
    LSectionPreset("L6x6x0.625", 152.0, 152.0, 15.9),
    LSectionPreset("L6x6x0.5625", 152.0, 152.0, 14.3),
    LSectionPreset("L6x6x0.500", 152.0, 152.0, 12.7),
    LSectionPreset("L6x6x0.4375", 152.0, 152.0, 11.1),
    LSectionPreset("L6x6x0.375", 152.0, 152.0, 9.53),
    LSectionPreset("L6x6x0.3125", 152.0, 152.0, 7.94),
    LSectionPreset("L6x4x0.875", 102.0, 152.0, 22.2),
    LSectionPreset("L6x4x0.750", 102.0, 152.0, 19.1),
    LSectionPreset("L6x4x0.625", 102.0, 152.0, 15.9),
    LSectionPreset("L6x4x0.5625", 102.0, 152.0, 14.3),
    LSectionPreset("L6x4x0.500", 102.0, 152.0, 12.7),
    LSectionPreset("L6x4x0.4375", 102.0, 152.0, 11.1),
    LSectionPreset("L6x4x0.375", 102.0, 152.0, 9.53),
    LSectionPreset("L6x4x0.3125", 102.0, 152.0, 7.94),
    LSectionPreset("L6x3.5x0.500", 88.9, 152.0, 12.7),
    LSectionPreset("L6x3.5x0.375", 88.9, 152.0, 9.53),
    LSectionPreset("L6x3.5x0.3125", 88.9, 152.0, 7.94),
    LSectionPreset("L7x4x0.750", 102.0, 178.0, 19.1),
    LSectionPreset("L7x4x0.625", 102.0, 178.0, 15.9),
    LSectionPreset("L7x4x0.500", 102.0, 178.0, 12.7),
    LSectionPreset("L7x4x0.4375", 102.0, 178.0, 11.1),
    LSectionPreset("L7x4x0.375", 102.0, 178.0, 9.53),
    LSectionPreset("L8x8x1.125", 203.0, 203.0, 28.6),
    LSectionPreset("L8x8x1", 203.0, 203.0, 25.4),
    LSectionPreset("L8x8x0.875", 203.0, 203.0, 22.2),
    LSectionPreset("L8x8x0.750", 203.0, 203.0, 19.1),
    LSectionPreset("L8x8x0.625", 203.0, 203.0, 15.9),
    LSectionPreset("L8x8x0.5625", 203.0, 203.0, 14.3),
    LSectionPreset("L8x8x0.500", 203.0, 203.0, 12.7),
    LSectionPreset("L8x6x1", 152.0, 203.0, 25.4),
    LSectionPreset("L8x6x0.875", 152.0, 203.0, 22.2),
    LSectionPreset("L8x6x0.750", 152.0, 203.0, 19.1),
    LSectionPreset("L8x6x0.625", 152.0, 203.0, 15.9),
    LSectionPreset("L8x6x0.5625", 152.0, 203.0, 14.3),
    LSectionPreset("L8x6x0.500", 152.0, 203.0, 12.7),
    LSectionPreset("L8x6x0.4375", 152.0, 203.0, 11.1),
    LSectionPreset("L8x4x1", 102.0, 203.0, 25.4),
    LSectionPreset("L8x4x0.875", 102.0, 203.0, 22.2),
    LSectionPreset("L8x4x0.750", 102.0, 203.0, 19.1),
    LSectionPreset("L8x4x0.625", 102.0, 203.0, 15.9),
    LSectionPreset("L8x4x0.5625", 102.0, 203.0, 14.3),
    LSectionPreset("L8x4x0.500", 102.0, 203.0, 12.7),
    LSectionPreset("L8x4x0.4375", 102.0, 203.0, 11.1),
]

CUSTOM = LSectionPreset(name="user", h=76.2, b=76.2, t=9.53)

PARAM_NAMES = ['h', 'b', 't']
PARAM_DESCRIPTIONS = ['Height', 'Width', 'Thickness']

def calculate_section_properties(params: dict) -> SectionProperties:
    # Implemented to match MpcBeamSection::compute() L-section logic.
    # Expects params with keys: h, b, t
    d = params['h']
    b = params['b']
    t = params['t']

    area = t * (b + d - t)
    Iyy = (b * d**3 - (b - t) * (d - t)**3) / 3.0 - area * ((d - (d**2 + b * t - t**2) / (2.0 * (b + d - t)))**2)
    Izz = (d * b**3 - (d - t) * (b - t)**3) / 3.0 - area * ((b - (b**2 + d * t - t**2) / (2.0 * (b + d - t)))**2)

    alphaY = 5.0 / 6.0 * _ureg.dimensionless
    alphaZ = 5.0 / 6.0 * _ureg.dimensionless

    centroidY = ( (b / 2.0) * (b * t) + (t / 2.0) * ((d - t) * t) ) / area
    centroidZ = ( (t / 2.0) * (b * t) + (((d - t) / 2.0 + t) * ((d - t) * t)) ) / area
    J = (1.0 / 3.0) * ((d - t / 2.0) * t**3 + (b - t / 2.0) * t**3)

    return SectionProperties(
        area=area, Iyy=Iyy, Izz=Izz, J=J,
        alphaY=alphaY, alphaZ=alphaZ,
        centroidY=centroidY, centroidZ=centroidZ,
    )

def calculate_extrusion_data(params: dict) -> MpcSectionExtrusionBeamData:
    d = float(params['h'])
    b = float(params['b'])
    t = float(params['t'])
    area = t * (b + d - t)
    cx = ((b / 2.0) * (b * t) + (t / 2.0) * ((d - t) * t)) / area
    cy = ((t / 2.0) * (b * t) + (((d - t) / 2.0 + t) * ((d - t) * t))) / area
    ed = MpcSectionExtrusionBeamData()
    ed.addPoint(0.0 - cx, 0.0 - cy)  # 0
    ed.addPoint(b - cx, 0.0 - cy)    # 1
    ed.addPoint(b - cx, t - cy)      # 2
    ed.addPoint(t - cx, t - cy)      # 3
    ed.addPoint(t - cx, d - cy)      # 4
    ed.addPoint(0.0 - cx, d - cy)    # 5
    # triangles
    ed.addTriangle(0, 1, 2)
    ed.addTriangle(0, 2, 3)
    ed.addTriangle(0, 3, 4)
    ed.addTriangle(0, 4, 5)
    # edges
    for i in range(6):
        ed.addEdge([i, (i + 1) % 6])
    # sweeps
    for i in range(6):
        ed.addSweep(i)
    return ed
