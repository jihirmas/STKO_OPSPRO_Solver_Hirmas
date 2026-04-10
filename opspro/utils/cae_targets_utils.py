"""
cae_targets_utils.py
--------------------
Utility functions for acquiring and decoding MpcCaeTargets from the
current document selection or from encoded initial_options data.

Public API
----------
get_targets(doc)                     -> MpcCaeTargets | None
decode_inline_targets(raw)           -> MpcCaeTargets | None
collect_targets(doc, opts)           -> MpcCaeTargets | None
"""

from __future__ import annotations

import json

from PyMpc import (
    App,
    MpcCaeTargets,
    MpcSubshapeType,
)


def get_targets(doc) -> 'MpcCaeTargets | None':
    """
    Return the current document selection as a MpcCaeTargets.

    Iterates doc.scene.selectedGeometries and doc.scene.selectedInteractions,
    converting each selected sub-shape to the appropriate MpcCaeTargetItem.
    When a geometry is selected without an explicit subset (i.e. the whole
    geometry is selected), addGeometry() is used so that
    collect_targets() can later expand it via convertGeometryToSubshapes().

    After collecting, clears the scene selection and triggers a view update.

    Returns None on any error; the caller is responsible for aborting.
    """
    try:
        targets = MpcCaeTargets()
        for geom, subset in doc.scene.selectedGeometries.items():
            if geom is None:
                continue
            if subset is None:
                targets.addGeometry(geom.id)
            else:
                for i in subset.vertices:
                    targets.addGeometrySubshape(geom.id, i, MpcSubshapeType.Vertex)
                for i in subset.edges:
                    targets.addGeometrySubshape(geom.id, i, MpcSubshapeType.Edge)
                for i in subset.faces:
                    targets.addGeometrySubshape(geom.id, i, MpcSubshapeType.Face)
                for i in subset.solids:
                    targets.addGeometrySubshape(geom.id, i, MpcSubshapeType.Solid)
        for interaction in doc.scene.selectedInteractions:
            if interaction is None:
                continue
            targets.addInteraction(interaction.id)

        # clear selection and refresh views
        doc.scene.unselectAll()
        App.updateAllViewsOfTheActiveDocument()

        return targets

    except Exception as e:
        print(f'[get_targets] Error acquiring targets from selection: {e}')
        return None


def decode_inline_targets(raw) -> 'MpcCaeTargets | None':
    """
    Decode targets encoded directly in initial_options['targets'].

    *raw* is the value already parsed from JSON (a list or a JSON-compatible
    object accepted by MpcCaeTargets.fromJsonStdString).

    Returns None on any error.
    """
    try:
        targets_json_str = json.dumps(raw)
        return MpcCaeTargets.fromJson(targets_json_str)
    except Exception as e:
        print(f'[decode_inline_targets] Error decoding inline targets: {e}')
        return None


def collect_targets(doc, opts: dict) -> 'MpcCaeTargets | None':
    """
    Return targets from opts['targets'] if present, otherwise from the
    current document selection.

    After acquisition, calls convertGeometryToSubshapes() to expand any
    whole-geometry or whole-subshape-collection items into individual
    subshape items, so that downstream code always works with concrete
    (geometry_id, subshape_type, subshape_id) triples.

    Returns None when acquisition fails or the targets are empty.
    """
    raw = opts.get('targets')
    if raw:
        targets = decode_inline_targets(raw)
    else:
        targets = get_targets(doc)
    if targets is not None:
        targets.convertGeometryToSubshapes()
    return targets
