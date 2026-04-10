from opspro.Materials.material_command_new import MaterialCommandNew
from opspro.Materials.concrete_material import ConcreteMaterial

"""
MCP_COMMAND_METADATA_START
{
    "name": "new_concrete_material",
    "description": "Creates a new concrete material in the active document. All parameters are optional; omitted parameters use sensible defaults (E=30 GPa, nu=0.2, rho=2400 kg/m3, fcp=30 MPa, ft=2.9 MPa, Gt and Gc auto-computed from fcp via Model Code 2010). Parameters with physical units use a quantity object with magnitude (float) and unit (string) fields; any Pint-compatible unit is accepted. Requires an active CAE document.",
    "command": "NewConcreteMaterial",
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
                    "E":   {"type": "object", "description": "Young's modulus as {magnitude, unit}. Default: 30 GPa"},
                    "nu":  {"type": "object", "description": "Poisson's ratio as {magnitude, unit}. Default: 0.2 (dimensionless)"},
                    "rho": {"type": "object", "description": "Mass density as {magnitude, unit}. Default: 2400 kg/m^3"},
                    "nonlinear": {"type": "boolean", "description": "Enable nonlinear fracture-based behaviour. Default: false"},
                    "auto_fracture_energy": {"type": "boolean", "description": "Auto-compute Gt and Gc from fcp via Model Code 2010 when nonlinear=true. Default: true. Set to false to supply Gt and Gc manually"},
                    "fcp": {"type": "object", "description": "Peak compressive strength as {magnitude, unit}. Default: 30 MPa. Active when nonlinear=true"},
                    "ft":  {"type": "object", "description": "Peak tensile strength as {magnitude, unit}. Default: 2.9 MPa. Active when nonlinear=true"},
                    "Gt":  {"type": "object", "description": "Tensile fracture energy as {magnitude, unit} in J/m^2. Only used when nonlinear=true and auto_fracture_energy=false"},
                    "Gc":  {"type": "object", "description": "Compressive fracture energy as {magnitude, unit} in J/m^2. Only used when nonlinear=true and auto_fracture_energy=false"},
                    "preset_standard":    {"type": "string", "description": "Provenance: the standard from which this material was taken (e.g. EN 1992). Informational only — does not trigger preset loading. Use list_material_presets to discover presets and pass all parameters explicitly."},
                    "preset_designation": {"type": "string", "description": "Provenance: the designation within the standard (e.g. C30/37). Informational only — does not trigger preset loading. Use list_material_presets to discover presets and pass all parameters explicitly."}
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


class ConcreteMaterialCommandNew(MaterialCommandNew):
    """Command that creates a new ConcreteMaterial."""

    COMMAND_NAME = 'NewConcreteMaterial'

    def material_class(self) -> ConcreteMaterial:
        return ConcreteMaterial

    def _init_new_material(self, mat: ConcreteMaterial):
        try:
            import PyMpc
            visual_mat = PyMpc.FxMaterial()
            PyMpc.randomizeFxMaterialProperty(visual_mat)
            mat.visual_material = visual_mat
        except Exception:
            pass

    def create(self):
        return ConcreteMaterialCommandNew()
