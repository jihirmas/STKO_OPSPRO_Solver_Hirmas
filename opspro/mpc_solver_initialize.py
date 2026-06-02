from PyMpc import (
	App,
	MpcContext,
	MpcPreProcessorContext,
	MpcPluginCaeComponent
)
import pkgutil

def _register_cae_components(doc):
	from opspro.assets.cae_components import CAEComponentGroups
	print('   Registering CAE Components...')
	for group in CAEComponentGroups.groups:
		icon_data = pkgutil.get_data('opspro', group.icon)
		class_icon_map = {}
		for class_name, icon_path in group.classIconMap.items():
			data = pkgutil.get_data('opspro', icon_path)
			if data is not None:
				class_icon_map[class_name] = data
		doc.pluginCaeComponents.registerGroup(
			group.id, 
			group.displayName, 
			group.description, 
			icon_data,
			group.assignmentFlags,
			group.collectionCommands,
			group.componentCommands,
			group.preferredComponentCommand,
			class_icon_map,
			group.hidden,
			group.assignCommand,
			group.unassignCommand
		)

def _unregister_builtin_commands():
	# Unregister some built-in commands that we don't want in our solver's UI.
	# This is optional, but it allows us to clean up the UI and remove commands 
	# that don't make sense for our solver.
	print('   Unregistering some built-in commands...')
	# definitions
	App.unregisterCommand('NewDefinition')
	App.unregisterCommand('DeleteDefinition')
	App.unregisterCommand('CloneDefinition')
	App.unregisterCommand('EditDefinition')
	# physical properties
	App.unregisterCommand('NewPhysicalProperty')
	App.unregisterCommand('DeletePhysicalProperty')
	App.unregisterCommand('ClonePhysicalProperty')
	App.unregisterCommand('EditPhysicalProperty')
	App.unregisterCommand('AssignPhysicalProperty')
	App.unregisterCommand('UnassignPhysicalProperty')
	App.unregisterCommand('SelectByPhysicalProperty')
	App.unregisterCommand('HideByPhysicalProperty')
	App.unregisterCommand('ShowByPhysicalProperty')
	# element properties
	App.unregisterCommand('NewElementProperty')
	App.unregisterCommand('DeleteElementProperty')
	App.unregisterCommand('CloneElementProperty')
	App.unregisterCommand('EditElementProperty')
	App.unregisterCommand('AssignElementProperty')
	App.unregisterCommand('UnassignElementProperty')
	App.unregisterCommand('SelectByElementProperty')
	App.unregisterCommand('HideByElementProperty')
	App.unregisterCommand('ShowByElementProperty')
	# conditions
	App.unregisterCommand('NewCondition')
	App.unregisterCommand('DeleteCondition')
	App.unregisterCommand('CloneCondition')
	App.unregisterCommand('EditCondition')
	# analysis steps
	App.unregisterCommand('NewAnalysisStep')
	App.unregisterCommand('DeleteAnalysisStep')
	App.unregisterCommand('CloneAnalysisStep')
	App.unregisterCommand('EditAnalysisStep')

