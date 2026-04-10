from .beam_hinge import BeamHinge, HingeAnchor

# TODO: auto-calculation of backbones (from material and section)
# or: user-defined BackBone object!
# separate for Momement-Rotation and Shear-Displacement (even though the relative one could be the same)

# Default: no DOF active
_DEFAULT_ROT_DOFS = {'Ry': False, 'Rz': False}


class BeamRotationalHinge(BeamHinge):
    """
    Nonlinear rotational spring hinge at a beam end.

    A zero-length rotational spring is placed at the anchor location(s)
    of the assigned beam edge.

    Attributes
    ----------
    anchor : str
        Placement anchor (HingeAnchor: I, J, IJ).  Defaults to IJ.
    offset : pint.Quantity
        Distance from the anchor (always >= 0).
    dofs : dict[str, bool]
        Which rotational DOFs the spring acts on.
        Keys: 'Ry' (strong-axis bending), 'Rz' (weak-axis bending).
    """

    DOF_KEYS = ('Ry', 'Rz')

    def __init__(self, id=1, name='BeamRotationalHinge'):
        super().__init__(id, name)
        # Rotational hinges default to both ends (IJ), offset 0
        self.anchor = HingeAnchor.IJ
        self.dofs: dict = dict(_DEFAULT_ROT_DOFS)

    # ------------------------------------------------------------------
    # MpcPluginCaeComponent interface
    # ------------------------------------------------------------------

    def className(self):
        return 'BeamRotationalHinge'

    def description(self):
        return 'Nonlinear rotational spring hinge at beam end(s)'

    @classmethod
    def dialog_class(cls):
        from opspro.Hinges.beam_rotational_hinge_dialog import BeamRotationalHingeDialog
        return BeamRotationalHingeDialog

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
