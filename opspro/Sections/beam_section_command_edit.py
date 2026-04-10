from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
    AsUndoRedoCommand,
)
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.Sections.beam_section import BeamSection
from opspro.parameters.ParameterManager import ParameterManager
from PySide2 import QtWidgets
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "edit_beam_section",
    "description": "Edits an existing beam cross-section in the active document, identified by its component_id. Supply only the fields you want to change; omitted fields keep their current values. To change the shape, set preset_module and preset_name (and optionally section_parameters for 'user' presets). To change only dimensions on the current shape, supply section_parameters alone. To change to a catalogue preset (e.g. 'IPE 200'), call list_section_presets first to confirm the name, then pass preset_module and preset_name. Physical quantities use the format {magnitude: <float>, unit: <string>}. Requires an active CAE document.",
    "command": "EditBeamSection",
    "inputSchema": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "ID of the beam section to edit"
            },
            "name": {
                "type": "string",
                "description": "Optional: new display name for the section"
            },
            "preset_module": {
                "type": "string",
                "description": "Optional: new section shape type (e.g. 'I Section', 'Rectangular'). Use list_section_shapes for the full list."
            },
            "preset_name": {
                "type": "string",
                "description": "Optional: preset designation (e.g. 'IPE 200') or 'user' for custom dimensions. Required when preset_module is supplied."
            },
            "section_parameters": {
                "type": "object",
                "description": "Optional dimension overrides. Keys depend on the shape (e.g. {h, b, tw, tf} for I Section). Values are {magnitude, unit} quantities. Omitted keys keep current values."
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


class _BeamSectionEditUndo(AsUndoRedoCommand):
    """Swap-based undo/redo for a BeamSection edit."""

    def __init__(self, command_name: str, component_id: int, snapshot: str):
        super().__init__(command_name)
        self._command_name = command_name
        self._component_id = component_id
        self._snapshot = snapshot

    def execute(self):
        doc = App.caeDocument()
        if doc is None:
            return None
        try:
            groups = doc.pluginCaeComponents.groups()
            section: BeamSection = groups[CAEComponentGroupUIDs.SECTIONS].collection[self._component_id]
        except Exception as e:
            print(f'[BeamSectionEditUndo] Could not retrieve section id={self._component_id}: {e}')
            return None

        current_snapshot = section.save()
        section.restore(self._snapshot)
        section.changed = True
        doc.commitChanges()
        doc.dirty = True

        return _BeamSectionEditUndo(self._command_name, self._component_id, current_snapshot)


class BeamSectionCommandEdit(AsCommand):
    """Command for editing an existing BeamSection."""

    COMMAND_NAME = 'EditBeamSection'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._dlg = None
        self._section: BeamSection = None
        self._before_snapshot: str = None
        self._headless = False
        self._error = ''

    def create(self) -> AsCommand:
        return BeamSectionCommandEdit()

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
            self._section = groups[CAEComponentGroupUIDs.SECTIONS].collection[component_id]
        except Exception as e:
            self._error = f'Section with id={component_id} not found: {e}'
            print(f'[{self.COMMAND_NAME}] Error: {self._error}')
            self.terminate(abort=True)
            return

        has_headless_changes = (
            'name' in opts or
            'preset_module' in opts or
            'preset_name' in opts or
            opts.get('section_parameters') is not None
        )
        self._headless = has_headless_changes

        if has_headless_changes:
            self._before_snapshot = self._section.save()
            try:
                self._apply_opts(opts)
            except Exception as e:
                self._error = str(e)
                print(f'[{self.COMMAND_NAME}] Error: {self._error}')
                self._section.restore(self._before_snapshot)
                self.terminate(abort=True)
                return

            self._section.changed = True
            doc.commitChanges()
            doc.dirty = True
            self.terminate(abort=False)
            return

        # GUI mode
        from opspro.Sections.beam_section_dialog import BeamSectionDialog
        self._dlg = BeamSectionDialog(
            section=self._section,
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
            undo_cmd = _BeamSectionEditUndo(
                self.COMMAND_NAME, int(self._section.id), self._before_snapshot
            )
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

        self._before_snapshot = self._section.save()
        self._dlg.apply_to(self._section)
        self._section.changed = True
        doc.commitChanges()
        doc.dirty = True
        self.terminate(abort=False)

    def _on_reject(self):
        self.terminate(abort=True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _apply_opts(self, opts: dict):
        """Apply headless edit options to self._section. Raises on error."""
        from opspro.Sections.presets import registry as section_registry

        if 'name' in opts:
            self._section.name = str(opts['name'])

        preset_module = opts.get('preset_module')
        preset_name   = opts.get('preset_name')
        raw_params    = opts.get('section_parameters')

        if preset_module is not None:
            if section_registry.get_preset_module(preset_module) is None:
                known = section_registry.list_section_types()
                raise ValueError(f"Unknown preset_module '{preset_module}'. Available: {known}")
            if preset_name is None:
                preset_name = self._section.preset_name or 'user'
            self._section.set_preset(preset_module, preset_name)

        elif preset_name is not None:
            # Shape unchanged, just switch preset within the same module
            current_module = self._section.preset_module
            if current_module is None:
                raise ValueError("Cannot set preset_name without a preset_module when the section has no current shape.")
            self._section.set_preset(current_module, preset_name)

        # Apply dimension overrides
        if raw_params and isinstance(raw_params, dict):
            for k, v in raw_params.items():
                if k in self._section.parameters:
                    self._section.parameters[k] = BeamSection._qty_from_dict(v)

    def _cleanup_dialog(self):
        if self._dlg is not None:
            self._dlg.deleteLater()
            self._dlg = None
