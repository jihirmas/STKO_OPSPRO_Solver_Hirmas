"""
C-section (channel) geometric presets database.

All values are in SI units (mm, kg/m, ...). Parameters:
  - name : string (designation)
  - G    : kg/m (linear weight)
  - h    : mm (height)
  - b    : mm (flange width)
  - tw   : mm (web thickness)
  - tf   : mm (flange thickness)

Sources: US/EN standard channels, legacy STKO CSV.
"""


from dataclasses import dataclass
from typing import List
from .section_properties import SectionProperties, _ensure_quantity, _ureg
from PyMpc import MpcSectionExtrusionBeamData
import math


@dataclass
class CSectionPreset:
  name: str
  h: object
  b: object
  tw: object
  tf: object

  def __post_init__(self):
      _ensure_quantity(self, ['h', 'b', 'tw', 'tf'], 'mm')

# List of standard C-section presets (from section_C.csv)
PRESETS: List[CSectionPreset] = [
    CSectionPreset("C 3x6", 76.2, 40.6, 9.04, 6.93),
    CSectionPreset("C 3x5", 76.2, 38.1, 6.55, 6.93),
    CSectionPreset("C 3x4.1", 76.2, 35.8, 4.32, 6.93),
    CSectionPreset("C 3x3.5", 76.2, 34.8, 3.35, 6.93),
    CSectionPreset("C 4x7.25", 102, 43.7, 8.15, 7.52),
    CSectionPreset("C 4x6.25", 102, 41.91, 6.27, 6.91),
    CSectionPreset("C 4x5.4", 102, 40.1, 4.67, 7.52),
    CSectionPreset("C 4x4.5", 102, 40.1, 3.18, 7.52),
    CSectionPreset("C 5x9", 127, 48, 8.26, 8.13),
    CSectionPreset("C 5x6.7", 127, 44.5, 4.83, 8.13),
    CSectionPreset("C 6x13", 152, 54.9, 11.1, 8.71),
    CSectionPreset("C 6x10.5", 152, 51.6, 7.98, 8.71),
    CSectionPreset("C 6x8.2", 152, 48.8, 5.08, 8.71),
    CSectionPreset("C 7x14.75", 178, 58.4, 10.6, 9.3),
    CSectionPreset("C 7x12.25", 178, 55.6, 7.98, 9.3),
    CSectionPreset("C 7x9.8", 178, 53.1, 5.33, 9.3),
    CSectionPreset("C 8x18.75", 203, 64.3, 12.4, 9.91),
    CSectionPreset("C 8x13.75", 203, 59.4, 7.7, 9.91),
    CSectionPreset("C 8x11.5", 203, 57.4, 5.59, 9.91),
    CSectionPreset("C 9x20", 229, 67.3, 11.4, 10.5),
    CSectionPreset("C 9x15", 229, 63.2, 7.24, 10.5),
    CSectionPreset("C 9x13.4", 229, 61.7, 5.92, 10.5),
    CSectionPreset("C 10x30", 254, 77, 17.1, 11.1),
    CSectionPreset("C 10x25", 254, 73.4, 13.4, 11.1),
    CSectionPreset("C 10x20", 254, 69.6, 9.63, 11.1),
    CSectionPreset("C 10x15.3", 254, 66, 6.1, 11.1),
    CSectionPreset("C 12x30", 305, 80.5, 13, 12.7),
    CSectionPreset("C 12x25", 305, 77.5, 9.83, 12.7),
    CSectionPreset("C 12x20.7", 305, 74.7, 7.16, 12.7),
    CSectionPreset("C 15x50", 381, 94.5, 18.2, 16.5),
    CSectionPreset("C 15x40", 381, 89.4, 13.2, 16.5),
    CSectionPreset("C 15x33.9", 381, 86.4, 10.2, 16.5),
]

CUSTOM = CSectionPreset(name="user", h=152.0, b=48.8, tw=5.08, tf=8.71)

PARAM_NAMES = ['h', 'b', 'tw', 'tf']
PARAM_DESCRIPTIONS = ['Total height', 'Flange width', 'Web thickness', 'Flange thickness']

def calculate_section_properties(params: dict) -> SectionProperties:
  """
  Compute section properties for a C-section (channel).
  All dimensions are in mm.
  Expects a dict with keys: h, b, tw, tf.
  Returns a SectionProperties with area, Iyy, Izz, J, alphaY, alphaZ, centroidY, centroidZ.
  """
  h = params['h']
  b = params['b']
  tw = params['tw']
  tf = params['tf']
  H = h - 2.0 * tf
  B = b
  area = 2 * B * tf + H * tw
  Iyy = (H**3) * (tw/12.0) + 2 * ((tf**3)*B/12.0 + tf*B*((tf+H)**2)/4.0)
  num = 2*tf*B**2/2 + tw**2*H/2
  centroidY = num / area
  centroidZ = H/2.0 + tf
  Izz = (tw**3)*H/12.0 + tw*H*((num/area - tw/2.0)**2) + 2*B**3*tf/12.0 + 2*B*tf*((num/area - B/2.0)**2)
  J = (1.0/3.0)*((h-tf)*tf**3 + 2.0*(B-tw/2.0)*tw**3)
  alphaY = 5.0/6.0 * _ureg.dimensionless
  alphaZ = 1.0 * _ureg.dimensionless
  return SectionProperties(
      area=area, Iyy=Iyy, Izz=Izz, J=J,
      alphaY=alphaY, alphaZ=alphaZ,
      centroidY=centroidY, centroidZ=centroidZ,
  )

def calculate_extrusion_data(params: dict) -> MpcSectionExtrusionBeamData:
    h = float(params['h'])
    B = float(params['b'])
    tw = float(params['tw'])
    tf = float(params['tf'])
    H = h - 2.0 * tf
    # centroid
    area = 2.0 * B * tf + H * tw
    cx = (2.0 * tf * B**2 / 2.0 + tw**2 * H / 2.0) / area
    cy = H / 2.0 + tf
    ed = MpcSectionExtrusionBeamData()
    ed.addPoint(-cx, -cy)                    # 0
    ed.addPoint(B - cx, -cy)                 # 1
    ed.addPoint(B - cx, tf - cy)             # 2
    ed.addPoint(tw - cx, tf - cy)            # 3
    ed.addPoint(tw - cx, H + tf - cy)        # 4
    ed.addPoint(B - cx, H + tf - cy)         # 5
    ed.addPoint(B - cx, H + 2.0 * tf - cy)  # 6
    ed.addPoint(-cx, H + 2.0 * tf - cy)     # 7
    # triangles
    ed.addTriangle(0, 1, 2)
    ed.addTriangle(2, 3, 0)
    ed.addTriangle(0, 3, 7)
    ed.addTriangle(7, 3, 4)
    ed.addTriangle(7, 4, 6)
    ed.addTriangle(4, 5, 6)
    # edges
    for i in range(8):
        ed.addEdge([i, (i + 1) % 8])
    # sweeps
    for i in range(8):
        ed.addSweep(i)
    return ed
