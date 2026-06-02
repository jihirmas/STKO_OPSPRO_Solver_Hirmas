from PyMpc import MpcCaeTargetType, MpcSubshapeType

from opspro.utils import get_assignment_registry


class GeneratorAssignmentType:
    NODE = 'Node'
    FACE = 'Face'
    SOLID = 'Solid'


def is_node_target(item) -> bool:
    return item.type == MpcCaeTargetType.Geometry and item.subshape_type == MpcSubshapeType.Vertex


def is_face_target(item) -> bool:
    return item.type == MpcCaeTargetType.Geometry and item.subshape_type == MpcSubshapeType.Face


def is_solid_target(item) -> bool:
    return item.type == MpcCaeTargetType.Geometry and item.subshape_type == MpcSubshapeType.Solid


def assign_generator(component, targets):
    registry = get_assignment_registry()
    if registry is None:
        raise RuntimeError('AssignmentRegistry not found.')
    registry.assign(component, targets)


def unassign_generator(component, targets):
    registry = get_assignment_registry()
    if registry is None:
        raise RuntimeError('AssignmentRegistry not found.')
    registry.unassign(component, targets)


def list_generator_assignments(component):
    registry = get_assignment_registry()
    if registry is None:
        return None
    return registry.assignment_for_component(component)

