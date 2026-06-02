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


class SpringFoundationGenerator(GeotechnicalElementGenerator):
    ORIENTATION_MODES = ('assigned_entity', 'global_axes')

    def __init__(self, id=1, name='Spring Foundation'):
        super().__init__(id, name)
        ureg = ParameterManager._unit_registry

        self.dimension_mode = DimensionMode.TWO_D

        self.B = ParameterManager.to_internal(2.5 * ureg.meter)
        self.H = ParameterManager.to_internal(0.6 * ureg.meter)

        self.Kx = ParameterManager.to_internal_like(10.0 * ureg.kilonewton / ureg.meter)
        self.Ky = ParameterManager.to_internal_like(20.0 * ureg.kilonewton / ureg.meter)
        self.Kz = ParameterManager.to_internal_like(20.0 * ureg.kilonewton / ureg.meter)

        self.Krx = ParameterManager.to_internal_like(30.0 * ureg.kilonewton * ureg.meter)
        self.Kry = ParameterManager.to_internal_like(30.0 * ureg.kilonewton * ureg.meter)
        self.Krz = ParameterManager.to_internal_like(30.0 * ureg.kilonewton * ureg.meter)

        self.orientation_mode = 'assigned_entity'
        self.use_global_axes = False
        self.changed = False

    def className(self):
        return 'SpringFoundationGenerator'

    def description(self):
        return 'Composite spring foundation element generator'

    @classmethod
    def dialog_class(cls):
        from opspro.GeotechnicalElementGenerators.spring_foundation.spring_foundation_dialog import (
            SpringFoundationDialog,
        )
        return SpringFoundationDialog

    def writer_class(self):
        from opspro.GeotechnicalElementGenerators.spring_foundation.spring_foundation_writer import (
            SpringFoundationWriter,
        )
        return SpringFoundationWriter

    def allowed_assignment_types(self):
        return ('Node',)

    def validate_assignment(self, assignment, document=None):
        errors = []
        warnings = []
        if assignment is None:
            errors.append('No assigned node.')
            return validation_result(errors, warnings)

        vertex_count = 0
        other_count = 0
        try:
            for _geom, item in assignment.geometries.items():
                vertex_count += len(item.vertices)
                other_count += len(item.edges) + len(item.faces) + len(item.solids)
            other_count += len(assignment.interactions)
        except Exception as e:
            errors.append(f'Could not inspect assignment: {e}')
            return validation_result(errors, warnings)

        if vertex_count == 0:
            errors.append('No assigned node.')
        elif vertex_count != 1 or other_count:
            errors.append('Spring Foundation requires exactly one node.')

        warnings.append('Assigned node degrees of freedom could not be fully validated.')
        if self.use_global_axes or self.orientation_mode == 'global_axes':
            warnings.append('Global axes will be used because no local system was detected.')
        return validation_result(errors, warnings)

    def validate_configuration(self):
        errors = []
        warnings = []
        try:
            self.dimension_mode = DimensionMode.normalize(self.dimension_mode)
        except Exception as e:
            errors.append(str(e))

        require_non_empty(self.name, 'Name', errors)
        require_positive_quantity(self.B, 'B', errors)
        require_positive_quantity(self.H, 'H', errors)

        if self.dimension_mode == DimensionMode.THREE_D:
            for label in ('Kx', 'Ky', 'Kz', 'Krx', 'Kry', 'Krz'):
                require_positive_quantity(getattr(self, label), label, errors)
        else:
            require_positive_quantity(self.Kx, 'Kx', errors)
            require_positive_quantity(self.Ky, 'Ky', errors)
            require_positive_quantity(self.Krz, 'Krz', errors)

        if self.orientation_mode not in self.ORIENTATION_MODES:
            errors.append(f'orientation_mode must be one of {self.ORIENTATION_MODES}.')
        return validation_result(errors, warnings)

    def describe_generated_entities(self):
        if self.dimension_mode == DimensionMode.TWO_D:
            return {
                'auxiliary_nodes': 1,
                'uniaxial_materials': 3,
                'elements': [
                    {'type': 'zeroLength', 'count': 1},
                ],
            }
        return {
            'auxiliary_nodes': 1,
            'uniaxial_materials': 6,
            'elements': [
                {'type': 'zeroLength', 'count': 1},
            ],
        }

    def _to_dict(self):
        data = self._base_to_dict()
        data.update({
            'B': self._qty_to_dict(self.B),
            'H': self._qty_to_dict(self.H),
            'Kx': self._qty_to_dict(self.Kx),
            'Ky': self._qty_to_dict(self.Ky),
            'Kz': self._qty_to_dict(self.Kz),
            'Krx': self._qty_to_dict(self.Krx),
            'Kry': self._qty_to_dict(self.Kry),
            'Krz': self._qty_to_dict(self.Krz),
            'orientation_mode': self.orientation_mode,
            'use_global_axes': bool(self.use_global_axes),
        })
        return data

    def _from_dict(self, data):
        self._base_from_dict(data)
        self.dimension_mode = normalize_dimension_mode(self.dimension_mode, DimensionMode.TWO_D)
        self.B = self._qty_from_dict(data.get('B'), self.B)
        self.H = self._qty_from_dict(data.get('H'), self.H)
        self.Kx = self._qty_from_dict(data.get('Kx'), self.Kx)
        self.Ky = self._qty_from_dict(data.get('Ky'), self.Ky)
        self.Kz = self._qty_from_dict(data.get('Kz'), self.Kz)
        self.Krx = self._qty_from_dict(data.get('Krx'), self.Krx)
        self.Kry = self._qty_from_dict(data.get('Kry'), self.Kry)
        self.Krz = self._qty_from_dict(data.get('Krz'), self.Krz)
        self.orientation_mode = data.get('orientation_mode', self.orientation_mode)
        self.use_global_axes = bool(data.get('use_global_axes', self.use_global_axes))

    def __repr__(self):
        return (
            f'SpringFoundationGenerator(id={int(self.id)}, name={self.name!r}, '
            f'dimension_mode={self.dimension_mode!r})'
        )

