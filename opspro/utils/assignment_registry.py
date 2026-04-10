"""
assignment_registry.py
----------------------
Document-level singleton MpcPluginCaeComponent that maintains the
global assignment maps between CAE entities and plugin components.

It keeps two parallel views of the same assignment data:

  Direct map  (entity → components)
  ----------------------------------
  GeometryAssignment     : MpcGeometry     → GeometryAssignmentItem
  InteractionAssignment  : MpcInteraction  → Set[MpcPluginCaeComponent]

  Inverse map  (component → entities)
  ------------------------------------
  ComponentAssignmentMap : MpcPluginCaeComponent → ComponentAssignment

This component lives in the INTERNAL group (UID '999-internal'), which is
always deserialized last by STKO.  That ordering guarantee is essential:
by the time restore() is called here, all user-visible components
(Materials, etc.) are already restored and their Python objects exist —
so the inverse map can reference them safely.

Serialization format for component references
---------------------------------------------
Components are stored as [group_idx, comp_id] pairs, where group_idx is
an index into a top-level 'groups' list of componentGroupID strings.
This avoids repeating the group ID string for every reference while
keeping the reference unambiguous — IDs are only unique within a group,
not across groups.
"""

from PyMpc import (
    MpcPluginCaeComponent, 
    MpcCaeTargets,
    MpcCaeTargetType,
    MpcCaeTargetItem,
    MpcGeometry, 
    MpcInteraction,
    MpcSubshapeType,
    App
)
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.utils.assignment_types import (
    GeometryAssignment,
    GeometryAssignmentItem,
    InteractionAssignment,
    ComponentAssignmentMap,
    ComponentAssignment,
    ComponentGeometryAssignmentItem,
)


# ---------------------------------------------------------------------------
# Module-level accessor
# ---------------------------------------------------------------------------

def get_assignment_registry() -> 'AssignmentRegistry | None':
    """
    Return the AssignmentRegistry singleton from the active CAE document.
    Returns None when the document or registry cannot be found.
    """
    try:
        doc = App.caeDocument()
        groups = doc.pluginCaeComponents.groups()
        coll = groups[CAEComponentGroupUIDs.INTERNAL].collection
        for key in coll.keys():
            comp = coll[key]
            if comp.className() == 'AssignmentRegistry':
                return comp
    except Exception as e:
        print(f'Warning: could not retrieve AssignmentRegistry: {e}')
    return None


# ---------------------------------------------------------------------------
# AssignmentRegistry
# ---------------------------------------------------------------------------

