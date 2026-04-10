
import functools
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
from PyMpc import MpcPluginCaeComponentAssignmentFlags
from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
import opspro.Hinges
import opspro.Materials
import opspro.Sections
import opspro.Settings
import opspro.UserNotes
import opspro.utils

@dataclass
class CAEComponentGroupItem:
    """
    Represents a single component group entry 
    (i.e. one item in the componentGroups list).
    """
    # The unique ID of the component group.
    id: str
    # The display name of the component group, shown in the UI (work-tree)
    displayName: str
    # A brief description of the component group, shown in the UI as a tooltip.
    description: str
    # The path to the icon for this component group, relative to the package root.
    icon: str
    # An optional mapping of specific component types to custom icons.
    classIconMap : Dict[str, str] = field(default_factory=dict)
    # The assignment flags for this component group, 
    # which determine how components in this group can be assigned to other entities in the model.
    assignmentFlags: MpcPluginCaeComponentAssignmentFlags = field(
        default_factory=lambda: MpcPluginCaeComponentAssignmentFlags.Nothing)
    # context menu commands for the collection.
    # This is a list of command names (strings) that will be added to the context menu 
    # when right-clicking on the collection in the work-tree.
    # Each item is a tuple of (command display name, command name)
    collectionCommands: List[Tuple[str, str]] = field(default_factory=list)
    # context menu commands for individual components in the collection.
    # This is a list of command names (strings) that will be added to the context menu
    # when right-clicking on a component in the work-tree.
    # Each item is a tuple of (command display name, command name)
    componentCommands: List[Tuple[str, str]] = field(default_factory=list)
    # command to invoke when the user double-clicks a component in the work-tree.
    # Empty string means no action on double-click.
    preferredComponentCommand: str = ''
    # command name to invoke for drag-and-drop assignment.
    # Empty string falls back to the generic built-in 'AssignPluginCaeComponent' command.
    assignCommand: str = ''
    # command name to invoke for drag-and-drop unassignment (Ctrl+drop).
    # Empty string falls back to the generic built-in 'UnassignPluginCaeComponent' command.
    unassignCommand: str = ''
    # Whether this component group should be hidden from the UI. 
    # Hidden groups are not shown in the work-tree and cannot be interacted with by the user, 
    # but they can still be used to store components that are managed entirely 
    # through commands or other logic.
    hidden: bool = False

