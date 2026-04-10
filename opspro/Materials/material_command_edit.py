from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
    AsUndoRedoCommand
)
from opspro.Materials.material import Material
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
import json
from PySide2 import QtWidgets

"""
MCP_COMMAND_METADATA_START
{
    "name": "edit_material",
    "description": "Edits an existing material in the active document, identified by its component_id. The optional material_parameters object works identically to new_steel_material / new_concrete_material: supply only the fields you want to change; omitted fields keep their current values. Physical quantities use the format {magnitude: <float>, unit: <string>}. To change a material to a standard preset, call list_material_presets first to get the full set of parameters for that preset, then pass them here. Requires an active CAE document.",
    "command": "EditMaterial",
    "inputSchema": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "ID of the material to edit"
            },
            "name": {
                "type": "string",
                "description": "Optional: new display name for the material"
            },
            "material_parameters": {
                "type": "object",
                "description": "Optional partial or full set of material parameters to update. For steel: E, nu, rho, nonlinear, sigma_y, sigma_u, epsilon_u, fracture, preset_standard, preset_designation. For concrete: E, nu, rho, nonlinear, auto_fracture_energy, fcp, ft, Gt, Gc, preset_standard, preset_designation. Physical quantities use {magnitude, unit}. Omitted fields keep their current values."
            }
        },
        "required": ["component_id"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status": { "type": "boolean", "description": "true on success, false on failure" },
            "error":  { "type": "string",  "description": "Error message if status is false, empty string on success" }
        }
    }
}
MCP_COMMAND_METADATA_END
"""

class _MaterialEditUndo(AsUndoRedoCommand):
    """
    Swap-based undo/redo for a Material edit (mirrors MpcCmdEditPropertyUndo).

    Each call to execute() captures the current material state, restores the
    stored snapshot, then returns a new _MaterialEditUndo holding the just-
    captured state so that the next call undoes/redoes correctly.
    """

    def __init__(self, command_name: str, component_id: int, snapshot: str):
        super().__init__(command_name)
        self._command_name = command_name
        self._component_id = component_id
        self._snapshot = snapshot   # material state to restore on next undo/redo

    def execute(self):
        doc = App.caeDocument()
        if doc is None:
            return None
        try:
            groups = doc.pluginCaeComponents.groups()
            mat : Material = groups[CAEComponentGroupUIDs.MATERIALS].collection[self._component_id]
        except Exception as e:
            print(f'[MaterialEditUndo] Could not retrieve material id={self._component_id}: {e}')
            return None

        current_snapshot = mat.save()   # capture state before overwriting
        mat.restore(self._snapshot)     # apply stored snapshot
        mat.changed = True
        doc.commitChanges()
        doc.dirty = True

        # Return inverse command so redo/undo always works
        return _MaterialEditUndo(self._command_name, self._component_id, current_snapshot)

class MaterialCommandEdit(AsCommand):
    """
    Generic command for editing any Material subtype.

    The dialog to open is obtained via type(material).dialog_class(), so it
    works for every concrete Material subclass without specialisation.

    ``initial_options`` passed to ``execute()`` must be a JSON string with at
    least the key ``"component_id"`` (int) identifying the material to edit.
    """

    COMMAND_NAME = 'EditMaterial'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._dlg = None              # dialog instance
        self._mat : Material = None   # material being edited
        self._before_snapshot : str = None  # JSON snapshot taken before edit, for undo
        self._headless = False
        self._error = ''

    def create(self) -> AsCommand:
        return MaterialCommandEdit()

    # ------------------------------------------------------------------
    # AsCommand interface
    # ------------------------------------------------------------------

    def execute(self, initial_options: str = ''):
        doc = App.caeDocument()
        if doc is None:
            self._error = 'No active CAE document.'
            print(f'[{self.COMMAND_NAME}] Error: no active CAE document.')
            self.terminate(abort=True)
            return

        try:
            opts = json.loads(initial_options)
            component_id = int(opts['component_id'])
        except Exception as e:
            self._error = f'Invalid input: {e}'
            print(f'[{self.COMMAND_NAME}] Error: failed to parse initial_options ({e}).')
            self.terminate(abort=True)
            return

        try:
            groups = doc.pluginCaeComponents.groups()
            self._mat = groups[CAEComponentGroupUIDs.MATERIALS].collection[component_id]
        except Exception as e:
            self._error = f'Material with id={component_id} not found: {e}'
            print(f'[{self.COMMAND_NAME}] Error: could not retrieve material id={component_id} ({e}).')
            self.terminate(abort=True)
            return

        # Headless mode only when actual edit parameters are provided beyond component_id
        has_changes = (opts.get('material_parameters') is not None) or ('name' in opts)
        self._headless = has_changes

        if has_changes:
            # Headless path
            self._before_snapshot = self._mat.save()

            # Apply optional name
            if 'name' in opts:
                self._mat.name = str(opts['name'])

            # Apply optional material_parameters via save/restore merge
            params = opts.get('material_parameters')
            if params:
                try:
                    state = json.loads(self._mat.save())
                    state.update(params)
                    self._mat.restore(json.dumps(state))
                    # restore() may overwrite name/id from snapshot — re-apply
                    self._mat.id = component_id
                    if 'name' in opts:
                        self._mat.name = str(opts['name'])
                except Exception as e:
                    self._error = f'Failed to apply material_parameters: {e}'
                    print(f'[{self.COMMAND_NAME}] Error: {self._error}')
                    # rollback
                    self._mat.restore(self._before_snapshot)
                    self.terminate(abort=True)
                    return

            self._mat.changed = True
            doc.commitChanges()
            doc.dirty = True
            self.terminate(abort=False)
            return

        # GUI mode: show dialog pre-populated with current material state
        dlg_cls = type(self._mat).dialog_class()
        self._dlg = dlg_cls(material=self._mat, parent=QtWidgets.QApplication.activeWindow())
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
            undo_cmd = _MaterialEditUndo(self.COMMAND_NAME, int(self._mat.id), self._before_snapshot)
            self.emitCommandExiting(AsCommandExitingArgs(False, undo_cmd, output))

    # ------------------------------------------------------------------
    # Dialog callbacks
    # ------------------------------------------------------------------

    def _on_accept(self):
        doc = App.caeDocument()
        if doc is None:
            print(f'[{self.COMMAND_NAME}] Error: document became unavailable.')
            self.terminate(abort=True)
            return

        self._before_snapshot = self._mat.save()
        self._dlg.apply_to(self._mat)
        self._mat.changed = True
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

