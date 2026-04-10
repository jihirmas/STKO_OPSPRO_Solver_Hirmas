from opspro.Materials.material_command_new import MaterialCommandNew
from opspro.Materials.asd_plastic_material import ASDPlasticMaterial

"""
MCP_COMMAND_METADATA_START
{
    "name": "new_asd_plastic_material",
    "description": "Creates a new ASD plastic material in the active document. All parameters are optional; omitted parameters use sensible defaults. This material supports advanced elasto-plastic behavior with configurable elasticity models (LinearIsotropic3D, DuncanChang), yield functions (VonMises, DruckerPrager, MohrCoulomb, TensionCutoff), plastic flow rules, and hardening laws. Parameters with physical units use a quantity object with magnitude (float) and unit (string) fields; any Pint-compatible unit is accepted. Requires an active CAE document.",
    "command": "NewASDPlasticMaterial",
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
                    "elasticity_type": {
                        "type": "string",
                        "description": "Elasticity model: 'LinearIsotropic3D' (default) or 'DuncanChang'"
                    },
                    "E": {
                        "type": "object",
                        "description": "Young's modulus as {magnitude, unit}. Default: 30 GPa"
                    },
                    "nu": {
                        "type": "object",
                        "description": "Poisson's ratio as {magnitude, unit}. Default: 0.3 (dimensionless)"
                    },
                    "rho": {
                        "type": "object",
                        "description": "Mass density as {magnitude, unit}. Default: 2400 kg/m^3"
                    },
                    "yield_function": {
                        "type": "string",
                        "description": "Yield function type: 'VonMises' (default), 'DruckerPrager', 'MohrCoulomb', or 'TensionCutoff'"
                    },
                    "plastic_flow": {
                        "type": "string",
                        "description": "Plastic flow rule: 'VonMises' (default), 'DruckerPrager', 'ConstantDilatancy', or 'MohrCoulomb'"
                    },
                    "VonMises_YieldStress": {
                        "type": "object",
                        "description": "Von Mises yield stress as {magnitude, unit}. Default: 250 MPa. Used when yield_function='VonMises'"
                    },
                    "MC_c": {
                        "type": "object",
                        "description": "Mohr-Coulomb cohesion as {magnitude, unit}. Default: 0 Pa. Used when yield_function='MohrCoulomb'"
                    },
                    "MC_phi": {
                        "type": "object",
                        "description": "Mohr-Coulomb friction angle as {magnitude, unit}. Default: 30 degrees. Used when yield_function='MohrCoulomb'"
                    },
                    "MC_ds": {
                        "type": "object",
                        "description": "Mohr-Coulomb numerical parameter as {magnitude, unit}. Default: 0.001 (dimensionless)"
                    },
                    "DP_xi_c": {
                        "type": "object",
                        "description": "Drucker-Prager xi_c parameter as {magnitude, unit}. Default: 0.0 (dimensionless)"
                    },
                    "DP_eta": {
                        "type": "object",
                        "description": "Drucker-Prager eta parameter as {magnitude, unit}. Default: 0.0 (dimensionless)"
                    },
                    "hardening_scalar": {
                        "type": "string",
                        "description": "Scalar hardening law: 'NullHardeningScalarFunction' (default), 'ScalarLinearHardeningFunction'"
                    },
                    "hardening_tensor": {
                        "type": "string",
                        "description": "Tensor hardening law: 'NullHardeningTensorFunction' (default), 'TensorLinearHardeningFunction', 'ArmstrongFrederickHardeningFunction'"
                    },
                    "integration_method": {
                        "type": "string",
                        "description": "Integration method: 'Runge_Kutta_45_Error_Control' (default), 'Forward_Euler', 'Backward_Euler', etc."
                    },
                    "f_absolute_tol": {
                        "type": "object",
                        "description": "Yield function absolute tolerance as {magnitude, unit}. Default: 1.0e-6 (dimensionless)"
                    },
                    "stress_absolute_tol": {
                        "type": "object",
                        "description": "Stress absolute tolerance as {magnitude, unit}. Default: 1.0e-6 Pa"
                    },
                    "n_max_iterations": {
                        "type": "object",
                        "description": "Maximum iterations for yield surface intersection as {magnitude, unit}. Default: 100 (dimensionless)"
                    },
                    "preset_standard": {
                        "type": "string",
                        "description": "Provenance: the standard from which this material was taken (informational only)"
                    },
                    "preset_designation": {
                        "type": "string",
                        "description": "Provenance: the designation within the standard (informational only)"
                    }
                }
            }
        }
    },
    "outputSchema": {
        "type": "object",
        "properties": {
            "status": {
                "type": "boolean",
                "description": "true on success, false on failure"
            },
            "component_id": {
                "type": "integer",
                "description": "ID of the newly created material, or -1 on failure"
            },
            "error": {
                "type": "string",
                "description": "Error message if status is false, empty string on success"
            }
        }
    }
}
MCP_COMMAND_METADATA_END
"""


class ASDPlasticMaterialCommandNew(MaterialCommandNew):
    """Command that creates a new ASDPlasticMaterial."""

    COMMAND_NAME = 'NewASDPlasticMaterial'

    def material_class(self) -> ASDPlasticMaterial:
        return ASDPlasticMaterial

    def _init_new_material(self, mat: ASDPlasticMaterial):
        try:
            import PyMpc
            visual_mat = PyMpc.FxMaterial()
            PyMpc.randomizeFxMaterialProperty(visual_mat)
            mat.visual_material = visual_mat
        except Exception:
            pass

    def create(self):
        return ASDPlasticMaterialCommandNew()