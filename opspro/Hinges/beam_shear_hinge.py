from .beam_hinge import BeamHinge, HingeAnchor


# Default: no DOF active
_DEFAULT_SHEAR_DOFS = {'Vy': False, 'Vz': False}


class BeamShearHinge(BeamHinge):
    """
    Nonlinear shear spring hinge along a beam.

    A zero-length shear spring is placed at the anchor location
    of the assigned beam edge.

    Attributes
    ----------
    anchor : str
        Placement anchor (HingeAnchor: I, J, IJ, C).  Defaults to C.
    offset : pint.Quantity
        Distance from the anchor (always >= 0; typically 0 for C).
    dofs : dict[str, bool]
        Which shear DOFs the spring acts on.
        Keys: 'Vy' (shear in local-y), 'Vz' (shear in local-z).
    """

    DOF_KEYS = ('Vy', 'Vz')

    def __init__(self, id=1, name='BeamShearHinge'):
        super().__init__(id, name)
        # Shear hinges default to centre (C), offset 0
        self.anchor = HingeAnchor.C
        self.dofs: dict = dict(_DEFAULT_SHEAR_DOFS)

    # ------------------------------------------------------------------
    # MpcPluginCaeComponent interface
    # ------------------------------------------------------------------

    def className(self):
        return 'BeamShearHinge'

    def description(self):
        return 'Nonlinear shear spring hinge along a beam'

    @classmethod
    def dialog_class(cls):
        from opspro.Hinges.beam_shear_hinge_dialog import BeamShearHingeDialog
        return BeamShearHingeDialog

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def _to_dict(self) -> dict:
        d = super()._to_dict()
        d['dofs'] = dict(self.dofs)
        return d

    def _from_dict(self, data: dict):
        super()._from_dict(data)
        saved = data.get('dofs', {})
        self.dofs = {k: bool(saved.get(k, False)) for k in self.DOF_KEYS}
