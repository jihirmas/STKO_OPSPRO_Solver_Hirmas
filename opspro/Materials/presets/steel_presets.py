"""
Steel material presets database.

All mechanical values are stored in SI units:
  - E         : Pa
  - nu        : dimensionless
  - rho       : kg/m³
  - sigma_y   : Pa
  - sigma_u   : Pa
  - epsilon_u : dimensionless  (elongation at fracture)
                               2" fixed gauge  — ASTM / API / AISI / ASME
                               proportional L₀ = 5.65√S₀ — EN / JIS / GB / AS⋅NZS / IS
                               Values from the two conventions are NOT directly comparable.

Sources
-------
- ASTM A36 / A36M
- ASTM A529 / A529M (Gr. 50, 55)
- ASTM A572 / A572M (Gr. 42, 50, 55, 60, 65)
- ASTM A588 / A588M (Gr. A — weathering)
- ASTM A709 / A709M (Gr. 36, 50, 50W, HPS 50W, HPS 70W, HPS 100W)
- ASTM A514 / A514M (t ≤ 2.5", t > 2.5")
- ASTM A913 / A913M (Gr. 50, 65, 70, 80 — QST)
- ASTM A992 / A992M  (AISC preferred for W-shapes; Fy/Fu ≤ 0.85, Fy ≤ 65 ksi)
- ASTM A500 / A500M  (Gr. B round/shaped, Gr. C round/shaped)
- ASTM A53  / A53M   (Gr. B pipe)
- ASTM A1085 / A1085M (HSS, tight tolerances; Fy/Fu ≤ 0.85)
- API 5L  (Gr. B, X42, X52, X56, X60, X65, X70, X80 — linepipe, PSL1)
- API 2H  (Gr. 42, 50 — offshore structural plate)
- AISI/SAE 1020, 1040, 1045 (carbon steels, hot-rolled)
- AISI/SAE 4130, 4140, 4340 (alloy steels, normalized / annealed)
- ASME BPVC Sec. II Part A: SA-516 (Gr. 60, 65, 70), SA-537 (Cl. 1, 2)
- EN 10025-2:2019  S235/S275/S355 (t≤16 and 16<t≤40), S450 (t≤16)  — hot-rolled non-alloy
- EN 10025-3:2019  S275N, S355N, S420N, S460N (t≤16)               — normalised
- EN 10025-4:2019  S275M, S355M, S420M, S460M (t≤16)               — thermomechanical
- EN 10025-5:2019  S235W, S355W (t≤16)                              — weathering
- EN 10025-6:2019  S460Q–S960Q (t≤50)                              — quenched & tempered
- JIS G3101:2020   SS400, SS490                                    — general structural
- JIS G3106:2020   SM400A, SM490A, SM490YA, SM570                  — welded structural
- JIS G3136:2020   SN400B, SN490B                                  — seismic building
- GB/T 700:2006    Q235B, Q275B                                    — carbon structural
- GB/T 1591:2018   Q355B, Q390B, Q420B, Q460C                     — high-strength HSLA
- AS/NZS 3678:2016 Grade 250, 350, 400, 450                       — hot-rolled plates
- AS/NZS 3679.1:2016 Grade 300, 350                               — hot-rolled sections
- IS 2062:2011        E250, E300, E350, E410, E450, E550           — hot-rolled structural steel
- CSA G40.20/G40.21:2013  230W, 260W, 300W, 350W, 400W, 480W      — weldable structural (W)
                          260WT, 350WT, 400WT                      — weldable, notch-tough (WT)
                          260AT, 350AT, 400AT                      — weathering (AT)
- UNI 7070:1982       Fe 360, Fe 430, Fe 510 (B/C)                — historic Italian structural (withdrawn)
- EN 10210-1:2006 /
  EN 10219-1:2006     S235H, S275H, S355H, S420H, S460H (t≤16)   — structural hollow sections

ksi → Pa  :  1 ksi = 6 894 757.29 Pa  (1 lbf/in² = 6 894.757 Pa)
MPa → Pa  :  multiply by 1 000 000
"""

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# 1 ksi in Pa (exact conversion used for all values)
_KSI = 6_894_757.293_168_36         # Pa per ksi
_E_STEEL     = 200_000.0 * 1e6      # 200 GPa — AISC-consistent (29,000 ksi ≈ 200 GPa)
_E_STEEL_EN  = 210_000.0 * 1e6      # 210 GPa — Eurocode EN 1993-1-1 §3.2.6(1)
_E_STEEL_JIS = 205_000.0 * 1e6      # 205 GPa — Japanese standard (JIS)
_E_STEEL_CN  = 206_000.0 * 1e6      # 206 GPa — Chinese standard (GB 50017-2017)
_NU_STEEL = 0.3
_RHO_STEEL = 7850.0                 # kg/m³
_MPA       = 1_000_000.0            # Pa per MPa (used for non-ksi presets)


# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SteelPreset:
    """Immutable record holding the nominal properties of a standard steel grade.

    All values are in SI units (Pa, kg/m³, dimensionless).
    """
    standard    : str    # e.g. 'ASTM'
    designation : str    # e.g. 'A572-50'
    name        : str    # human-readable label shown in the UI
    E           : float  # Young's modulus [Pa]
    nu          : float  # Poisson's ratio [-]
    rho         : float  # mass density [kg/m³]
    sigma_y     : float  # yield strength [Pa]
    sigma_u     : float  # ultimate tensile strength [Pa]
    epsilon_u   : float  # elongation at fracture, 2" gauge [-]
    notes       : str    # normative reference / remarks


