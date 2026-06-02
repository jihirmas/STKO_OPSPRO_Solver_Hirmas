import json

import pint

from opspro.parameters.ParameterManager import ParameterManager
from opspro.GeotechnicalElementGenerators.dimension_mode import DimensionMode


def quantity_to_dict(qty) -> dict:
    if isinstance(qty, pint.Quantity):
        return {'magnitude': float(qty.magnitude), 'unit': str(qty.units)}
    return {'magnitude': float(qty), 'unit': 'dimensionless'}


def quantity_from_dict(data, fallback):
    ureg = ParameterManager._unit_registry
    if isinstance(data, dict):
        return ureg.Quantity(data['magnitude'], data['unit'])
    if isinstance(data, (int, float)):
        if isinstance(fallback, pint.Quantity):
            return float(data) * fallback.units
        return float(data) * ureg.dimensionless
    return fallback


def normalize_dimension_mode(value, fallback=DimensionMode.TWO_D) -> str:
    try:
        return DimensionMode.normalize(value)
    except Exception:
        return fallback


def validation_result(errors=None, warnings=None) -> dict:
    errors = list(errors or [])
    warnings = list(warnings or [])
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
    }


def require_non_empty(value, label: str, errors: list):
    if not str(value or '').strip():
        errors.append(f'{label} must not be empty.')


def require_positive_quantity(qty, label: str, errors: list):
    try:
        if float(qty.to_base_units().magnitude) <= 0.0:
            errors.append(f'{label} must be greater than zero.')
    except Exception as e:
        errors.append(f'{label}: invalid quantity ({e}).')


def require_non_negative_quantity(qty, label: str, errors: list):
    try:
        if float(qty.to_base_units().magnitude) < 0.0:
            errors.append(f'{label} must be greater than or equal to zero.')
    except Exception as e:
        errors.append(f'{label}: invalid quantity ({e}).')


def safe_json_dumps(data: dict, context: str) -> str:
    try:
        return json.dumps(data)
    except Exception as e:
        print(f'Error serializing {context}: {e}')
        import traceback
        print(traceback.format_exc())
        return ''


def safe_json_loads(state: str, context: str):
    if not state:
        return None
    try:
        return json.loads(state)
    except Exception as e:
        print(f'Error parsing state for {context}: {e}')
        return None

