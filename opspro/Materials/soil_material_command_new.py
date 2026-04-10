from opspro.Materials.material_command_new import MaterialCommandNew
from opspro.Materials.soil_material import SoilMaterial

"""
MCP_COMMAND_METADATA_START
{
    "name": "new_soil_material",
    "description": "Creates a new geotechnical soil material in the active document. All parameters are optional; omitted parameters use sensible defaults (E=50 MPa, nu=0.3, rho=1800 kg/m3, phi=30 deg, c=10 kPa). Parameters with physical units use a quantity object with magnitude (float) and unit (string) fields; any Pint-compatible unit is accepted. Requires an active CAE document.",
    "command": "NewSoilMaterial",
    "inputSchema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Optional display name for the new material"
            },
            "material_parameters": {
                "type": "object",
                "description": "Optional material-specific parameters. Omitted fields keep their default values. Physical quantities use the format {magnitude: <float>, unit: <string>}.",
                "properties": {
                    "E":         {"type": "object", "description": "Young's modulus as {magnitude, unit}. Default: 50 MPa"},
                    "nu":        {"type": "object", "description": "Poisson's ratio as {magnitude, unit}. Default: 0.3 (dimensionless)"},
                    "rho":       {"type": "object", "description": "Mass density as {magnitude, unit}. Default: 1800 kg/m^3"},
                    "nonlinear": {"type": "boolean", "description": "Enable Mohr-Coulomb plastic behaviour. Default: false"},
                    "phi":       {"type": "object", "description": "Friction angle as {magnitude, unit}. Default: 30 deg. Active when nonlinear=true"},
                    "c":         {"type": "object", "description": "Cohesion as {magnitude, unit}. Default: 10 kPa. Active when nonlinear=true"}
                }
            }
        }
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status":       {"type": "boolean", "description": "true on success, false on failure"},
            "component_id": {"type": "integer", "description": "ID of the newly created material, or -1 on failure"},
            "error":        {"type": "string",  "description": "Error message if status is false, empty string on success"}
        }
    }
}
MCP_COMMAND_METADATA_END
"""


class SoilMaterialCommandNew(MaterialCommandNew):
    """Command that creates a new SoilMaterial."""

    COMMAND_NAME = 'NewSoilMaterial'

    def material_class(self) -> SoilMaterial:
        return SoilMaterial

    def _init_new_material(self, mat: SoilMaterial):
        try:
            import PyMpc
            visual_mat = PyMpc.FxMaterial()
            PyMpc.randomizeFxMaterialProperty(visual_mat)
            mat.visual_material = visual_mat
        except Exception:
            pass

    def create(self):
        return SoilMaterialCommandNew()
