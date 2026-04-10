from PyMpc import (
    App,
    AsCommand,
    AsCommandExitingArgs,
    MpcCaeDocumentGeneralUndo,
)
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.Materials.material import Material
from PySide2 import QtWidgets
import json

class MaterialCommandNew(AsCommand):
    """
    Base command for creating any Material subtype.

    Subclasses must:
      - define COMMAND_NAME
      - override material_class() to return the concrete Material subclass
      - override create() to return a fresh instance of themselves

    The dialog to open is obtained via material_class().dialog_class(), so no
    dialog type needs to be hard-coded here.
    """

    def __init__(self):
        super().__init__(self.COMMAND_NAME)
        self._dlg = None       # dialog instance
        self._ret_args = None  # MpcCaeDocumentReturnArgs from addPluginCaeComponent
        self._new_id = -1
        self._error = ''
        self._headless = False

    # ------------------------------------------------------------------
    # Subclass contract
    # ------------------------------------------------------------------

    def material_class(self) -> Material:
        """Return the Material subclass this command creates."""
        raise NotImplementedError

    def create(self) -> AsCommand:
        raise NotImplementedError

    def _init_new_material(self, mat: Material):
        """Called after a fresh material instance is created. Subclasses can
        override to apply default values that are not part of the persisted
        state (e.g. a random visual material)."""
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
                print(f'[{self.COMMAND_NAME}] Error: failed to parse initial_options ({e}).')
                self.terminate(abort=True)
                return

            next_id = self._next_material_id(doc)
            mat = self.material_class()(id=next_id)
            self._init_new_material(mat)

            # Apply optional name
            if 'name' in opts:
                mat.name = str(opts['name'])

            # Apply optional material_parameters via save/restore
            params = opts.get('material_parameters')
            if params:
                try:
                    state = json.loads(mat.save())
                    state.update(params)
                    mat.restore(json.dumps(state))
                    # Ensure id/name are not overridden by params
                    mat.id = next_id
                    if 'name' in opts:
                        mat.name = str(opts['name'])
                except Exception as e:
                    self._error = f'Failed to apply material_parameters: {e}'
                    print(f'[{self.COMMAND_NAME}] Error: failed to apply material_parameters ({e}).')
                    self.terminate(abort=True)
                    return

            self._new_id = next_id
            self._ret_args = doc.addPluginCaeComponent(mat)
            doc.commitChanges()
            doc.dirty = True
            self.terminate(abort=False)
            return

        # GUI mode: show dialog
        mat_cls = self.material_class()
        dlg_cls = mat_cls.dialog_class()
        proto_mat = mat_cls()  # empty instance just to pass to dialog for population/defaults
        self._init_new_material(proto_mat)
        self._dlg = dlg_cls(material=proto_mat, parent=QtWidgets.QApplication.activeWindow(), is_new=True)
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
            print(f'[{self.COMMAND_NAME}] Error: document became unavailable.')
            self.terminate(abort=True)
            return

        next_id = self._next_material_id(doc)
        self._new_id = next_id
        mat = self.material_class()(id=next_id)
        self._dlg.apply_to(mat)

        self._ret_args = doc.addPluginCaeComponent(mat)
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
    def _next_material_id(doc) -> int:
        """Return max(existing material IDs) + 1, or 1 if the group is empty."""
        try:
            groups = doc.pluginCaeComponents.groups()
            group_id = CAEComponentGroupUIDs.MATERIALS
            if group_id not in groups:
                return 1
            coll = groups[group_id].collection
            return coll.getlastkey(0) + 1
        except Exception as e:
            print(f'[MaterialCommandNew] Warning: could not compute next ID ({e}); defaulting to 1.')
            return 1