# ---------------------------------------------------------------------------
# ASTM presets
# ---------------------------------------------------------------------------
_ASTM: list[SteelPreset] = [

    # ------------------------------------------------------------------ A36
    # Table 2 — Fy_min = 36 ksi, Fu = 58–80 ksi (use min 58), el_2" = 23 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A36',
        name        = 'ASTM A36',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 36.0 * _KSI,    # 248 MPa
        sigma_u     = 58.0 * _KSI,    # 400 MPa  (minimum)
        epsilon_u   = 0.23,
        notes       = 'ASTM A36/A36M. Plates, bars and rolled shapes. '
                      'Fu range 58–80 ksi; minimum value used.',
    ),

    # --------------------------------------------------------------- A572-42
    # Table 1 — Gr. 42: Fy = 42 ksi, Fu = 60 ksi, el_2" = 24 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A572-42',
        name        = 'ASTM A572 Gr.42',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 42.0 * _KSI,    # 290 MPa
        sigma_u     = 60.0 * _KSI,    # 414 MPa
        epsilon_u   = 0.24,
        notes       = 'ASTM A572/A572M Grade 42. HSLA columbium-vanadium steel.',
    ),

    # --------------------------------------------------------------- A572-50
    # Table 1 — Gr. 50: Fy = 50 ksi, Fu = 65 ksi, el_2" = 21 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A572-50',
        name        = 'ASTM A572 Gr.50',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 50.0 * _KSI,    # 345 MPa
        sigma_u     = 65.0 * _KSI,    # 448 MPa
        epsilon_u   = 0.21,
        notes       = 'ASTM A572/A572M Grade 50. Most widely used HSLA grade.',
    ),

    # --------------------------------------------------------------- A572-55
    # Table 1 — Gr. 55: Fy = 55 ksi, Fu = 70 ksi, el_2" = 20 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A572-55',
        name        = 'ASTM A572 Gr.55',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 55.0 * _KSI,    # 379 MPa
        sigma_u     = 70.0 * _KSI,    # 483 MPa
        epsilon_u   = 0.20,
        notes       = 'ASTM A572/A572M Grade 55.',
    ),

    # --------------------------------------------------------------- A572-60
    # Table 1 — Gr. 60: Fy = 60 ksi, Fu = 75 ksi, el_2" = 18 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A572-60',
        name        = 'ASTM A572 Gr.60',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 60.0 * _KSI,    # 414 MPa
        sigma_u     = 75.0 * _KSI,    # 517 MPa
        epsilon_u   = 0.18,
        notes       = 'ASTM A572/A572M Grade 60.',
    ),

    # --------------------------------------------------------------- A572-65
    # Table 1 — Gr. 65: Fy = 65 ksi, Fu = 80 ksi, el_2" = 17 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A572-65',
        name        = 'ASTM A572 Gr.65',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 65.0 * _KSI,    # 448 MPa
        sigma_u     = 80.0 * _KSI,    # 552 MPa
        epsilon_u   = 0.17,
        notes       = 'ASTM A572/A572M Grade 65.',
    ),

    # ----------------------------------------------------------------- A992
    # Fy_min = 50 ksi, Fu_min = 65 ksi; AISC: Fy/Fu ≤ 0.85, Fy ≤ 65 ksi
    # el_2" = 21 % (same base as A572-50; A992 references A572 elongation)
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A992',
        name        = 'ASTM A992',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 50.0 * _KSI,    # 345 MPa  (minimum)
        sigma_u     = 65.0 * _KSI,    # 448 MPa  (minimum)
        epsilon_u   = 0.21,
        notes       = 'ASTM A992/A992M. W-shapes (wide-flange). '
                      'Minimum values used; AISC imposes Fy/Fu ≤ 0.85 and Fy ≤ 65 ksi.',
    ),

    # --------------------------------------------------------- A500 Gr.B round
    # Circular HSS: Fy = 42 ksi, Fu = 58 ksi, el_2" = 23 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A500-B-R',
        name        = 'ASTM A500 Gr.B (round)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 42.0 * _KSI,    # 290 MPa
        sigma_u     = 58.0 * _KSI,    # 400 MPa
        epsilon_u   = 0.23,
        notes       = 'ASTM A500/A500M Grade B, round (circular) HSS.',
    ),

    # ------------------------------------------------------- A500 Gr.B shaped
    # Rectangular/square HSS: Fy = 46 ksi, Fu = 58 ksi, el_2" = 23 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A500-B-S',
        name        = 'ASTM A500 Gr.B (shaped)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 46.0 * _KSI,    # 317 MPa
        sigma_u     = 58.0 * _KSI,    # 400 MPa
        epsilon_u   = 0.23,
        notes       = 'ASTM A500/A500M Grade B, shaped (rectangular/square) HSS.',
    ),

    # --------------------------------------------------------- A500 Gr.C round
    # Circular HSS: Fy = 46 ksi, Fu = 62 ksi, el_2" = 21 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A500-C-R',
        name        = 'ASTM A500 Gr.C (round)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 46.0 * _KSI,    # 317 MPa
        sigma_u     = 62.0 * _KSI,    # 427 MPa
        epsilon_u   = 0.21,
        notes       = 'ASTM A500/A500M Grade C, round (circular) HSS.',
    ),

    # ------------------------------------------------------- A500 Gr.C shaped
    # Rectangular/square HSS: Fy = 50 ksi, Fu = 62 ksi, el_2" = 21 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A500-C-S',
        name        = 'ASTM A500 Gr.C (shaped)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 50.0 * _KSI,    # 345 MPa
        sigma_u     = 62.0 * _KSI,    # 427 MPa
        epsilon_u   = 0.21,
        notes       = 'ASTM A500/A500M Grade C, shaped (rectangular/square) HSS.',
    ),

    # ------------------------------------------------------------------ A53-B
    # Pipe: Fy = 35 ksi, Fu = 60 ksi, el_2" = 30 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A53-B',
        name        = 'ASTM A53 Gr.B',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 35.0 * _KSI,    # 241 MPa
        sigma_u     = 60.0 * _KSI,    # 414 MPa
        epsilon_u   = 0.30,
        notes       = 'ASTM A53/A53M Grade B. Welded and seamless steel pipe.',
    ),

    # ----------------------------------------------------------------- A1085
    # Fy = 50 ksi, Fu = 65 ksi, el_2" = 25 %; Fy/Fu ≤ 0.85 (same as A992)
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A1085',
        name        = 'ASTM A1085',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 50.0 * _KSI,    # 345 MPa
        sigma_u     = 65.0 * _KSI,    # 448 MPa
        epsilon_u   = 0.25,
        notes       = 'ASTM A1085/A1085M. HSS with tighter tolerances. '
                      'Fy/Fu ≤ 0.85 required.',
    ),

    # --------------------------------------------------------------- A529-50
    # Gr. 50: Fy = 50 ksi, Fu = 65–100 ksi (use min 65), el_2" = 21 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A529-50',
        name        = 'ASTM A529 Gr.50',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 50.0 * _KSI,    # 345 MPa
        sigma_u     = 65.0 * _KSI,    # 448 MPa  (minimum)
        epsilon_u   = 0.21,
        notes       = 'ASTM A529/A529M Grade 50. Carbon-manganese shapes and bars. '
                      'Fu range 65–100 ksi; minimum value used.',
    ),

    # --------------------------------------------------------------- A529-55
    # Gr. 55: Fy = 55 ksi, Fu = 70–100 ksi (use min 70), el_2" = 20 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A529-55',
        name        = 'ASTM A529 Gr.55',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 55.0 * _KSI,    # 379 MPa
        sigma_u     = 70.0 * _KSI,    # 483 MPa  (minimum)
        epsilon_u   = 0.20,
        notes       = 'ASTM A529/A529M Grade 55. Carbon-manganese shapes and bars. '
                      'Fu range 70–100 ksi; minimum value used.',
    ),

    # --------------------------------------------------------------- A588-A
    # Weathering steel ("Cor-Ten"): Fy = 50 ksi, Fu = 70 ksi, el_2" = 21 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A588-A',
        name        = 'ASTM A588 Gr.A',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 50.0 * _KSI,    # 345 MPa
        sigma_u     = 70.0 * _KSI,    # 483 MPa
        epsilon_u   = 0.21,
        notes       = 'ASTM A588/A588M Grade A. High-strength low-alloy weathering steel. '
                      'Suitable for exposed structures without coating.',
    ),

    # --------------------------------------------------------------- A709-36
    # Bridge equivalent of A36: Fy = 36 ksi, Fu = 58 ksi, el_2" = 23 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A709-36',
        name        = 'ASTM A709 Gr.36',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 36.0 * _KSI,    # 248 MPa
        sigma_u     = 58.0 * _KSI,    # 400 MPa
        epsilon_u   = 0.23,
        notes       = 'ASTM A709/A709M Grade 36. Bridge structural steel (AASHTO LRFD). '
                      'Mechanically equivalent to A36.',
    ),

    # --------------------------------------------------------------- A709-50
    # Bridge equivalent of A572-50: Fy = 50 ksi, Fu = 65 ksi, el_2" = 21 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A709-50',
        name        = 'ASTM A709 Gr.50',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 50.0 * _KSI,    # 345 MPa
        sigma_u     = 65.0 * _KSI,    # 448 MPa
        epsilon_u   = 0.21,
        notes       = 'ASTM A709/A709M Grade 50. Bridge structural steel (AASHTO LRFD). '
                      'Mechanically equivalent to A572-50.',
    ),

    # ------------------------------------------------------------- A709-50W
    # Bridge weathering: Fy = 50 ksi, Fu = 70 ksi, el_2" = 21 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A709-50W',
        name        = 'ASTM A709 Gr.50W',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 50.0 * _KSI,    # 345 MPa
        sigma_u     = 70.0 * _KSI,    # 483 MPa
        epsilon_u   = 0.21,
        notes       = 'ASTM A709/A709M Grade 50W. Weathering bridge steel (AASHTO LRFD).',
    ),

    # --------------------------------------------------------- A709-HPS-50W
    # High-performance weathering: Fy = 50 ksi, Fu = 70 ksi, el_2" = 21 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A709-HPS50W',
        name        = 'ASTM A709 HPS 50W',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 50.0 * _KSI,    # 345 MPa
        sigma_u     = 70.0 * _KSI,    # 483 MPa
        epsilon_u   = 0.21,
        notes       = 'ASTM A709/A709M HPS 50W. High-performance weathering bridge steel. '
                      'Enhanced weldability and toughness vs. Grade 50W.',
    ),

    # --------------------------------------------------------- A709-HPS-70W
    # High-performance weathering: Fy = 70 ksi, Fu = 85 ksi, el_2" = 19 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A709-HPS70W',
        name        = 'ASTM A709 HPS 70W',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 70.0 * _KSI,    # 483 MPa
        sigma_u     = 85.0 * _KSI,    # 586 MPa
        epsilon_u   = 0.19,
        notes       = 'ASTM A709/A709M HPS 70W. High-performance weathering bridge steel.',
    ),

    # ------------------------------------------------------- A709-HPS-100W
    # Ultra-high-strength: Fy = 100 ksi, Fu = 110 ksi, el_2" = 16 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A709-HPS100W',
        name        = 'ASTM A709 HPS 100W',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 100.0 * _KSI,   # 689 MPa
        sigma_u     = 110.0 * _KSI,   # 758 MPa  (minimum)
        epsilon_u   = 0.16,
        notes       = 'ASTM A709/A709M HPS 100W. Ultra-high-strength weathering bridge steel. '
                      'Fu range 110–130 ksi; minimum value used.',
    ),

    # --------------------------------------------------------------- A514 thin
    # Q&T high-strength, t ≤ 2.5": Fy = 100 ksi, Fu = 110 ksi, el_2" = 18 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A514-thin',
        name        = 'ASTM A514 (t ≤ 2.5")',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 100.0 * _KSI,   # 689 MPa
        sigma_u     = 110.0 * _KSI,   # 758 MPa  (minimum)
        epsilon_u   = 0.18,
        notes       = 'ASTM A514/A514M, thickness ≤ 2.5 in. Quenched & tempered '
                      'high-strength steel. Fu range 110–130 ksi; minimum value used.',
    ),

    # -------------------------------------------------------------- A514 thick
    # Q&T high-strength, t > 2.5": Fy = 90 ksi, Fu = 100 ksi, el_2" = 16 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A514-thick',
        name        = 'ASTM A514 (t > 2.5")',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 90.0 * _KSI,    # 621 MPa
        sigma_u     = 100.0 * _KSI,   # 689 MPa  (minimum)
        epsilon_u   = 0.16,
        notes       = 'ASTM A514/A514M, thickness > 2.5 in. Quenched & tempered '
                      'high-strength steel. Fu range 100–130 ksi; minimum value used.',
    ),

    # --------------------------------------------------------------- A913-50
    # QST (Quench & Self-Tempered): Fy = 50 ksi, Fu = 65 ksi, el_2" = 21 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A913-50',
        name        = 'ASTM A913 Gr.50',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 50.0 * _KSI,    # 345 MPa
        sigma_u     = 65.0 * _KSI,    # 448 MPa
        epsilon_u   = 0.21,
        notes       = 'ASTM A913/A913M Grade 50. Quench & self-tempered (QST) W-shapes. '
                      'AISC 341 seismic applications.',
    ),

    # --------------------------------------------------------------- A913-65
    # QST: Fy = 65 ksi, Fu = 80 ksi, el_2" = 17 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A913-65',
        name        = 'ASTM A913 Gr.65',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 65.0 * _KSI,    # 448 MPa
        sigma_u     = 80.0 * _KSI,    # 552 MPa
        epsilon_u   = 0.17,
        notes       = 'ASTM A913/A913M Grade 65. Quench & self-tempered (QST) W-shapes.',
    ),

    # --------------------------------------------------------------- A913-70
    # QST: Fy = 70 ksi, Fu = 90 ksi, el_2" = 15 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A913-70',
        name        = 'ASTM A913 Gr.70',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 70.0 * _KSI,    # 483 MPa
        sigma_u     = 90.0 * _KSI,    # 621 MPa
        epsilon_u   = 0.15,
        notes       = 'ASTM A913/A913M Grade 70. Quench & self-tempered (QST) W-shapes.',
    ),

    # --------------------------------------------------------------- A913-80
    # QST: Fy = 80 ksi, Fu = 100 ksi, el_2" = 14 %
    SteelPreset(
        standard    = 'ASTM',
        designation = 'A913-80',
        name        = 'ASTM A913 Gr.80',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 80.0 * _KSI,    # 552 MPa
        sigma_u     = 100.0 * _KSI,   # 689 MPa
        epsilon_u   = 0.14,
        notes       = 'ASTM A913/A913M Grade 80. Quench & self-tempered (QST) W-shapes.',
    ),
]


