from opspro.GeotechnicalElementGenerators.dimension_mode import DimensionMode
from opspro.GeotechnicalElementGenerators.internal_tag_allocator import InternalTagAllocator
from opspro.GeotechnicalElementGenerators.serialization_tools import validation_result
from opspro.parameters.ParameterManager import ParameterManager
from opspro.utils import get_assignment_registry


class SpringFoundationWriter:
    def __init__(self, doc, pinfo, allocator: InternalTagAllocator = None):
        self.doc = doc
        self.pinfo = pinfo
        self.allocator = allocator or InternalTagAllocator(pinfo)

    def write(self, component):
        result = component.validate_configuration()
        if not result['valid']:
            raise RuntimeError(
                f'Spring Foundation "{component.name}" has invalid configuration: '
                + '; '.join(result['errors'])
            )

        assignment = self._assignment_for(component)
        assignment_result = component.validate_assignment(assignment, self.doc)
        if not assignment_result['valid']:
            raise RuntimeError(
                f'Spring Foundation "{component.name}" has invalid assignment: '
                + '; '.join(assignment_result['errors'])
            )

        target_node = self._resolve_assigned_mesh_node(assignment)
        if component.dimension_mode == DimensionMode.THREE_D:
            self._write_zero_length(component, target_node, ndm=3, ndf=6)
        else:
            self._write_zero_length(component, target_node, ndm=2, ndf=3)

    def _assignment_for(self, component):
        registry = get_assignment_registry()
        if registry is None:
            raise RuntimeError('AssignmentRegistry not found.')
        return registry.assignment_for_component(component)

    def _resolve_assigned_mesh_node(self, assignment):
        for geom, item in assignment.geometries.items():
            for vertex_id in sorted(item.vertices):
                mesh_geom = self.doc.mesh.getMeshedGeometry(int(geom.id))
                node = self._node_from_meshed_vertex(mesh_geom, vertex_id)
                if node is not None:
                    return node
        raise RuntimeError(
            'Could not resolve the mesh node for the assigned geometry vertex. '
            'Confirm the geometry is meshed and the target is a vertex.'
        )

    def _node_from_meshed_vertex(self, mesh_geom, vertex_id):
        vertices = getattr(mesh_geom, 'vertices', None)
        if vertices is None:
            return None

        vertex_mesh = None
        try:
            vertex_mesh = vertices[vertex_id]
        except Exception:
            try:
                vertex_mesh = vertices.get(vertex_id)
            except Exception:
                pass
        if vertex_mesh is None:
            return None

        direct = self._as_node(vertex_mesh)
        if direct is not None:
            return direct

        for attr in ('node', 'meshNode'):
            node = self._as_node(getattr(vertex_mesh, attr, None))
            if node is not None:
                return node

        nodes = getattr(vertex_mesh, 'nodes', None)
        if nodes is not None:
            node = self._first_node(nodes)
            if node is not None:
                return node
        return None

    def _first_node(self, nodes):
        if nodes is None:
            return None
        try:
            if hasattr(nodes, 'values'):
                iterator = iter(nodes.values())
            else:
                iterator = iter(nodes)
            return self._as_node(next(iterator))
        except Exception:
            return None

    def _as_node(self, value):
        if value is None:
            return None
        if hasattr(value, 'id') and (
            hasattr(value, 'position')
            or hasattr(value, 'x')
            or hasattr(value, 'coords')
            or hasattr(value, 'coordinates')
        ):
            return value
        return None

    def _write_zero_length(self, component, target_node, ndm: int, ndf: int):
        out = self.pinfo.out_file
        target_id = int(target_node.id)
        coords = self._node_coordinates(target_node)
        aux_node = self.allocator.allocate_node()

        if hasattr(self.pinfo, 'updateModelBuilder'):
            self.pinfo.updateModelBuilder(ndm, ndf)

        out.write('\n# Geotechnical Element Generator: Spring Foundation "{}" (id={})\n'.format(
            component.name, int(component.id)
        ))
        if ndm == 2:
            out.write('node {} {:.12g} {:.12g}\n'.format(aux_node, coords[0], coords[1]))
            out.write('fix {} 1 1 1\n'.format(aux_node))
            stiffnesses = (component.Kx, component.Ky, component.Krz)
            dirs = (1, 2, 3)
        else:
            out.write('node {} {:.12g} {:.12g} {:.12g}\n'.format(aux_node, coords[0], coords[1], coords[2]))
            out.write('fix {} 1 1 1 1 1 1\n'.format(aux_node))
            stiffnesses = (component.Kx, component.Ky, component.Kz, component.Krx, component.Kry, component.Krz)
            dirs = (1, 2, 3, 4, 5, 6)

        mat_tags = []
        for qty in stiffnesses:
            tag = self.allocator.allocate_uniaxial_material()
            mat_tags.append(tag)
            out.write('uniaxialMaterial Elastic {} {:.12g}\n'.format(tag, self._quantity_value(qty)))

        elem_tag = self.allocator.allocate_element()
        out.write(
            'element zeroLength {} {} {} -mat {} -dir {} '
            '-orient 1.0 0.0 0.0 0.0 1.0 0.0\n'.format(
                elem_tag,
                aux_node,
                target_id,
                ' '.join(str(i) for i in mat_tags),
                ' '.join(str(i) for i in dirs),
            )
        )

    def _quantity_value(self, qty) -> float:
        return float(ParameterManager.to_internal_like(qty).magnitude)

    def _node_coordinates(self, node):
        if all(hasattr(node, attr) for attr in ('x', 'y')):
            return (
                float(getattr(node, 'x')),
                float(getattr(node, 'y')),
                float(getattr(node, 'z', 0.0)),
            )

        pos = getattr(node, 'position', None)
        if pos is not None:
            if all(hasattr(pos, attr) for attr in ('x', 'y')):
                return (
                    float(getattr(pos, 'x')),
                    float(getattr(pos, 'y')),
                    float(getattr(pos, 'z', 0.0)),
                )
            try:
                values = list(pos)
                return (
                    float(values[0]),
                    float(values[1]),
                    float(values[2]) if len(values) > 2 else 0.0,
                )
            except Exception:
                pass

        for attr in ('coords', 'coordinates'):
            coords = getattr(node, attr, None)
            if coords is not None:
                try:
                    values = list(coords)
                    return (
                        float(values[0]),
                        float(values[1]),
                        float(values[2]) if len(values) > 2 else 0.0,
                    )
                except Exception:
                    pass

        raise RuntimeError(f'Could not resolve coordinates for mesh node {int(node.id)}.')


def write_spring_foundations(doc, pinfo, components):
    writer = SpringFoundationWriter(doc, pinfo)
    for component in components:
        writer.write(component)

