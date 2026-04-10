from opspro.Materials.material_command_new import MaterialCommandNew
from opspro.Materials.steel_material import SteelMaterial

"""
MCP_COMMAND_METADATA_START
{
    "name": "new_steel_material",
    "description": "Creates a new steel material in the active document. All parameters are optional; omitted parameters use sensible defaults (E=210 GPa, nu=0.3, rho=7850 kg/m3, sigma_y=355 MPa, sigma_u=510 MPa, epsilon_u=0.15). Parameters with physical units use a quantity object with magnitude (float) and unit (string) fields; any Pint-compatible unit is accepted (e.g. Pa, MPa, GPa). Requires an active CAE document.",
    "command": "NewSteelMaterial",
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
                    "E":         {"type": "object", "description": "Young's modulus as {magnitude, unit}. Default: 210 GPa"},
                    "nu":        {"type": "object", "description": "Poisson's ratio as {magnitude, unit}. Default: 0.3 (dimensionless)"},
                    "rho":       {"type": "object", "description": "Mass density as {magnitude, unit}. Default: 7850 kg/m^3"},
                    "nonlinear": {"type": "boolean", "description": "Enable elasto-plastic nonlinear behaviour. Default: false"},
                    "sigma_y":   {"type": "object", "description": "Yield stress as {magnitude, unit}. Default: 355 MPa. Active when nonlinear=true"},
                    "sigma_u":   {"type": "object", "description": "Ultimate stress as {magnitude, unit}. Default: 510 MPa. Active when nonlinear=true"},
                    "epsilon_u": {"type": "object", "description": "Ultimate strain at sigma_u as {magnitude, unit}. Default: 0.15 (dimensionless). Active when nonlinear=true"},
                    "fracture":  {"type": "boolean", "description": "Enable stress/stiffness decay beyond epsilon_u. Default: false. Active when nonlinear=true"},
                    "preset_standard":    {"type": "string", "description": "Provenance: the standard from which this material was taken (e.g. ASTM). Informational only — does not trigger preset loading. Use list_material_presets to discover presets and pass all parameters explicitly."},
                    "preset_designation": {"type": "string", "description": "Provenance: the designation within the standard (e.g. A572-50). Informational only — does not trigger preset loading. Use list_material_presets to discover presets and pass all parameters explicitly."}
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


class SteelMaterialCommandNew(MaterialCommandNew):
    """Command that creates a new SteelMaterial."""

    COMMAND_NAME = 'NewSteelMaterial'

    def material_class(self) -> SteelMaterial:
        return SteelMaterial

    def _init_new_material(self, mat: SteelMaterial):
        try:
            import PyMpc
            visual_mat = PyMpc.FxMaterial()
            PyMpc.randomizeFxMaterialProperty(visual_mat)
            mat.visual_material = visual_mat
        except Exception:
            pass

    def create(self):
        return SteelMaterialCommandNew()