# ---------------------------------------------------------------------------
# API presets
# ---------------------------------------------------------------------------
_API: list[SteelPreset] = [

    # ------------------------------------------------------------ API 5L Gr.B
    # PSL1: SMYS = 245 MPa, SMTS = 415 MPa, el_2" ≈ 28 %
    SteelPreset(
        standard    = 'API',
        designation = '5L-GrB',
        name        = 'API 5L Grade B',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 245.0 * _MPA,
        sigma_u     = 415.0 * _MPA,
        epsilon_u   = 0.28,
        notes       = 'API 5L Grade B (PSL1). Welded and seamless linepipe. '
                      'SMYS=245 MPa, SMTS=415 MPa. '
                      'Elongation is wall-thickness-dependent; value shown is approximate.',
    ),

    # ------------------------------------------------------------ API 5L X42
    # PSL1: SMYS = 290 MPa, SMTS = 415 MPa, el_2" ≈ 24 %
    SteelPreset(
        standard    = 'API',
        designation = '5L-X42',
        name        = 'API 5L X42',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 290.0 * _MPA,
        sigma_u     = 415.0 * _MPA,
        epsilon_u   = 0.24,
        notes       = 'API 5L Grade X42 (PSL1). SMYS=290 MPa, SMTS=415 MPa. '
                      'Elongation is approximate.',
    ),

    # ------------------------------------------------------------ API 5L X52
    # PSL1: SMYS = 360 MPa, SMTS = 460 MPa, el_2" ≈ 22 %
    SteelPreset(
        standard    = 'API',
        designation = '5L-X52',
        name        = 'API 5L X52',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 360.0 * _MPA,
        sigma_u     = 460.0 * _MPA,
        epsilon_u   = 0.22,
        notes       = 'API 5L Grade X52 (PSL1). SMYS=360 MPa, SMTS=460 MPa. '
                      'Elongation is approximate.',
    ),

    # ------------------------------------------------------------ API 5L X56
    # PSL1: SMYS = 390 MPa, SMTS = 490 MPa, el_2" ≈ 21 %
    SteelPreset(
        standard    = 'API',
        designation = '5L-X56',
        name        = 'API 5L X56',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 390.0 * _MPA,
        sigma_u     = 490.0 * _MPA,
        epsilon_u   = 0.21,
        notes       = 'API 5L Grade X56 (PSL1). SMYS=390 MPa, SMTS=490 MPa. '
                      'Elongation is approximate.',
    ),

    # ------------------------------------------------------------ API 5L X60
    # PSL1: SMYS = 415 MPa, SMTS = 520 MPa, el_2" ≈ 21 %
    SteelPreset(
        standard    = 'API',
        designation = '5L-X60',
        name        = 'API 5L X60',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 415.0 * _MPA,
        sigma_u     = 520.0 * _MPA,
        epsilon_u   = 0.21,
        notes       = 'API 5L Grade X60 (PSL1). SMYS=415 MPa, SMTS=520 MPa. '
                      'Elongation is approximate.',
    ),

    # ------------------------------------------------------------ API 5L X65
    # PSL1: SMYS = 450 MPa, SMTS = 535 MPa, el_2" ≈ 20 %
    SteelPreset(
        standard    = 'API',
        designation = '5L-X65',
        name        = 'API 5L X65',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 450.0 * _MPA,
        sigma_u     = 535.0 * _MPA,
        epsilon_u   = 0.20,
        notes       = 'API 5L Grade X65 (PSL1). SMYS=450 MPa, SMTS=535 MPa. '
                      'Elongation is approximate.',
    ),

    # ------------------------------------------------------------ API 5L X70
    # PSL1: SMYS = 485 MPa, SMTS = 570 MPa, el_2" ≈ 19 %
    SteelPreset(
        standard    = 'API',
        designation = '5L-X70',
        name        = 'API 5L X70',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 485.0 * _MPA,
        sigma_u     = 570.0 * _MPA,
        epsilon_u   = 0.19,
        notes       = 'API 5L Grade X70 (PSL1). SMYS=485 MPa, SMTS=570 MPa. '
                      'Elongation is approximate.',
    ),

    # ------------------------------------------------------------ API 5L X80
    # PSL1: SMYS = 555 MPa, SMTS = 625 MPa, el_2" ≈ 18 %
    SteelPreset(
        standard    = 'API',
        designation = '5L-X80',
        name        = 'API 5L X80',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 555.0 * _MPA,
        sigma_u     = 625.0 * _MPA,
        epsilon_u   = 0.18,
        notes       = 'API 5L Grade X80 (PSL1). SMYS=555 MPa, SMTS=625 MPa. '
                      'Elongation is approximate.',
    ),

    # ------------------------------------------------------- API 2H Grade 42
    # Offshore structural plate: Fy = 42 ksi (290 MPa), Fu = 62 ksi (427 MPa), el = 22 %
    SteelPreset(
        standard    = 'API',
        designation = '2H-Gr42',
        name        = 'API 2H Grade 42',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 42.0 * _KSI,    # 290 MPa
        sigma_u     = 62.0 * _KSI,    # 427 MPa
        epsilon_u   = 0.22,
        notes       = 'API 2H Grade 42. Normalised carbon-manganese plate for '
                      'offshore structures. Fy=290 MPa, Fu=427 MPa. '
                      'API 2W/2Y Gr.42 share the same mechanical minimums.',
    ),

    # ------------------------------------------------------- API 2H Grade 50
    # Offshore structural plate: Fy = 50 ksi (345 MPa), Fu = 70 ksi (483 MPa), el = 22 %
    SteelPreset(
        standard    = 'API',
        designation = '2H-Gr50',
        name        = 'API 2H Grade 50',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 50.0 * _KSI,    # 345 MPa
        sigma_u     = 70.0 * _KSI,    # 483 MPa
        epsilon_u   = 0.22,
        notes       = 'API 2H Grade 50. Normalised carbon-manganese plate for '
                      'offshore structures. Fy=345 MPa, Fu=483 MPa. '
                      'API 2W/2Y Gr.50T share the same mechanical minimums.',
    ),
]


# ---------------------------------------------------------------------------
# AISI/SAE presets  (carbon and alloy steels)
# Source: Shigley's Mechanical Engineering Design, ASM Metals Handbook
# ---------------------------------------------------------------------------
_AISI: list[SteelPreset] = [

    # ---------------------------------------------------------- AISI 1020 HR
    # Hot-rolled: Fy = 210 MPa, Fu = 380 MPa, el_2" = 36 %
    SteelPreset(
        standard    = 'AISI',
        designation = '1020-HR',
        name        = 'AISI 1020 (hot-rolled)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 210.0 * _MPA,
        sigma_u     = 380.0 * _MPA,
        epsilon_u   = 0.36,
        notes       = 'AISI/SAE 1020 low-carbon steel, hot-rolled condition. '
                      'Source: Shigley 9th ed. / ASM Handbook Vol. 1.',
    ),

    # ---------------------------------------------------------- AISI 1040 HR
    # Hot-rolled: Fy = 290 MPa, Fu = 520 MPa, el_2" = 28 %
    SteelPreset(
        standard    = 'AISI',
        designation = '1040-HR',
        name        = 'AISI 1040 (hot-rolled)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 290.0 * _MPA,
        sigma_u     = 520.0 * _MPA,
        epsilon_u   = 0.28,
        notes       = 'AISI/SAE 1040 medium-carbon steel, hot-rolled condition.',
    ),

    # ---------------------------------------------------------- AISI 1045 HR
    # Hot-rolled: Fy = 310 MPa, Fu = 570 MPa, el_2" = 20 %
    SteelPreset(
        standard    = 'AISI',
        designation = '1045-HR',
        name        = 'AISI 1045 (hot-rolled)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 310.0 * _MPA,
        sigma_u     = 570.0 * _MPA,
        epsilon_u   = 0.20,
        notes       = 'AISI/SAE 1045 medium-carbon steel, hot-rolled condition.',
    ),

    # -------------------------------------------------------- AISI 4130 norm.
    # Normalized (870 °C): Fy = 435 MPa, Fu = 670 MPa, el_2" = 26 %
    SteelPreset(
        standard    = 'AISI',
        designation = '4130-N',
        name        = 'AISI 4130 (normalized)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 435.0 * _MPA,
        sigma_u     = 670.0 * _MPA,
        epsilon_u   = 0.26,
        notes       = 'AISI/SAE 4130 Cr-Mo low-alloy steel, normalized at 870 °C. '
                      'Common in aerospace and mechanical structures. '
                      'Q&T grades can reach significantly higher strengths.',
    ),

    # -------------------------------------------------------- AISI 4140 ann.
    # Annealed: Fy = 415 MPa, Fu = 655 MPa, el_2" = 26 %
    SteelPreset(
        standard    = 'AISI',
        designation = '4140-A',
        name        = 'AISI 4140 (annealed)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 415.0 * _MPA,
        sigma_u     = 655.0 * _MPA,
        epsilon_u   = 0.26,
        notes       = 'AISI/SAE 4140 Cr-Mo alloy steel, annealed condition. '
                      'Q&T to 315 °C can raise Fy above 1500 MPa.',
    ),

    # -------------------------------------------------------- AISI 4340 norm.
    # Normalized: Fy = 470 MPa, Fu = 745 MPa, el_2" = 22 %
    SteelPreset(
        standard    = 'AISI',
        designation = '4340-N',
        name        = 'AISI 4340 (normalized)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 470.0 * _MPA,
        sigma_u     = 745.0 * _MPA,
        epsilon_u   = 0.22,
        notes       = 'AISI/SAE 4340 Ni-Cr-Mo low-alloy steel, normalized condition. '
                      'High toughness; widely used for heavy machinery and shafts.',
    ),
]


# ---------------------------------------------------------------------------
# ASME presets  (pressure vessel / boiler steels)
# Source: ASME BPVC Section II Part A
# ---------------------------------------------------------------------------
_ASME: list[SteelPreset] = [

    # -------------------------------------------------- SA-516 Grade 60
    # Carbon steel PV plate: Fy = 220 MPa, Fu_min = 415 MPa, el_2" = 25 %
    SteelPreset(
        standard    = 'ASME',
        designation = 'SA-516-60',
        name        = 'ASME SA-516 Gr.60',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 220.0 * _MPA,
        sigma_u     = 415.0 * _MPA,   # minimum; range 415–550 MPa
        epsilon_u   = 0.25,
        notes       = 'ASME BPVC Sec. II Part A, SA-516 Grade 60. '
                      'Carbon steel plates for moderate/lower-temperature pressure vessels. '
                      'Fu range 415–550 MPa; minimum used.',
    ),

    # -------------------------------------------------- SA-516 Grade 65
    # Carbon steel PV plate: Fy = 240 MPa, Fu_min = 450 MPa, el_2" = 23 %
    SteelPreset(
        standard    = 'ASME',
        designation = 'SA-516-65',
        name        = 'ASME SA-516 Gr.65',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 240.0 * _MPA,
        sigma_u     = 450.0 * _MPA,   # minimum; range 450–585 MPa
        epsilon_u   = 0.23,
        notes       = 'ASME BPVC Sec. II Part A, SA-516 Grade 65. '
                      'Carbon steel pressure vessel plate. '
                      'Fu range 450–585 MPa; minimum used.',
    ),

    # -------------------------------------------------- SA-516 Grade 70
    # Most common PV plate: Fy = 260 MPa, Fu_min = 485 MPa, el_2" = 21 %
    SteelPreset(
        standard    = 'ASME',
        designation = 'SA-516-70',
        name        = 'ASME SA-516 Gr.70',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 260.0 * _MPA,
        sigma_u     = 485.0 * _MPA,   # minimum; range 485–620 MPa
        epsilon_u   = 0.21,
        notes       = 'ASME BPVC Sec. II Part A, SA-516 Grade 70. '
                      'Most widely used carbon steel pressure vessel plate. '
                      'Fu range 485–620 MPa; minimum used.',
    ),

    # ------------------------------------------------- SA-537 Class 1
    # Normalised C-Mn-Si PV plate: Fy = 345 MPa, Fu_min = 485 MPa, el_2" = 22 %
    SteelPreset(
        standard    = 'ASME',
        designation = 'SA-537-Cl1',
        name        = 'ASME SA-537 Cl.1',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 345.0 * _MPA,
        sigma_u     = 485.0 * _MPA,   # minimum; range 485–620 MPa
        epsilon_u   = 0.22,
        notes       = 'ASME BPVC Sec. II Part A, SA-537 Class 1. '
                      'Normalised carbon-manganese-silicon pressure vessel plate. '
                      'Fu range 485–620 MPa; minimum used.',
    ),

    # ------------------------------------------------- SA-537 Class 2
    # Q&T C-Mn-Si PV plate: Fy = 415 MPa, Fu_min = 550 MPa, el_2" = 22 %
    SteelPreset(
        standard    = 'ASME',
        designation = 'SA-537-Cl2',
        name        = 'ASME SA-537 Cl.2',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 415.0 * _MPA,
        sigma_u     = 550.0 * _MPA,   # minimum; range 550–690 MPa
        epsilon_u   = 0.22,
        notes       = 'ASME BPVC Sec. II Part A, SA-537 Class 2. '
                      'Quenched & tempered carbon-manganese-silicon pressure vessel plate. '
                      'Fu range 550–690 MPa; minimum used.',
    ),
]


