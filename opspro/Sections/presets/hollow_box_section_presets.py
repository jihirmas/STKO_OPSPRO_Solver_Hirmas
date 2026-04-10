
from dataclasses import dataclass
from .section_properties import SectionProperties, _ensure_quantity, _ureg
from PyMpc import MpcSectionExtrusionBeamData
import math


@dataclass
class HollowBoxSectionPreset:
    name: str
    h: object  # outer height
    b: object  # outer width
    t: object  # wall thickness (single value)

    def __post_init__(self):
        _ensure_quantity(self, ['h', 'b', 't'], 'mm')
    
PRESETS = [
    HollowBoxSectionPreset(name="HSS 2x2x0.250", h=50.8, b=33, t=4.76),
    HollowBoxSectionPreset(name="HSS 2x2x0.1875", h=50.8, b=37.6, t=3.18),
    HollowBoxSectionPreset(name="HSS 2x2x0.125", h=50.8, b=41.9, t=4.76),
    HollowBoxSectionPreset(name="HSS 2x1.5x0.1875", h=50.8, b=37.6, t=3.18),
    HollowBoxSectionPreset(name="HSS 2x1.5x0.125", h=50.8, b=41.9, t=4.76),
    HollowBoxSectionPreset(name="HSS 2x1x0.1875", h=50.8, b=37.6, t=3.18),
    HollowBoxSectionPreset(name="HSS 2x1x0.125", h=50.8, b=41.9, t=6.35),
    HollowBoxSectionPreset(name="HSS 2.25x2.25x0.250", h=57.2, b=39.4, t=4.76),
    HollowBoxSectionPreset(name="HSS 2.25x2.25x0.1875", h=57.2, b=43.9, t=3.18),
    HollowBoxSectionPreset(name="HSS 2.25x2.25x0.125", h=57.2, b=48.3, t=4.76),
    HollowBoxSectionPreset(name="HSS 2.25x2x0.1875", h=57.2, b=43.9, t=3.18),
    HollowBoxSectionPreset(name="HSS 2.25x2x0.125", h=57.2, b=48.3, t=7.94),
    HollowBoxSectionPreset(name="HSS 2.5x2.5x0.3125", h=63.5, b=41.4, t=6.35),
    HollowBoxSectionPreset(name="HSS 2.5x2.5x0.250", h=63.5, b=45.7, t=4.76),
    HollowBoxSectionPreset(name="HSS 2.5x2.5x0.1875", h=63.5, b=50.3, t=3.18),
    HollowBoxSectionPreset(name="HSS 2.5x2.5x0.125", h=63.5, b=54.6, t=6.35),
    HollowBoxSectionPreset(name="HSS 2.5x2x0.250", h=63.5, b=45.7, t=4.76),
    HollowBoxSectionPreset(name="HSS 2.5x2x0.1875", h=63.5, b=50.3, t=3.18),
    HollowBoxSectionPreset(name="HSS 2.5x2x0.125", h=63.5, b=54.6, t=6.35),
    HollowBoxSectionPreset(name="HSS 2.5x1.5x0.250", h=63.5, b=45.7, t=4.76),
    HollowBoxSectionPreset(name="HSS 2.5x1.5x0.1875", h=63.5, b=50.3, t=3.18),
    HollowBoxSectionPreset(name="HSS 2.5x1.5x0.125", h=63.5, b=54.6, t=4.76),
    HollowBoxSectionPreset(name="HSS 2.5x1x0.1875", h=63.5, b=50.3, t=3.18),
    HollowBoxSectionPreset(name="HSS 2.5x1x0.125", h=63.5, b=54.6, t=9.53),
    HollowBoxSectionPreset(name="HSS 3x3x0.375", h=76.2, b=49.5, t=7.94),
    HollowBoxSectionPreset(name="HSS 3x3x0.3125", h=76.2, b=54.1, t=6.35),
    HollowBoxSectionPreset(name="HSS 3x3x0.250", h=76.2, b=58.4, t=4.76),
    HollowBoxSectionPreset(name="HSS 3x3x0.1875", h=76.2, b=63, t=3.18),
    HollowBoxSectionPreset(name="HSS 3x3x0.125", h=76.2, b=67.3, t=7.94),
    HollowBoxSectionPreset(name="HSS 3x2.5x0.3125", h=76.2, b=54.1, t=6.35),
    HollowBoxSectionPreset(name="HSS 3x2.5x0.250", h=76.2, b=58.4, t=4.76),
    HollowBoxSectionPreset(name="HSS 3x2.5x0.1875", h=76.2, b=63, t=3.18),
    HollowBoxSectionPreset(name="HSS 3x2.5x0.125", h=76.2, b=67.3, t=7.94),
    HollowBoxSectionPreset(name="HSS 3x2x0.3125", h=76.2, b=54.1, t=6.35),
    HollowBoxSectionPreset(name="HSS 3x2x0.250", h=76.2, b=58.4, t=4.76),
    HollowBoxSectionPreset(name="HSS 3x2x0.1875", h=76.2, b=63, t=3.18),
    HollowBoxSectionPreset(name="HSS 3x2x0.125", h=76.2, b=67.3, t=6.35),
    HollowBoxSectionPreset(name="HSS 3x1.5x0.250", h=76.2, b=58.4, t=4.76),
    HollowBoxSectionPreset(name="HSS 3x1.5x0.1875", h=76.2, b=63, t=3.18),
    HollowBoxSectionPreset(name="HSS 3x1.5x0.125", h=76.2, b=67.3, t=4.76),
    HollowBoxSectionPreset(name="HSS 3x1x0.1875", h=76.2, b=63, t=3.18),
    HollowBoxSectionPreset(name="HSS 3x1x0.125", h=76.2, b=67.3, t=9.53),
    HollowBoxSectionPreset(name="HSS 3.5x3.5x0.375", h=88.9, b=62.2, t=7.94),
    HollowBoxSectionPreset(name="HSS 3.5x3.5x0.3125", h=88.9, b=66.8, t=6.35),
    HollowBoxSectionPreset(name="HSS 3.5x3.5x0.250", h=88.9, b=71.1, t=4.76),
    HollowBoxSectionPreset(name="HSS 3.5x3.5x0.1875", h=88.9, b=75.7, t=3.18),
    HollowBoxSectionPreset(name="HSS 3.5x3.5x0.125", h=88.9, b=80, t=9.53),
    HollowBoxSectionPreset(name="HSS 3.5x2.5x0.375", h=88.9, b=62.2, t=7.94),
    HollowBoxSectionPreset(name="HSS 3.5x2.5x0.3125", h=88.9, b=66.8, t=6.35),
    HollowBoxSectionPreset(name="HSS 3.5x2.5x0.250", h=88.9, b=71.1, t=4.76),
    HollowBoxSectionPreset(name="HSS 3.5x2.5x0.1875", h=88.9, b=75.7, t=3.18),
    HollowBoxSectionPreset(name="HSS 3.5x2.5x0.125", h=88.9, b=80, t=6.35),
    HollowBoxSectionPreset(name="HSS 3.5x2x0.250", h=88.9, b=71.1, t=4.76),
    HollowBoxSectionPreset(name="HSS 3.5x2x0.1875", h=88.9, b=75.7, t=3.18),
    HollowBoxSectionPreset(name="HSS 3.5x2x0.125", h=88.9, b=80, t=6.35),
    HollowBoxSectionPreset(name="HSS 3.5x1.5x0.250", h=88.9, b=71.1, t=4.76),
    HollowBoxSectionPreset(name="HSS 3.5x1.5x0.1875", h=88.9, b=75.7, t=3.18),
    HollowBoxSectionPreset(name="HSS 3.5x1.5x0.125", h=88.9, b=80, t=12.7),
    HollowBoxSectionPreset(name="HSS 4x4x0.500", h=102, b=66, t=9.53),
    HollowBoxSectionPreset(name="HSS 4x4x0.375", h=102, b=74.9, t=7.94),
    HollowBoxSectionPreset(name="HSS 4x4x0.3125", h=102, b=79.5, t=6.35),
    HollowBoxSectionPreset(name="HSS 4x4x0.250", h=102, b=83.8, t=4.76),
    HollowBoxSectionPreset(name="HSS 4x4x0.1875", h=102, b=88.4, t=3.18),
    HollowBoxSectionPreset(name="HSS 4x4x0.125", h=102, b=92.7, t=9.53),
    HollowBoxSectionPreset(name="HSS 4x3x0.375", h=102, b=74.9, t=7.94),
    HollowBoxSectionPreset(name="HSS 4x3x0.3125", h=102, b=79.5, t=6.35),
    HollowBoxSectionPreset(name="HSS 4x3x0.250", h=102, b=83.8, t=4.76),
    HollowBoxSectionPreset(name="HSS 4x3x0.1875", h=102, b=88.4, t=3.18),
    HollowBoxSectionPreset(name="HSS 4x3x0.125", h=102, b=92.7, t=9.53),
    HollowBoxSectionPreset(name="HSS 4x2.5x0.375", h=102, b=74.9, t=7.94),
    HollowBoxSectionPreset(name="HSS 4x2.5x0.3125", h=102, b=79.5, t=6.35),
    HollowBoxSectionPreset(name="HSS 4x2.5x0.250", h=102, b=83.8, t=4.76),
    HollowBoxSectionPreset(name="HSS 4x2.5x0.1875", h=102, b=88.4, t=3.18),
    HollowBoxSectionPreset(name="HSS 4x2.5x0.125", h=102, b=92.7, t=9.53),
    HollowBoxSectionPreset(name="HSS 4x2x0.375", h=102, b=74.9, t=7.94),
    HollowBoxSectionPreset(name="HSS 4x2x0.3125", h=102, b=79.5, t=6.35),
    HollowBoxSectionPreset(name="HSS 4x2x0.250", h=102, b=83.8, t=4.76),
    HollowBoxSectionPreset(name="HSS 4x2x0.1875", h=102, b=88.4, t=3.18),
    HollowBoxSectionPreset(name="HSS 4x2x0.125", h=102, b=92.7, t=12.7),
    HollowBoxSectionPreset(name="HSS 4.5x4.5x0.500", h=114, b=78.7, t=9.53),
    HollowBoxSectionPreset(name="HSS 4.5x4.5x0.375", h=114, b=87.6, t=7.94),
    HollowBoxSectionPreset(name="HSS 4.5x4.5x0.3125", h=114, b=92.2, t=6.35),
    HollowBoxSectionPreset(name="HSS 4.5x4.5x0.250", h=114, b=96.5, t=4.76),
    HollowBoxSectionPreset(name="HSS 4.5x4.5x0.1875", h=114, b=101, t=3.18),
    HollowBoxSectionPreset(name="HSS 4.5x4.5x0.125", h=114, b=105, t=12.7),
    HollowBoxSectionPreset(name="HSS 5x5x0.500", h=127, b=91.4, t=9.53),
    HollowBoxSectionPreset(name="HSS 5x5x0.375", h=127, b=100, t=7.94),
    HollowBoxSectionPreset(name="HSS 5x5x0.3125", h=127, b=105, t=6.35),
    HollowBoxSectionPreset(name="HSS 5x5x0.250", h=127, b=109, t=4.76),
    HollowBoxSectionPreset(name="HSS 5x5x0.1875", h=127, b=114, t=3.18),
    HollowBoxSectionPreset(name="HSS 5x5x0.125", h=127, b=118, t=12.7),
    HollowBoxSectionPreset(name="HSS 5x4x0.500", h=127, b=91.4, t=9.53),
    HollowBoxSectionPreset(name="HSS 5x4x0.375", h=127, b=100, t=7.94),
    HollowBoxSectionPreset(name="HSS 5x4x0.3125", h=127, b=105, t=6.35),
    HollowBoxSectionPreset(name="HSS 5x4x0.250", h=127, b=109, t=4.76),
    HollowBoxSectionPreset(name="HSS 5x4x0.1875", h=127, b=114, t=3.18),
    HollowBoxSectionPreset(name="HSS 5x4x0.125", h=127, b=118, t=12.7),
    HollowBoxSectionPreset(name="HSS 5x3x0.500", h=127, b=91.4, t=9.53),
    HollowBoxSectionPreset(name="HSS 5x3x0.375", h=127, b=100, t=7.94),
    HollowBoxSectionPreset(name="HSS 5x3x0.3125", h=127, b=105, t=6.35),
    HollowBoxSectionPreset(name="HSS 5x3x0.250", h=127, b=109, t=4.76),
    HollowBoxSectionPreset(name="HSS 5x3x0.1875", h=127, b=114, t=3.18),
    HollowBoxSectionPreset(name="HSS 5x3x0.125", h=127, b=118, t=6.35),
    HollowBoxSectionPreset(name="HSS 5x2.5x0.250", h=127, b=109, t=4.76),
    HollowBoxSectionPreset(name="HSS 5x2.5x0.1875", h=127, b=114, t=3.18),
    HollowBoxSectionPreset(name="HSS 5x2.5x0.125", h=127, b=118, t=9.53),
    HollowBoxSectionPreset(name="HSS 5x2x0.375", h=127, b=100, t=7.94),
    HollowBoxSectionPreset(name="HSS 5x2x0.3125", h=127, b=105, t=6.35),
    HollowBoxSectionPreset(name="HSS 5x2x0.250", h=127, b=109, t=4.76),
    HollowBoxSectionPreset(name="HSS 5x2x0.1875", h=127, b=114, t=3.18),
    HollowBoxSectionPreset(name="HSS 5x2x0.125", h=127, b=118, t=9.53),
    HollowBoxSectionPreset(name="HSS 5.5x5.5x0.375", h=140, b=113, t=7.94),
    HollowBoxSectionPreset(name="HSS 5.5x5.5x0.3125", h=140, b=118, t=6.35),
    HollowBoxSectionPreset(name="HSS 5.5x5.5x0.250", h=140, b=122, t=4.76),
    HollowBoxSectionPreset(name="HSS 5.5x5.5x0.1875", h=140, b=126, t=3.18),
    HollowBoxSectionPreset(name="HSS 5.5x5.5x0.125", h=140, b=131, t=15.9),
    HollowBoxSectionPreset(name="HSS 6x6x0.625", h=152, b=108, t=12.7),
    HollowBoxSectionPreset(name="HSS 6x6x0.500", h=152, b=117, t=9.53),
    HollowBoxSectionPreset(name="HSS 6x6x0.375", h=152, b=126, t=7.94),
    HollowBoxSectionPreset(name="HSS 6x6x0.3125", h=152, b=130, t=6.35),
    HollowBoxSectionPreset(name="HSS 6x6x0.250", h=152, b=135, t=4.76),
    HollowBoxSectionPreset(name="HSS 6x6x0.1875", h=152, b=139, t=3.18),
    HollowBoxSectionPreset(name="HSS 6x6x0.125", h=152, b=144, t=12.7),
    HollowBoxSectionPreset(name="HSS 6x5x0.500", h=152, b=117, t=9.53),
    HollowBoxSectionPreset(name="HSS 6x5x0.375", h=152, b=126, t=7.94),
    HollowBoxSectionPreset(name="HSS 6x5x0.3125", h=152, b=130, t=6.35),
    HollowBoxSectionPreset(name="HSS 6x5x0.250", h=152, b=135, t=4.76),
    HollowBoxSectionPreset(name="HSS 6x5x0.1875", h=152, b=139, t=3.18),
    HollowBoxSectionPreset(name="HSS 6x5x0.125", h=152, b=144, t=12.7),
    HollowBoxSectionPreset(name="HSS 6x4x0.500", h=152, b=117, t=9.53),
    HollowBoxSectionPreset(name="HSS 6x4x0.375", h=152, b=126, t=7.94),
    HollowBoxSectionPreset(name="HSS 6x4x0.3125", h=152, b=130, t=6.35),
    HollowBoxSectionPreset(name="HSS 6x4x0.250", h=152, b=135, t=4.76),
    HollowBoxSectionPreset(name="HSS 6x4x0.1875", h=152, b=139, t=3.18),
    HollowBoxSectionPreset(name="HSS 6x4x0.125", h=152, b=144, t=12.7),
    HollowBoxSectionPreset(name="HSS 6x3x0.500", h=152, b=117, t=9.53),
    HollowBoxSectionPreset(name="HSS 6x3x0.375", h=152, b=126, t=7.94),
    HollowBoxSectionPreset(name="HSS 6x3x0.3125", h=152, b=130, t=6.35),
    HollowBoxSectionPreset(name="HSS 6x3x0.250", h=152, b=135, t=4.76),
    HollowBoxSectionPreset(name="HSS 6x3x0.1875", h=152, b=139, t=3.18),
    HollowBoxSectionPreset(name="HSS 6x3x0.125", h=152, b=144, t=9.53),
    HollowBoxSectionPreset(name="HSS 6x2x0.375", h=152, b=126, t=7.94),
    HollowBoxSectionPreset(name="HSS 6x2x0.3125", h=152, b=130, t=6.35),
    HollowBoxSectionPreset(name="HSS 6x2x0.250", h=152, b=135, t=4.76),
    HollowBoxSectionPreset(name="HSS 6x2x0.1875", h=152, b=139, t=3.18),
    HollowBoxSectionPreset(name="HSS 6x2x0.125", h=152, b=144, t=15.9),
    HollowBoxSectionPreset(name="HSS 7x7x0.625", h=178, b=134, t=12.7),
    HollowBoxSectionPreset(name="HSS 7x7x0.500", h=178, b=142, t=9.53),
    HollowBoxSectionPreset(name="HSS 7x7x0.375", h=178, b=151, t=7.94),
    HollowBoxSectionPreset(name="HSS 7x7x0.3125", h=178, b=156, t=6.35),
    HollowBoxSectionPreset(name="HSS 7x7x0.250", h=178, b=160, t=4.76),
    HollowBoxSectionPreset(name="HSS 7x7x0.1875", h=178, b=165, t=3.18),
    HollowBoxSectionPreset(name="HSS 7x7x0.125", h=178, b=169, t=12.7),
    HollowBoxSectionPreset(name="HSS 7x5x0.500", h=178, b=142, t=9.53),
    HollowBoxSectionPreset(name="HSS 7x5x0.375", h=178, b=151, t=7.94),
    HollowBoxSectionPreset(name="HSS 7x5x0.3125", h=178, b=156, t=6.35),
    HollowBoxSectionPreset(name="HSS 7x5x0.250", h=178, b=160, t=4.76),
    HollowBoxSectionPreset(name="HSS 7x5x0.1875", h=178, b=165, t=3.18),
    HollowBoxSectionPreset(name="HSS 7x5x0.125", h=178, b=169, t=12.7),
    HollowBoxSectionPreset(name="HSS 7x4x0.500", h=178, b=142, t=9.53),
    HollowBoxSectionPreset(name="HSS 7x4x0.375", h=178, b=151, t=7.94),
    HollowBoxSectionPreset(name="HSS 7x4x0.3125", h=178, b=156, t=6.35),
    HollowBoxSectionPreset(name="HSS 7x4x0.250", h=178, b=160, t=4.76),
    HollowBoxSectionPreset(name="HSS 7x4x0.1875", h=178, b=165, t=3.18),
    HollowBoxSectionPreset(name="HSS 7x4x0.125", h=178, b=169, t=12.7),
    HollowBoxSectionPreset(name="HSS 7x3x0.500", h=178, b=142, t=9.53),
    HollowBoxSectionPreset(name="HSS 7x3x0.375", h=178, b=151, t=7.94),
    HollowBoxSectionPreset(name="HSS 7x3x0.3125", h=178, b=156, t=6.35),
    HollowBoxSectionPreset(name="HSS 7x3x0.250", h=178, b=160, t=4.76),
    HollowBoxSectionPreset(name="HSS 7x3x0.1875", h=178, b=165, t=3.18),
    HollowBoxSectionPreset(name="HSS 7x3x0.125", h=178, b=169, t=6.35),
    HollowBoxSectionPreset(name="HSS 7x2x0.250", h=178, b=160, t=4.76),
    HollowBoxSectionPreset(name="HSS 7x2x0.1875", h=178, b=165, t=3.18),
    HollowBoxSectionPreset(name="HSS 7x2x0.125", h=178, b=169, t=15.9),
    HollowBoxSectionPreset(name="HSS 8x8x0.625", h=203, b=159, t=12.7),
    HollowBoxSectionPreset(name="HSS 8x8x0.500", h=203, b=168, t=9.53),
    HollowBoxSectionPreset(name="HSS 8x8x0.375", h=203, b=177, t=7.94),
    HollowBoxSectionPreset(name="HSS 8x8x0.3125", h=203, b=181, t=6.35),
    HollowBoxSectionPreset(name="HSS 8x8x0.250", h=203, b=185, t=4.76),
    HollowBoxSectionPreset(name="HSS 8x8x0.1875", h=203, b=190, t=3.18),
    HollowBoxSectionPreset(name="HSS 8x8x0.125", h=203, b=194, t=15.9),
    HollowBoxSectionPreset(name="HSS 8x6x0.625", h=203, b=159, t=12.7),
    HollowBoxSectionPreset(name="HSS 8x6x0.500", h=203, b=168, t=9.53),
    HollowBoxSectionPreset(name="HSS 8x6x0.375", h=203, b=177, t=7.94),
    HollowBoxSectionPreset(name="HSS 8x6x0.3125", h=203, b=181, t=6.35),
    HollowBoxSectionPreset(name="HSS 8x6x0.250", h=203, b=185, t=4.76),
    HollowBoxSectionPreset(name="HSS 8x6x0.1875", h=203, b=190, t=15.9),
    HollowBoxSectionPreset(name="HSS 8x4x0.625", h=203, b=159, t=12.7),
    HollowBoxSectionPreset(name="HSS 8x4x0.500", h=203, b=168, t=9.53),
    HollowBoxSectionPreset(name="HSS 8x4x0.375", h=203, b=177, t=7.94),
    HollowBoxSectionPreset(name="HSS 8x4x0.3125", h=203, b=181, t=6.35),
    HollowBoxSectionPreset(name="HSS 8x4x0.250", h=203, b=185, t=4.76),
    HollowBoxSectionPreset(name="HSS 8x4x0.1875", h=203, b=190, t=3.18),
    HollowBoxSectionPreset(name="HSS 8x4x0.125", h=203, b=194, t=12.7),
    HollowBoxSectionPreset(name="HSS 8x3x0.500", h=203, b=168, t=9.53),
    HollowBoxSectionPreset(name="HSS 8x3x0.375", h=203, b=177, t=7.94),
    HollowBoxSectionPreset(name="HSS 8x3x0.3125", h=203, b=181, t=6.35),
    HollowBoxSectionPreset(name="HSS 8x3x0.250", h=203, b=185, t=4.76),
    HollowBoxSectionPreset(name="HSS 8x3x0.1875", h=203, b=190, t=3.18),
    HollowBoxSectionPreset(name="HSS 8x3x0.125", h=203, b=194, t=9.53),
    HollowBoxSectionPreset(name="HSS 8x2x0.375", h=203, b=177, t=7.94),
    HollowBoxSectionPreset(name="HSS 8x2x0.3125", h=203, b=181, t=6.35),
    HollowBoxSectionPreset(name="HSS 8x2x0.250", h=203, b=185, t=4.76),
    HollowBoxSectionPreset(name="HSS 8x2x0.1875", h=203, b=190, t=3.18),
    HollowBoxSectionPreset(name="HSS 8x2x0.125", h=203, b=194, t=15.9),
    HollowBoxSectionPreset(name="HSS 9x9x0.625", h=229, b=184, t=12.7),
    HollowBoxSectionPreset(name="HSS 9x9x0.500", h=229, b=193, t=9.53),
    HollowBoxSectionPreset(name="HSS 9x9x0.375", h=229, b=202, t=7.94),
    HollowBoxSectionPreset(name="HSS 9x9x0.3125", h=229, b=207, t=6.35),
    HollowBoxSectionPreset(name="HSS 9x9x0.250", h=229, b=211, t=4.76),
    HollowBoxSectionPreset(name="HSS 9x9x0.1875", h=229, b=215, t=3.18),
    HollowBoxSectionPreset(name="HSS 9x9x0.125", h=229, b=220, t=15.9),
    HollowBoxSectionPreset(name="HSS 9x7x0.625", h=229, b=184, t=12.7),
    HollowBoxSectionPreset(name="HSS 9x7x0.500", h=229, b=193, t=9.53),
    HollowBoxSectionPreset(name="HSS 9x7x0.375", h=229, b=202, t=7.94),
    HollowBoxSectionPreset(name="HSS 9x7x0.3125", h=229, b=207, t=6.35),
    HollowBoxSectionPreset(name="HSS 9x7x0.250", h=229, b=211, t=4.76),
    HollowBoxSectionPreset(name="HSS 9x7x0.1875", h=229, b=215, t=15.9),
    HollowBoxSectionPreset(name="HSS 9x5x0.625", h=229, b=184, t=12.7),
    HollowBoxSectionPreset(name="HSS 9x5x0.500", h=229, b=193, t=9.53),
    HollowBoxSectionPreset(name="HSS 9x5x0.375", h=229, b=202, t=7.94),
    HollowBoxSectionPreset(name="HSS 9x5x0.3125", h=229, b=207, t=6.35),
    HollowBoxSectionPreset(name="HSS 9x5x0.250", h=229, b=211, t=4.76),
    HollowBoxSectionPreset(name="HSS 9x5x0.1875", h=229, b=215, t=12.7),
    HollowBoxSectionPreset(name="HSS 9x3x0.500", h=229, b=193, t=9.53),
    HollowBoxSectionPreset(name="HSS 9x3x0.375", h=229, b=202, t=7.94),
    HollowBoxSectionPreset(name="HSS 9x3x0.3125", h=229, b=207, t=6.35),
    HollowBoxSectionPreset(name="HSS 9x3x0.250", h=229, b=211, t=4.76),
    HollowBoxSectionPreset(name="HSS 9x3x0.1875", h=229, b=215, t=15.9),
    HollowBoxSectionPreset(name="HSS 10x10x0.625", h=254, b=210, t=12.7),
    HollowBoxSectionPreset(name="HSS 10x10x0.500", h=254, b=218, t=9.53),
    HollowBoxSectionPreset(name="HSS 10x10x0.375", h=254, b=227, t=7.94),
    HollowBoxSectionPreset(name="HSS 10x10x0.3125", h=254, b=232, t=6.35),
    HollowBoxSectionPreset(name="HSS 10x10x0.250", h=254, b=236, t=4.76),
    HollowBoxSectionPreset(name="HSS 10x10x0.1875", h=254, b=241, t=15.9),
    HollowBoxSectionPreset(name="HSS 10x8x0.625", h=254, b=210, t=12.7),
    HollowBoxSectionPreset(name="HSS 10x8x0.500", h=254, b=218, t=9.53),
    HollowBoxSectionPreset(name="HSS 10x8x0.375", h=254, b=227, t=7.94),
    HollowBoxSectionPreset(name="HSS 10x8x0.3125", h=254, b=232, t=6.35),
    HollowBoxSectionPreset(name="HSS 10x8x0.250", h=254, b=236, t=4.76),
    HollowBoxSectionPreset(name="HSS 10x8x0.1875", h=254, b=241, t=15.9),
    HollowBoxSectionPreset(name="HSS 10x6x0.625", h=254, b=210, t=12.7),
    HollowBoxSectionPreset(name="HSS 10x6x0.500", h=254, b=218, t=9.53),
    HollowBoxSectionPreset(name="HSS 10x6x0.375", h=254, b=227, t=7.94),
    HollowBoxSectionPreset(name="HSS 10x6x0.3125", h=254, b=232, t=6.35),
    HollowBoxSectionPreset(name="HSS 10x6x0.250", h=254, b=236, t=4.76),
    HollowBoxSectionPreset(name="HSS 10x6x0.1875", h=254, b=241, t=9.53),
    HollowBoxSectionPreset(name="HSS 10x5x0.375", h=254, b=227, t=7.94),
    HollowBoxSectionPreset(name="HSS 10x5x0.3125", h=254, b=232, t=6.35),
    HollowBoxSectionPreset(name="HSS 10x5x0.250", h=254, b=236, t=4.76),
    HollowBoxSectionPreset(name="HSS 10x5x0.1875", h=254, b=241, t=15.9),
    HollowBoxSectionPreset(name="HSS 10x4x0.625", h=254, b=210, t=12.7),
    HollowBoxSectionPreset(name="HSS 10x4x0.500", h=254, b=218, t=9.53),
    HollowBoxSectionPreset(name="HSS 10x4x0.375", h=254, b=227, t=7.94),
    HollowBoxSectionPreset(name="HSS 10x4x0.3125", h=254, b=232, t=6.35),
    HollowBoxSectionPreset(name="HSS 10x4x0.250", h=254, b=236, t=4.76),
    HollowBoxSectionPreset(name="HSS 10x4x0.1875", h=254, b=241, t=3.18),
    HollowBoxSectionPreset(name="HSS 10x4x0.125", h=254, b=245, t=12.7),
    HollowBoxSectionPreset(name="HSS 10x3.5x0.500", h=254, b=218, t=9.53),
    HollowBoxSectionPreset(name="HSS 10x3.5x0.375", h=254, b=227, t=7.94),
    HollowBoxSectionPreset(name="HSS 10x3.5x0.3125", h=254, b=232, t=6.35),
    HollowBoxSectionPreset(name="HSS 10x3.5x0.250", h=254, b=236, t=4.76),
    HollowBoxSectionPreset(name="HSS 10x3.5x0.1875", h=254, b=241, t=3.18),
    HollowBoxSectionPreset(name="HSS 10x3.5x0.125", h=254, b=245, t=9.53),
    HollowBoxSectionPreset(name="HSS 10x3x0.375", h=254, b=227, t=7.94),
    HollowBoxSectionPreset(name="HSS 10x3x0.3125", h=254, b=232, t=6.35),
    HollowBoxSectionPreset(name="HSS 10x3x0.250", h=254, b=236, t=4.76),
    HollowBoxSectionPreset(name="HSS 10x3x0.1875", h=254, b=241, t=3.18),
    HollowBoxSectionPreset(name="HSS 10x3x0.125", h=254, b=245, t=9.53),
    HollowBoxSectionPreset(name="HSS 10x2x0.375", h=254, b=227, t=7.94),
    HollowBoxSectionPreset(name="HSS 10x2x0.3125", h=254, b=232, t=6.35),
    HollowBoxSectionPreset(name="HSS 10x2x0.250", h=254, b=236, t=4.76),
    HollowBoxSectionPreset(name="HSS 10x2x0.1875", h=254, b=241, t=3.18),
    HollowBoxSectionPreset(name="HSS 10x2x0.125", h=254, b=245, t=15.9),
    HollowBoxSectionPreset(name="HSS 12x12x0.625", h=305, b=262, t=12.7),
    HollowBoxSectionPreset(name="HSS 12x12x0.500", h=305, b=269, t=9.53),
    HollowBoxSectionPreset(name="HSS 12x12x0.375", h=305, b=279, t=7.94),
    HollowBoxSectionPreset(name="HSS 12x12x0.3125", h=305, b=282, t=6.35),
    HollowBoxSectionPreset(name="HSS 12x12x0.250", h=305, b=287, t=4.76),
    HollowBoxSectionPreset(name="HSS 12x12x0.1875", h=305, b=292, t=12.7),
    HollowBoxSectionPreset(name="HSS 12x10x0.500", h=305, b=269, t=9.53),
    HollowBoxSectionPreset(name="HSS 12x10x0.375", h=305, b=279, t=7.94),
    HollowBoxSectionPreset(name="HSS 12x10x0.3125", h=305, b=282, t=6.35),
    HollowBoxSectionPreset(name="HSS 12x10x0.250", h=305, b=287, t=15.9),
    HollowBoxSectionPreset(name="HSS 12x8x0.625", h=305, b=262, t=12.7),
    HollowBoxSectionPreset(name="HSS 12x8x0.500", h=305, b=269, t=9.53),
    HollowBoxSectionPreset(name="HSS 12x8x0.375", h=305, b=279, t=7.94),
    HollowBoxSectionPreset(name="HSS 12x8x0.3125", h=305, b=282, t=6.35),
    HollowBoxSectionPreset(name="HSS 12x8x0.250", h=305, b=287, t=4.77),
    HollowBoxSectionPreset(name="HSS 12x8x0.1875", h=305, b=292, t=15.9),
    HollowBoxSectionPreset(name="HSS 12x6x0.625", h=305, b=262, t=12.7),
    HollowBoxSectionPreset(name="HSS 12x6x0.500", h=305, b=269, t=9.53),
    HollowBoxSectionPreset(name="HSS 12x6x0.375", h=305, b=279, t=7.94),
    HollowBoxSectionPreset(name="HSS 12x6x0.3125", h=305, b=282, t=6.35),
    HollowBoxSectionPreset(name="HSS 12x6x0.250", h=305, b=287, t=4.76),
    HollowBoxSectionPreset(name="HSS 12x6x0.1875", h=305, b=292, t=15.9),
    HollowBoxSectionPreset(name="HSS 12x4x0.625", h=305, b=262, t=12.7),
    HollowBoxSectionPreset(name="HSS 12x4x0.500", h=305, b=269, t=9.53),
    HollowBoxSectionPreset(name="HSS 12x4x0.375", h=305, b=279, t=7.94),
    HollowBoxSectionPreset(name="HSS 12x4x0.3125", h=305, b=282, t=6.35),
    HollowBoxSectionPreset(name="HSS 12x4x0.250", h=305, b=287, t=4.76),
    HollowBoxSectionPreset(name="HSS 12x4x0.1875", h=305, b=292, t=9.53),
    HollowBoxSectionPreset(name="HSS 12x3.5x0.375", h=305, b=279, t=7.94),
    HollowBoxSectionPreset(name="HSS 12x3.5x0.3125", h=305, b=282, t=7.94),
    HollowBoxSectionPreset(name="HSS 12x3x0.3125", h=305, b=282, t=6.35),
    HollowBoxSectionPreset(name="HSS 12x3x0.250", h=305, b=287, t=4.76),
    HollowBoxSectionPreset(name="HSS 12x3x0.1875", h=305, b=292, t=7.94),
    HollowBoxSectionPreset(name="HSS 12x2x0.3125", h=305, b=282, t=6.35),
    HollowBoxSectionPreset(name="HSS 12x2x0.250", h=305, b=287, t=4.76),
    HollowBoxSectionPreset(name="HSS 12x2x0.1875", h=305, b=292, t=15.9),
    HollowBoxSectionPreset(name="HSS 14x14x0.625", h=356, b=312, t=12.7),
    HollowBoxSectionPreset(name="HSS 14x14x0.500", h=356, b=320, t=9.53),
    HollowBoxSectionPreset(name="HSS 14x14x0.375", h=356, b=330, t=7.94),
    HollowBoxSectionPreset(name="HSS 14x14x0.3125", h=356, b=333, t=15.9),
    HollowBoxSectionPreset(name="HSS 14x10x0.625", h=356, b=312, t=12.7),
    HollowBoxSectionPreset(name="HSS 14x10x0.500", h=356, b=320, t=9.53),
    HollowBoxSectionPreset(name="HSS 14x10x0.375", h=356, b=330, t=7.94),
    HollowBoxSectionPreset(name="HSS 14x10x0.3125", h=356, b=333, t=6.35),
    HollowBoxSectionPreset(name="HSS 14x10x0.250", h=356, b=338, t=15.9),
    HollowBoxSectionPreset(name="HSS 14x6x0.625", h=356, b=312, t=12.7),
    HollowBoxSectionPreset(name="HSS 14x6x0.500", h=356, b=320, t=9.53),
    HollowBoxSectionPreset(name="HSS 14x6x0.375", h=356, b=330, t=7.94),
    HollowBoxSectionPreset(name="HSS 14x6x0.3125", h=356, b=333, t=6.35),
    HollowBoxSectionPreset(name="HSS 14x6x0.250", h=356, b=338, t=4.76),
    HollowBoxSectionPreset(name="HSS 14x6x0.1875", h=356, b=343, t=15.9),
    HollowBoxSectionPreset(name="HSS 14x4x0.625", h=356, b=312, t=12.7),
    HollowBoxSectionPreset(name="HSS 14x4x0.500", h=356, b=320, t=9.53),
    HollowBoxSectionPreset(name="HSS 14x4x0.375", h=356, b=330, t=7.94),
    HollowBoxSectionPreset(name="HSS 14x4x0.3125", h=356, b=333, t=6.35),
    HollowBoxSectionPreset(name="HSS 14x4x0.250", h=356, b=338, t=4.76),
    HollowBoxSectionPreset(name="HSS 14x4x0.1875", h=356, b=343, t=15.9),
    HollowBoxSectionPreset(name="HSS 16x16x0.625", h=406, b=363, t=12.7),
    HollowBoxSectionPreset(name="HSS 16x16x0.500", h=406, b=371, t=9.53),
    HollowBoxSectionPreset(name="HSS 16x16x0.375", h=406, b=381, t=7.94),
    HollowBoxSectionPreset(name="HSS 16x16x0.3125", h=406, b=384, t=15.9),
    HollowBoxSectionPreset(name="HSS 16x12x0.625", h=406, b=363, t=12.7),
    HollowBoxSectionPreset(name="HSS 16x12x0.500", h=406, b=371, t=9.53),
    HollowBoxSectionPreset(name="HSS 16x12x0.375", h=406, b=381, t=7.94),
    HollowBoxSectionPreset(name="HSS 16x12x0.3125", h=406, b=384, t=15.9),
    HollowBoxSectionPreset(name="HSS 16x8x0.625", h=406, b=363, t=12.7),
    HollowBoxSectionPreset(name="HSS 16x8x0.500", h=406, b=371, t=9.53),
    HollowBoxSectionPreset(name="HSS 16x8x0.375", h=406, b=381, t=7.94),
    HollowBoxSectionPreset(name="HSS 16x8x0.3125", h=406, b=384, t=6.35),
    HollowBoxSectionPreset(name="HSS 16x8x0.250", h=406, b=389, t=15.9),
    HollowBoxSectionPreset(name="HSS 16x4x0.625", h=406, b=363, t=12.7),
    HollowBoxSectionPreset(name="HSS 16x4x0.500", h=406, b=371, t=9.53),
    HollowBoxSectionPreset(name="HSS 16x4x0.375", h=406, b=381, t=7.94),
    HollowBoxSectionPreset(name="HSS 16x4x0.3125", h=406, b=384, t=6.35),
    HollowBoxSectionPreset(name="HSS 16x4x0.250", h=406, b=389, t=4.76),
    HollowBoxSectionPreset(name="HSS 16x4x0.1875", h=406, b=394, t=15.9),
    HollowBoxSectionPreset(name="HSS 18x6x0.625", h=457, b=414, t=12.7),
    HollowBoxSectionPreset(name="HSS 18x6x0.500", h=457, b=422, t=9.53),
    HollowBoxSectionPreset(name="HSS 18x6x0.375", h=457, b=432, t=7.94),
    HollowBoxSectionPreset(name="HSS 18x6x0.3125", h=457, b=434, t=6.35),
    HollowBoxSectionPreset(name="HSS 18x6x0.250", h=457, b=439, t=15.9),
    HollowBoxSectionPreset(name="HSS 20x12x0.625", h=508, b=465, t=12.7),
    HollowBoxSectionPreset(name="HSS 20x12x0.500", h=508, b=472, t=9.53),
    HollowBoxSectionPreset(name="HSS 20x12x0.375", h=508, b=483, t=7.94),
    HollowBoxSectionPreset(name="HSS 20x12x0.3125", h=508, b=485, t=15.9),
    HollowBoxSectionPreset(name="HSS 20x8x0.625", h=508, b=465, t=12.7),
    HollowBoxSectionPreset(name="HSS 20x8x0.500", h=508, b=472, t=9.53),
    HollowBoxSectionPreset(name="HSS 20x8x0.375", h=508, b=483, t=7.94),
    HollowBoxSectionPreset(name="HSS 20x8x0.3125", h=508, b=485, t=12.7),
    HollowBoxSectionPreset(name="HSS 20x4x0.500", h=508, b=472, t=9.53),
    HollowBoxSectionPreset(name="HSS 20x4x0.375", h=508, b=483, t=7.94),
    HollowBoxSectionPreset(name="HSS 20x4x0.3125", h=508, b=485, t=6.35),
    HollowBoxSectionPreset(name="HSS 20x4x0.250", h=508, b=490, t=102),
]

