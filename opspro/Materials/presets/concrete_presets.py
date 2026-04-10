"""
Concrete material presets database.

All mechanical values are stored in SI units:
  - E   : Pa
  - nu  : dimensionless
  - rho : kg/m³
  - fcp : Pa   (peak compressive strength — cylinder characteristic fck or f'c)
  - ft  : Pa   (peak tensile strength)
  - Gt  : J/m² (tensile fracture energy)
  - Gc  : J/m² (compressive fracture energy)

Fracture energies are computed with CEB-FIP Model Code 2010 (eq. 5.1-9):
    Gt = 73 × fcp_MPa^0.18   [J/m²]
    Gc = 250 × Gt             [J/m²]

Sources
-------
- EN 1992-1-1:2004 (Eurocode 2)  Table 3.1 — C12/15 … C90/105
    Ecm = 22 000 × (fcm/10)^0.3  MPa       (fcm = fck + 8 MPa)
    fctm: 0.30 × fck^(2/3)       if fck ≤ 50 MPa
          2.12 × ln(1+fcm/10)    if fck > 50 MPa
- ACI 318-19  §19.2.2.1 (Ec), §19.2.3.1 (fr) — f'c = 2500 … 12 000 psi
    Ec = 57 000 √f'c  [psi]   (normal-weight concrete, wc ≈ 145 pcf)
    fr = 7.5   √f'c  [psi]   (modulus of rupture)
- GB 50010-2010  Table 4.1.3 and Table E.0.1 — C15 … C80
    Ec, fck, ftk from tabled values
- CEB-FIP Model Code 2010  §5.1.8.1 — fracture energies
- CSA A23.3:2019            f'c = 20 … 70 MPa (11 grades, normal-weight concrete)
    Ec = (3300√f'c + 6900)(wc/2300)^1.5  MPa  →  for wc = 2300 kg/m³: 3300√f'c + 6900
    fr = 0.6λ√f'c  MPa  (λ = 1.0, normal density)

MPa → Pa  : multiply by 1 000 000
GPa → Pa  : multiply by 1 000 000 000
psi → Pa  : multiply by 6 894.757 293 168
"""

import math
from dataclasses import dataclass

_MPA = 1_000_000.0
_GPA = 1_000_000_000.0
_PSI = 6_894.757_293_168     # Pa per psi

_NU_CONCRETE  = 0.2
_RHO_CONCRETE = 2400.0       # kg/m³


# ---------------------------------------------------------------------------
# CEB-FIP Model Code 2010  §5.1.8.1 — fracture energy formulae
# ---------------------------------------------------------------------------

def mc2010_fracture_energy(fcp_MPa: float) -> tuple:
    """Return *(Gt, Gc)* in J/m² using CEB-FIP Model Code 2010 eq. 5.1-9.

    Parameters
    ----------
    fcp_MPa : float
        Compressive strength in **MPa** (cylinder characteristic or mean).

    Returns
    -------
    Gt : float
        Tensile fracture energy  [J/m²]
    Gc : float
        Compressive fracture energy [J/m²]  (≈ 250 × Gt)
    """
    Gt = 73.0 * (fcp_MPa ** 0.18)
    Gc = 250.0 * Gt
    return Gt, Gc


# ---------------------------------------------------------------------------
# ConcretePreset dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ConcretePreset:
    """Immutable record holding the nominal properties of a standard concrete class.

    All values are in SI units (Pa, kg/m³, J/m², dimensionless).
    """
    standard    : str    # e.g. 'EN 1992'
    designation : str    # e.g. 'C30/37'
    name        : str    # human-readable label shown in the UI
    E           : float  # Young's modulus [Pa]
    nu          : float  # Poisson's ratio [-]
    rho         : float  # mass density [kg/m³]
    fcp         : float  # peak compressive strength [Pa]
    ft          : float  # peak tensile strength [Pa]
    Gt          : float  # tensile fracture energy [J/m²]
    Gc          : float  # compressive fracture energy [J/m²]
    notes       : str    # normative reference / remarks


# ---------------------------------------------------------------------------
# EN 1992-1-1 (Eurocode 2) — classes C12/15 … C90/105
# ---------------------------------------------------------------------------

