"""
material_assign_undo.py
-----------------------
Swap-based AsUndoRedoCommand for material assignment and unassignment,
shared by MaterialCommandAssign and MaterialCommandUnassign.
"""

from __future__ import annotations

from PyMpc import App, AsUndoRedoCommand

from opspro.utils import AssignDiff


# ---------------------------------------------------------------------------
# MaterialAssignUndo  — swap-based undo/redo (mirrors _MaterialEditUndo)
# ---------------------------------------------------------------------------

class MaterialAssignUndo(AsUndoRedoCommand):
    """
    Swap-based undo/redo for a material assignment or unassignment.

    Stores the diff JSON and an *invert* flag.  Each call to execute():
      1. Applies the diff in the current direction (forward or inverse).
      2. Returns a new MaterialAssignUndo with the opposite direction,
         so that the next undo/redo is always correct.
    """

    def __init__(self, command_name: str, diff_json: str, *, invert: bool):
        super().__init__(command_name)
        self._command_name = command_name
        self._diff_json    = diff_json
        self._invert       = invert   # True → apply inverse diff on execute()

    def execute(self) -> 'MaterialAssignUndo | None':
        App.processEvents()
        try:
            diff = AssignDiff.from_json(self._diff_json)
            diff.apply(invert=self._invert)
        except Exception as e:
            direction = 'undo' if self._invert else 'redo'
            print(f'[MaterialAssignUndo] Error during {direction}: {e}')
            return None
        # Return the inverse command so the next undo/redo is correct
        return MaterialAssignUndo(
            self._command_name, self._diff_json, invert=not self._invert
        )