def _register_plugin_commands():
	# Register custom commands for our solver.
	# This is where you would add any additional commands that your solver needs.
	print('   Registering custom commands...')
	import opspro.Settings
	App.registerCommand(opspro.Settings.DocumentSettingsCommandEdit())
	import opspro.UserNotes
	App.registerCommand(opspro.UserNotes.UserNoteCommandNew())
	App.registerCommand(opspro.UserNotes.UserNoteCommandEdit())
	App.registerCommand(opspro.UserNotes.UserNoteCommandDelete())
	import opspro.utils
	App.registerCommand(opspro.utils.AssignmentRegistryCommandShow())
	import opspro.View
	App.registerCommand(opspro.View.ViewGetCameraState())
	App.registerCommand(opspro.View.ViewFitAll())
	App.registerCommand(opspro.View.ViewSetViewPoint())
	App.registerCommand(opspro.View.ViewSetProjection())
	App.registerCommand(opspro.View.ViewApplyRotation())
	App.registerCommand(opspro.View.ViewApplyZoom())
	App.registerCommand(opspro.View.ViewGrabScreenShot())
	import opspro.Materials
	App.registerCommand(opspro.Materials.SteelMaterialCommandNew())
	App.registerCommand(opspro.Materials.ConcreteMaterialCommandNew())
	App.registerCommand(opspro.Materials.SoilMaterialCommandNew())
	App.registerCommand(opspro.Materials.MaterialCommandDelete())
	App.registerCommand(opspro.Materials.MaterialCommandClone())
	App.registerCommand(opspro.Materials.MaterialCommandEdit())
	App.registerCommand(opspro.Materials.MaterialCommandAssign())
	App.registerCommand(opspro.Materials.MaterialCommandUnassign())
	App.registerCommand(opspro.Materials.MaterialCommandListPresets())
	App.registerCommand(opspro.Materials.MaterialCommandListAssignments())
	import opspro.Sections
	App.registerCommand(opspro.Sections.BeamSectionCommandNew())
	App.registerCommand(opspro.Sections.BeamSectionCommandEdit())
	App.registerCommand(opspro.Sections.BeamSectionCommandDelete())
	App.registerCommand(opspro.Sections.BeamSectionCommandClone())
	App.registerCommand(opspro.Sections.BeamSectionCommandAssign())
	App.registerCommand(opspro.Sections.BeamSectionCommandUnassign())
	App.registerCommand(opspro.Sections.SectionCommandListShapes())
	App.registerCommand(opspro.Sections.SectionCommandListPresets())
	import opspro.Hinges
	App.registerCommand(opspro.Hinges.BeamEndReleaseCommandNew())
	App.registerCommand(opspro.Hinges.BeamRotationalHingeCommandNew())
	App.registerCommand(opspro.Hinges.BeamShearHingeCommandNew())
	App.registerCommand(opspro.Hinges.BeamHingeCommandEdit())
	App.registerCommand(opspro.Hinges.BeamHingeCommandDelete())
	App.registerCommand(opspro.Hinges.BeamHingeCommandClone())
	App.registerCommand(opspro.Hinges.BeamHingeCommandAssign())
	App.registerCommand(opspro.Hinges.BeamHingeCommandUnassign())
	import opspro.GeotechnicalElementGenerators
	App.registerCommand(opspro.GeotechnicalElementGenerators.SpringFoundationCommandNew())
	App.registerCommand(opspro.GeotechnicalElementGenerators.EmbeddedFoundationCommandNew())
	App.registerCommand(opspro.GeotechnicalElementGenerators.GeotechnicalElementGeneratorCommandEdit())
	App.registerCommand(opspro.GeotechnicalElementGenerators.GeotechnicalElementGeneratorCommandAssign())
	App.registerCommand(opspro.GeotechnicalElementGenerators.GeotechnicalElementGeneratorCommandUnassign())
	App.registerCommand(opspro.GeotechnicalElementGenerators.GeotechnicalElementGeneratorCommandListAssignments())

def _update_command_categories():
	# This is an example of how to update command categories.
	# In this case, we are moving the "New Material" command from the "Property" category to a new "Materials" category.
	print('   Updating command categories...')

	# remove un-used categories
	App.removeCommandCategory(MpcContext.PreProcessor, 'Property')
	App.removeCommandCategory(MpcContext.PreProcessor, 'Condition')

	# add new categories
	App.addCommandCategory(MpcContext.PreProcessor, 'Settings', MpcPreProcessorContext.Property, -2)
	App.addCommandCategory(MpcContext.PreProcessor, 'Properties', MpcPreProcessorContext.Property, -2)

