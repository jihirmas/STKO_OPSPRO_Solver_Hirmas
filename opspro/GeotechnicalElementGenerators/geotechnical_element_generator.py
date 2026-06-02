from PyMpc import MpcPluginCaeComponent

from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.GeotechnicalElementGenerators.dimension_mode import DimensionMode
from opspro.GeotechnicalElementGenerators.serialization_tools import (
    normalize_dimension_mode,
    quantity_from_dict,
    quantity_to_dict,
    safe_json_dumps,
    safe_json_loads,
)


class GeotechnicalElementGenerator(MpcPluginCaeComponent):
    def __init__(self, id=1, name='GeotechnicalElementGenerator'):
        super().__init__(id, name)
        self.dimension_mode = DimensionMode.TWO_D

    def componentGroupID(self):
        return CAEComponentGroupUIDs.GEOTECHNICAL_ELEMENT_GENERATORS

    def className(self):
        raise NotImplementedError

    def description(self):
        raise NotImplementedError

    @classmethod
    def dialog_class(cls):
        raise NotImplementedError

    def writer_class(self):
        raise NotImplementedError

    def allowed_assignment_types(self):
        raise NotImplementedError

    def validate_assignment(self, assignment, document=None):
        raise NotImplementedError

    def validate_configuration(self):
        raise NotImplementedError

    def describe_generated_entities(self):
        raise NotImplementedError

    def save(self) -> str:
        return safe_json_dumps(self._to_dict(), f'{self.className()} "{self.name}"')

    def restore(self, state: str) -> None:
        data = safe_json_loads(state, f'{self.className()} "{self.name}"')
        if data is None:
            return
        try:
            self._from_dict(data)
        except Exception as e:
            print(f'Error restoring {self.className()} "{self.name}" from state: {e}')
            import traceback
            print(traceback.format_exc())

    def _to_dict(self) -> dict:
        raise NotImplementedError

    def _from_dict(self, data: dict) -> None:
        raise NotImplementedError

    def _base_to_dict(self) -> dict:
        return {
            'ID': int(self.id),
            'name': self.name,
            'changed': self.changed,
            'dimension_mode': self.dimension_mode,
        }

    def _base_from_dict(self, data: dict):
        self.id = data.get('ID', self.id)
        self.name = data.get('name', self.name)
        self.changed = data.get('changed', self.changed)
        self.dimension_mode = normalize_dimension_mode(
            data.get('dimension_mode', self.dimension_mode),
            self.dimension_mode,
        )

    @staticmethod
    def _qty_to_dict(qty) -> dict:
        return quantity_to_dict(qty)

    @staticmethod
    def _qty_from_dict(data, fallback):
        return quantity_from_dict(data, fallback)

