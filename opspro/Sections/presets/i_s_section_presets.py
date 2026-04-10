from dataclasses import dataclass
from typing import List
from .section_properties import SectionProperties, _ensure_quantity
from . import i_section_presets as i_section


@dataclass
class ISSectionPreset:
    name: str
    h: object
    b: object
    tw: object
    tf: object

    def __post_init__(self):
        _ensure_quantity(self, ['h', 'b', 'tw', 'tf'], 'mm')

PRESETS: List[ISSectionPreset] = [
    ISSectionPreset("S 3x7.5", 76.2, 63.8, 8.86, 6.6),
    ISSectionPreset("S 3x5.7", 76.2, 59.2, 4.32, 6.6),
    ISSectionPreset("S 4x9.5", 102.0, 71.1, 8.28, 7.44),
    ISSectionPreset("S 4x7.7", 102.0, 67.6, 4.9, 7.44),
    ISSectionPreset("S 5x10", 127.0, 76.2, 5.44, 8.28),
    ISSectionPreset("S 6x17.25", 152.0, 90.7, 11.8, 9.12),
    ISSectionPreset("S 6x12.5", 152.0, 84.6, 5.89, 9.12),
    ISSectionPreset("S 8x23", 203.0, 106.0, 11.2, 10.8),
    ISSectionPreset("S 8x18.4", 203.0, 102.0, 6.88, 10.8),
    ISSectionPreset("S 10x35", 254.0, 125.0, 15.1, 12.5),
    ISSectionPreset("S 10x25.4", 254.0, 118.0, 7.9, 12.5),
    ISSectionPreset("S 12x50", 305.0, 139.0, 17.4, 16.7),
    ISSectionPreset("S 12x40.8", 305.0, 133.0, 11.7, 16.7),
    ISSectionPreset("S 12x35", 305.0, 129.0, 10.9, 13.8),
    ISSectionPreset("S 12x31.8", 305.0, 127.0, 8.89, 13.8),
    ISSectionPreset("S 15x50", 381.0, 143.0, 14.0, 15.8),
    ISSectionPreset("S 15x42.9", 381.0, 140.0, 10.4, 15.8),
    ISSectionPreset("S 18x70", 457.0, 159.0, 18.1, 17.6),
    ISSectionPreset("S 18x54.7", 457.0, 152.0, 11.7, 17.6),
    ISSectionPreset("S 20x96", 516.0, 183.0, 20.3, 23.4),
    ISSectionPreset("S 20x86", 516.0, 179.0, 16.8, 23.4),
    ISSectionPreset("S 20x75", 508.0, 162.0, 16.1, 20.2),
    ISSectionPreset("S 20x66", 508.0, 159.0, 12.8, 20.2),
    ISSectionPreset("S 24x121", 622.0, 204.0, 20.3, 27.7),
    ISSectionPreset("S 24x106", 622.0, 200.0, 15.7, 27.7),
    ISSectionPreset("S 24x100", 610.0, 184.0, 18.9, 22.1),
    ISSectionPreset("S 24x90", 610.0, 181.0, 15.9, 22.1),
    ISSectionPreset("S 24x80", 610.0, 178.0, 12.7, 22.1),
]

CUSTOM = ISSectionPreset(name="user", h=203.0, b=106.0, tw=11.2, tf=10.8)

PARAM_NAMES = ['h', 'b', 'tw', 'tf']
PARAM_DESCRIPTIONS = ['Total height', 'Flange width', 'Web thickness', 'Flange thickness']

def calculate_section_properties(params: dict) -> SectionProperties:
    # Delegate to the I-section calculation to avoid duplication.
    return i_section.calculate_section_properties(params)

def calculate_extrusion_data(params: dict):
    return i_section.calculate_extrusion_data(params)