def _register_actions():
	# This is an example of how to add actions to the UI.
	# In this case, we are adding a "New Material" action to the "Properties" category in the PreProcessor context.
	print('   Adding a command action to the new category...')

	# Settings
	import opspro.Settings
	App.addCommandAction(
		MpcContext.PreProcessor, 
		'Settings', 
		[
			(
				'Document Settings', opspro.Settings.DocumentSettingsCommandEdit.COMMAND_NAME,
				pkgutil.get_data('opspro', 'assets/images/document_settings.ico'), True
			),
		],
		'Settings'
	)

	# Properties
	import opspro.UserNotes
	App.addCommandAction(
		MpcContext.PreProcessor,
		'Properties',
		[
			(
				'User Note', opspro.UserNotes.UserNoteCommandNew.COMMAND_NAME,
				pkgutil.get_data('opspro', 'assets/images/user_notes_add.ico'), True
			),
		],
		'User Notes'
	)
	import opspro.Materials
	App.addCommandAction(
		MpcContext.PreProcessor, 
		'Properties', 
		[
			(
				'Steel', opspro.Materials.SteelMaterialCommandNew.COMMAND_NAME,
				pkgutil.get_data('opspro', 'assets/images/material_steel_add.ico'), True
			),
			(
				'Concrete', opspro.Materials.ConcreteMaterialCommandNew.COMMAND_NAME,
				pkgutil.get_data('opspro', 'assets/images/material_concrete_add.ico'), True
			),
			(
				'Soil', opspro.Materials.SoilMaterialCommandNew.COMMAND_NAME,
				pkgutil.get_data('opspro', 'assets/images/material_soil_add.ico'), True
			),
		],
		'Materials'
	)
	import opspro.Sections
	App.addCommandAction(
		MpcContext.PreProcessor,
		'Properties',
		[
			(
				'Beam Section', opspro.Sections.BeamSectionCommandNew.COMMAND_NAME,
				pkgutil.get_data('opspro', 'assets/images/beam_section_add.ico'), True
			),
		],
		'Sections'
	)
	import opspro.Hinges
	App.addCommandAction(
		MpcContext.PreProcessor,
		'Properties',
		[
			(
				'End Release', opspro.Hinges.BeamEndReleaseCommandNew.COMMAND_NAME,
				pkgutil.get_data('opspro', 'assets/images/beam_end_release_add.ico'), True
			),
			(
				'Rotational Hinge', opspro.Hinges.BeamRotationalHingeCommandNew.COMMAND_NAME,
				pkgutil.get_data('opspro', 'assets/images/beam_rotational_hinge_add.ico'), True
			),
			(
				'Shear Hinge', opspro.Hinges.BeamShearHingeCommandNew.COMMAND_NAME,
				pkgutil.get_data('opspro', 'assets/images/beam_shear_hinge_add.ico'), True
			),
		],
		'Beam Hinges'
	)
	import opspro.GeotechnicalElementGenerators
	App.addCommandAction(
		MpcContext.PreProcessor,
		'Properties',
		[
			(
				'Spring Foundation',
				opspro.GeotechnicalElementGenerators.SpringFoundationCommandNew.COMMAND_NAME,
				pkgutil.get_data('opspro', 'assets/images/material_soil_add.ico'),
				True
			),
			(
				'Embedded Foundation',
				opspro.GeotechnicalElementGenerators.EmbeddedFoundationCommandNew.COMMAND_NAME,
				pkgutil.get_data('opspro', 'assets/images/material_soil_add.ico'),
				True
			),
		],
		'Geotechnical Element Generators'
	)
	import opspro.utils
	App.addCommandAction(
		MpcContext.PreProcessor,
		'Properties',
		[
			(
				'Show Assignments', opspro.utils.AssignmentRegistryCommandShow.COMMAND_NAME,
				pkgutil.get_data('opspro', 'assets/images/materials.ico'), True
			),
		],
		'Assignments'
	)

def _add_default_components(doc):
	import opspro.Settings
	def _add_comp(comp : MpcPluginCaeComponent):
		groups = doc.pluginCaeComponents.groups()
		group_id = comp.componentGroupID()
		coll = groups[group_id].collection
		comp.id = coll.getlastkey(0) + 1
		doc.addPluginCaeComponent(comp)
	try:
		# If the current document is new/empty, we can add some default components to it.
		# For example, we can add a default DocumentSettings component to the document.
		if doc.new:
			print('   Adding default components to new document...')
			settings = opspro.Settings.DocumentSettings()
			_add_comp(settings)
			import opspro.utils
			registry = opspro.utils.AssignmentRegistry()
			_add_comp(registry)
			doc.commitChanges()
	except Exception as e:
		print(f"Error adding default components: {e}")

def initialize():
	
	"""
	  Called by @ref mpc_initialize module when this solver
	  is set as the current solver for the active document
	"""

	print('Loading External Solver: OpenSees for STKO-Professional')
	
	# get the current document
	doc = App.caeDocument()
	
	# clear old solver stuff (legacy from previous versions)
	doc.unregisterMetaDataAll()

	# register all CAE Components
	_register_cae_components(doc)
	
	# resetting to builtin commands (just in case)
	App.revertToBuiltinCommands()

	# register custom commands
	print('   Registering custom commands...')
	App.beginRegisteringCommands()
	_unregister_builtin_commands()
	_register_plugin_commands()
	App.endRegisteringCommands()

	# customize command categories
	_update_command_categories()

	# add actions to the UI
	_register_actions()

	# add default components to new documents
	_add_default_components(doc)
