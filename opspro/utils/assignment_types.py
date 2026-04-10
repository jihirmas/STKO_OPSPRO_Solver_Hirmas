"""
assignment_types.py
-------------------
Typed containers that track which MpcPluginCaeComponent instances are
assigned to each geometry sub-shape or interaction in the document.

Types
-----
SubgeometryAssignment
    Dict[int, Set[MpcPluginCaeComponent]]
    Maps a sub-shape index (0-based) to the set of components
    currently assigned to that sub-shape.

GeometryAssignmentItem
    Container with four SubgeometryAssignment attributes —
    one per sub-shape kind: vertices, edges, faces, solids.

GeometryAssignment
    Dict[MpcGeometry, GeometryAssignmentItem]
    Maps a geometry instance to its per-sub-shape assignment table.

InteractionAssignment
    Dict[MpcInteraction, Set[MpcPluginCaeComponent]]
    Maps an interaction instance to the set of components assigned to it.
"""

from __future__ import annotations
from typing import Dict, Set

# PyMpc types
from PyMpc import (
    MpcPluginCaeComponent, 
    MpcGeometry, 
    MpcInteraction, 
    MpcSubshapeType
)


# ---------------------------------------------------------------------------
# SubgeometryAssignment
# ---------------------------------------------------------------------------
# Maps sub-shape index → set of assigned components.
# Keys are the 0-based integer indices used by the topology map.
SubgeometryAssignment = Dict[int, Set[MpcPluginCaeComponent]]


# ---------------------------------------------------------------------------
# GeometryAssignmentItem
# ---------------------------------------------------------------------------

class GeometryAssignmentItem:
    """
    Holds per-sub-shape-type assignment lists for a single MpcGeometry.

    Attributes
    ----------
    vertices : SubgeometryAssignment
    edges    : SubgeometryAssignment
    faces    : SubgeometryAssignment
    solids   : SubgeometryAssignment
    """

    __slots__ = ('vertices', 'edges', 'faces', 'solids')

    def __init__(self):
        self.vertices: SubgeometryAssignment = {}
        self.edges:    SubgeometryAssignment = {}
        self.faces:    SubgeometryAssignment = {}
        self.solids:   SubgeometryAssignment = {}

    def get_by_subshape_type(self, subshape_type : MpcSubshapeType) -> SubgeometryAssignment:
        """
        Return the appropriate SubgeometryAssignment for a given
        MpcSubshapeType / FxSubShapeType enum value.
        Raises ValueError for unrecognised types.
        """
        if subshape_type == MpcSubshapeType.Vertex:
            return self.vertices
        elif subshape_type == MpcSubshapeType.Edge:
            return self.edges
        elif subshape_type == MpcSubshapeType.Face:
            return self.faces
        elif subshape_type == MpcSubshapeType.Solid:
            return self.solids
        else:
            raise ValueError(
                f'get_by_subshape_type: unrecognised subshape type {subshape_type!r}. '
                f'Expected one of: Vertex, Edge, Face, Solid.'
            )

    def is_empty(self) -> bool:
        return not (self.vertices or self.edges or self.faces or self.solids)

    def __repr__(self) -> str:
        return (
            f'GeometryAssignmentItem('
            f'vertices={len(self.vertices)}, '
            f'edges={len(self.edges)}, '
            f'faces={len(self.faces)}, '
            f'solids={len(self.solids)})'
        )


# ---------------------------------------------------------------------------
# GeometryAssignment
# ---------------------------------------------------------------------------
# Maps a geometry instance to the per-sub-shape-type assignment table.
# Keys use identity-based hashing (Python's default object.__hash__ = id()).
# This is safe because Boost.Python's register_ptr_to_python cache guarantees
# that the same underlying C++ MpcGeometry* always yields the same Python
# wrapper object — equivalent to keying by C++ pointer.
GeometryAssignment = Dict[MpcGeometry, GeometryAssignmentItem]


# ---------------------------------------------------------------------------
# InteractionAssignment
# ---------------------------------------------------------------------------
# Maps an interaction instance to the set of components assigned to it.
# Keys use identity-based hashing — same guarantee as GeometryAssignment.
InteractionAssignment = Dict[MpcInteraction, Set[MpcPluginCaeComponent]]


# ===========================================================================
# INVERSE MAPS  (component → entities it is assigned to)
# ===========================================================================

# ---------------------------------------------------------------------------
# ComponentGeometryAssignmentItem
# ---------------------------------------------------------------------------

class ComponentGeometryAssignmentItem:
    """
    Inverse counterpart of GeometryAssignmentItem.

    For a single (component, geometry) pair, records *which* sub-shape
    indices of that geometry the component is assigned to, broken down
    by sub-shape type.

    Attributes
    ----------
    vertices : Set[int]
    edges    : Set[int]
    faces    : Set[int]
    solids   : Set[int]
    """

    def __init__(self):
        self.vertices: Set[int] = set()
        self.edges:    Set[int] = set()
        self.faces:    Set[int] = set()
        self.solids:   Set[int] = set()

    def get_by_subshape_type(self, subshape_type : MpcSubshapeType) -> Set[int]:
        """
        Return the appropriate index set for a given MpcSubshapeType value.
        Raises ValueError for unrecognised types.
        """
        if subshape_type == MpcSubshapeType.Vertex:
            return self.vertices
        elif subshape_type == MpcSubshapeType.Edge:
            return self.edges
        elif subshape_type == MpcSubshapeType.Face:
            return self.faces
        elif subshape_type == MpcSubshapeType.Solid:
            return self.solids
        else:
            raise ValueError(
                f'get_by_subshape_type: unrecognised subshape type {subshape_type!r}. '
                f'Expected one of: Vertex, Edge, Face, Solid.'
            )

    def is_empty(self) -> bool:
        return not (self.vertices or self.edges or self.faces or self.solids)

    def __repr__(self) -> str:
        return (
            f'ComponentGeometryAssignmentItem('
            f'vertices={self.vertices}, '
            f'edges={self.edges}, '
            f'faces={self.faces}, '
            f'solids={self.solids})'
        )


# ---------------------------------------------------------------------------
# ComponentGeometryAssignment
# ---------------------------------------------------------------------------
# Maps a geometry instance to the sub-shape indices assigned to a component.
# Keys use identity-based hashing — same guarantee as GeometryAssignment.
ComponentGeometryAssignment = Dict[MpcGeometry, ComponentGeometryAssignmentItem]


# ---------------------------------------------------------------------------
# ComponentAssignment
# ---------------------------------------------------------------------------

class ComponentAssignment:
    """
    Inverse assignment record for a single MpcPluginCaeComponent.

    Attributes
    ----------
    geometries   : ComponentGeometryAssignment
        Geometries (and their sub-shape indices) this component is assigned to.
    interactions : Set[MpcInteraction]
        Interactions this component is assigned to.
    """

    def __init__(self):
        self.geometries:   ComponentGeometryAssignment = {}
        self.interactions: Set[MpcInteraction] = set()

    def is_empty(self) -> bool:
        return not self.geometries and not self.interactions

    def __repr__(self) -> str:
        return (
            f'ComponentAssignment('
            f'geometries={len(self.geometries)}, '
            f'interactions={len(self.interactions)})'
        )


# ---------------------------------------------------------------------------
# ComponentAssignmentMap
# ---------------------------------------------------------------------------
# The top-level inverse map: component → what it is assigned to.
# Keys use identity-based hashing — same guarantee as GeometryAssignment.
ComponentAssignmentMap = Dict[MpcPluginCaeComponent, ComponentAssignment]
