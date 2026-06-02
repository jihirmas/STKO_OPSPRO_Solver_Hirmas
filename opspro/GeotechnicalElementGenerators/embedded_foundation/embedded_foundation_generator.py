from opspro.parameters.ParameterManager import ParameterManager
from opspro.GeotechnicalElementGenerators.dimension_mode import DimensionMode
from opspro.GeotechnicalElementGenerators.geotechnical_element_generator import (
    GeotechnicalElementGenerator,
)
from opspro.GeotechnicalElementGenerators.serialization_tools import (
    normalize_dimension_mode,
    require_non_empty,
    require_positive_quantity,
    validation_result,
)


class EmbeddedFoundationGenerator(GeotechnicalElementGenerator):
    INTERACTION_MODELS = ('pending',)

    def __init__(self, id=1, name='Embedded Foundation'):
        super().__init__(id, name)
        ureg = ParameterManager._unit_registry
        self.dimension_mode = DimensionMode.TWO_D
        self.foundation_material_id = None
        self.interaction_model = 'pending'
        self.mesh_tolerance = ParameterManager.to_internal(0.001 * ureg.meter)
        self.interface_tolerance = ParameterManager.to_internal(0.001 * ureg.meter)
        self.interaction_parameters = {}
        self.geometry_summary = {}
        self.changed = False

    def className(self):
        return 'EmbeddedFoundationGenerator'

    def description(self):
        return 'Composite embedded foundation element generator'

    @classmethod
    def dialog_class(cls):
        from opspro.GeotechnicalElementGenerators.embedded_foundation.embedded_foundation_dialog import (
            EmbeddedFoundationDialog,
        )
        return EmbeddedFoundationDialog

    def writer_class(self):
        from opspro.GeotechnicalElementGenerators.embedded_foundation.embedded_foundation_writer import (
            EmbeddedFoundationWriter,
        )
        return EmbeddedFoundationWriter

    def allowed_assignment_types(self):
        if self.dimension_mode == DimensionMode.THREE_D:
            return ('Solid',)
        return ('Face',)

    def validate_assignment(self, assignment, document=None):
        errors = []
        warnings = []
        if assignment is None:
            errors.append('No geometry assigned.')
            return validation_result(errors, warnings)

        faces = solids = other = 0
        try:
            for _geom, item in assignment.geometries.items():
                faces += len(item.faces)
                solids += len(item.solids)
                other += len(item.vertices) + len(item.edges)
            other += len(assignment.interactions)
        except Exception as e:
            errors.append(f'Could not inspect assignment: {e}')
            return validation_result(errors, warnings)

        if self.dimension_mode == DimensionMode.THREE_D:
            if solids != 1 or faces or other:
                errors.append('Embedded Foundation 3D requires one compatible solid geometry.')
        else:
            if faces != 1 or solids or other:
                errors.append('Embedded Foundation 2D requires one compatible 2D geometry.')

        warnings.append('Mechanical expansion is not implemented yet.')
        warnings.append('Mesh information could not be detected.')
        warnings.append('Interface parameters are pending final specification.')
        return validation_result(errors, warnings)

    def validate_configuration(self):
        errors = []
        warnings = [
            'Mechanical expansion is not implemented yet.',
            'Interface parameters are pending final specification.',
        ]
        try:
            self.dimension_mode = DimensionMode.normalize(self.dimension_mode)
        except Exception as e:
            errors.append(str(e))
        require_non_empty(self.name, 'Name', errors)
        if self.foundation_material_id is None:
            errors.append('Foundation material is required.')
        if self.interaction_model not in self.INTERACTION_MODELS:
            errors.append(f'interaction_model must be one of {self.INTERACTION_MODELS}.')
        require_positive_quantity(self.mesh_tolerance, 'Mesh tolerance', errors)
        require_positive_quantity(self.interface_tolerance, 'Interface tolerance', errors)
        return validation_result(errors, warnings)

    def describe_generated_entities(self):
        return {
            'mechanical_expansion': 'pending',
            'auxiliary_nodes': 0,
            'materials': 0,
            'elements': [],
            'constraints': [],
        }

    def _to_dict(self):
        data = self._base_to_dict()
        data.update({
            'foundation_material_id': self.foundation_material_id,
            'interaction_model': self.interaction_model,
            'mesh_tolerance': self._qty_to_dict(self.mesh_tolerance),
            'interface_tolerance': self._qty_to_dict(self.interface_tolerance),
            'interaction_parameters': dict(self.interaction_parameters),
        })
        return data

    def _from_dict(self, data):
        self._base_from_dict(data)
        self.dimension_mode = normalize_dimension_mode(self.dimension_mode, DimensionMode.TWO_D)
        material_id = data.get('foundation_material_id', self.foundation_material_id)
        self.foundation_material_id = None if material_id is None else int(material_id)
        self.interaction_model = data.get('interaction_model', self.interaction_model)
        self.mesh_tolerance = self._qty_from_dict(data.get('mesh_tolerance'), self.mesh_tolerance)
        self.interface_tolerance = self._qty_from_dict(data.get('interface_tolerance'), self.interface_tolerance)
        params = data.get('interaction_parameters', self.interaction_parameters)
        self.interaction_parameters = dict(params or {})

    def __repr__(self):
        return (
            f'EmbeddedFoundationGenerator(id={int(self.id)}, name={self.name!r}, '
            f'dimension_mode={self.dimension_mode!r})'
        )

