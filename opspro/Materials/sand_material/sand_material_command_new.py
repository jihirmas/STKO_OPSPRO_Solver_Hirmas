from opspro.Materials.material_command_new import MaterialCommandNew
from opspro.Materials.sand_material.sand_material import SandMaterial

"""
MCP_COMMAND_METADATA_START
{
    "name": "new_sand_material",
    "description": "Creates a new geotechnical sand material in the active document. Sand material supports three constitutive models: Mohr-Coulomb, Drucker-Prager, and Von-Mises. All parameters are optional; omitted parameters use sensible defaults (E=50 MPa, G=20 MPa, K=40 MPa, phi=30 deg, c=10 kPa, material_type='Mohr-Coulomb'). Parameters with physical units use a quantity object with magnitude (float) and unit (string) fields; any Pint-compatible unit is accepted. Requires an active CAE document.",
    "command": "NewSandMaterial",
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
                    "E":           {"type": "object", "description": "Young's modulus as {magnitude, unit}. Default: 50 MPa"},
                    "G":           {"type": "object", "description": "Shear modulus as {magnitude, unit}. Default: 20 MPa"},
                    "K":           {"type": "object", "description": "Bulk modulus as {magnitude, unit}. Default: 40 MPa"},
                    "nu":          {"type": "object", "description": "Poisson's ratio as {magnitude, unit}. Default: 0.3 (dimensionless)"},
                    "gamma_unsat": {"type": "object", "description": "Unsaturated unit weight as {magnitude, unit}. Default: 16000 kg/m^3"},
                    "gamma_sat":   {"type": "object", "description": "Saturated unit weight as {magnitude, unit}. Default: 18000 kg/m^3"},
                    "e_init":      {"type": "object", "description": "Initial void ratio as {magnitude, unit}. Default: 0.8 (dimensionless)"},
                    "n_init":      {"type": "object", "description": "Initial porosity as {magnitude, unit}. Default: 0.444 (dimensionless)"},
                    "material_type": {"type": "string", "description": "Constitutive model type: 'Mohr-Coulomb', 'Drucker-Prager', or 'Von-Mises'. Default: 'Mohr-Coulomb'"},
                    "phi":         {"type": "object", "description": "Friction angle as {magnitude, unit}. Default: 30 deg. Active for Mohr-Coulomb and Drucker-Prager"},
                    "c":           {"type": "object", "description": "Cohesion as {magnitude, unit}. Default: 10 kPa"},
                    "psi":         {"type": "object", "description": "Dilatancy angle as {magnitude, unit}. Default: 0 deg"},
                    "sigma_y":     {"type": "object", "description": "Yield stress as {magnitude, unit}. Default: 100 kPa. Active for Von-Mises"},
                    "calibration_mode": {"type": "string", "description": "Calibration mode for Drucker-Prager: 'Inner match', 'Outer match', or 'Plane-Strain'. Default: 'Inner match'"},
                    "nonlinear_elasticity": {"type": "boolean", "description": "Enable pressure-dependent elasticity. Default: false"},
                    "E_ref":       {"type": "object", "description": "Reference elasticity as {magnitude, unit}. Default: 50 MPa. Active when nonlinear_elasticity=true"},
                    "P_ref":       {"type": "object", "description": "Reference pressure as {magnitude, unit}. Default: 100 kPa. Active when nonlinear_elasticity=true"},
                    "n_exp":       {"type": "object", "description": "Elasticity exponent as {magnitude, unit}. Default: 0.5 (dimensionless). Active when nonlinear_elasticity=true"}
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


class SandMaterialCommandNew(MaterialCommandNew):
    """Command that creates a new SandMaterial."""

    COMMAND_NAME = 'NewSandMaterial'

    def material_class(self) -> SandMaterial:
        return SandMaterial

    def _init_new_material(self, mat: SandMaterial):
        try:
            import PyMpc
            visual_mat = PyMpc.FxMaterial()
            PyMpc.randomizeFxMaterialProperty(visual_mat)
            mat.visual_material = visual_mat
        except Exception:
            pass

    def create(self):
        return SandMaterialCommandNew()