# ---------------------------------------------------------------------------
# EN (European) presets
# Source: EN 10025-2/3/4/5/6 : 2019
#
# Note on E:  Eurocode EN 1993-1-1 §3.2.6(1) specifies E = 210 000 MPa.
# Note on ε_u: EN uses proportional gauge L0 = 5.65√S0 (≈ A5 in older notation).
# Note on σ_u: minimum of the Rm range is used throughout.
# Note on thickness: two classes given for high-tonnage Part-2 grades;
#   all other parts use the t ≤ 16 mm (highest-strength) range only.
# ---------------------------------------------------------------------------
_EN: list[SteelPreset] = [

    # ================================================================
    # EN 10025-2 — hot-rolled non-alloy structural steels
    # ================================================================

    # ---------------------------------------------------- S235 t ≤ 16 mm
    # Table 7: ReH = 235, Rm = 360–510, A = 26 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S235-t16',
        name        = 'EN S235 (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 235.0 * _MPA,
        sigma_u     = 360.0 * _MPA,   # minimum; range 360–510 MPa
        epsilon_u   = 0.26,
        notes       = 'EN 10025-2:2019, S235, thickness ≤ 16 mm. '
                      'Hot-rolled non-alloy structural steel. '
                      'E = 210 GPa (EN 1993-1-1). Rm range 360–510 MPa; minimum used.',
    ),

    # -------------------------------------------------- S235 16 < t ≤ 40 mm
    # Table 7: ReH = 225, Rm = 360–510, A = 26 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S235-t40',
        name        = 'EN S235 (16 < t ≤ 40 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 225.0 * _MPA,
        sigma_u     = 360.0 * _MPA,
        epsilon_u   = 0.26,
        notes       = 'EN 10025-2:2019, S235, thickness 16–40 mm. '
                      'Hot-rolled non-alloy structural steel.',
    ),

    # ---------------------------------------------------- S275 t ≤ 16 mm
    # Table 7: ReH = 275, Rm = 430–580, A = 23 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S275-t16',
        name        = 'EN S275 (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 275.0 * _MPA,
        sigma_u     = 430.0 * _MPA,   # minimum; range 430–580 MPa
        epsilon_u   = 0.23,
        notes       = 'EN 10025-2:2019, S275, thickness ≤ 16 mm. '
                      'Hot-rolled non-alloy structural steel. '
                      'E = 210 GPa (EN 1993-1-1). Rm range 430–580 MPa; minimum used.',
    ),

    # -------------------------------------------------- S275 16 < t ≤ 40 mm
    # Table 7: ReH = 265, Rm = 410–560, A = 23 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S275-t40',
        name        = 'EN S275 (16 < t ≤ 40 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 265.0 * _MPA,
        sigma_u     = 410.0 * _MPA,
        epsilon_u   = 0.23,
        notes       = 'EN 10025-2:2019, S275, thickness 16–40 mm. '
                      'Hot-rolled non-alloy structural steel.',
    ),

    # ---------------------------------------------------- S355 t ≤ 16 mm
    # Table 7: ReH = 355, Rm = 490–630, A = 22 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S355-t16',
        name        = 'EN S355 (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 355.0 * _MPA,
        sigma_u     = 490.0 * _MPA,   # minimum; range 490–630 MPa
        epsilon_u   = 0.22,
        notes       = 'EN 10025-2:2019, S355, thickness ≤ 16 mm. '
                      'Most widely used European structural steel. '
                      'E = 210 GPa (EN 1993-1-1). Rm range 490–630 MPa; minimum used.',
    ),

    # -------------------------------------------------- S355 16 < t ≤ 40 mm
    # Table 7: ReH = 345, Rm = 490–630, A = 22 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S355-t40',
        name        = 'EN S355 (16 < t ≤ 40 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 345.0 * _MPA,
        sigma_u     = 490.0 * _MPA,
        epsilon_u   = 0.22,
        notes       = 'EN 10025-2:2019, S355, thickness 16–40 mm. '
                      'Most widely used European structural steel.',
    ),

    # ---------------------------------------------------- S450 t ≤ 16 mm
    # Table 7 (2019 revision): ReH = 440, Rm = 550–720, A = 17 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S450-t16',
        name        = 'EN S450 (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 440.0 * _MPA,
        sigma_u     = 550.0 * _MPA,   # minimum; range 550–720 MPa
        epsilon_u   = 0.17,
        notes       = 'EN 10025-2:2019, S450, thickness ≤ 16 mm. '
                      'High-strength hot-rolled structural steel (2019 revision). '
                      'Rm range 550–720 MPa; minimum used.',
    ),

    # ================================================================
    # EN 10025-3 — normalized / normalized-rolled (N / NL)
    # NL subgrade has lower CVN temperature requirement; same Fy/Fu.
    # ================================================================

    # ---------------------------------------------------- S275N t ≤ 16 mm
    # Table 4: ReH = 275, Rm = 370–510, A = 24 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S275N-t16',
        name        = 'EN S275N (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 275.0 * _MPA,
        sigma_u     = 370.0 * _MPA,   # minimum; range 370–510 MPa
        epsilon_u   = 0.24,
        notes       = 'EN 10025-3:2019, S275N, thickness ≤ 16 mm. '
                      'Normalized fine-grain structural steel. '
                      'S275NL has same mechanical values, improved CVN at −50 °C.',
    ),

    # ---------------------------------------------------- S355N t ≤ 16 mm
    # Table 4: ReH = 355, Rm = 470–630, A = 22 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S355N-t16',
        name        = 'EN S355N (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 355.0 * _MPA,
        sigma_u     = 470.0 * _MPA,   # minimum; range 470–630 MPa
        epsilon_u   = 0.22,
        notes       = 'EN 10025-3:2019, S355N, thickness ≤ 16 mm. '
                      'Normalized fine-grain structural steel. '
                      'S355NL has same mechanical values, improved CVN at −50 °C.',
    ),

    # ---------------------------------------------------- S420N t ≤ 16 mm
    # Table 4: ReH = 420, Rm = 520–680, A = 19 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S420N-t16',
        name        = 'EN S420N (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 420.0 * _MPA,
        sigma_u     = 520.0 * _MPA,   # minimum; range 520–680 MPa
        epsilon_u   = 0.19,
        notes       = 'EN 10025-3:2019, S420N, thickness ≤ 16 mm. '
                      'Normalized high-strength fine-grain structural steel.',
    ),

    # ---------------------------------------------------- S460N t ≤ 16 mm
    # Table 4: ReH = 460, Rm = 540–720, A = 17 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S460N-t16',
        name        = 'EN S460N (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 460.0 * _MPA,
        sigma_u     = 540.0 * _MPA,   # minimum; range 540–720 MPa
        epsilon_u   = 0.17,
        notes       = 'EN 10025-3:2019, S460N, thickness ≤ 16 mm. '
                      'Normalized high-strength fine-grain structural steel.',
    ),

    # ================================================================
    # EN 10025-4 — thermomechanically rolled (M / ML)
    # ================================================================

    # ---------------------------------------------------- S275M t ≤ 16 mm
    # Table 4: ReH = 275, Rm = 360–430, A = 24 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S275M-t16',
        name        = 'EN S275M (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 275.0 * _MPA,
        sigma_u     = 360.0 * _MPA,   # minimum; range 360–430 MPa
        epsilon_u   = 0.24,
        notes       = 'EN 10025-4:2019, S275M, thickness ≤ 16 mm. '
                      'Thermomechanically rolled fine-grain structural steel. '
                      'S275ML has improved CVN at −50 °C.',
    ),

    # ---------------------------------------------------- S355M t ≤ 16 mm
    # Table 4: ReH = 355, Rm = 470–630, A = 22 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S355M-t16',
        name        = 'EN S355M (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 355.0 * _MPA,
        sigma_u     = 470.0 * _MPA,   # minimum; range 470–630 MPa
        epsilon_u   = 0.22,
        notes       = 'EN 10025-4:2019, S355M, thickness ≤ 16 mm. '
                      'Thermomechanically rolled fine-grain structural steel.',
    ),

    # ---------------------------------------------------- S420M t ≤ 16 mm
    # Table 4: ReH = 420, Rm = 500–660, A = 19 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S420M-t16',
        name        = 'EN S420M (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 420.0 * _MPA,
        sigma_u     = 500.0 * _MPA,   # minimum; range 500–660 MPa
        epsilon_u   = 0.19,
        notes       = 'EN 10025-4:2019, S420M, thickness ≤ 16 mm. '
                      'Thermomechanically rolled high-strength fine-grain steel.',
    ),

    # ---------------------------------------------------- S460M t ≤ 16 mm
    # Table 4: ReH = 460, Rm = 530–720, A = 17 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S460M-t16',
        name        = 'EN S460M (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 460.0 * _MPA,
        sigma_u     = 530.0 * _MPA,   # minimum; range 530–720 MPa
        epsilon_u   = 0.17,
        notes       = 'EN 10025-4:2019, S460M, thickness ≤ 16 mm. '
                      'Thermomechanically rolled high-strength fine-grain steel.',
    ),

    # ================================================================
    # EN 10025-5 — structural steels with improved atmospheric corrosion
    #              resistance (weathering — equivalent to "Cor-Ten")
    # ================================================================

    # ---------------------------------------------------- S235W t ≤ 16 mm
    # Table 4: ReH = 235, Rm = 360–510, A = 26 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S235W-t16',
        name        = 'EN S235W (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 235.0 * _MPA,
        sigma_u     = 360.0 * _MPA,
        epsilon_u   = 0.26,
        notes       = 'EN 10025-5:2019, S235W, thickness ≤ 16 mm. '
                      'Weathering structural steel. Suitable for uncoated exposed structures.',
    ),

    # ---------------------------------------------------- S355W t ≤ 16 mm
    # Table 4: ReH = 355, Rm = 490–630, A = 22 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S355W-t16',
        name        = 'EN S355W (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 355.0 * _MPA,
        sigma_u     = 490.0 * _MPA,
        epsilon_u   = 0.22,
        notes       = 'EN 10025-5:2019, S355W, thickness ≤ 16 mm. '
                      'Weathering high-strength structural steel.',
    ),

    # ================================================================
    # EN 10025-6 — quenched and tempered (Q / QL / QL1)
    # QL / QL1 subgrades: same Fy/Fu, tighter CVN requirements.
    # Values below are for the principal thickness range t ≤ 50 mm.
    # ================================================================

    # ---------------------------------------------------- S460Q t ≤ 50 mm
    # Table 4: ReH = 460, Rm = 570–720, A = 17 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S460Q-t50',
        name        = 'EN S460Q (t ≤ 50 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 460.0 * _MPA,
        sigma_u     = 570.0 * _MPA,   # minimum; range 570–720 MPa
        epsilon_u   = 0.17,
        notes       = 'EN 10025-6:2019, S460Q, thickness ≤ 50 mm. '
                      'Quenched & tempered high-strength structural steel. '
                      'S460QL/QL1 same mechanical values, increased toughness.',
    ),

    # ---------------------------------------------------- S500Q t ≤ 50 mm
    # Table 4: ReH = 500, Rm = 590–770, A = 17 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S500Q-t50',
        name        = 'EN S500Q (t ≤ 50 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 500.0 * _MPA,
        sigma_u     = 590.0 * _MPA,   # minimum; range 590–770 MPa
        epsilon_u   = 0.17,
        notes       = 'EN 10025-6:2019, S500Q, thickness ≤ 50 mm. '
                      'Quenched & tempered high-strength structural steel.',
    ),

    # ---------------------------------------------------- S550Q t ≤ 50 mm
    # Table 4: ReH = 550, Rm = 640–820, A = 16 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S550Q-t50',
        name        = 'EN S550Q (t ≤ 50 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 550.0 * _MPA,
        sigma_u     = 640.0 * _MPA,   # minimum; range 640–820 MPa
        epsilon_u   = 0.16,
        notes       = 'EN 10025-6:2019, S550Q, thickness ≤ 50 mm. '
                      'Quenched & tempered high-strength structural steel.',
    ),

    # ---------------------------------------------------- S620Q t ≤ 50 mm
    # Table 4: ReH = 620, Rm = 700–890, A = 15 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S620Q-t50',
        name        = 'EN S620Q (t ≤ 50 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 620.0 * _MPA,
        sigma_u     = 700.0 * _MPA,   # minimum; range 700–890 MPa
        epsilon_u   = 0.15,
        notes       = 'EN 10025-6:2019, S620Q, thickness ≤ 50 mm. '
                      'Quenched & tempered high-strength structural steel.',
    ),

    # ---------------------------------------------------- S690Q t ≤ 50 mm
    # Table 4: ReH = 690, Rm = 770–940, A = 14 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S690Q-t50',
        name        = 'EN S690Q (t ≤ 50 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 690.0 * _MPA,
        sigma_u     = 770.0 * _MPA,   # minimum; range 770–940 MPa
        epsilon_u   = 0.14,
        notes       = 'EN 10025-6:2019, S690Q, thickness ≤ 50 mm. '
                      'Quenched & tempered high-strength structural steel.',
    ),

    # ---------------------------------------------------- S890Q t ≤ 50 mm
    # Table 4: ReH = 890, Rm = 940–1100, A = 11 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S890Q-t50',
        name        = 'EN S890Q (t ≤ 50 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 890.0 * _MPA,
        sigma_u     = 940.0 * _MPA,   # minimum; range 940–1100 MPa
        epsilon_u   = 0.11,
        notes       = 'EN 10025-6:2019, S890Q, thickness ≤ 50 mm. '
                      'Ultra-high-strength quenched & tempered structural steel.',
    ),

    # ---------------------------------------------------- S960Q t ≤ 50 mm
    # Table 4: ReH = 960, Rm = 980–1150, A = 10 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S960Q-t50',
        name        = 'EN S960Q (t ≤ 50 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 960.0 * _MPA,
        sigma_u     = 980.0 * _MPA,   # minimum; range 980–1150 MPa
        epsilon_u   = 0.10,
        notes       = 'EN 10025-6:2019, S960Q, thickness ≤ 50 mm. '
                      'Ultra-high-strength quenched & tempered structural steel.',
    ),

    # ================================================================
    # EN 10210-1 / EN 10219-1 — structural hollow sections (t ≤ 16 mm)
    # ================================================================
    # EN 10210-1:2006 (hot-finished) and EN 10219-1:2006 (cold-formed).
    # Fy/Fu values are identical for corresponding grades; the 'H' suffix
    # identifies the hollow-section product form.  E = 210 GPa (EC3).
    # Elongation: proportional gauge L₀ = 5.65√S₀.

    # ---------------------------------------------------- S235H t ≤ 16 mm
    # Table 1: ReH = 235, Rm = 360–510, A = 26 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S235H-t16',
        name        = 'EN S235H (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 235.0 * _MPA,
        sigma_u     = 360.0 * _MPA,   # minimum; range 360–510 MPa
        epsilon_u   = 0.26,
        notes       = 'EN 10210-1:2006 / EN 10219-1:2006, S235H, thickness ≤ 16 mm. '
                      'Structural hollow sections (hot-finished / cold-formed). '
                      'Fy/Fu identical to EN 10025-2 S235. Rm range 360–510 MPa; minimum used.',
    ),

    # ---------------------------------------------------- S275H t ≤ 16 mm
    # Table 1: ReH = 275, Rm = 430–580, A = 23 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S275H-t16',
        name        = 'EN S275H (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 275.0 * _MPA,
        sigma_u     = 430.0 * _MPA,   # minimum; range 430–580 MPa
        epsilon_u   = 0.23,
        notes       = 'EN 10210-1:2006 / EN 10219-1:2006, S275H, thickness ≤ 16 mm. '
                      'Structural hollow sections. '
                      'Fy/Fu identical to EN 10025-2 S275. Rm range 430–580 MPa; minimum used.',
    ),

    # ---------------------------------------------------- S355H t ≤ 16 mm
    # Table 1: ReH = 355, Rm = 470–630, A = 22 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S355H-t16',
        name        = 'EN S355H (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 355.0 * _MPA,
        sigma_u     = 470.0 * _MPA,   # minimum; range 470–630 MPa
        epsilon_u   = 0.22,
        notes       = 'EN 10210-1:2006 / EN 10219-1:2006, S355H, thickness ≤ 16 mm. '
                      'Structural hollow sections. '
                      'Fy/Fu identical to EN 10025-3 S355N. Rm range 470–630 MPa; minimum used.',
    ),

    # ---------------------------------------------------- S420H t ≤ 16 mm
    # Table 1: ReH = 420, Rm = 500–660, A = 19 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S420H-t16',
        name        = 'EN S420H (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 420.0 * _MPA,
        sigma_u     = 500.0 * _MPA,   # minimum; range 500–660 MPa
        epsilon_u   = 0.19,
        notes       = 'EN 10210-1:2006 / EN 10219-1:2006, S420H, thickness ≤ 16 mm. '
                      'Structural hollow sections. '
                      'Fy/Fu identical to EN 10025-3 S420N. Rm range 500–660 MPa; minimum used.',
    ),

    # ---------------------------------------------------- S460H t ≤ 16 mm
    # Table 1: ReH = 460, Rm = 540–720, A = 17 %
    SteelPreset(
        standard    = 'EN',
        designation = 'S460H-t16',
        name        = 'EN S460H (t ≤ 16 mm)',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 460.0 * _MPA,
        sigma_u     = 540.0 * _MPA,   # minimum; range 540–720 MPa
        epsilon_u   = 0.17,
        notes       = 'EN 10210-1:2006 / EN 10219-1:2006, S460H, thickness ≤ 16 mm. '
                      'Structural hollow sections. '
                      'Fy/Fu identical to EN 10025-3 S460N. Rm range 540–720 MPa; minimum used.',
    ),
]