def _en1992(fck: float, designation: str) -> ConcretePreset:
    """Build an EN 1992-1-1 preset from the characteristic cylinder strength *fck* (MPa)."""
    fcm = fck + 8.0
    Ecm = 22_000.0 * (fcm / 10.0) ** 0.3                  # MPa
    if fck <= 50.0:
        fctm = 0.30 * fck ** (2.0 / 3.0)                  # MPa — EN 1992 Expr.(3.1)
    else:
        fctm = 2.12 * math.log(1.0 + fcm / 10.0)          # MPa — EN 1992 Expr.(3.2)
    Gt, Gc = mc2010_fracture_energy(fck)
    return ConcretePreset(
        standard    = 'EN 1992',
        designation = designation,
        name        = f'EN 1992 {designation}',
        E           = Ecm  * _MPA,
        nu          = _NU_CONCRETE,
        rho         = _RHO_CONCRETE,
        fcp         = fck  * _MPA,
        ft          = fctm * _MPA,
        Gt          = Gt,
        Gc          = Gc,
        notes       = (f'EN 1992-1-1:2004 Table 3.1. '
                       f'fck = {fck:.0f} MPa, fcm = {fcm:.0f} MPa, '
                       f'Ecm = {Ecm:.0f} MPa, fctm = {fctm:.2f} MPa.'),
    )


_EN1992 = [
    _en1992(12,  'C12/15'),
    _en1992(16,  'C16/20'),
    _en1992(20,  'C20/25'),
    _en1992(25,  'C25/30'),
    _en1992(30,  'C30/37'),
    _en1992(35,  'C35/45'),
    _en1992(40,  'C40/50'),
    _en1992(45,  'C45/55'),
    _en1992(50,  'C50/60'),
    _en1992(55,  'C55/67'),
    _en1992(60,  'C60/75'),
    _en1992(70,  'C70/85'),
    _en1992(80,  'C80/95'),
    _en1992(90,  'C90/105'),
]


# ---------------------------------------------------------------------------
# ACI 318-19 — f'c = 2 500 … 12 000 psi
# ---------------------------------------------------------------------------

def _aci318(fc_psi: float) -> ConcretePreset:
    """Build an ACI 318-19 preset from the cylinder strength *fc_psi* (psi)."""
    Ec_psi = 57_000.0 * math.sqrt(fc_psi)   # psi — §19.2.2.1 (wc = 145 pcf)
    fr_psi =      7.5 * math.sqrt(fc_psi)   # psi — §19.2.3.1 (modulus of rupture)
    fc_mpa  = fc_psi  * _PSI / _MPA
    Gt, Gc  = mc2010_fracture_energy(fc_mpa)
    fc_mpa_r = round(fc_mpa)
    designation = f"{fc_psi:.0f} psi ({fc_mpa_r} MPa)"
    return ConcretePreset(
        standard    = 'ACI 318',
        designation = designation,
        name        = f"ACI 318 f'c {fc_psi:.0f} psi",
        E           = Ec_psi * _PSI,
        nu          = _NU_CONCRETE,
        rho         = _RHO_CONCRETE,
        fcp         = fc_psi * _PSI,
        ft          = fr_psi * _PSI,
        Gt          = Gt,
        Gc          = Gc,
        notes       = (f"ACI 318-19. Ec = 57 000\u221af'c (§19.2.2.1), "
                       f"fr = 7.5\u221af'c (§19.2.3.1). "
                       f"f'c = {fc_psi:.0f} psi = {fc_mpa:.1f} MPa. "
                       f"Normal-weight concrete (wc \u2248 145 pcf / 2320 kg/m\u00b3)."),
    )


_ACI318 = [
    _aci318( 2500),
    _aci318( 3000),
    _aci318( 3500),
    _aci318( 4000),
    _aci318( 4500),
    _aci318( 5000),
    _aci318( 6000),
    _aci318( 8000),
    _aci318(10000),
    _aci318(12000),
]


# ---------------------------------------------------------------------------
# GB 50010-2010 — C15 … C80
# ---------------------------------------------------------------------------

