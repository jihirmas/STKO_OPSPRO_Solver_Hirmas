"""
Section preset registry: provides unified access to all section preset modules (C, C_MC, ...).
Allows listing all available presets, retrieving preset modules by type, etc.
"""

from . import (
    c_section_presets,
    c_mc_section_presets,
    box_section_presets,
    hollow_box_section_presets,
    circular_section_presets,
    hollow_circular_section_presets,
    i_section_presets,
    i_hp_section_presets,
    i_s_section_presets,
    l_section_presets,
    l_u_section_presets,
    t_section_presets,
    custom_section_presets,
)

# Map section type string to preset module
_PROFILE_IMAGES = {
    'Rectangular':        'assets/images/profiles/section_Box.png',
    'Hollow Rectangular': 'assets/images/profiles/section_HollowBox.png',
    'Circular':           'assets/images/profiles/section_Circular.png',
    'Hollow Circular':    'assets/images/profiles/section_HollowCircular.png',
    'I Section':          'assets/images/profiles/section_I.png',
    'I HP Section':       'assets/images/profiles/section_I_HP.png',
    'I S Section':        'assets/images/profiles/section_I_S.png',
    'C Channel':          'assets/images/profiles/section_C.png',
    'C MC Channel':       'assets/images/profiles/section_C_MC.png',
    'T Section':          'assets/images/profiles/section_T.png',
    'L Angle':            'assets/images/profiles/section_L.png',
    'L U Angle':          'assets/images/profiles/section_L_U.png',
    'Custom':             'assets/images/profiles/section_Custom.png',
}

_PRESET_MODULES = {
    'Rectangular':       box_section_presets,
    'Hollow Rectangular': hollow_box_section_presets,
    'Circular':          circular_section_presets,
    'Hollow Circular':   hollow_circular_section_presets,
    'I Section':         i_section_presets,
    'I HP Section':      i_hp_section_presets,
    'I S Section':       i_s_section_presets,
    'C Channel':         c_section_presets,
    'C MC Channel':      c_mc_section_presets,
    'T Section':         t_section_presets,
    'L Angle':           l_section_presets,
    'L U Angle':         l_u_section_presets,
    'Custom':            custom_section_presets,
}

def list_section_types():
    """Return a list of all available section type keys (e.g. ['C', 'C_MC'])."""
    return list(_PRESET_MODULES.keys())

def get_preset_module(section_type: str):
    """Return the preset module for the given section type string."""
    return _PRESET_MODULES.get(section_type)

def list_presets(section_type: str):
    """Return the list of preset objects for the given section type."""
    mod = get_preset_module(section_type)
    if mod is not None:
        return getattr(mod, 'PRESETS', [])
    return []

def get_preset(section_type: str, name: str):
    """Return the preset object with the given name for the given section type, or None."""
    mod = get_preset_module(section_type)
    if mod is not None:
        for preset in getattr(mod, 'PRESETS', []):
            if getattr(preset, 'name', None) == name:
                return preset
    return None

def get_custom(section_type: str):
    """Return the custom preset object for the given section type."""
    mod = get_preset_module(section_type)
    if mod is not None:
        return getattr(mod, 'CUSTOM', None)
    return None

def get_calculate_function(section_type: str):
    """Return the calculate_section_properties function for the given section type."""
    mod = get_preset_module(section_type)
    if mod is not None:
        return getattr(mod, 'calculate_section_properties', None)
    return None

def get_param_names(section_type: str):
    """Return the list of parameter names for the given section type."""
    mod = get_preset_module(section_type)
    if mod is not None:
        return getattr(mod, 'PARAM_NAMES', [])
    return []

def get_param_descriptions(section_type: str):
    """Return the list of parameter descriptions for the given section type."""
    mod = get_preset_module(section_type)
    if mod is not None:
        return getattr(mod, 'PARAM_DESCRIPTIONS', [])
    return []

def get_profile_image(section_type: str):
    """Return the profile image path (relative to opspro package) for the given section type."""
    return _PROFILE_IMAGES.get(section_type)

def get_extrusion_function(section_type: str):
    """Return the calculate_extrusion_data function for the given section type."""
    mod = get_preset_module(section_type)
    if mod is not None:
        return getattr(mod, 'calculate_extrusion_data', None)
    return None