# ---------------------------------------------------------------------------
# JIS presets  (Japanese Industrial Standards)
# Source: JIS G3101:2020 (SS), JIS G3106:2020 (SM), JIS G3136:2020 (SN)
# E = 205 GPa, elongation = proportional gauge L₀ = 5.65√S₀ (A₅)
# ---------------------------------------------------------------------------
_JIS: list[SteelPreset] = [

    # =========================================================
    # JIS G3101 — general structural rolled steel
    # =========================================================

    # ------------------------------------------------ SS400 t ≤ 16 mm
    # Fy = 245 MPa, Fu = 400–510 MPa, A₅ = 21 %
    SteelPreset(
        standard    = 'JIS',
        designation = 'SS400-t16',
        name        = 'JIS SS400 (t ≤ 16 mm)',
        E           = _E_STEEL_JIS,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 245.0 * _MPA,
        sigma_u     = 400.0 * _MPA,   # minimum; range 400–510 MPa
        epsilon_u   = 0.21,
        notes       = 'JIS G3101:2020, SS400, t ≤ 16 mm. '
                      'Most widely used Japanese general structural steel. '
                      'E = 205 GPa (JIS). Rm range 400–510 MPa; minimum used.',
    ),

    # ------------------------------------------------ SS490 t ≤ 16 mm
    # Fy = 285 MPa, Fu = 490–610 MPa, A₅ = 19 %
    SteelPreset(
        standard    = 'JIS',
        designation = 'SS490-t16',
        name        = 'JIS SS490 (t ≤ 16 mm)',
        E           = _E_STEEL_JIS,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 285.0 * _MPA,
        sigma_u     = 490.0 * _MPA,   # minimum; range 490–610 MPa
        epsilon_u   = 0.19,
        notes       = 'JIS G3101:2020, SS490, t ≤ 16 mm. '
                      'General structural rolled steel. Rm range 490–610 MPa; minimum used.',
    ),

    # =========================================================
    # JIS G3106 — rolled steel for welded structures
    # =========================================================

    # ----------------------------------------------- SM400A t ≤ 16 mm
    # Fy = 245 MPa, Fu = 400–510 MPa, A₅ = 21 %
    SteelPreset(
        standard    = 'JIS',
        designation = 'SM400A-t16',
        name        = 'JIS SM400A (t ≤ 16 mm)',
        E           = _E_STEEL_JIS,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 245.0 * _MPA,
        sigma_u     = 400.0 * _MPA,   # minimum; range 400–510 MPa
        epsilon_u   = 0.21,
        notes       = 'JIS G3106:2020, SM400A, t ≤ 16 mm. '
                      'Rolled steel for welded structures. '
                      'Sub-grade A: no Charpy impact requirement.',
    ),

    # ----------------------------------------------- SM490A t ≤ 16 mm
    # Fy = 325 MPa, Fu = 490–610 MPa, A₅ = 17 %
    SteelPreset(
        standard    = 'JIS',
        designation = 'SM490A-t16',
        name        = 'JIS SM490A (t ≤ 16 mm)',
        E           = _E_STEEL_JIS,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 325.0 * _MPA,
        sigma_u     = 490.0 * _MPA,   # minimum; range 490–610 MPa
        epsilon_u   = 0.17,
        notes       = 'JIS G3106:2020, SM490A, t ≤ 16 mm. '
                      'Rolled steel for welded structures.',
    ),

    # ---------------------------------------------- SM490YA t ≤ 16 mm
    # Fy = 365 MPa, Fu = 490–610 MPa, A₅ = 17 %
    SteelPreset(
        standard    = 'JIS',
        designation = 'SM490YA-t16',
        name        = 'JIS SM490YA (t ≤ 16 mm)',
        E           = _E_STEEL_JIS,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 365.0 * _MPA,
        sigma_u     = 490.0 * _MPA,   # minimum; range 490–610 MPa
        epsilon_u   = 0.17,
        notes       = 'JIS G3106:2020, SM490YA, t ≤ 16 mm. '
                      'Higher-yield variant of SM490; frequently used in bridge design.',
    ),

    # ------------------------------------------------ SM570 t ≤ 16 mm
    # Fy = 460 MPa, Fu = 570–720 MPa, A₅ = 19 %
    SteelPreset(
        standard    = 'JIS',
        designation = 'SM570-t16',
        name        = 'JIS SM570 (t ≤ 16 mm)',
        E           = _E_STEEL_JIS,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 460.0 * _MPA,
        sigma_u     = 570.0 * _MPA,   # minimum; range 570–720 MPa
        epsilon_u   = 0.19,
        notes       = 'JIS G3106:2020, SM570, t ≤ 16 mm. '
                      'High-strength rolled steel for welded structures. '
                      'Rm range 570–720 MPa; minimum used.',
    ),

    # =========================================================
    # JIS G3136 — rolled steel for building structures (seismic)
    # Fy is specified as both minimum AND maximum for ductility control.
    # =========================================================

    # ---------------------------------------------------- SN400B
    # Fy = 235–355 MPa, Fu = 400–510 MPa, A₅ = 21 %
    SteelPreset(
        standard    = 'JIS',
        designation = 'SN400B',
        name        = 'JIS SN400B',
        E           = _E_STEEL_JIS,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 235.0 * _MPA,   # minimum; maximum = 355 MPa (seismic overstrength control)
        sigma_u     = 400.0 * _MPA,   # minimum; range 400–510 MPa
        epsilon_u   = 0.21,
        notes       = 'JIS G3136:2020, SN400B. '
                      'Rolled steel for building structures (seismic). '
                      'Fy specified as 235–355 MPa (min/max) for ductility control; '
                      'minimum value used here.',
    ),

    # ---------------------------------------------------- SN490B
    # Fy = 325–445 MPa, Fu = 490–610 MPa, A₅ = 17 %
    SteelPreset(
        standard    = 'JIS',
        designation = 'SN490B',
        name        = 'JIS SN490B',
        E           = _E_STEEL_JIS,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 325.0 * _MPA,   # minimum; maximum = 445 MPa (seismic overstrength control)
        sigma_u     = 490.0 * _MPA,   # minimum; range 490–610 MPa
        epsilon_u   = 0.17,
        notes       = 'JIS G3136:2020, SN490B. '
                      'Rolled steel for building structures (seismic). '
                      'Fy specified as 325–445 MPa (min/max) for ductility control; '
                      'minimum value used here.',
    ),
]