# (fcu_k MPa, designation, fck_axial MPa, ftk MPa, Ec GPa)
# fck  : axial compressive standard value — Table 4.1.3
# ftk  : axial tensile standard value     — Table 4.1.3
# Ec   : elastic modulus                  — Table E.0.1
_GB_DATA = [
    (15,  'C15',  10.0, 1.27, 22.0),
    (20,  'C20',  13.4, 1.54, 25.5),
    (25,  'C25',  16.7, 1.78, 28.0),
    (30,  'C30',  20.1, 2.01, 30.0),
    (35,  'C35',  23.4, 2.20, 31.5),
    (40,  'C40',  26.8, 2.39, 32.5),
    (45,  'C45',  29.6, 2.51, 33.5),
    (50,  'C50',  32.4, 2.64, 34.5),
    (55,  'C55',  35.5, 2.74, 35.5),
    (60,  'C60',  38.5, 2.85, 36.0),
    (65,  'C65',  41.5, 2.93, 36.5),
    (70,  'C70',  44.5, 2.99, 37.0),
    (75,  'C75',  47.4, 3.05, 37.5),
    (80,  'C80',  50.2, 3.11, 38.0),
]

_GB50010 = []
for _fcu, _desig, _fck, _ftk, _Ec_gpa in _GB_DATA:
    _Gt, _Gc = mc2010_fracture_energy(_fck)
    _GB50010.append(ConcretePreset(
        standard    = 'GB 50010',
        designation = _desig,
        name        = f'GB 50010 {_desig}',
        E           = _Ec_gpa * _GPA,
        nu          = _NU_CONCRETE,
        rho         = _RHO_CONCRETE,
        fcp         = _fck  * _MPA,
        ft          = _ftk  * _MPA,
        Gt          = _Gt,
        Gc          = _Gc,
        notes       = (f'GB 50010-2010 Table 4.1.3 & Table E.0.1. '
                       f'fcu,k = {_fcu} MPa, fck = {_fck:.1f} MPa, '
                       f'ftk = {_ftk:.2f} MPa, Ec = {_Ec_gpa:.1f} GPa.'),
    ))


# ---------------------------------------------------------------------------
# CSA A23.3:2019 — f'c = 20 … 70 MPa, normal-weight concrete
# ---------------------------------------------------------------------------
# Cl. 8.6.2.2:  Ec = (3300√f'c + 6900)(wc/2300)^1.5  MPa
#               for normal-density concrete (wc = 2300 kg/m³) → 3300√f'c + 6900
# Cl. 8.6.4.2:  fr = 0.6 λ √f'c  MPa  (λ = 1.0, normal density)
# Fracture energies: CEB-FIP Model Code 2010 (same formula as other standards)
# ---------------------------------------------------------------------------

def _csa_a23(fc_mpa: float) -> ConcretePreset:
    """Build a CSA A23.3:2019 preset from the cylinder strength *fc_mpa* (MPa)."""
    Ec_mpa = 3300.0 * math.sqrt(fc_mpa) + 6900.0   # MPa — Cl. 8.6.2.2, wc=2300 kg/m³
    fr_mpa = 0.6 * math.sqrt(fc_mpa)                # MPa — Cl. 8.6.4.2, λ=1.0
    Gt, Gc = mc2010_fracture_energy(fc_mpa)
    designation = f"f'c {fc_mpa:.0f} MPa"
    return ConcretePreset(
        standard    = 'CSA A23.3',
        designation = designation,
        name        = f"CSA A23.3 f'c {fc_mpa:.0f} MPa",
        E           = Ec_mpa * _MPA,
        nu          = _NU_CONCRETE,
        rho         = _RHO_CONCRETE,
        fcp         = fc_mpa * _MPA,
        ft          = fr_mpa * _MPA,
        Gt          = Gt,
        Gc          = Gc,
        notes       = (f"CSA A23.3:2019. "
                       f"Ec = (3300\u221af'c + 6900) MPa (Cl.\u00a08.6.2.2, wc = 2300 kg/m\u00b3). "
                       f"fr = 0.6\u221af'c MPa (Cl.\u00a08.6.4.2, \u03bb = 1.0). "
                       f"f'c = {fc_mpa:.0f} MPa, Ec = {Ec_mpa:.0f} MPa, fr = {fr_mpa:.2f} MPa."),
    )


_CSA_A23 = [
    _csa_a23(20),
    _csa_a23(25),
    _csa_a23(30),
    _csa_a23(35),
    _csa_a23(40),
    _csa_a23(45),
    _csa_a23(50),
    _csa_a23(55),
    _csa_a23(60),
    _csa_a23(65),
    _csa_a23(70),
]


# ---------------------------------------------------------------------------
# Master dict
# ---------------------------------------------------------------------------

PRESETS = {
    'EN 1992':  _EN1992,
    'ACI 318':  _ACI318,
    'GB 50010': _GB50010,
    'CSA A23.3': _CSA_A23,
}
