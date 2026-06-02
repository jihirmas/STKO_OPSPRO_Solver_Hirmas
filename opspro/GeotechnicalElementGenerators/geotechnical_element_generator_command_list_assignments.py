from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.utils import ComponentCommandListAssignments


class GeotechnicalElementGeneratorCommandListAssignments(ComponentCommandListAssignments):
    COMMAND_NAME = 'ListGeotechnicalElementGeneratorAssignments'

    @property
    def component_group_id(self) -> str:
        return CAEComponentGroupUIDs.GEOTECHNICAL_ELEMENT_GENERATORS

    def create(self):
        return GeotechnicalElementGeneratorCommandListAssignments()

