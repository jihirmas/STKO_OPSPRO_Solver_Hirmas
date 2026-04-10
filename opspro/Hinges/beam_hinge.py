from PyMpc import MpcPluginCaeComponent
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.parameters.ParameterManager import ParameterManager
import pint
import json


# ---------------------------------------------------------------------------
# Anchor constants
# ---------------------------------------------------------------------------

# (has_I, has_C, has_J) bitmask for each anchor value
_ANCHOR_BITS = {
    'I':  (True,  False, False),
    'C':  (False, True,  False),
    'J':  (False, False, True),
    'IJ': (True,  False, True),
}


class _AnchorKey:
    """
    Conflict key for hinge assignment, based on bitwise overlap.

    Stores anchor presence as a (has_I, has_C, has_J) bool tuple.
    Two keys conflict when they share at least one True position:

        _AnchorKey('I')  == _AnchorKey('IJ')  → True  (both have I)
        _AnchorKey('J')  == _AnchorKey('IJ')  → True  (both have J)
        _AnchorKey('I')  == _AnchorKey('J')   → False
        _AnchorKey('C')  == _AnchorKey('IJ')  → False

    Hash is constant because equality is non-transitive (I==IJ, J==IJ,
    yet I!=J), so no consistent non-trivial hash exists.
    """
    __slots__ = ('_bits',)

    def __init__(self, anchor: str):
        self._bits = _ANCHOR_BITS.get(anchor, (False, False, False))

    def __eq__(self, other):
        if isinstance(other, _AnchorKey):
            return any(a and b for a, b in zip(self._bits, other._bits))
        return NotImplemented

    def __hash__(self):
        return 0

    def __repr__(self):
        return f'_AnchorKey({self._bits!r})'


class HingeAnchor:
    """
    Symbolic constants for the hinge anchor position along the beam edge.

    Convention for `offset` (always >= 0):
        I  — offset measured from node-I in the direction I → J
        J  — offset measured from node-J in the direction J → I (i.e. inward)
        IJ — shorthand for "one hinge at I and one at J", each with the same
             offset measured from their respective end (I→J and J→I)
        C  — centre of the element; offset is always 0 in this case

    In all cases the offset is a non-negative physical length (pint.Quantity).
    """
    I  = 'I'
    J  = 'J'
    IJ = 'IJ'
    C  = 'C'

    ALL = (I, J, IJ, C)


class BeamHinge(MpcPluginCaeComponent):
    """
    Abstract base class for all beam hinge / end-release components.

    Subclasses must implement:
        - className()
        - description()
        - dialog_class()   (classmethod)
        - _to_dict()
        - _from_dict(data)

    Placement along the beam is described by two attributes:

    anchor : str  (one of HingeAnchor.ALL)
        Reference point from which the offset is measured.
        See HingeAnchor for the full sign convention.

    offset : pint.Quantity  (length, always >= 0)
        Physical distance from the anchor.
        - anchor == C  → offset must be 0 (centre, no shift makes sense)
        - anchor == IJ → same offset applied symmetrically at both ends
    """

    def __init__(self, id=1, name='BeamHinge'):
        super().__init__(id, name)
        ureg = ParameterManager._unit_registry
        self.anchor: str           = HingeAnchor.IJ
        self.offset: pint.Quantity = 0.0 * ureg.m

    # ------------------------------------------------------------------
    # MpcPluginCaeComponent interface
    # ------------------------------------------------------------------

    def componentGroupID(self):
        return CAEComponentGroupUIDs.BEAM_HINGES

    def className(self):
        raise NotImplementedError

    def description(self):
        raise NotImplementedError

    @classmethod
    def dialog_class(cls):
        """Return the QDialog class used to create/edit this hinge type."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def save(self):
        """Serialize plugin state to a JSON string."""
        try:
            return json.dumps(self._to_dict())
        except Exception as e:
            print(f'Error serializing {self.className()} "{self.name}": {e}')
            import traceback
            print(traceback.format_exc())
            return ''

    def restore(self, state):
        """Restore plugin state from a JSON string produced by save()."""
        if not state:
            return
        try:
            data = json.loads(state)
        except Exception as e:
            print(f'Error parsing state for {self.className()} "{self.name}": {e}')
            return
        try:
            self._from_dict(data)
        except Exception as e:
            print(f'Error restoring {self.className()} "{self.name}" from state: {e}')
            import traceback
            print(traceback.format_exc())

    # ------------------------------------------------------------------
    # Subclass hooks
    # ------------------------------------------------------------------

    def _to_dict(self) -> dict:
        """Return a JSON-serializable dict of all state.
        Subclasses should call super()._to_dict() and extend the result."""
        return {
            'ID':      int(self.id),
            'name':    self.name,
            'changed': self.changed,
            'anchor':  self.anchor,
            'offset':  self._qty_to_dict(self.offset),
        }

    def _from_dict(self, data: dict):
        """Restore state from a dict produced by _to_dict().
        Subclasses should call super()._from_dict(data) first."""
        self.id      = data.get('ID',      self.id)
        self.name    = data.get('name',    self.name)
        self.changed = data.get('changed', self.changed)
        self.anchor  = data.get('anchor',  self.anchor)
        raw_off = data.get('offset', None)
        if raw_off is not None:
            self.offset = self._qty_from_dict(raw_off)

    # ------------------------------------------------------------------
    # Quantity helpers (shared with subclasses)
    # ------------------------------------------------------------------

    @staticmethod
    def _qty_to_dict(qty) -> dict:
        if isinstance(qty, pint.Quantity):
            return {'magnitude': float(qty.magnitude), 'unit': str(qty.units)}
        return {'magnitude': float(qty), 'unit': 'm'}

    @staticmethod
    def _qty_from_dict(data) -> pint.Quantity:
        ureg = ParameterManager._unit_registry
        if isinstance(data, dict):
            return ureg.Quantity(data['magnitude'], data['unit'])
        elif isinstance(data, (int, float)):
            return float(data) * ureg.m
        return 0.0 * ureg.m

    # ------------------------------------------------------------------

    def assignment_key(self):
        """
        Conflict key for AssignDiff.  Returns an _AnchorKey whose __eq__
        uses set intersection: IJ conflicts with I and J individually,
        while I, J, and C are mutually non-conflicting.
        """
        return _AnchorKey(self.anchor)

    def __repr__(self):
        return (
            f'{self.className()}(id={self.id}, name={self.name!r}, '
            f'anchor={self.anchor!r}, offset={self.offset})'
        )
