"""
material_command_list_assignments.py
-------------------------------------
Lists all CAE entities (geometries and interactions) to which a given
material is currently assigned.

Delegates all logic to ComponentCommandListAssignments; this class only
supplies the component group ID and the MCP metadata.
"""

from __future__ import annotations

from opspro.assets.cae_components_uids import CAEComponentGroupUIDs
from opspro.utils.component_command_list_assignments import ComponentCommandListAssignments

"""
MCP_COMMAND_METADATA_START
{
    "name": "list_material_assignments",
    "description": "Returns all CAE entities (geometry sub-shapes and interactions) to which a given material is currently assigned. Requires an active CAE document.",
    "command": "ListMaterialAssignments",
    "inputSchema": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "ID of the material whose assignments should be listed"
            }
        },
        "required": ["component_id"]
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status": { "type": "boolean", "description": "true on success, false on failure" },
            "error":  { "type": "string",  "description": "Error message if status is false, empty string on success" },
            "assignments": {
                "type": "object",
                "description": "The full assignment picture for this material",
                "properties": {
                    "geometries": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": { "type": "integer", "description": "Geometry ID" },
                                "subshapes": {
                                    "type": "object",
                                    "properties": {
                                        "vertex": { "type": "array", "items": { "type": "integer" } },
                                        "edge":   { "type": "array", "items": { "type": "integer" } },
                                        "face":   { "type": "array", "items": { "type": "integer" } },
                                        "solid":  { "type": "array", "items": { "type": "integer" } }
                                    }
                                }
                            }
                        }
                    },
                    "interactions": {
                        "type": "array",
                        "items": { "type": "integer" },
                        "description": "IDs of interactions the material is assigned to"
                    }
                }
            }
        }
    }
}
MCP_COMMAND_METADATA_END
"""


class MaterialCommandListAssignments(ComponentCommandListAssignments):
    """Lists all CAE entities assigned to a given material."""

    COMMAND_NAME = 'ListMaterialAssignments'

    @property
    def component_group_id(self) -> str:
        return CAEComponentGroupUIDs.MATERIALS

    def create(self) -> 'MaterialCommandListAssignments':
        return MaterialCommandListAssignments()
