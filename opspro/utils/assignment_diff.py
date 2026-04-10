"""
assignment_diff.py
------------------
Diff-based utilities for material assignment/unassignment operations,
shared by MaterialCommandAssign and MaterialCommandUnassign.

Public API
----------
AssignDiff          -- compact, JSON-serialisable per-target state change
AssignDiff.apply         -- apply (or invert) a diff on the live registry
AssignDiff.makeAssignDiff   -- build a diff for an assign operation
AssignDiff.makeUnassignDiff -- build a diff for an unassign operation
"""

from __future__ import annotations

import json

from PyMpc import (
    App,
    MpcCaeTargets, 
    MpcCaeTargetType,
    MpcCaeDocument, 
    MpcGeometry,
    MpcInteraction,
    MpcSubshapeType,
    MpcPluginCaeComponent,
    MpcPluginCaeComponentAssignmentFlags
)

from opspro.utils.assignment_registry import (
    AssignmentRegistry,
    get_assignment_registry
)

# ---------------------------------------------------------------------------
# Sub-shape type conversion helpers (private)
# ---------------------------------------------------------------------------

def _stype_to_name(stype) -> str:
    return {
        MpcSubshapeType.Vertex: 'vertex',
        MpcSubshapeType.Edge:   'edge',
        MpcSubshapeType.Face:   'face',
        MpcSubshapeType.Solid:  'solid',
    }.get(stype, 'unknown')


def _name_to_stype(name: str):
    return {
        'vertex': MpcSubshapeType.Vertex,
        'edge':   MpcSubshapeType.Edge,
        'face':   MpcSubshapeType.Face,
        'solid':  MpcSubshapeType.Solid,
    }.get(name)


_STYPE_TO_ASSIGNMENT_FLAG: dict = {}  # populated lazily on first use (MpcSubshapeType values not available at import time)


def _get_assignment_key(comp) -> object:
    """Return comp.assignment_key() if implemented, otherwise None (one-per-group fallback)."""
    fn = getattr(comp, 'assignment_key', None)
    return fn() if callable(fn) else None

def _stype_to_assignment_flag(stype) -> int:
    """Map a MpcSubshapeType to the corresponding MpcPluginCaeComponentAssignmentFlags int value."""
    global _STYPE_TO_ASSIGNMENT_FLAG
    if not _STYPE_TO_ASSIGNMENT_FLAG:
        _STYPE_TO_ASSIGNMENT_FLAG = {
            MpcSubshapeType.Vertex: int(MpcPluginCaeComponentAssignmentFlags.Vertices),
            MpcSubshapeType.Edge:   int(MpcPluginCaeComponentAssignmentFlags.Edges),
            MpcSubshapeType.Face:   int(MpcPluginCaeComponentAssignmentFlags.Faces),
            MpcSubshapeType.Solid:  int(MpcPluginCaeComponentAssignmentFlags.Solids),
        }
    return _STYPE_TO_ASSIGNMENT_FLAG.get(stype, 0)


# ---------------------------------------------------------------------------
# Duck-typed stand-ins for MpcCaeTargetItem / MpcCaeTargets (private)
# ---------------------------------------------------------------------------
# AssignmentRegistry.assign/unassign iterate targets.items and read
# .type, .id, .subshape_type, .subshape_id from each item.
# These lightweight classes satisfy the same interface without requiring
# a constructible MpcCaeTargets from Python.

class _FakeTargetItem:
    __slots__ = ('type', 'id', 'subshape_type', 'subshape_id')

    def __init__(self, ttype, entity_id, stype=None, ssid=None):
        self.type          = ttype
        self.id            = entity_id
        self.subshape_type = stype
        self.subshape_id   = ssid


class _FakeTargets:
    __slots__ = ('items',)

    def __init__(self, items: list):
        self.items = items


# ---------------------------------------------------------------------------
# _existing_component_on_* helpers (private)
# ---------------------------------------------------------------------------

def _all_conflicting_on_geometry(
        registry : AssignmentRegistry,
        geom : MpcGeometry,
        stype : MpcSubshapeType,
        ssid : int,
        group_id : str,
        conflict_key = None) -> list:
    """Return ALL components of *group_id* that conflict with *conflict_key* on this sub-shape.

    If *conflict_key* is None (fallback / one-per-group), any component of the same group conflicts.
    Otherwise only components whose assignment_key() overlaps with *conflict_key* are included.
    Returns a list (possibly empty) so that callers can handle multiple simultaneous conflicts.
    """
    result = []
    for comp in registry.components_for_geometry(geom, stype, ssid):
        if comp.componentGroupID() != group_id:
            continue
        if conflict_key is None or _get_assignment_key(comp) == conflict_key:
            result.append(comp)
    return result


