from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
    MpcCaeDocumentGeneralUndo,
)
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.Hinges.beam_end_release import BeamEndRelease
from PySide2 import QtWidgets
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "new_beam_end_release",
    "description": "Creates a new Beam End Release component in the active document. A beam end release sets specified translational and/or rotational DOFs free at the I-end, J-end, or both ends of an assigned beam edge. Anchor controls which end(s) to apply the release; offset is a non-negative length measured from the anchor along the beam axis. dofs_I and dofs_J each specify which of the six DOFs (Ux, Uy, Uz, Rx, Ry, Rz) are released at their respective end; when anchor is 'I' only dofs_I is used, when 'J' only dofs_J, when 'IJ' both. Requires an active CAE document.",
    "command": "NewBeamEndRelease",
    "inputSchema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Optional display name for the new component"
            },
            "anchor": {
                "type": "string",
                "enum": ["I", "J", "IJ"],
                "description": "Reference end(s): 'I' (near end), 'J' (far end), 'IJ' (both ends). Default: 'IJ'."
            },
            "offset": {
                "type": "object",
                "description": "Optional non-negative distance from the anchor along the beam axis. Format: {magnitude, unit} (e.g. {\"magnitude\": 0.3, \"unit\": \"m\"}). Default: 0 m.",
                "properties": {
                    "magnitude": {"type": "number"},
                    "unit":      {"type": "string"}
                }
            },
            "dofs_I": {
                "type": "object",
                "description": "DOFs to release at the I-end (local frame). Keys: Ux (translation along local-x), Uy (translation along local-y), Uz (translation along local-z), Rx (rotation about local-x), Ry (rotation about local-y), Rz (rotation about local-z). true = DOF is released; false = DOF is continuous (no release). Omitted keys default to false.",
                "properties": {
                    "Ux": {"type": "boolean"}, "Uy": {"type": "boolean"}, "Uz": {"type": "boolean"},
                    "Rx": {"type": "boolean"}, "Ry": {"type": "boolean"}, "Rz": {"type": "boolean"}
                }
            },
            "dofs_J": {
                "type": "object",
                "description": "DOFs to release at the J-end (local frame). Same keys as dofs_I. true = DOF is released; false = DOF is continuous (no release). Omitted keys default to false.",
                "properties": {
                    "Ux": {"type": "boolean"}, "Uy": {"type": "boolean"}, "Uz": {"type": "boolean"},
                    "Rx": {"type": "boolean"}, "Ry": {"type": "boolean"}, "Rz": {"type": "boolean"}
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


class BeamEndReleaseCommandNew(AsCommand):
    """Command that creates a new BeamEndRelease component."""

    COMMAND_NAME = 'NewBeamEndRelease'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._dlg = None
        self._ret_args = None
        self._new_id = -1
        self._error = ''
        self._headless = False

    def create(self):
        return BeamEndReleaseCommandNew()

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
            comp = BeamEndRelease(id=next_id)

            if 'name' in opts:
                comp.name = str(opts['name'])

            if 'anchor' in opts:
                anchor = opts['anchor']
                if anchor not in ('I', 'J', 'IJ'):
                    self._error = "anchor must be one of: 'I', 'J', 'IJ'."
                    self.terminate(abort=True)
                    return
                comp.anchor = anchor

            if 'offset' in opts:
                try:
                    comp.offset = BeamEndRelease._qty_from_dict(opts['offset'])
                except Exception as e:
                    self._error = f'Invalid offset: {e}'
                    self.terminate(abort=True)
                    return
                if float(comp.offset.to_base_units().magnitude) < 0.0:
                    self._error = 'offset must be >= 0.'
                    self.terminate(abort=True)
                    return

            dofs_I_raw = opts.get('dofs_I', {})
            dofs_J_raw = opts.get('dofs_J', {})
            for key in BeamEndRelease.DOF_KEYS:
                comp.dofs_I[key] = bool(dofs_I_raw.get(key, False))
                comp.dofs_J[key] = bool(dofs_J_raw.get(key, False))

            if not any(comp.dofs_I.values()) and not any(comp.dofs_J.values()):
                self._error = 'At least one DOF must be released.'
                self.terminate(abort=True)
                return

            self._new_id = next_id
            self._ret_args = doc.addPluginCaeComponent(comp)
            doc.commitChanges()
            doc.dirty = True
            self.terminate(abort=False)
            return

        # ---- GUI mode --------------------------------------------------
        from opspro.Hinges.beam_end_release_dialog import BeamEndReleaseDialog
        self._dlg = BeamEndReleaseDialog(
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
                'status': not abort,
                'component_id': self._new_id,
                'error': self._error if abort else '',
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
        comp = BeamEndRelease(id=next_id)
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
            groups = doc.pluginCaeComponents.groups()
            group_id = CAEComponentGroupUIDs.BEAM_HINGES
            if group_id not in groups:
                return 1
            coll = groups[group_id].collection
            return coll.getlastkey(0) + 1
        except Exception as e:
            print(f'[{BeamEndReleaseCommandNew.COMMAND_NAME}] Warning: could not compute next ID ({e}); defaulting to 1.')
            return 1