CUSTOM = HollowBoxSectionPreset(name="user", h=100.0, b=50.0, t=5.0)

PARAM_NAMES = ['h', 'b', 't']
PARAM_DESCRIPTIONS = ['Outer height', 'Outer width', 'Wall thickness']

def calculate_section_properties(params: dict) -> SectionProperties:
    """
    Calculate section properties for a hollow box (rectangular tube) with uniform thickness.
    params: dict with keys 'b', 'h', 't' (all in mm)
    """
    # Map parameters to same names used in MpcBeamSection.cpp
    B = params['b']
    H = params['h']
    t = params['t']
    b = B - 2.0 * t
    h = H - 2.0 * t
    fb = B - t
    fh = H - t
    area = B * H - b * h
    Iyy = (B * H**3 - b * h**3) / 12.0
    Izz = (H * B**3 - h * b**3) / 12.0
    numerator = 2.0 * ((B - t) * (H - t))**2
    denominator = ((B - t) / fb) + ((H - t) / fh)
    J = numerator / denominator
    alphaY = 2.0 * _ureg.dimensionless
    alphaZ = 2.0 * _ureg.dimensionless
    centroidY = B / 2.0
    centroidZ = H / 2.0
    return SectionProperties(
        area=area, Iyy=Iyy, Izz=Izz, J=J,
        alphaY=alphaY, alphaZ=alphaZ,
        centroidY=centroidY, centroidZ=centroidZ,
    )

