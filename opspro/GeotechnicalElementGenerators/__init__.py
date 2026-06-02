from .dimension_mode import DimensionMode
from .geotechnical_element_generator import GeotechnicalElementGenerator
from .internal_tag_allocator import InternalTagAllocator
from .geotechnical_element_generator_command_assign import (
    GeotechnicalElementGeneratorCommandAssign,
)
from .geotechnical_element_generator_command_unassign import (
    GeotechnicalElementGeneratorCommandUnassign,
)
from .geotechnical_element_generator_command_list_assignments import (
    GeotechnicalElementGeneratorCommandListAssignments,
)
from .geotechnical_element_generator_command_edit import (
    GeotechnicalElementGeneratorCommandEdit,
)
from .spring_foundation import SpringFoundationCommandNew, SpringFoundationGenerator
from .embedded_foundation import EmbeddedFoundationCommandNew, EmbeddedFoundationGenerator


def _components_by_type(doc, component_type):
    try:
        from opspro.assets.cae_components_uids import CAEComponentGroupUIDs

        group = doc.pluginCaeComponents.groups().get(
            CAEComponentGroupUIDs.GEOTECHNICAL_ELEMENT_GENERATORS
        )
        if group is None:
            return []
        result = []
        for key in group.collection.keys():
            comp = group.collection[key]
            if isinstance(comp, component_type):
                result.append(comp)
        return result
    except Exception:
        return []


def write_geotechnical_element_generators(doc, pinfo):
    from opspro.GeotechnicalElementGenerators.spring_foundation.spring_foundation_writer import (
        write_spring_foundations,
    )
    from opspro.GeotechnicalElementGenerators.embedded_foundation.embedded_foundation_writer import (
        write_embedded_foundations,
    )

    springs = _components_by_type(doc, SpringFoundationGenerator)
    embedded = _components_by_type(doc, EmbeddedFoundationGenerator)
    if springs:
        write_spring_foundations(doc, pinfo, springs)
    if embedded:
        write_embedded_foundations(doc, pinfo, embedded)


__all__ = [
    'DimensionMode',
    'GeotechnicalElementGenerator',
    'InternalTagAllocator',
    'SpringFoundationGenerator',
    'EmbeddedFoundationGenerator',
    'SpringFoundationCommandNew',
    'EmbeddedFoundationCommandNew',
    'GeotechnicalElementGeneratorCommandAssign',
    'GeotechnicalElementGeneratorCommandUnassign',
    'GeotechnicalElementGeneratorCommandListAssignments',
    'GeotechnicalElementGeneratorCommandEdit',
    'write_geotechnical_element_generators',
]
