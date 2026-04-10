from dataclasses import dataclass
from typing import List
from .section_properties import SectionProperties, _ensure_quantity
from . import i_section_presets as i_section


@dataclass
class IHPSectionPreset:
    name: str
    h: object
    b: object
    tw: object
    tf: object

    def __post_init__(self):
        _ensure_quantity(self, ['h', 'b', 'tw', 'tf'], 'mm')

PRESETS: List[IHPSectionPreset] = [
    IHPSectionPreset("HP 8x36", 204.0, 207.0, 11.3, 11.3),
    IHPSectionPreset("HP 10x57", 254.0, 259.0, 14.4, 14.4),
    IHPSectionPreset("HP 10x42", 246.0, 257.0, 10.5, 10.7),
    IHPSectionPreset("HP 12x84", 312.0, 312.0, 17.4, 17.4),
    IHPSectionPreset("HP 12x74", 307.0, 310.0, 15.4, 15.5),
    IHPSectionPreset("HP 12x63", 302.0, 307.0, 13.1, 13.1),
    IHPSectionPreset("HP 12x53", 300.0, 305.0, 11.0, 11.0),
    IHPSectionPreset("HP 14x117", 361.0, 378.0, 20.4, 20.4),
    IHPSectionPreset("HP 14x102", 356.0, 376.0, 17.9, 17.9),
    IHPSectionPreset("HP 14x89", 351.0, 373.0, 15.6, 15.6),
    IHPSectionPreset("HP 14x73", 345.0, 371.0, 12.8, 12.8),
    IHPSectionPreset("HP 16x183", 419.0, 414.0, 28.7, 28.7),
    IHPSectionPreset("HP 16x162", 414.0, 408.9, 25.4, 25.4),
    IHPSectionPreset("HP 16x141", 406.0, 406.4, 22.2, 22.2),
    IHPSectionPreset("HP 16x121", 401.0, 403.9, 19.1, 19.1),
    IHPSectionPreset("HP 16x101", 394.0, 401.3, 15.9, 15.9),
    IHPSectionPreset("HP 16x88", 389.0, 398.8, 13.7, 13.7),
    IHPSectionPreset("HP 18x204", 465.0, 459.7, 28.7, 28.7),
    IHPSectionPreset("HP 18x181", 457.0, 457.2, 25.4, 25.4),
    IHPSectionPreset("HP 18x157", 451.0, 454.7, 22.1, 22.1),
    IHPSectionPreset("HP 18x135", 445.0, 452.1, 19.1, 19.1),
]

CUSTOM = IHPSectionPreset(name="user", h=254.0, b=259.0, tw=14.4, tf=14.4)

PARAM_NAMES = ['h', 'b', 'tw', 'tf']
PARAM_DESCRIPTIONS = ['Total height', 'Flange width', 'Web thickness', 'Flange thickness']

def calculate_section_properties(params: dict) -> SectionProperties:
    # Delegate to the I-section calculation to avoid duplication.
    return i_section.calculate_section_properties(params)

def calculate_extrusion_data(params: dict):
    return i_section.calculate_extrusion_data(params)
