"""
beam_shear_hinge_command_new.py
--------------------------------
Command that creates a new BeamShearHinge component.
"""

from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
    MpcCaeDocumentGeneralUndo,
)
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.Hinges.beam_shear_hinge import BeamShearHinge
from PySide2 import QtWidgets
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "new_beam_shear_hinge",
    "description": "Creates a new Beam Shear Hinge component in the active document. A beam shear hinge places a nonlinear shear spring at a specified location along an assigned beam edge. Anchor can be 'C' (centre), 'I' (near end), 'J' (far end), or 'IJ' (both ends). The spring can activate the local-y shear DOF (Vy), the local-z shear DOF (Vz), or both. When anchor is 'C', offset is always 0 and cannot be changed. Requires an active CAE document.",
    "command": "NewBeamShearHinge",
    "inputSchema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Optional display name for the new component"
            },
            "anchor": {
                "type": "string",
                "enum": ["C", "I", "J", "IJ"],
                "description": "Placement anchor: 'C' (centre, default), 'I' (near end), 'J' (far end), 'IJ' (both ends)."
            },
            "offset": {
                "type": "object",
                "description": "Optional non-negative distance from the anchor. Ignored (forced to 0) when anchor is 'C'. Format: {magnitude, unit} (e.g. {\"magnitude\": 0.2, \"unit\": \"m\"}). Default: 0 m.",
                "properties": {
                    "magnitude": {"type": "number"},
                    "unit":      {"type": "string"}
                }
            },
            "dofs": {
                "type": "object",
                "description": "Which shear DOFs the spring acts on (local frame). Keys: 'Vy' (shear along the local-y axis), 'Vz' (shear along the local-z axis). true = spring is active on that DOF; false = DOF is continuous (no spring). At least one must be true.",
                "properties": {
                    "Vy": {"type": "boolean"},
                    "Vz": {"type": "boolean"}
                }
            }
        },
        "required": []
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status":       {"type": "boolean", "description": "true on success, false on failure"},
            "component_id": {"type": "integer", "description": "ID of the newly created component, or -1 on failure"},
            "error":        {"type": "string",  "description": "Error message if status is false, empty string on success"}
        }
    }
}
MCP_COMMAND_METADATA_END
"""

# Anchors that allow a non-zero offset (i.e. all except C)
_OFFSET_ANCHORS = ('I', 'J', 'IJ')


class BeamShearHingeCommandNew(AsCommand):
    """Command that creates a new BeamShearHinge component."""

    COMMAND_NAME = 'NewBeamShearHinge'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._dlg      = None
        self._ret_args = None
        self._new_id   = -1
        self._error    = ''
        self._headless = False

    def create(self):
        return BeamShearHingeCommandNew()

    # ------------------------------------------------------------------
    # AsCommand interface
    # ------------------------------------------------------------------

    def execute(self, initial_options: str = ''):
        self._headless = bool(initial_options)
        doc = App.caeDocument()
        if doc is None:
            self._error = 'No active CAE document.'
            print(f'[{self.COMMAND_NAME}] Error: no active CAE document.')
            self.terminate(abort=True)
            return

        if initial_options:
            # ---- Headless (MCP) mode -----------------------------------
            try:
                opts = json.loads(initial_options)
            except Exception as e:
                self._error = f'Invalid JSON input: {e}'
                self.terminate(abort=True)
                return

            next_id = self._next_id(doc)
            comp = BeamShearHinge(id=next_id)

            if 'name' in opts:
                comp.name = str(opts['name'])

            anchor = opts.get('anchor', comp.anchor)
            if anchor not in ('C', 'I', 'J', 'IJ'):
                self._error = "anchor must be one of: 'C', 'I', 'J', 'IJ'."
                self.terminate(abort=True)
                return
            comp.anchor = anchor

            if 'offset' in opts:
                if anchor == 'C':
                    # silently enforce offset=0 for centre anchor
                    pass
                else:
                    try:
                        comp.offset = BeamShearHinge._qty_from_dict(opts['offset'])
                    except Exception as e:
                        self._error = f'Invalid offset: {e}'
                        self.terminate(abort=True)
                        return
                    if float(comp.offset.to_base_units().magnitude) < 0.0:
                        self._error = 'offset must be >= 0.'
                        self.terminate(abort=True)
                        return

            dofs_raw = opts.get('dofs', {})
            for key in BeamShearHinge.DOF_KEYS:
                comp.dofs[key] = bool(dofs_raw.get(key, False))

            if not any(comp.dofs.values()):
                self._error = 'At least one shear DOF (Vy or Vz) must be active.'
                self.terminate(abort=True)
                return

            self._new_id   = next_id
            self._ret_args = doc.addPluginCaeComponent(comp)
            doc.commitChanges()
            doc.dirty = True
            self.terminate(abort=False)
            return

        # ---- GUI mode --------------------------------------------------
        from opspro.Hinges.beam_shear_hinge_dialog import BeamShearHingeDialog
        self._dlg = BeamShearHingeDialog(
            parent=QtWidgets.QApplication.activeWindow(),
            is_new=True,
        )
        self._dlg.setModal(True)
        self._dlg.accepted.connect(self._on_accept)
        self._dlg.rejected.connect(self._on_reject)
        self._dlg.show()

    def terminate(self, abort: bool):
        self._cleanup_dialog()
        output = ''
        if self._headless:
            output = json.dumps({
                'status':       not abort,
                'component_id': self._new_id,
                'error':        self._error if abort else '',
            })
        if abort:
            self.emitCommandExiting(AsCommandExitingArgs(True, None, output))
        else:
            undo_cmd = MpcCaeDocumentGeneralUndo(self.COMMAND_NAME, self._ret_args)
            self.emitCommandExiting(AsCommandExitingArgs(False, undo_cmd, output))

    # ------------------------------------------------------------------
    # Dialog callbacks
    # ------------------------------------------------------------------

    def _on_accept(self):
        doc = App.caeDocument()
        if doc is None:
            self._error = 'Document became unavailable.'
            self.terminate(abort=True)
            return

        next_id = self._next_id(doc)
        self._new_id = next_id
        comp = BeamShearHinge(id=next_id)
        self._dlg.apply_to(comp)

        self._ret_args = doc.addPluginCaeComponent(comp)
        doc.commitChanges()
        doc.dirty = True
        self.terminate(abort=False)

    def _on_reject(self):
        self.terminate(abort=True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _cleanup_dialog(self):
        if self._dlg is not None:
            self._dlg.deleteLater()
            self._dlg = None

    @staticmethod
    def _next_id(doc) -> int:
        """Return max(existing BEAM_HINGES component IDs) + 1, or 1 if empty."""
        try:
            groups   = doc.pluginCaeComponents.groups()
            group_id = CAEComponentGroupUIDs.BEAM_HINGES
            if group_id not in groups:
                return 1
            coll = groups[group_id].collection
            return coll.getlastkey(0) + 1
        except Exception as e:
            print(f'[{BeamShearHingeCommandNew.COMMAND_NAME}] Warning: could not compute next ID ({e}); defaulting to 1.')
            return 1
