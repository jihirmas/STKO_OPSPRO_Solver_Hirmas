from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
    MpcCaeDocumentGeneralUndo,
)
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.Sections.beam_section import BeamSection
from opspro.Sections.presets import registry as section_registry
from opspro.parameters.ParameterManager import ParameterManager
from PySide2 import QtWidgets
import json

"""
MCP_COMMAND_METADATA_START
{
    "name": "new_beam_section",
    "description": "Creates a new beam cross-section in the active document. Choose a preset_module (shape type) and either a named preset or 'user' for custom dimensions. When preset_name is a named preset (e.g. 'IPE 200'), the section uses catalogue values and section_parameters is ignored. When preset_name is 'user', section_parameters supplies the dimensions; omitted parameters keep the module's defaults. For the 'Custom' module (user-defined properties), section_parameters keys are: area, Iyy, Izz, J, alphaY, alphaZ, centroidY, centroidZ. For geometric modules, keys are the module's dimension names (e.g. h, b, tw, tf for I Section). Physical quantities use {magnitude, unit} format. Requires an active CAE document.",
    "command": "NewBeamSection",
    "inputSchema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Optional display name for the new section"
            },
            "preset_module": {
                "type": "string",
                "description": "Section shape type. One of: Rectangular, Hollow Rectangular, Circular, Hollow Circular, I Section, I HP Section, I S Section, C Channel, C MC Channel, T Section, L Angle, L U Angle, Custom"
            },
            "preset_name": {
                "type": "string",
                "description": "Preset designation (e.g. 'IPE 200') or 'user' for custom dimensions. Use list_section_presets to discover available names."
            },
            "section_parameters": {
                "type": "object",
                "description": "Optional dimension overrides when preset_name is 'user' (or module is 'Custom'). Keys depend on the module (e.g. {h, b, tw, tf} for I Section). Values are {magnitude, unit} quantities. Omitted keys keep module defaults."
            }
        },
        "required": ["preset_module", "preset_name"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status":       {"type": "boolean", "description": "true on success, false on failure"},
            "component_id": {"type": "integer", "description": "ID of the newly created section, or -1 on failure"},
            "error":        {"type": "string",  "description": "Error message if status is false, empty string on success"}
        }
    }
}
MCP_COMMAND_METADATA_END
"""


class BeamSectionCommandNew(AsCommand):
    """Command that creates a new BeamSection."""

    COMMAND_NAME = 'NewBeamSection'

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._dlg = None
        self._ret_args = None
        self._new_id = -1
        self._error = ''
        self._headless = False

    def create(self):
        return BeamSectionCommandNew()

    # ------------------------------------------------------------------
    # Subclass hook
    # ------------------------------------------------------------------

    def _init_new_section(self, section: BeamSection):
        """Called after a fresh BeamSection is created. Override to apply
        default values (e.g. randomized visual material)."""
        try:
            import PyMpc
            visual_mat = PyMpc.FxMaterial()
            PyMpc.randomizeFxMaterialProperty(visual_mat)
            section.visual_material = visual_mat
        except Exception:
            pass

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
            try:
                opts = json.loads(initial_options)
            except Exception as e:
                self._error = f'Invalid JSON input: {e}'
                self.terminate(abort=True)
                return

            preset_module = opts.get('preset_module', '')
            preset_name = opts.get('preset_name', 'user')

            if not preset_module:
                self._error = 'preset_module is required.'
                self.terminate(abort=True)
                return

            if section_registry.get_preset_module(preset_module) is None:
                self._error = f"Unknown preset_module '{preset_module}'."
                self.terminate(abort=True)
                return

            next_id = self._next_section_id(doc)
            section = BeamSection(id=next_id)
            self._init_new_section(section)

            if 'name' in opts:
                section.name = str(opts['name'])

            # Use set_preset to initialize parameters from preset or CUSTOM defaults
            section.set_preset(preset_module, preset_name)

            # Apply optional parameter overrides
            raw_params = opts.get('section_parameters')
            if raw_params and isinstance(raw_params, dict):
                ureg = ParameterManager._unit_registry
                for k, v in raw_params.items():
                    if k in section.parameters:
                        section.parameters[k] = BeamSection._qty_from_dict(v)

            self._new_id = next_id
            self._ret_args = doc.addPluginCaeComponent(section)
            doc.commitChanges()
            doc.dirty = True
            self.terminate(abort=False)
            return

        # GUI mode: show dialog
        from opspro.Sections.beam_section_dialog import BeamSectionDialog
        proto = BeamSection()
        self._init_new_section(proto)
        self._dlg = BeamSectionDialog(section=proto, parent=QtWidgets.QApplication.activeWindow(), is_new=True)
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
                'error': self._error if abort else ''
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

        next_id = self._next_section_id(doc)
        self._new_id = next_id
        section = BeamSection(id=next_id)
        self._dlg.apply_to(section)

        self._ret_args = doc.addPluginCaeComponent(section)
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
    def _next_section_id(doc) -> int:
        """Return max(existing section IDs) + 1, or 1 if the group is empty."""
        try:
            groups = doc.pluginCaeComponents.groups()
            group_id = CAEComponentGroupUIDs.SECTIONS
            if group_id not in groups:
                return 1
            coll = groups[group_id].collection
            return coll.getlastkey(0) + 1
        except Exception as e:
            print(f'[BeamSectionCommandNew] Warning: could not compute next ID ({e}); defaulting to 1.')
            return 1