class AssignmentRegistry(MpcPluginCaeComponent):
    """
    Maintains the global direct and inverse assignment maps for the document.

    Direct maps
    -----------
    geometry_assignment     : GeometryAssignment
    interaction_assignment  : InteractionAssignment

    Inverse map
    -----------
    component_assignment    : ComponentAssignmentMap

    All three are kept in sync by assign() / unassign().
    """

    def __init__(self, id: int = 1, name: str = 'AssignmentRegistry'):
        super().__init__(id, name)
        self.geometry_assignment:    GeometryAssignment    = {}
        self.interaction_assignment: InteractionAssignment = {}
        self.component_assignment:   ComponentAssignmentMap = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def assign(self, component: MpcPluginCaeComponent, targets: MpcCaeTargets):
        """Register *component* as assigned to every item in *targets*."""
        for item in targets.items:
            if item.type == MpcCaeTargetType.Geometry:
                self._assign_geometry(component, item)
            elif item.type == MpcCaeTargetType.Interaction:
                self._assign_interaction(component, item)

    def unassign(self, component: MpcPluginCaeComponent, targets: MpcCaeTargets):
        """Remove the assignment of *component* from every item in *targets*."""
        for item in targets.items:
            if item.type == MpcCaeTargetType.Geometry:
                self._unassign_geometry(component, item)
            elif item.type == MpcCaeTargetType.Interaction:
                self._unassign_interaction(component, item)

    def components_for_geometry(
        self, geometry: MpcGeometry, subshape_type, subshape_id: int
    ) -> set:
        """
        Return the set of components assigned to a specific sub-shape.
        *subshape_type* is a MpcSubshapeType value.
        If subshape_id == -1, return all components assigned to any sub-shape
        of the given type on this geometry.
        """
        item = self.geometry_assignment.get(geometry)
        if item is None:
            return set()
        sub = item.get_by_subshape_type(subshape_type)
        if subshape_id == -1:
            result = set()
            for s in sub.values():
                result |= s
            return result
        return set(sub.get(subshape_id, set()))

    def components_for_interaction(self, interaction: MpcInteraction) -> set:
        """Return the set of components assigned to *interaction*."""
        return set(self.interaction_assignment.get(interaction, set()))

    def assignment_for_component(
        self, component: MpcPluginCaeComponent
    ) -> 'ComponentAssignment | None':
        """Return the ComponentAssignment record for *component*, or None."""
        return self.component_assignment.get(component)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _assign_geometry(self, component : MpcPluginCaeComponent, item : MpcCaeTargetItem):
        doc = App.caeDocument()
        geom = doc.getGeometry(item.id)
        if geom is None:
            print(f"AssignmentRegistry warning: geometry with ID {item.id} not found for assignment")
            return
        if component is None:
            print(f"AssignmentRegistry warning: component is None for geometry assignment (ID {item.id})")
            return

        # direct map
        geom_asn = self.geometry_assignment.setdefault(geom, GeometryAssignmentItem())
        subgeom_asn = geom_asn.get_by_subshape_type(item.subshape_type)
        subgeom_asn.setdefault(item.subshape_id, set()).add(component)

        # inverse map
        comp_asn = self.component_assignment.setdefault(component, ComponentAssignment())
        com_geom_asn = comp_asn.geometries.setdefault(geom, ComponentGeometryAssignmentItem())
        com_geom_asn.get_by_subshape_type(item.subshape_type).add(item.subshape_id)

    def _unassign_geometry(self, component: MpcPluginCaeComponent, item: MpcCaeTargetItem):
        doc = App.caeDocument()
        geom = doc.geometries[item.id]

        # direct map
        geom_asn = self.geometry_assignment.get(geom)
        if geom_asn is not None:
            subgeom_asn = geom_asn.get_by_subshape_type(item.subshape_type)
            comp_set = subgeom_asn.get(item.subshape_id)
            if comp_set is not None:
                comp_set.discard(component)
                if not comp_set:
                    del subgeom_asn[item.subshape_id]

        # inverse map
        comp_asn = self.component_assignment.get(component)
        if comp_asn is not None:
            com_geom_asn = comp_asn.geometries.get(geom)
            if com_geom_asn is not None:
                com_geom_asn.get_by_subshape_type(item.subshape_type).discard(item.subshape_id)
                if com_geom_asn.is_empty():
                    del comp_asn.geometries[geom]
            if comp_asn.is_empty():
                del self.component_assignment[component]

    def _assign_interaction(self, component: MpcPluginCaeComponent, item: MpcCaeTargetItem):
        doc = App.caeDocument()
        interaction = doc.interactions[item.id]

        # direct map
        self.interaction_assignment.setdefault(interaction, set()).add(component)

        # inverse map
        comp_asn = self.component_assignment.setdefault(component, ComponentAssignment())
        comp_asn.interactions.add(interaction)

    def _unassign_interaction(self, component: MpcPluginCaeComponent, item: MpcCaeTargetItem):
        doc = App.caeDocument()
        interaction = doc.interactions[item.id]

        # direct map
        comp_set = self.interaction_assignment.get(interaction)
        if comp_set is not None:
            comp_set.discard(component)
            if not comp_set:
                del self.interaction_assignment[interaction]

        # inverse map
        comp_asn = self.component_assignment.get(component)
        if comp_asn is not None:
            comp_asn.interactions.discard(interaction)
            if comp_asn.is_empty():
                del self.component_assignment[component]

    # ------------------------------------------------------------------
    # MpcPluginCaeComponent interface
    # ------------------------------------------------------------------

    def componentGroupID(self):
        return CAEComponentGroupUIDs.INTERNAL

    def className(self):
        return 'AssignmentRegistry'

    def description(self):
        return 'Global assignment registry (internal, do not edit)'

    def onTransfer(self, tool):
        """
        Called by MpcTransferPluginCaeComponentReturnArgs when a geometry
        transfer operation is performed (transformation, copy-in-series, …).

        For each assigned (geom, stype, ssid, comp) tuple, asks the tool for
        target sub-shapes on the destination geometry and ADDS (copies) the
        same component assignment there, leaving the source assignment intact.

        Diff convention (restore() always calls apply(invert=True)):
          undo_diff  entries (prev=None, new=comp)  → invert removes comp from new position ✓
          redo_diff  entries (prev=comp, new=None)  → invert adds  comp back to new position ✓
        Both diffs share the same (new_geom, stype, ssid) coordinates — only
        prev/new are swapped, so we build them in a single loop.

        Returns (undo_str, redo_str).
        """
        from opspro.utils.assignment_diff import AssignDiff

        _stypes = [
            MpcSubshapeType.Vertex,
            MpcSubshapeType.Edge,
            MpcSubshapeType.Face,
            MpcSubshapeType.Solid,
        ]
        _stype_name = {
            MpcSubshapeType.Vertex: 'vertex',
            MpcSubshapeType.Edge:   'edge',
            MpcSubshapeType.Face:   'face',
            MpcSubshapeType.Solid:  'solid',
        }

        # First pass: read-only scan — collect only the actual transfer targets.
        # self.geometry_assignment is not mutated here, so iteration is safe.
        new_targets = []  # list of (new_geom, stype, new_ssid, comp)
        for geom, ga_item in self.geometry_assignment.items():
            for stype in _stypes:
                sub = ga_item.get_by_subshape_type(stype)
                for ssid, comp_set in sub.items():
                    for comp in comp_set:
                        for new_geom, new_ssid in tool.findTargets(geom, stype, ssid):
                            new_targets.append((new_geom, stype, new_ssid, comp))

        if not new_targets:
            return ('', '')

        # Second pass: add new assignments + build both diffs in one loop.
        undo_diff = AssignDiff(custom='transfer-undo')
        redo_diff = AssignDiff(custom='transfer-redo')
        for new_geom, stype, new_ssid, comp in new_targets:
            sname = _stype_name[stype]
            gid   = int(new_geom.id)
            # direct map
            ga_item = self.geometry_assignment.setdefault(new_geom, GeometryAssignmentItem())
            ga_item.get_by_subshape_type(stype).setdefault(new_ssid, set()).add(comp)
            # inverse map
            comp_asn = self.component_assignment.setdefault(comp, ComponentAssignment())
            com_geom_asn = comp_asn.geometries.setdefault(new_geom, ComponentGeometryAssignmentItem())
            com_geom_asn.get_by_subshape_type(stype).add(new_ssid)
            # diffs
            undo_diff.add_geometry_item(gid, sname, new_ssid, prev_comp=None, new_comp=comp)
            redo_diff.add_geometry_item(gid, sname, new_ssid, prev_comp=comp, new_comp=None)

        return (undo_diff.to_json(), redo_diff.to_json())

    def onInteractionChanged(self, interaction_collection, signal_type):
        from PyMpc import MpcCaeDocumentComponentSignalType
        # A newly added interaction cannot have any prior assignments, nothing to do.
        if signal_type != MpcCaeDocumentComponentSignalType.Removed:
            return ''
        # Collect only affected entries — skip entirely if none are registered.
        affected = {}
        for inter in interaction_collection.values():
            if inter is None:
                continue
            comp_set = self.interaction_assignment.get(inter)
            if comp_set:
                affected[inter] = set(comp_set)  # snapshot before mutation
        if not affected:
            return ''
        # Build a compact AssignDiff (prev_comp → None) for undo via restore().
        from opspro.utils.assignment_diff import AssignDiff
        diff = AssignDiff(custom='interaction-removed')
        for inter, comp_set in affected.items():
            for comp in comp_set:
                diff.add_interaction_item(int(inter.id), prev_comp=comp, new_comp=None)
        state = diff.to_json()
        # Clean up both direct and inverse maps.
        for inter, comp_set in affected.items():
            del self.interaction_assignment[inter]
            for comp in comp_set:
                comp_asn = self.component_assignment.get(comp)
                if comp_asn is not None:
                    comp_asn.interactions.discard(inter)
                    if comp_asn.is_empty():
                        del self.component_assignment[comp]
        return state

    def onPluginCaeComponentChanged(self, plugin_cae_component_collection, signal_type):
        from PyMpc import MpcCaeDocumentComponentSignalType
        # A newly added component cannot have any prior assignments, nothing to do.
        if signal_type != MpcCaeDocumentComponentSignalType.Removed:
            return ''
        # Collect only the removed components that actually have assignments.
        affected = []
        for comp in plugin_cae_component_collection.values():
            if comp is None:
                continue
            if comp in self.component_assignment:
                affected.append(comp)
        if not affected:
            return ''
        # Build a compact AssignDiff (prev_comp → None) for undo via restore().
        from opspro.utils.assignment_diff import AssignDiff
        from PyMpc import MpcSubshapeType
        _stype_name = {
            MpcSubshapeType.Vertex: 'vertex',
            MpcSubshapeType.Edge:   'edge',
            MpcSubshapeType.Face:   'face',
            MpcSubshapeType.Solid:  'solid',
        }
        diff = AssignDiff(custom='component-removed')
        for comp in affected:
            comp_asn = self.component_assignment[comp]
            for geom, comp_geom_item in comp_asn.geometries.items():
                for stype, sname in _stype_name.items():
                    for ssid in comp_geom_item.get_by_subshape_type(stype):
                        diff.add_geometry_item(int(geom.id), sname, ssid, prev_comp=comp, new_comp=None)
            for inter in comp_asn.interactions:
                diff.add_interaction_item(int(inter.id), prev_comp=comp, new_comp=None)
        state = diff.to_json()
        # Clean up both direct and inverse maps.
        for comp in affected:
            comp_asn = self.component_assignment.pop(comp)
            # clean direct geometry map
            for geom, comp_geom_item in comp_asn.geometries.items():
                ga_item = self.geometry_assignment.get(geom)
                if ga_item is None:
                    continue
                for stype in (MpcSubshapeType.Vertex, MpcSubshapeType.Edge,
                            MpcSubshapeType.Face, MpcSubshapeType.Solid):
                    sub = ga_item.get_by_subshape_type(stype)
                    for ssid in comp_geom_item.get_by_subshape_type(stype):
                        comp_set = sub.get(ssid)
                        if comp_set is not None:
                            comp_set.discard(comp)
                            if not comp_set:
                                del sub[ssid]
                if ga_item.is_empty():
                    del self.geometry_assignment[geom]
            # clean direct interaction map
            for inter in comp_asn.interactions:
                inter_comps = self.interaction_assignment.get(inter)
                if inter_comps is not None:
                    inter_comps.discard(comp)
                    if not inter_comps:
                        del self.interaction_assignment[inter]
        return state

    def onGeometryChanged(self, geometry_collection, signal_type):
        from PyMpc import MpcCaeDocumentComponentSignalType, MpcSubshapeType
        # A newly added geometry cannot have any prior assignments, nothing to do.
        if signal_type != MpcCaeDocumentComponentSignalType.Removed:
            return ''
        # Collect only affected entries — skip entirely if none are registered.
        affected = {}
        for geom in geometry_collection.values():
            if geom is None:
                continue
            ga_item = self.geometry_assignment.get(geom)
            if ga_item is not None:
                affected[geom] = ga_item
        if not affected:
            return ''
        # Build a compact AssignDiff (prev_comp → None) for undo via restore().
        # Lazy import to avoid circular dependency (assignment_diff imports us).
        from opspro.utils.assignment_diff import AssignDiff
        _stype_name = {
            MpcSubshapeType.Vertex: 'vertex',
            MpcSubshapeType.Edge:   'edge',
            MpcSubshapeType.Face:   'face',
            MpcSubshapeType.Solid:  'solid',
        }
        diff = AssignDiff(custom='geometry-removed')
        for geom, ga_item in affected.items():
            for stype, sname in _stype_name.items():
                sub = ga_item.get_by_subshape_type(stype)
                for ssid, comp_set in sub.items():
                    for comp in comp_set:
                        diff.add_geometry_item(int(geom.id), sname, ssid, prev_comp=comp, new_comp=None)
        state = diff.to_json()
        # Clean up both direct and inverse maps.
        for geom, ga_item in affected.items():
            del self.geometry_assignment[geom]
            for stype_dict in (ga_item.vertices, ga_item.edges, ga_item.faces, ga_item.solids):
                for comp_set in stype_dict.values():
                    for comp in comp_set:
                        comp_asn = self.component_assignment.get(comp)
                        if comp_asn is not None:
                            comp_asn.geometries.pop(geom, None)
                            if comp_asn.is_empty():
                                del self.component_assignment[comp]
        
        return state

    # ------------------------------------------------------------------
    # Serialization
    # Note: MpcGeometry / MpcInteraction / MpcPluginCaeComponent objects
    # cannot be serialized directly; we store their integer IDs and
    # rebuild the maps on restore() — by which point all components and
    # document entities are guaranteed to be loaded (INTERNAL group is last).
    # ------------------------------------------------------------------

    def save(self) -> str:
        import json
        try:
            return json.dumps(self._to_dict())
        except Exception as e:
            print(f'Error saving AssignmentRegistry: {e}')
            return ''

    def restore(self, state_str: str):
        import json
        if not state_str:
            return
        try:
            data = json.loads(state_str)
            if data.get('type') == 'assign_diff':
                from opspro.utils.assignment_diff import AssignDiff
                AssignDiff.from_json(state_str).apply(invert=True)
            else:
                self._from_dict(data)
        except Exception as e:
            print(f'Error restoring AssignmentRegistry: {e}')

    def _to_dict(self) -> dict:
        """
        Serialize both maps to plain JSON-serializable structures.

        Component references are encoded as [group_idx, comp_id] where
        group_idx is an index into the top-level 'groups' list.  This
        avoids repeating the componentGroupID string for every component
        while still making the reference unambiguous (IDs are only unique
        within a group, not across groups).

        Format
        ------
        {
          "ID": int,
          "name": str,
          "groups": ["001-materials", "002-sections", ...],
          "geometry_assignment": {
            "<geom_id>": {
              "<stype_name>": {
                "<subshape_id>": [[group_idx, comp_id], ...]
              }
            }
          },
          "interaction_assignment": {
            "<interaction_id>": [[group_idx, comp_id], ...]
          }
        }
        """
        from PyMpc import MpcSubshapeType
        _stype_name = {
            MpcSubshapeType.Vertex: 'vertex',
            MpcSubshapeType.Edge:   'edge',
            MpcSubshapeType.Face:   'face',
            MpcSubshapeType.Solid:  'solid',
        }

        # Build group_id → index table on the fly
        groups: list = []
        group_index: dict[str, int] = {}

        def _comp_ref(comp) -> list:
            gid = comp.componentGroupID()
            if gid not in group_index:
                group_index[gid] = len(groups)
                groups.append(gid)
            return [group_index[gid], int(comp.id)]

        geom_data = {}
        for geom, ga_item in self.geometry_assignment.items():
            gd = {}
            for stype, sname in _stype_name.items():
                sub = ga_item.get_by_subshape_type(stype)
                if sub:
                    gd[sname] = {
                        str(ssid): [_comp_ref(c) for c in comps]
                        for ssid, comps in sub.items()
                    }
            if gd:
                geom_data[str(int(geom.id))] = gd

        inter_data = {
            str(int(inter.id)): [_comp_ref(c) for c in comps]
            for inter, comps in self.interaction_assignment.items()
            if comps
        }

        return {
            'ID':   int(self.id),
            'name': self.name,
            'groups': groups,
            'geometry_assignment':    geom_data,
            'interaction_assignment': inter_data,
        }

    def _from_dict(self, data: dict):
        doc = App.caeDocument()
        self.id   = data.get('ID',   self.id)
        self.name = data.get('name', self.name)

        _stype = {
            'vertex': MpcSubshapeType.Vertex,
            'edge':   MpcSubshapeType.Edge,
            'face':   MpcSubshapeType.Face,
            'solid':  MpcSubshapeType.Solid,
        }

        # Decode groups list → collection lookup table
        groups: list = data.get('groups', [])
        all_groups = doc.pluginCaeComponents.groups()

        def _comp(ref: list):
            """Resolve [group_idx, comp_id] to the live component object."""
            group_id = groups[ref[0]]
            group = all_groups.get(group_id)
            if group is None:
                return None
            return group.collection.get(ref[1])

        # Rebuild all three maps from scratch
        self.geometry_assignment    = {}
        self.interaction_assignment = {}
        self.component_assignment   = {}

        for gid_str, gd in data.get('geometry_assignment', {}).items():
            geom = doc.geometries.get(int(gid_str))
            if geom is None:
                continue
            ga_item = GeometryAssignmentItem()
            self.geometry_assignment[geom] = ga_item
            for sname, ssid_map in gd.items():
                stype = _stype.get(sname)
                if stype is None:
                    continue
                sub = ga_item.get_by_subshape_type(stype)
                for ssid_str, comp_refs in ssid_map.items():
                    ssid = int(ssid_str)
                    for ref in comp_refs:
                        comp = _comp(ref)
                        if comp is None:
                            continue
                        sub.setdefault(ssid, set()).add(comp)
                        # inverse
                        comp_asn = self.component_assignment.setdefault(comp, ComponentAssignment())
                        com_geom_asn = comp_asn.geometries.setdefault(geom, ComponentGeometryAssignmentItem())
                        com_geom_asn.get_by_subshape_type(stype).add(ssid)

        for iid_str, comp_refs in data.get('interaction_assignment', {}).items():
            inter = doc.interactions.get(int(iid_str))
            if inter is None:
                continue
            for ref in comp_refs:
                comp = _comp(ref)
                if comp is None:
                    continue
                self.interaction_assignment.setdefault(inter, set()).add(comp)
                comp_asn = self.component_assignment.setdefault(comp, ComponentAssignment())
                comp_asn.interactions.add(inter)

    def __repr__(self) -> str:
        return (
            f'AssignmentRegistry(id={int(self.id)}, '
            f'geometries={len(self.geometry_assignment)}, '
            f'interactions={len(self.interaction_assignment)}, '
            f'components={len(self.component_assignment)})'
        )
