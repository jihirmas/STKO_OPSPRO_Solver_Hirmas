"""
C_MC-section (miscellaneous channel) geometric presets database.

All values are in SI units (mm). Parameters:
  - name : string (designation)
  - h    : mm (height)
  - b    : mm (flange width)
  - tw   : mm (web thickness)
  - tf   : mm (flange thickness)

Sources: US/EN MC channels, legacy STKO CSV.
"""

from dataclasses import dataclass
from typing import List
from .section_properties import SectionProperties, _ensure_quantity
from . import c_section_presets as c_section


@dataclass
class CMCSectionPreset:
    name: str
    h: object
    b: object
    tw: object
    tf: object

    def __post_init__(self):
        _ensure_quantity(self, ['h', 'b', 'tw', 'tf'], 'mm')

PRESETS: List[CMCSectionPreset] = [
    CMCSectionPreset("MC 3x7.1", 76.2, 49.3, 7.92, 8.92),
    CMCSectionPreset("MC 4x13.8", 102, 63.5, 12.7, 12.7),
    CMCSectionPreset("MC 6x18", 152, 88.9, 9.63, 12.1),
    CMCSectionPreset("MC 6x15.3", 152, 88.9, 8.64, 9.78),
    CMCSectionPreset("MC 6x16.3", 152, 76.2, 9.53, 12.1),
    CMCSectionPreset("MC 6x15.1", 152, 74.7, 8.03, 12.1),
    CMCSectionPreset("MC 6x12", 152, 63.5, 7.87, 9.53),
    CMCSectionPreset("MC 6x7", 152, 47.8, 4.55, 7.39),
    CMCSectionPreset("MC 6x6.5", 152, 47, 3.94, 7.39),
    CMCSectionPreset("MC 7x22.7", 178, 91.4, 12.8, 12.7),
    CMCSectionPreset("MC 7x19.1", 178, 87.6, 8.94, 12.7),
    CMCSectionPreset("MC 8x22.8", 203, 88.9, 10.8, 13.3),
    CMCSectionPreset("MC 8x21.4", 203, 87.6, 9.53, 13.3),
    CMCSectionPreset("MC 8x20", 203, 77, 10.2, 12.7),
    CMCSectionPreset("MC 8x18.7", 203, 75.7, 8.97, 12.7),
    CMCSectionPreset("MC 8x8.5", 203, 47.5, 4.55, 7.9),
    CMCSectionPreset("MC 9x25.4", 229, 88.9, 11.4, 14),
    CMCSectionPreset("MC 9x23.9", 229, 87.6, 10.2, 14),
    CMCSectionPreset("MC 10x41.1", 254, 110, 20.2, 14.6),
    CMCSectionPreset("MC 10x33.6", 254, 104, 14.6, 14.6),
    CMCSectionPreset("MC 10x28.5", 254, 100, 10.8, 14.6),
    CMCSectionPreset("MC 10x25", 254, 86.6, 9.65, 14.6),
    CMCSectionPreset("MC 10x22", 254, 84.3, 7.37, 14.6),
    CMCSectionPreset("MC 10x8.4", 254, 38.1, 4.32, 7.11),
    CMCSectionPreset("MC 10x6.5", 254, 29.7, 3.86, 5.13),
    CMCSectionPreset("MC 12x50", 305, 105, 21.2, 17.8),
    CMCSectionPreset("MC 12x45", 305, 102, 18, 17.8),
    CMCSectionPreset("MC 12x40", 305, 98.8, 15, 17.8),
    CMCSectionPreset("MC 12x35", 305, 95.8, 11.8, 17.8),
    CMCSectionPreset("MC 12x31", 305, 93.2, 9.4, 17.8),
    CMCSectionPreset("MC 12x14.3", 305, 53.8, 6.35, 7.95),
    CMCSectionPreset("MC 12x10.6", 305, 38.1, 4.83, 7.85),
    CMCSectionPreset("MC 13x50", 330, 112, 20, 15.5),
    CMCSectionPreset("MC 13x40", 330, 106, 14.2, 15.5),
    CMCSectionPreset("MC 13x35", 330, 103, 11.4, 15.5),
    CMCSectionPreset("MC 13x31.8", 330, 102, 9.53, 15.5),
    CMCSectionPreset("MC 18x58", 457, 107, 17.8, 15.9),
    CMCSectionPreset("MC 18x51.9", 457, 104, 15.2, 15.9),
    CMCSectionPreset("MC 18x45.8", 457, 102, 12.7, 15.9),
    CMCSectionPreset("MC 18x42.7", 457, 100, 11.4, 15.9),
]

CUSTOM = CMCSectionPreset(name="user", h=152.0, b=63.5, tw=7.87, tf=9.53)

PARAM_NAMES = ['h', 'b', 'tw', 'tf']
PARAM_DESCRIPTIONS = ['Total height', 'Flange width', 'Web thickness', 'Flange thickness']

# Provide a local wrapper for readability that delegates to the implementation
# in `c_section_presets.py`.
def calculate_section_properties(params: dict) -> SectionProperties:
  """Wrapper around `c_section_presets.calculate_section_properties`.
  Keeps the same local API while delegating the computation to the canonical
  implementation to avoid code duplication.
  """
  return c_section.calculate_section_properties(params)

def calculate_extrusion_data(params: dict):
  return c_section.calculate_extrusion_data(params)