# ---------------------------------------------------------------------------
# GB/T presets  (Chinese National Standards)
# Source: GB/T 700:2006 (Q235/Q275), GB/T 1591:2018 (Q355–Q460)
# E = 206 GPa (GB 50017-2017 §3.4), elongation = proportional gauge A₅ (L₀ = 5.65√S₀)
# ---------------------------------------------------------------------------
_GB: list[SteelPreset] = [

    # ================================================
    # GB/T 700 — carbon structural steel
    # ================================================

    # ----------------------------------------------- Q235B t ≤ 16 mm
    # Re = 235 MPa, Rm = 370–500 MPa, A₅ = 26 %
    SteelPreset(
        standard    = 'GB',
        designation = 'Q235B-t16',
        name        = 'GB Q235B (t ≤ 16 mm)',
        E           = _E_STEEL_CN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 235.0 * _MPA,
        sigma_u     = 370.0 * _MPA,   # minimum; range 370–500 MPa
        epsilon_u   = 0.26,
        notes       = 'GB/T 700:2006, Q235B, t ≤ 16 mm. '
                      'Most widely used Chinese structural steel. '
                      'E = 206 GPa (GB 50017-2017). '
                      'Rm range 370–500 MPa; minimum used.',
    ),

    # ----------------------------------------- Q235B 16 < t ≤ 40 mm
    # Re = 225 MPa, Rm = 370–500 MPa, A₅ = 26 %
    SteelPreset(
        standard    = 'GB',
        designation = 'Q235B-t40',
        name        = 'GB Q235B (16 < t ≤ 40 mm)',
        E           = _E_STEEL_CN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 225.0 * _MPA,
        sigma_u     = 370.0 * _MPA,
        epsilon_u   = 0.26,
        notes       = 'GB/T 700:2006, Q235B, 16 < t ≤ 40 mm.',
    ),

    # ----------------------------------------------- Q275B t ≤ 16 mm
    # Re = 275 MPa, Rm = 410–540 MPa, A₅ = 22 %
    SteelPreset(
        standard    = 'GB',
        designation = 'Q275B-t16',
        name        = 'GB Q275B (t ≤ 16 mm)',
        E           = _E_STEEL_CN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 275.0 * _MPA,
        sigma_u     = 410.0 * _MPA,   # minimum; range 410–540 MPa
        epsilon_u   = 0.22,
        notes       = 'GB/T 700:2006, Q275B, t ≤ 16 mm. '
                      'Rm range 410–540 MPa; minimum used.',
    ),

    # ================================================
    # GB/T 1591 — HSLA structural steel (2018 revision)
    # ================================================

    # ----------------------------------------------- Q355B t ≤ 16 mm
    # Re = 355 MPa, Rm = 470–630 MPa, A₅ = 22 %
    SteelPreset(
        standard    = 'GB',
        designation = 'Q355B-t16',
        name        = 'GB Q355B (t ≤ 16 mm)',
        E           = _E_STEEL_CN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 355.0 * _MPA,
        sigma_u     = 470.0 * _MPA,   # minimum; range 470–630 MPa
        epsilon_u   = 0.22,
        notes       = 'GB/T 1591:2018, Q355B, t ≤ 16 mm. '
                      'HSLA structural steel. Supersedes Q345B (GB/T 1591-2008). '
                      'Rm range 470–630 MPa; minimum used.',
    ),

    # ----------------------------------------- Q355B 16 < t ≤ 40 mm
    # Re = 345 MPa, Rm = 470–630 MPa, A₅ = 22 %
    SteelPreset(
        standard    = 'GB',
        designation = 'Q355B-t40',
        name        = 'GB Q355B (16 < t ≤ 40 mm)',
        E           = _E_STEEL_CN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 345.0 * _MPA,
        sigma_u     = 470.0 * _MPA,
        epsilon_u   = 0.22,
        notes       = 'GB/T 1591:2018, Q355B, 16 < t ≤ 40 mm. '
                      'HSLA structural steel.',
    ),

    # ----------------------------------------------- Q390B t ≤ 16 mm
    # Re = 390 MPa, Rm = 490–650 MPa, A₅ = 20 %
    SteelPreset(
        standard    = 'GB',
        designation = 'Q390B-t16',
        name        = 'GB Q390B (t ≤ 16 mm)',
        E           = _E_STEEL_CN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 390.0 * _MPA,
        sigma_u     = 490.0 * _MPA,   # minimum; range 490–650 MPa
        epsilon_u   = 0.20,
        notes       = 'GB/T 1591:2018, Q390B, t ≤ 16 mm. '
                      'High-strength HSLA structural steel.',
    ),

    # ----------------------------------------------- Q420B t ≤ 16 mm
    # Re = 420 MPa, Rm = 520–680 MPa, A₅ = 19 %
    SteelPreset(
        standard    = 'GB',
        designation = 'Q420B-t16',
        name        = 'GB Q420B (t ≤ 16 mm)',
        E           = _E_STEEL_CN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 420.0 * _MPA,
        sigma_u     = 520.0 * _MPA,   # minimum; range 520–680 MPa
        epsilon_u   = 0.19,
        notes       = 'GB/T 1591:2018, Q420B, t ≤ 16 mm. '
                      'High-strength HSLA structural steel.',
    ),

    # ----------------------------------------------- Q460C t ≤ 16 mm
    # Re = 460 MPa, Rm = 550–720 MPa, A₅ = 17 %
    SteelPreset(
        standard    = 'GB',
        designation = 'Q460C-t16',
        name        = 'GB Q460C (t ≤ 16 mm)',
        E           = _E_STEEL_CN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 460.0 * _MPA,
        sigma_u     = 550.0 * _MPA,   # minimum; range 550–720 MPa
        epsilon_u   = 0.17,
        notes       = 'GB/T 1591:2018, Q460C, t ≤ 16 mm. '
                      'High-strength HSLA structural steel.',
    ),
]


