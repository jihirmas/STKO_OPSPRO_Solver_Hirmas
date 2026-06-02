from opspro.utils import get_assignment_registry


class EmbeddedFoundationWriter:
    def __init__(self, doc, pinfo, allocator=None):
        self.doc = doc
        self.pinfo = pinfo
        self.allocator = allocator

    def write(self, component):
        result = component.validate_configuration()
        if not result['valid']:
            raise RuntimeError(
                f'Embedded Foundation "{component.name}" has invalid configuration: '
                + '; '.join(result['errors'])
            )

        registry = get_assignment_registry()
        if registry is None:
            raise RuntimeError('AssignmentRegistry not found.')
        assignment = registry.assignment_for_component(component)
        assignment_result = component.validate_assignment(assignment, self.doc)
        if not assignment_result['valid']:
            raise RuntimeError(
                f'Embedded Foundation "{component.name}" has invalid assignment: '
                + '; '.join(assignment_result['errors'])
            )

        raise NotImplementedError(
            'Embedded Foundation mechanical expansion is not implemented yet. '
            'Pending specification: auxiliary elements, constraints, soil-foundation '
            'connectivity, meshing and interface strategy.'
        )


def write_embedded_foundations(doc, pinfo, components):
    writer = EmbeddedFoundationWriter(doc, pinfo)
    for component in components:
        writer.write(component)