def calculate_extrusion_data(params: dict) -> MpcSectionExtrusionBeamData:
    B = float(params['b'])
    H = float(params['h'])
    t = float(params['t'])
    b = B - 2.0 * t
    h = H - 2.0 * t
    cx = B / 2.0
    cy = H / 2.0
    ed = MpcSectionExtrusionBeamData()
    # outer rectangle
    ed.addPoint(-cx, -cy)               # 0
    ed.addPoint(B - cx, -cy)            # 1
    ed.addPoint(B - cx, H - cy)         # 2
    ed.addPoint(-cx, H - cy)            # 3
    # inner rectangle
    ed.addPoint((B - b) / 2.0 - cx, (H - h) / 2.0 - cy)  # 4
    ed.addPoint((B + b) / 2.0 - cx, (H - h) / 2.0 - cy)  # 5
    ed.addPoint((B + b) / 2.0 - cx, (H + h) / 2.0 - cy)  # 6
    ed.addPoint((B - b) / 2.0 - cx, (H + h) / 2.0 - cy)  # 7
    # triangles
    ed.addTriangle(0, 5, 4)
    ed.addTriangle(0, 1, 5)
    ed.addTriangle(1, 6, 5)
    ed.addTriangle(1, 2, 6)
    ed.addTriangle(2, 7, 6)
    ed.addTriangle(2, 3, 7)
    ed.addTriangle(3, 4, 7)
    ed.addTriangle(3, 0, 4)
    # edges
    ed.addEdge([0, 1])
    ed.addEdge([1, 2])
    ed.addEdge([2, 3])
    ed.addEdge([3, 0])
    ed.addEdge([5, 4])
    ed.addEdge([4, 7])
    ed.addEdge([7, 6])
    ed.addEdge([6, 5])
    # sweeps
    for i in range(8):
        ed.addSweep(i)
    return ed