# ---------------------------------------------------------------------------
# AS/NZS presets  (Australian / New Zealand Standards)
# Source: AS/NZS 3678:2016 (plates & floorplates),
#         AS/NZS 3679.1:2016 (hot-rolled bars & sections)
# E = 200 GPa (AS 4100-1998 §1.4), elongation = proportional gauge L₀ = 5.65√S₀
# ---------------------------------------------------------------------------
_ASNZS: list[SteelPreset] = [

    # ================================================
    # AS/NZS 3678 — hot-rolled plates & floorplates
    # ================================================

    # --------------------------------------- Grade 250 t ≤ 40 mm
    # Fy = 250 MPa, Fu = 410–530 MPa, A = 22 %
    SteelPreset(
        standard    = 'AS/NZS',
        designation = '3678-Gr250-t40',
        name        = 'AS/NZS 3678 Gr.250 (t ≤ 40 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 250.0 * _MPA,
        sigma_u     = 410.0 * _MPA,   # minimum; range 410–530 MPa
        epsilon_u   = 0.22,
        notes       = 'AS/NZS 3678:2016, Grade 250, t ≤ 40 mm. '
                      'Hot-rolled plates and floorplates. '
                      'E = 200 GPa (AS 4100-1998). '
                      'Rm range 410–530 MPa; minimum used.',
    ),

    # --------------------------------------- Grade 350 t ≤ 17 mm
    # Fy = 350 MPa, Fu = 480–600 MPa, A = 20 %
    SteelPreset(
        standard    = 'AS/NZS',
        designation = '3678-Gr350-t17',
        name        = 'AS/NZS 3678 Gr.350 (t ≤ 17 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 350.0 * _MPA,
        sigma_u     = 480.0 * _MPA,   # minimum; range 480–600 MPa
        epsilon_u   = 0.20,
        notes       = 'AS/NZS 3678:2016, Grade 350, t ≤ 17 mm. '
                      'Hot-rolled plates and floorplates. '
                      'Rm range 480–600 MPa; minimum used.',
    ),

    # --------------------------------- Grade 350 17 < t ≤ 40 mm
    # Fy = 340 MPa, Fu = 480–600 MPa, A = 20 %
    SteelPreset(
        standard    = 'AS/NZS',
        designation = '3678-Gr350-t40',
        name        = 'AS/NZS 3678 Gr.350 (17 < t ≤ 40 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 340.0 * _MPA,
        sigma_u     = 480.0 * _MPA,
        epsilon_u   = 0.20,
        notes       = 'AS/NZS 3678:2016, Grade 350, 17 < t ≤ 40 mm.',
    ),

    # --------------------------------------- Grade 400 t ≤ 17 mm
    # Fy = 380 MPa (t ≤ 17), Fu = 480–620 MPa, A = 19 %
    SteelPreset(
        standard    = 'AS/NZS',
        designation = '3678-Gr400-t17',
        name        = 'AS/NZS 3678 Gr.400 (t ≤ 17 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 380.0 * _MPA,   # t ≤ 17 mm; 400 MPa for t ≤ 11 mm
        sigma_u     = 480.0 * _MPA,   # minimum; range 480–620 MPa
        epsilon_u   = 0.19,
        notes       = 'AS/NZS 3678:2016, Grade 400, t ≤ 17 mm (Fy = 380 MPa). '
                      'Use Fy = 400 MPa for t ≤ 11 mm. '
                      'Rm range 480–620 MPa; minimum used.',
    ),

    # --------------------------------------- Grade 450 t ≤ 11 mm
    # Fy = 450 MPa, Fu = 520–640 MPa, A = 17 %
    SteelPreset(
        standard    = 'AS/NZS',
        designation = '3678-Gr450-t11',
        name        = 'AS/NZS 3678 Gr.450 (t ≤ 11 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 450.0 * _MPA,
        sigma_u     = 520.0 * _MPA,   # minimum; range 520–640 MPa
        epsilon_u   = 0.17,
        notes       = 'AS/NZS 3678:2016, Grade 450, t ≤ 11 mm. '
                      'High-strength hot-rolled plate. '
                      'Rm range 520–640 MPa; minimum used.',
    ),

    # ================================================
    # AS/NZS 3679.1 — hot-rolled bars & sections
    # ================================================

    # --------------------------------------- Grade 300 t ≤ 17 mm
    # Fy = 300 MPa, Fu = 440–560 MPa, A = 22 %
    SteelPreset(
        standard    = 'AS/NZS',
        designation = '3679.1-Gr300-t17',
        name        = 'AS/NZS 3679.1 Gr.300 (t ≤ 17 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 300.0 * _MPA,
        sigma_u     = 440.0 * _MPA,   # minimum; range 440–560 MPa
        epsilon_u   = 0.22,
        notes       = 'AS/NZS 3679.1:2016, Grade 300, flange/web t ≤ 17 mm. '
                      'Hot-rolled bars and sections (I, H, channel, angle). '
                      'Most common grade for Australian structural sections. '
                      'Rm range 440–560 MPa; minimum used.',
    ),

    # --------------------------------------- Grade 350 t ≤ 17 mm
    # Fy = 350 MPa, Fu = 480–600 MPa, A = 20 %
    SteelPreset(
        standard    = 'AS/NZS',
        designation = '3679.1-Gr350-t17',
        name        = 'AS/NZS 3679.1 Gr.350 (t ≤ 17 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 350.0 * _MPA,
        sigma_u     = 480.0 * _MPA,   # minimum; range 480–600 MPa
        epsilon_u   = 0.20,
        notes       = 'AS/NZS 3679.1:2016, Grade 350, flange/web t ≤ 17 mm. '
                      'Hot-rolled bars and sections. '
                      'Rm range 480–600 MPa; minimum used.',
    ),
]


# ---------------------------------------------------------------------------
# IS presets  (India)
# Source: IS 2062:2011 — Hot Rolled Medium and High Tensile Structural Steel
# E = 200 GPa (IS 800:2007 §2.2.4.1), elongation = proportional gauge L₀ = 5.65√S₀
# Subgrades A/B/C denote impact toughness; mechanical properties shown are
# identical across A/B/C — use notes to record the specific subgrade if needed.
# ---------------------------------------------------------------------------
_IS: list[SteelPreset] = [

    # ================================================
    # E250 (Fe 410W) — most common structural grade
    # ================================================

    # --------------------------------------- E250 t ≤ 20 mm
    SteelPreset(
        standard    = 'IS',
        designation = 'E250-t20',
        name        = 'IS 2062 E250 (t ≤ 20 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 250.0 * _MPA,
        sigma_u     = 410.0 * _MPA,
        epsilon_u   = 0.23,
        notes       = 'IS 2062:2011, Grade E250 (Fe 410W), t ≤ 20 mm. '
                      'Subgrades A/B/C have identical tensile properties. '
                      'E = 200 GPa (IS 800:2007).',
    ),

    # --------------------------------------- E250 20 < t ≤ 40 mm
    SteelPreset(
        standard    = 'IS',
        designation = 'E250-t40',
        name        = 'IS 2062 E250 (20 < t ≤ 40 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 240.0 * _MPA,
        sigma_u     = 410.0 * _MPA,
        epsilon_u   = 0.23,
        notes       = 'IS 2062:2011, Grade E250 (Fe 410W), 20 < t ≤ 40 mm.',
    ),

    # ================================================
    # E300 (Fe 440)
    # ================================================

    # --------------------------------------- E300 t ≤ 20 mm
    SteelPreset(
        standard    = 'IS',
        designation = 'E300-t20',
        name        = 'IS 2062 E300 (t ≤ 20 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 300.0 * _MPA,
        sigma_u     = 440.0 * _MPA,
        epsilon_u   = 0.22,
        notes       = 'IS 2062:2011, Grade E300 (Fe 440), t ≤ 20 mm.',
    ),

    # ================================================
    # E350 (Fe 490)
    # ================================================

    # --------------------------------------- E350 t ≤ 20 mm
    SteelPreset(
        standard    = 'IS',
        designation = 'E350-t20',
        name        = 'IS 2062 E350 (t ≤ 20 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 350.0 * _MPA,
        sigma_u     = 490.0 * _MPA,
        epsilon_u   = 0.22,
        notes       = 'IS 2062:2011, Grade E350 (Fe 490), t ≤ 20 mm.',
    ),

    # --------------------------------------- E350 20 < t ≤ 40 mm
    SteelPreset(
        standard    = 'IS',
        designation = 'E350-t40',
        name        = 'IS 2062 E350 (20 < t ≤ 40 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 330.0 * _MPA,
        sigma_u     = 490.0 * _MPA,
        epsilon_u   = 0.22,
        notes       = 'IS 2062:2011, Grade E350 (Fe 490), 20 < t ≤ 40 mm.',
    ),

    # ================================================
    # E410 (Fe 540)
    # ================================================

    # --------------------------------------- E410 t ≤ 20 mm
    SteelPreset(
        standard    = 'IS',
        designation = 'E410-t20',
        name        = 'IS 2062 E410 (t ≤ 20 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 410.0 * _MPA,
        sigma_u     = 540.0 * _MPA,
        epsilon_u   = 0.20,
        notes       = 'IS 2062:2011, Grade E410 (Fe 540), t ≤ 20 mm.',
    ),

    # ================================================
    # E450 (Fe 570)
    # ================================================

    # --------------------------------------- E450 t ≤ 20 mm
    SteelPreset(
        standard    = 'IS',
        designation = 'E450-t20',
        name        = 'IS 2062 E450 (t ≤ 20 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 450.0 * _MPA,
        sigma_u     = 570.0 * _MPA,
        epsilon_u   = 0.20,
        notes       = 'IS 2062:2011, Grade E450 (Fe 570), t ≤ 20 mm. '
                      'Available in subgrades A, B, C (impact toughness classes).',
    ),

    # ================================================
    # E550 (Fe 670) — high-strength
    # ================================================

    # --------------------------------------- E550 t ≤ 20 mm
    SteelPreset(
        standard    = 'IS',
        designation = 'E550-t20',
        name        = 'IS 2062 E550 (t ≤ 20 mm)',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 550.0 * _MPA,
        sigma_u     = 670.0 * _MPA,
        epsilon_u   = 0.18,
        notes       = 'IS 2062:2011, Grade E550 (Fe 670), t ≤ 20 mm. '
                      'High-strength structural steel.',
    ),
]