class CAEComponentGroups:
    """
    This class represents the entire component groups section of the settings.
    It contains a list of ComponentGroupItem instances, which represent each individual component group entry.
    """
    groups : List[CAEComponentGroupItem] = [

        CAEComponentGroupItem(
            id = CAEComponentGroupUIDs.SETTINGS,
            displayName = "Settings",
            description = "General settings for the current document",
            icon = "assets/images/document_settings.ico",
            assignmentFlags = MpcPluginCaeComponentAssignmentFlags.Nothing,
            collectionCommands = [],
            componentCommands = [
                ('Edit', opspro.Settings.DocumentSettingsCommandEdit.COMMAND_NAME),
            ],
            preferredComponentCommand = opspro.Settings.DocumentSettingsCommandEdit.COMMAND_NAME
        ),

        CAEComponentGroupItem(
            id = CAEComponentGroupUIDs.MATERIALS,
            displayName = "Materials",
            description = "Constitutive models for structural analysis",
            icon = "assets/images/materials.ico",
            classIconMap = {
                'SteelMaterial':    'assets/images/material_steel.ico',
                'ConcreteMaterial': 'assets/images/material_concrete.ico',
                'SoilMaterial':     'assets/images/material_soil.ico',
                'ASDPlasticMaterial': 'assets/images/material_soil.ico',
            },
            assignmentFlags = MpcPluginCaeComponentAssignmentFlags.All,
            collectionCommands = [
                ('Add Steel...', opspro.Materials.SteelMaterialCommandNew.COMMAND_NAME),
                ('Add Concrete...', opspro.Materials.ConcreteMaterialCommandNew.COMMAND_NAME),
                ('Add Soil...', opspro.Materials.SoilMaterialCommandNew.COMMAND_NAME),
                ('Add ASD Plastic...', opspro.Materials.ASDPlasticMaterialCommandNew.COMMAND_NAME),
            ],
            componentCommands = [
                ('Remove', opspro.Materials.MaterialCommandDelete.COMMAND_NAME),
                ('Clone', opspro.Materials.MaterialCommandClone.COMMAND_NAME),
                ('Edit', opspro.Materials.MaterialCommandEdit.COMMAND_NAME),
                ('Assign to...', opspro.Materials.MaterialCommandAssign.COMMAND_NAME),
                ('Unassign from...', opspro.Materials.MaterialCommandUnassign.COMMAND_NAME),
                ('Select', 'MaterialCommandSelect'),
                ('Hide', 'MaterialCommandHide'),
                ('Show', 'MaterialCommandShow'),
            ],
            preferredComponentCommand = opspro.Materials.MaterialCommandEdit.COMMAND_NAME,
            assignCommand = opspro.Materials.MaterialCommandAssign.COMMAND_NAME,
            unassignCommand = opspro.Materials.MaterialCommandUnassign.COMMAND_NAME,
        ),

        CAEComponentGroupItem(
            id = CAEComponentGroupUIDs.SECTIONS,
            displayName = "Sections",
            description = "Beam cross-section profiles for structural analysis",
            icon = "assets/images/beam_section.ico",
            classIconMap = {
                'BeamSection': 'assets/images/beam_section.ico',
            },
            assignmentFlags = MpcPluginCaeComponentAssignmentFlags.Edges,
            collectionCommands = [
                ('Add Beam Section...', opspro.Sections.BeamSectionCommandNew.COMMAND_NAME),
            ],
            componentCommands = [
                ('Remove', opspro.Sections.BeamSectionCommandDelete.COMMAND_NAME),
                ('Clone', opspro.Sections.BeamSectionCommandClone.COMMAND_NAME),
                ('Edit', opspro.Sections.BeamSectionCommandEdit.COMMAND_NAME),
                ('Assign to...', opspro.Sections.BeamSectionCommandAssign.COMMAND_NAME),
                ('Unassign from...', opspro.Sections.BeamSectionCommandUnassign.COMMAND_NAME),
            ],
            preferredComponentCommand = opspro.Sections.BeamSectionCommandEdit.COMMAND_NAME,
            assignCommand = opspro.Sections.BeamSectionCommandAssign.COMMAND_NAME,
            unassignCommand = opspro.Sections.BeamSectionCommandUnassign.COMMAND_NAME,
        ),

        CAEComponentGroupItem(
            id = CAEComponentGroupUIDs.BEAM_HINGES,
            displayName = "Beam Hinges",
            description = "End releases and nonlinear hinges for frame elements",
            icon = "assets/images/beam_end_release.ico",
            classIconMap = {
                'BeamEndRelease':      'assets/images/beam_end_release.ico',
                'BeamRotationalHinge': 'assets/images/beam_rotational_hinge.ico',
                'BeamShearHinge':      'assets/images/beam_shear_hinge.ico',
            },
            assignmentFlags = MpcPluginCaeComponentAssignmentFlags.Edges,
            collectionCommands = [
                ('Add End Release...',       opspro.Hinges.BeamEndReleaseCommandNew.COMMAND_NAME),
                ('Add Rotational Hinge...', opspro.Hinges.BeamRotationalHingeCommandNew.COMMAND_NAME),
                ('Add Shear Hinge...',       opspro.Hinges.BeamShearHingeCommandNew.COMMAND_NAME),
            ],
            componentCommands = [
                ('Remove',        opspro.Hinges.BeamHingeCommandDelete.COMMAND_NAME),
                ('Clone',         opspro.Hinges.BeamHingeCommandClone.COMMAND_NAME),
                ('Edit',          opspro.Hinges.BeamHingeCommandEdit.COMMAND_NAME),
                ('Assign to...',  opspro.Hinges.BeamHingeCommandAssign.COMMAND_NAME),
                ('Unassign from...', opspro.Hinges.BeamHingeCommandUnassign.COMMAND_NAME),
            ],
            preferredComponentCommand = opspro.Hinges.BeamHingeCommandEdit.COMMAND_NAME,
            assignCommand = opspro.Hinges.BeamHingeCommandAssign.COMMAND_NAME,
            unassignCommand = opspro.Hinges.BeamHingeCommandUnassign.COMMAND_NAME,
        ),

        CAEComponentGroupItem(
            id = CAEComponentGroupUIDs.USER_NOTES,
            displayName = "User Notes",
            description = "Free-text annotations stored in the document",
            icon = "assets/images/user_notes.ico",
            assignmentFlags = MpcPluginCaeComponentAssignmentFlags.Nothing,
            collectionCommands = [
                ('Add Note...', opspro.UserNotes.UserNoteCommandNew.COMMAND_NAME),
            ],
            componentCommands = [
                ('Edit',   opspro.UserNotes.UserNoteCommandEdit.COMMAND_NAME),
                ('Remove', opspro.UserNotes.UserNoteCommandDelete.COMMAND_NAME),
            ],
            preferredComponentCommand = opspro.UserNotes.UserNoteCommandEdit.COMMAND_NAME,
        ),

        CAEComponentGroupItem(
            id = CAEComponentGroupUIDs.INTERNAL,
            displayName = 'Internal',
            description = 'Internal components managed automatically by the solver',
            icon = 'assets/images/document_settings.ico',
            assignmentFlags = MpcPluginCaeComponentAssignmentFlags.Nothing,
            collectionCommands = [],
            componentCommands = [],
            preferredComponentCommand = '',
            hidden = True
        ),

    ]