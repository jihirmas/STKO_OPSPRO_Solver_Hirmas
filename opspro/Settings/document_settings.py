from PyMpc import (
    MpcPluginCaeComponent, 
    MpcCaeDocumentComponentSignalType,
    MpcCaeTargets
)
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.parameters.ParameterManager import ParameterManager
from opspro.parameters.UnitSystemTools import UnitSystem
import json

class DocumentSettings(MpcPluginCaeComponent):
    """
    Document-level settings component for the opspro CAE plugin.

    Stores user-configurable options that affect the whole document and
    persists them across sessions via save/restore.

    Unit system
    -----------
    The user sets each base unit independently (length, mass, time,
    temperature).  A custom UnitSystem is built from these four strings
    and pushed into ParameterManager via apply().

    Defaults are SI: m / kg / s / K.
    Any pint-recognised unit symbol is valid (mm, t, ms, degC, …).
    """

    # Default base units (SI)
    DEFAULT_LENGTH      = 'm'
    DEFAULT_MASS        = 'kg'
    DEFAULT_TIME        = 's'
    DEFAULT_TEMPERATURE = 'K'

    def __init__(self, id=1, name='DocumentSettings'):
        super().__init__(id, name)
        self.length_unit:      str = self.DEFAULT_LENGTH
        self.mass_unit:        str = self.DEFAULT_MASS
        self.time_unit:        str = self.DEFAULT_TIME
        self.temperature_unit: str = self.DEFAULT_TEMPERATURE

    # ------------------------------------------------------------------
    # MpcPluginCaeComponent interface
    # ------------------------------------------------------------------

    def componentGroupID(self):
        return CAEComponentGroupUIDs.SETTINGS

    def className(self):
        return 'DocumentSettings'

    def description(self):
        return 'Document-level settings (unit system, ...)'

    def onGeometryChanged(self, geometry_collection, signal_type):
        return ''

    def save(self):
        """Serialize plugin state to a JSON string."""
        try:
            return json.dumps(self._to_dict())
        except Exception as e:
            print(f'Error saving DocumentSettings {self.name}: {e}')
            return ''

    def restore(self, state_str):
        """Restore plugin state from a JSON string and apply settings."""
        if not state_str:
            return
        try:
            data = json.loads(state_str)
            self._from_dict(data)
        except Exception as e:
            print(f'Error restoring DocumentSettings {self.name}: {e}')
        self.apply()

    # ------------------------------------------------------------------
    # Apply settings to the rest of the application
    # ------------------------------------------------------------------

    def apply(self):
        """
        Build a UnitSystem from the four base unit strings and push it
        into ParameterManager.
        """
        name = f'{self.length_unit}-{self.mass_unit}-{self.time_unit}'
        us = UnitSystem(name, self.length_unit, self.mass_unit,
                        self.time_unit, self.temperature_unit)
        ParameterManager.set_unit_system(us)

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------

    def _to_dict(self) -> dict:
        return {
            'ID':               int(self.id),
            'name':             self.name,
            'length_unit':      self.length_unit,
            'mass_unit':        self.mass_unit,
            'time_unit':        self.time_unit,
            'temperature_unit': self.temperature_unit,
        }

    def _from_dict(self, data: dict):
        self.id               = data.get('ID',               self.id)
        self.name             = data.get('name',             self.name)
        self.length_unit      = data.get('length_unit',      self.length_unit)
        self.mass_unit        = data.get('mass_unit',        self.mass_unit)
        self.time_unit        = data.get('time_unit',        self.time_unit)
        self.temperature_unit = data.get('temperature_unit', self.temperature_unit)

    def __repr__(self):
        return (
            f'DocumentSettings(id={int(self.id)}, '
            f'L={self.length_unit}, M={self.mass_unit}, '
            f'T={self.time_unit}, \u0398={self.temperature_unit})'
        )