# ---------------------------------------------------------------------------
# CSA presets  (Canadian Standards Association)
# Source: CSA G40.20/G40.21:2013 — Structural Quality Steels
# E = 200 GPa (CSA S16:19 §27.1.4), elongation = 50 mm gauge (A₅₀)
# ---------------------------------------------------------------------------
_CSA: list[SteelPreset] = [

    # ================================================================
    # CSA G40.21 — W  (weldable structural quality)
    # Table 1, Class 1 (t ≤ 65 mm)
    # ================================================================

    # ------------------------------------------------------- 230W
    SteelPreset(
        standard    = 'CSA',
        designation = '230W',
        name        = 'CSA G40.21 230W',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 230.0 * _MPA,
        sigma_u     = 310.0 * _MPA,   # minimum; range 310–450 MPa
        epsilon_u   = 0.22,
        notes       = 'CSA G40.20/G40.21:2013, Grade 230W, t ≤ 65 mm. '
                      'Weldable structural quality steel. '
                      'Fu range 310–450 MPa; minimum value used.',
    ),

    # ------------------------------------------------------- 260W
    SteelPreset(
        standard    = 'CSA',
        designation = '260W',
        name        = 'CSA G40.21 260W',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 260.0 * _MPA,
        sigma_u     = 410.0 * _MPA,   # minimum; range 410–590 MPa
        epsilon_u   = 0.22,
        notes       = 'CSA G40.20/G40.21:2013, Grade 260W, t ≤ 65 mm. '
                      'Weldable structural quality steel. '
                      'Fu range 410–590 MPa; minimum value used.',
    ),

    # ------------------------------------------------------- 300W
    SteelPreset(
        standard    = 'CSA',
        designation = '300W',
        name        = 'CSA G40.21 300W',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 300.0 * _MPA,
        sigma_u     = 450.0 * _MPA,   # minimum; range 450–620 MPa
        epsilon_u   = 0.20,
        notes       = 'CSA G40.20/G40.21:2013, Grade 300W, t ≤ 65 mm. '
                      'Weldable structural quality steel. '
                      'Fu range 450–620 MPa; minimum value used.',
    ),

    # ------------------------------------------------------- 350W
    SteelPreset(
        standard    = 'CSA',
        designation = '350W',
        name        = 'CSA G40.21 350W',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 350.0 * _MPA,
        sigma_u     = 480.0 * _MPA,   # minimum; range 480–650 MPa
        epsilon_u   = 0.20,
        notes       = 'CSA G40.20/G40.21:2013, Grade 350W, t ≤ 65 mm. '
                      'Most widely used Canadian structural steel. '
                      'Mechanically similar to ASTM A572-50. '
                      'Fu range 480–650 MPa; minimum value used.',
    ),

    # ------------------------------------------------------- 400W
    SteelPreset(
        standard    = 'CSA',
        designation = '400W',
        name        = 'CSA G40.21 400W',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 400.0 * _MPA,
        sigma_u     = 520.0 * _MPA,   # minimum; range 520–690 MPa
        epsilon_u   = 0.17,
        notes       = 'CSA G40.20/G40.21:2013, Grade 400W, t ≤ 65 mm. '
                      'High-strength weldable structural steel. '
                      'Fu range 520–690 MPa; minimum value used.',
    ),

    # ------------------------------------------------------- 480W
    SteelPreset(
        standard    = 'CSA',
        designation = '480W',
        name        = 'CSA G40.21 480W',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 480.0 * _MPA,
        sigma_u     = 590.0 * _MPA,   # minimum; range 590–790 MPa
        epsilon_u   = 0.16,
        notes       = 'CSA G40.20/G40.21:2013, Grade 480W, t ≤ 65 mm. '
                      'High-strength weldable structural steel. '
                      'Fu range 590–790 MPa; minimum value used.',
    ),

    # ================================================================
    # CSA G40.21 — WT  (weldable, notch-tough)
    # Same Fy/Fu as W grades; WT suffix mandates CVN impact testing.
    # ================================================================

    # ------------------------------------------------------- 260WT
    SteelPreset(
        standard    = 'CSA',
        designation = '260WT',
        name        = 'CSA G40.21 260WT',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 260.0 * _MPA,
        sigma_u     = 410.0 * _MPA,   # minimum; range 410–590 MPa
        epsilon_u   = 0.22,
        notes       = 'CSA G40.20/G40.21:2013, Grade 260WT, t ≤ 65 mm. '
                      'Weldable structural quality with mandatory CVN impact testing. '
                      'Identical Fy/Fu to 260W.',
    ),

    # ------------------------------------------------------- 350WT
    SteelPreset(
        standard    = 'CSA',
        designation = '350WT',
        name        = 'CSA G40.21 350WT',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 350.0 * _MPA,
        sigma_u     = 480.0 * _MPA,   # minimum; range 480–650 MPa
        epsilon_u   = 0.20,
        notes       = 'CSA G40.20/G40.21:2013, Grade 350WT, t ≤ 65 mm. '
                      'Weldable structural quality with mandatory CVN impact testing. '
                      'Identical Fy/Fu to 350W. Used in seismic and bridge applications.',
    ),

    # ------------------------------------------------------- 400WT
    SteelPreset(
        standard    = 'CSA',
        designation = '400WT',
        name        = 'CSA G40.21 400WT',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 400.0 * _MPA,
        sigma_u     = 520.0 * _MPA,   # minimum; range 520–690 MPa
        epsilon_u   = 0.17,
        notes       = 'CSA G40.20/G40.21:2013, Grade 400WT, t ≤ 65 mm. '
                      'Weldable structural quality with mandatory CVN impact testing. '
                      'Identical Fy/Fu to 400W.',
    ),

    # ================================================================
    # CSA G40.21 — AT  (atmospheric corrosion-resistant, weldable)
    # Weathering steels; similar application to ASTM A588 / A709-50W.
    # ================================================================

    # ------------------------------------------------------- 260AT
    SteelPreset(
        standard    = 'CSA',
        designation = '260AT',
        name        = 'CSA G40.21 260AT',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 260.0 * _MPA,
        sigma_u     = 410.0 * _MPA,   # minimum; range 410–590 MPa
        epsilon_u   = 0.22,
        notes       = 'CSA G40.20/G40.21:2013, Grade 260AT, t ≤ 65 mm. '
                      'Atmospheric corrosion-resistant (weathering) steel. '
                      'Suitable for exposed structures without coating. '
                      'Analogous to ASTM A588.',
    ),

    # ------------------------------------------------------- 350AT
    SteelPreset(
        standard    = 'CSA',
        designation = '350AT',
        name        = 'CSA G40.21 350AT',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 350.0 * _MPA,
        sigma_u     = 480.0 * _MPA,   # minimum; range 480–650 MPa
        epsilon_u   = 0.20,
        notes       = 'CSA G40.20/G40.21:2013, Grade 350AT, t ≤ 65 mm. '
                      'Atmospheric corrosion-resistant (weathering) steel. '
                      'Analogous to ASTM A709-50W.',
    ),

    # ------------------------------------------------------- 400AT
    SteelPreset(
        standard    = 'CSA',
        designation = '400AT',
        name        = 'CSA G40.21 400AT',
        E           = _E_STEEL,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 400.0 * _MPA,
        sigma_u     = 520.0 * _MPA,   # minimum; range 520–690 MPa
        epsilon_u   = 0.17,
        notes       = 'CSA G40.20/G40.21:2013, Grade 400AT, t ≤ 65 mm. '
                      'High-strength atmospheric corrosion-resistant (weathering) steel.',
    ),
]


# ---------------------------------------------------------------------------
# UNI presets  (Italian national standards — historic grades)
# Source: UNI 7070:1982 — Acciai per costruzioni metalliche (withdrawn;
#         replaced by EN 10025.  Still referenced for existing structures.)
# E = 210 GPa (EC3 / NTC 2018 §11.3.4.1 remand),
# elongation = proportional gauge L₀ = 5.65√S₀ (A₅)
# ---------------------------------------------------------------------------
_UNI: list[SteelPreset] = [

    # ================================================================
    # UNI 7070 — Fe 360 / Fe 430 / Fe 510
    # Equivalent (by conversion) to EN S235 / S275 / S355 respectively.
    # Table values are for sub-grades B and C (same tensile properties).
    # ================================================================

    # ---------------------------------------------------------------- Fe 360 B/C
    # ReH = 235 MPa (t ≤ 16 mm), Rm_min = 360 MPa, A5 = 26 %
    SteelPreset(
        standard    = 'UNI',
        designation = 'Fe360',
        name        = 'UNI Fe 360',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 235.0 * _MPA,
        sigma_u     = 360.0 * _MPA,
        epsilon_u   = 0.26,
        notes       = 'UNI 7070:1982, Fe 360 (sub-grades B/C), t ≤ 16 mm. '
                      'Historic Italian structural steel, replaced by EN 10025-2 S235. '
                      'Still referenced for verification of existing structures. '
                      'E = 210 GPa per EC3 / NTC 2018.',
    ),

    # ---------------------------------------------------------------- Fe 430 B/C
    # ReH = 275 MPa (t ≤ 16 mm), Rm_min = 430 MPa, A5 = 21 %
    SteelPreset(
        standard    = 'UNI',
        designation = 'Fe430',
        name        = 'UNI Fe 430',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 275.0 * _MPA,
        sigma_u     = 430.0 * _MPA,
        epsilon_u   = 0.21,
        notes       = 'UNI 7070:1982, Fe 430 (sub-grades B/C), t ≤ 16 mm. '
                      'Historic Italian structural steel, replaced by EN 10025-2 S275. '
                      'Still referenced for verification of existing structures. '
                      'E = 210 GPa per EC3 / NTC 2018.',
    ),

    # ---------------------------------------------------------------- Fe 510 B/C
    # ReH = 355 MPa (t ≤ 16 mm), Rm_min = 510 MPa, A5 = 22 %
    SteelPreset(
        standard    = 'UNI',
        designation = 'Fe510',
        name        = 'UNI Fe 510',
        E           = _E_STEEL_EN,
        nu          = _NU_STEEL,
        rho         = _RHO_STEEL,
        sigma_y     = 355.0 * _MPA,
        sigma_u     = 510.0 * _MPA,
        epsilon_u   = 0.22,
        notes       = 'UNI 7070:1982, Fe 510 (sub-grades B/C), t ≤ 16 mm. '
                      'Historic Italian structural steel, replaced by EN 10025-2 S355. '
                      'Still referenced for verification of existing structures. '
                      'E = 210 GPa per EC3 / NTC 2018.',
    ),
]


# ---------------------------------------------------------------------------
# Public registry — partitioned by standard code.
# ---------------------------------------------------------------------------
PRESETS: dict[str, list[SteelPreset]] = {
    'ASTM'  : _ASTM,
    'API'   : _API,
    'AISI'  : _AISI,
    'ASME'  : _ASME,
    'EN'    : _EN,
    'JIS'   : _JIS,
    'GB'    : _GB,
    'AS/NZS': _ASNZS,
    'IS'    : _IS,
    'CSA'   : _CSA,
    'UNI'   : _UNI,
}
