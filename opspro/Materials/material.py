from PyMpc import (
    MpcPluginCaeComponent
)
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.parameters.ParameterManager import ParameterManager
import pint
import json

# Base class for all material components
class Material(MpcPluginCaeComponent):

    def __init__(self, id=1, name='Material'):
        super().__init__(id, name)

    def componentGroupID(self):
        return CAEComponentGroupUIDs.MATERIALS

    @classmethod
    def dialog_class(cls):
        """Return the QDialog class used to create/edit this material type."""
        raise NotImplementedError

    def save(self):
        """Serialize plugin state to a JSON string."""
        try:
            return json.dumps(self._to_dict())
        except Exception as e:
            print(f"Error serializing Material {self.name}: {e}")
            return ''

    def restore(self, state):
        """Restore plugin state from a JSON string produced by `save()`."""
        if not state:
            return
        try:
            data = json.loads(state)
        except Exception as e:
            print(f"Error parsing state for Material {self.name}: {e}")
            return
        try:
            self._from_dict(data)
        except Exception as e:
            print(f"Error restoring Material {self.name} from state: {e}")

    @staticmethod
    def _qty_to_dict(qty: pint.Quantity) -> dict:
        return {'magnitude': float(qty.magnitude), 'unit': str(qty.units)}

    @staticmethod
    def _qty_from_dict(data, fallback: pint.Quantity) -> pint.Quantity:
        """Restore a Quantity from a serialized dict, with backward-compat for plain floats."""
        ureg = ParameterManager._unit_registry
        if isinstance(data, dict):
            return ureg.Quantity(data['magnitude'], data['unit'])
        elif isinstance(data, (int, float)):
            # legacy: bare float stored without unit — keep the fallback's unit
            return float(data) * fallback.units
        return fallback

    def __repr__(self):
        return f"Material(id={int(self.id)}, name={self.name})"
