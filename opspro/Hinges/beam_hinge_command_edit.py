"""
beam_hinge_command_edit.py
--------------------------
Command for editing any BeamHinge subtype (BeamEndRelease,
BeamRotationalHinge, BeamShearHinge) via its own dialog.
"""

from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
    AsUndoRedoCommand,
)
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from PySide2 import QtWidgets
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "edit_beam_hinge",
    "description": "Edits an existing beam hinge component (BeamEndRelease, BeamRotationalHinge, or BeamShearHinge) in the active document, identified by its component_id. All editable fields are optional; omitted fields keep their current values. Physical quantities use {magnitude, unit} format. Requires an active CAE document.",
    "command": "EditBeamHinge",
    "inputSchema": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "ID of the hinge component to edit"
            },
            "name": {
                "type": "string",
                "description": "Optional: new display name"
            },
            "anchor": {
                "type": "string",
                "description": "Optional: placement anchor. BeamEndRelease/BeamRotationalHinge: 'I','J','IJ'. BeamShearHinge: adds 'C'."
            },
            "offset": {
                "type": "object",
                "description": "Optional: distance from anchor along beam axis (>= 0). Format: {magnitude, unit}.",
                "properties": {
                    "magnitude": {"type": "number"},
                    "unit":      {"type": "string"}
                }
            },
            "dofs_I": {
                "type": "object",
                "description": "BeamEndRelease only: DOFs to release at I-end (local frame). Keys: Ux (translation along local-x), Uy (translation along local-y), Uz (translation along local-z), Rx (rotation about local-x), Ry (rotation about local-y), Rz (rotation about local-z). true = DOF is released; false = DOF is continuous (no release)."
            },
            "dofs_J": {
                "type": "object",
                "description": "BeamEndRelease only: DOFs to release at J-end (local frame). Same keys as dofs_I. true = DOF is released; false = DOF is continuous (no release)."
            },
            "dofs": {
                "type": "object",
                "description": "BeamRotationalHinge: Ry (moment about local-y), Rz (moment about local-z). BeamShearHinge: Vy (shear along local-y), Vz (shear along local-z). true = spring is active on that DOF; false = DOF is continuous (no spring)."
            }
        },
        "required": ["component_id"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status": {"type": "boolean", "description": "true on success, false on failure"},
            "error":  {"type": "string",  "description": "Error message if status is false, empty string on success"}
        }
    }
}
MCP_COMMAND_METADATA_END
"""


class _BeamHingeEditUndo(AsUndoRedoCommand):
    """Swap-based undo/redo for a BeamHinge edit."""

    def __init__(self, command_name: str, component_id: int, snapshot: str):
        super().__init__(command_name)
        self._command_name = command_name
        self._component_id = component_id
        self._snapshot     = snapshot

    def execute(self):
        doc = App.caeDocument()
        if doc is None:
            return None
        try:
            groups = doc.pluginCaeComponents.groups()
            comp = groups[CAEComponentGroupUIDs.BEAM_HINGES].collection[self._component_id]
        except Exception as e:
            print(f'[BeamHingeEditUndo] Could not retrieve component id={self._component_id}: {e}')
            return None
        current_snapshot = comp.save()
        comp.restore(self._snapshot)
        comp.changed = True
        doc.commitChanges()
        doc.dirty = True
        return _BeamHingeEditUndo(self._command_name, self._component_id, current_snapshot)


class BeamHingeCommandEdit(AsCommand):
    """Command for editing any BeamHinge subtype via its own dialog."""

    COMMAND_NAME = 'EditBeamHinge'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._dlg = None
        self._comp = None
        self._before_snapshot: str = None
        self._headless = False
        self._error = ''

    def create(self):
        return BeamHingeCommandEdit()

    # ------------------------------------------------------------------
    # AsCommand interface
    # ------------------------------------------------------------------

    def execute(self, initial_options: str = ''):
        doc = App.caeDocument()
        if doc is None:
            self._error = 'No active CAE document.'
            self.terminate(abort=True)
            return

        try:
            opts = json.loads(initial_options)
            component_id = int(opts['component_id'])
        except Exception as e:
            self._error = f'Invalid input: {e}'
            self.terminate(abort=True)
            return

        try:
            groups = doc.pluginCaeComponents.groups()
            self._comp = groups[CAEComponentGroupUIDs.BEAM_HINGES].collection[component_id]
        except Exception as e:
            self._error = f'Hinge component with id={component_id} not found: {e}'
            self.terminate(abort=True)
            return

        # Headless mode only when actual edit parameters are provided beyond component_id
        headless_keys = ('name', 'anchor', 'offset', 'dofs_I', 'dofs_J', 'dofs')
        has_changes = any(k in opts for k in headless_keys)
        self._headless = has_changes

        if has_changes:
            self._before_snapshot = self._comp.save()
            try:
                self._apply_opts(opts)
            except Exception as e:
                self._error = str(e)
                self._comp.restore(self._before_snapshot)
                self.terminate(abort=True)
                return
            self._comp.changed = True
            doc.commitChanges()
            doc.dirty = True
            self.terminate(abort=False)
            return

        # GUI mode — dispatch to the component's own dialog class
        dlg_cls = type(self._comp).dialog_class()
        self._dlg = dlg_cls(
            component=self._comp,
            parent=QtWidgets.QApplication.activeWindow(),
            is_new=False,
        )
        self._dlg.setModal(True)
        self._dlg.accepted.connect(self._on_accept)
        self._dlg.rejected.connect(self._on_reject)
        self._dlg.show()

    def terminate(self, abort: bool):
        self._cleanup_dialog()
        output = ''
        if self._headless:
            output = json.dumps({'status': not abort, 'error': self._error if abort else ''})
        if abort:
            self.emitCommandExiting(AsCommandExitingArgs(True, None, output))
        else:
            undo_cmd = _BeamHingeEditUndo(
                self.COMMAND_NAME, int(self._comp.id), self._before_snapshot
            )
            self.emitCommandExiting(AsCommandExitingArgs(False, undo_cmd, output))

    # ------------------------------------------------------------------
    # Dialog callbacks
    # ------------------------------------------------------------------

    def _on_accept(self):
        doc = App.caeDocument()
        if doc is None:
            self.terminate(abort=True)
            return
        self._before_snapshot = self._comp.save()
        self._dlg.apply_to(self._comp)
        self._comp.changed = True
        doc.commitChanges()
        doc.dirty = True
        self.terminate(abort=False)

    def _on_reject(self):
        self.terminate(abort=True)

    # ------------------------------------------------------------------
    # Headless field application
    # ------------------------------------------------------------------

    def _apply_opts(self, opts: dict):
        from opspro.Hinges.beam_hinge import HingeAnchor
        from opspro.Hinges.beam_end_release import BeamEndRelease
        from opspro.Hinges.beam_rotational_hinge import BeamRotationalHinge
        from opspro.Hinges.beam_shear_hinge import BeamShearHinge

        comp = self._comp

        if 'name' in opts:
            comp.name = str(opts['name'])

        if 'anchor' in opts:
            anchor = opts['anchor']
            if anchor not in HingeAnchor.ALL:
                raise ValueError(f"anchor must be one of {HingeAnchor.ALL}.")
            comp.anchor = anchor

        if 'offset' in opts:
            comp.offset = comp._qty_from_dict(opts['offset'])
            if float(comp.offset.to_base_units().magnitude) < 0.0:
                raise ValueError('offset must be >= 0.')

        if isinstance(comp, BeamEndRelease):
            if 'dofs_I' in opts:
                raw = opts['dofs_I']
                for k in BeamEndRelease.DOF_KEYS:
                    if k in raw:
                        comp.dofs_I[k] = bool(raw[k])
            if 'dofs_J' in opts:
                raw = opts['dofs_J']
                for k in BeamEndRelease.DOF_KEYS:
                    if k in raw:
                        comp.dofs_J[k] = bool(raw[k])

        elif isinstance(comp, (BeamRotationalHinge, BeamShearHinge)):
            if 'dofs' in opts:
                raw = opts['dofs']
                for k in comp.DOF_KEYS:
                    if k in raw:
                        comp.dofs[k] = bool(raw[k])

    # ------------------------------------------------------------------

    def _cleanup_dialog(self):
        if self._dlg is not None:
            self._dlg.deleteLater()
            self._dlg = None
