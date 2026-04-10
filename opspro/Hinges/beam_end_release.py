from .beam_hinge import BeamHinge, HingeAnchor

# Default released-DOF state: all False (nothing released)
_DEFAULT_DOFS = {
    'Ux': False,
    'Uy': False,
    'Uz': False,
    'Rx': False,
    'Ry': False,
    'Rz': False,
}


class BeamEndRelease(BeamHinge):
    """
    Beam end-release component.

    Specifies which translational / rotational DOFs are released
    (set free) at the near end (I), far end (J), or both ends of
    an assigned beam edge.

    Attributes
    ----------
    end : str
        Which end to apply the release: 'I', 'J', or 'both'.
    dofs_I : dict[str, bool]
        Released DOFs at the I-end.
        Keys: 'Ux', 'Uy', 'Uz', 'Rx', 'Ry', 'Rz'.
    dofs_J : dict[str, bool]
        Released DOFs at the J-end.
        Keys: same as dofs_I.
        Ignored when end == 'I'.
    """

    DOF_KEYS = ('Ux', 'Uy', 'Uz', 'Rx', 'Ry', 'Rz')

    def __init__(self, id=1, name='BeamEndRelease'):
        super().__init__(id, name)
        # BeamEndRelease defaults to both ends (IJ), offset 0
        self.anchor = HingeAnchor.IJ
        self.dofs_I: dict = dict(_DEFAULT_DOFS)
        self.dofs_J: dict = dict(_DEFAULT_DOFS)

    # ------------------------------------------------------------------
    # MpcPluginCaeComponent interface
    # ------------------------------------------------------------------

    def className(self):
        return 'BeamEndRelease'

    def description(self):
        return 'Releases specified DOFs at beam end(s)'

    @classmethod
    def dialog_class(cls):
        from opspro.Hinges.beam_end_release_dialog import BeamEndReleaseDialog
        return BeamEndReleaseDialog

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def _to_dict(self) -> dict:
        d = super()._to_dict()
        d['dofs_I'] = dict(self.dofs_I)
        d['dofs_J'] = dict(self.dofs_J)
        return d

    def _from_dict(self, data: dict):
        super()._from_dict(data)
        saved_I = data.get('dofs_I', {})
        saved_J = data.get('dofs_J', {})
        self.dofs_I = {k: bool(saved_I.get(k, False)) for k in self.DOF_KEYS}
        self.dofs_J = {k: bool(saved_J.get(k, False)) for k in self.DOF_KEYS}

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def get_active_dofs(self, end: str) -> dict:
        """Return the dofs dict for the requested end ('I' or 'J')."""
        return self.dofs_I if end == 'I' else self.dofs_J