def _all_conflicting_on_interaction(
        registry : AssignmentRegistry,
        interaction : MpcInteraction,
        group_id : str,
        conflict_key = None) -> list:
    """Return ALL components of *group_id* that conflict with *conflict_key* on this interaction.

    If *conflict_key* is None (fallback / one-per-group), any component of the same group conflicts.
    Otherwise only components whose assignment_key() overlaps with *conflict_key* are included.
    """
    result = []
    for comp in registry.components_for_interaction(interaction):
        if comp.componentGroupID() != group_id:
            continue
        if conflict_key is None or _get_assignment_key(comp) == conflict_key:
            result.append(comp)
    return result


# ---------------------------------------------------------------------------
# AssignDiff  — compact, JSON-serialisable diff
# ---------------------------------------------------------------------------

class AssignDiff:
    """
    Per-target record of the state change produced by a single assignment
    or unassignment command.

    Component references are encoded as compact [group_idx, comp_id] pairs
    (group_idx indexes the top-level 'groups' list), matching the convention
    used by AssignmentRegistry._to_dict().

    JSON schema
    -----------
    {
      "type":   "assign_diff",
      "groups": ["001-materials", ...],
      "items": [
        {
          "target_type":   "geometry" | "interaction",
          "entity_id":     <int>,
          // geometry-only:
          "stype_name":    "vertex" | "edge" | "face" | "solid",
          "subshape_id":   <int>,
          // state:
          "prev_comp_ref": [<group_idx>, <comp_id>] | null,
          "new_comp_ref":  [<group_idx>, <comp_id>] | null
        },
        ...
      ]
    }

    The "type" field is used by AssignmentRegistry.restore() to dispatch
    to AssignDiff.apply() instead of the full _from_dict() path.

    The optional "custom" field is a free-form string for debug / logging
    purposes and is ignored during apply().
    """

    def __init__(self, custom: str = ''):
        self.groups: list = []
        self._group_index: dict = {}
        self.items: list = []
        self.custom: str = custom

    def _ref(self, comp: MpcPluginCaeComponent) -> list | None:
        """Encode a live component as [group_idx, comp_id], or None."""
        if comp is None:
            return None
        gid = comp.componentGroupID()
        if gid not in self._group_index:
            self._group_index[gid] = len(self.groups)
            self.groups.append(gid)
        return [self._group_index[gid], int(comp.id)]

    def add_geometry_item(
        self,
        entity_id: int,
        stype_name: str,
        subshape_id: int,
        prev_comp: MpcPluginCaeComponent,
        new_comp: MpcPluginCaeComponent,
    ):
        self.items.append({
            'target_type':   'geometry',
            'entity_id':     entity_id,
            'stype_name':    stype_name,
            'subshape_id':   subshape_id,
            'prev_comp_ref': self._ref(prev_comp),
            'new_comp_ref':  self._ref(new_comp),
        })

    def add_interaction_item(
            self,
            entity_id: int, 
            prev_comp: MpcPluginCaeComponent, 
            new_comp: MpcPluginCaeComponent):
        self.items.append({
            'target_type':   'interaction',
            'entity_id':     entity_id,
            'prev_comp_ref': self._ref(prev_comp),
            'new_comp_ref':  self._ref(new_comp),
        })

    def to_json(self) -> str:
        return json.dumps({'type': 'assign_diff', 'custom': self.custom, 'groups': self.groups, 'items': self.items})

    @staticmethod
    def from_json(s: str) -> 'AssignDiff':
        data = json.loads(s)
        d = AssignDiff(custom=data.get('custom', ''))
        d.groups = data['groups']
        d._group_index = {g: i for i, g in enumerate(d.groups)}
        d.items = data['items']
        return d

    def apply(self, *, invert: bool) -> None:
        """
        Apply this diff to the live AssignmentRegistry.

        invert=False (forward)  : new_comp replaces prev_comp for each target.
        invert=True  (inverse)  : prev_comp replaces new_comp  (undo direction).

        Emits commitChanges() and sets doc.dirty = True when done.
        """
        doc = App.caeDocument()
        if doc is None:
            return

        registry = get_assignment_registry()
        if registry is None:
            print('[AssignDiff.apply] Warning: AssignmentRegistry not found; skipping.')
            return

        groups_list = self.groups
        all_groups  = doc.pluginCaeComponents.groups()

        def resolve(ref):
            if ref is None:
                return None
            try:
                gid = groups_list[ref[0]]
                grp = all_groups.get(gid)
                return grp.collection.get(ref[1]) if grp is not None else None
            except Exception:
                return None

        for item in self.items:
            if invert:
                remove_ref = item['new_comp_ref']
                add_ref    = item['prev_comp_ref']
            else:
                remove_ref = item['prev_comp_ref']
                add_ref    = item['new_comp_ref']

            remove_comp = resolve(remove_ref)
            add_comp    = resolve(add_ref)

            if item['target_type'] == 'geometry':
                stype = _name_to_stype(item['stype_name'])
                if stype is None:
                    continue
                fake = _FakeTargetItem(
                    MpcCaeTargetType.Geometry,
                    item['entity_id'], stype, item['subshape_id'],
                )
                tgts = _FakeTargets([fake])
                if remove_comp is not None:
                    registry.unassign(remove_comp, tgts)
                if add_comp is not None:
                    registry.assign(add_comp, tgts)

            else:  # interaction
                fake = _FakeTargetItem(MpcCaeTargetType.Interaction, item['entity_id'])
                tgts = _FakeTargets([fake])
                if remove_comp is not None:
                    registry.unassign(remove_comp, tgts)
                if add_comp is not None:
                    registry.assign(add_comp, tgts)

        doc.commitChanges()
        doc.dirty = True

    @staticmethod
    def makeAssignDiff(
            doc: MpcCaeDocument,
            registry: AssignmentRegistry,
            comp: MpcPluginCaeComponent,
            targets: MpcCaeTargets
            ) -> 'AssignDiff':
        """Build a diff for assigning *comp* to *targets*.

        Targets where *comp* is already assigned are silently skipped.
        Targets assigned to another component of the same group record the evicted
        component as prev_comp so undo can restore it.
        """
        diff = AssignDiff(custom='assign')
        group_id = comp.componentGroupID()
        group_item = doc.pluginCaeComponents.groups().get(group_id)
        aflags = int(group_item.assignmentFlags) if group_item is not None else 0
        conflict_key = _get_assignment_key(comp)
        for item in targets.items:

            # geometry
            if item.type == MpcCaeTargetType.Geometry:
                geom = doc.getGeometry(item.id)
                if geom is None:
                    continue
                sname = _stype_to_name(item.subshape_type)
                if sname == 'unknown':
                    continue
                if not (aflags & _stype_to_assignment_flag(item.subshape_type)):
                    continue  # subshape type not allowed by group's assignmentFlags
                conflicts = _all_conflicting_on_geometry(registry, geom, item.subshape_type, item.subshape_id, group_id, conflict_key)
                if any(c is comp for c in conflicts):
                    continue  # already assigned; skip
                # Evict every conflicting component, then add the new one
                for evicted in conflicts:
                    diff.add_geometry_item(item.id, sname, item.subshape_id, prev_comp=evicted, new_comp=None)
                diff.add_geometry_item(item.id, sname, item.subshape_id, prev_comp=None, new_comp=comp)

            # interaction
            elif item.type == MpcCaeTargetType.Interaction:
                interaction = doc.getInteraction(item.id)
                if interaction is None:
                    continue
                if not (aflags & int(MpcPluginCaeComponentAssignmentFlags.Interactions)):
                    continue  # interactions not allowed by group's assignmentFlags
                conflicts = _all_conflicting_on_interaction(registry, interaction, group_id, conflict_key)
                if any(c is comp for c in conflicts):
                    continue  # already assigned; skip
                for evicted in conflicts:
                    diff.add_interaction_item(item.id, prev_comp=evicted, new_comp=None)
                diff.add_interaction_item(item.id, prev_comp=None, new_comp=comp)

        return diff

    @staticmethod
    def makeUnassignDiff(
            doc: MpcCaeDocument,
            registry: AssignmentRegistry,
            comp: MpcPluginCaeComponent,
            targets: MpcCaeTargets
            ) -> 'AssignDiff':
        """Build a diff for unassigning *comp* from *targets*.

        Targets where *comp* is not currently assigned are silently skipped.
        """
        diff = AssignDiff(custom='unassign')
        for item in targets.items:

            # geometry
            if item.type == MpcCaeTargetType.Geometry:
                geom = doc.getGeometry(item.id)
                if geom is None:
                    continue
                sname = _stype_to_name(item.subshape_type)
                if sname == 'unknown':
                    continue
                # Search by identity: find comp directly among all components on this sub-shape.
                # Using conflict_key here would be wrong when multiple components with overlapping
                # anchor keys coexist (e.g. I + J on the same edge): the key search could return
                # a different component first, causing comp to be silently skipped.
                if not any(c is comp for c in registry.components_for_geometry(geom, item.subshape_type, item.subshape_id)):
                    continue  # comp not assigned here; skip
                diff.add_geometry_item(
                    item.id, sname, item.subshape_id,
                    prev_comp=comp, new_comp=None,
                )

            # interaction
            elif item.type == MpcCaeTargetType.Interaction:
                interaction = doc.getInteraction(item.id)
                if interaction is None:
                    continue
                if not any(c is comp for c in registry.components_for_interaction(interaction)):
                    continue  # comp not assigned here; skip
                diff.add_interaction_item(item.id, prev_comp=comp, new_comp=None)

        return diff

