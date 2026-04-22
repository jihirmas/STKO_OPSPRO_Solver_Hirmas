from typing import Optional, Dict

def validate_inputs(E=None, G=None, K=None, v=None):
    if E is not None and E <= 0:
        raise ValueError("E debe ser > 0")
    if G is not None and G <= 0:
        raise ValueError("G debe ser > 0")
    if K is not None and K <= 0:
        raise ValueError("K debe ser > 0")
    if v is not None and not (-1 < v < 0.5):
        raise ValueError("v debe cumplir -1 < v < 0.5")


# ---- Casos específicos ----

def from_E_G(E: float, G: float) -> Dict[str, float]:
    validate_inputs(E=E, G=G)
    v = E / (2 * G) - 1
    K = E * G / (3 * (3 * G - E))
    return {"E": E, "G": G, "K": K, "v": v}


def from_E_K(E: float, K: float) -> Dict[str, float]:
    validate_inputs(E=E, K=K)
    v = (3 * K - E) / (6 * K)
    G = 3 * E * K / (9 * K - E)
    return {"E": E, "G": G, "K": K, "v": v}


def from_E_v(E: float, v: float) -> Dict[str, float]:
    validate_inputs(E=E, v=v)
    G = E / (2 * (1 + v))
    K = E / (3 * (1 - 2 * v))
    return {"E": E, "G": G, "K": K, "v": v}


def from_G_K(G: float, K: float) -> Dict[str, float]:
    validate_inputs(G=G, K=K)
    E = 9 * K * G / (3 * K + G)
    v = (3 * K - 2 * G) / (2 * (3 * K + G))
    return {"E": E, "G": G, "K": K, "v": v}


def from_G_v(G: float, v: float) -> Dict[str, float]:
    validate_inputs(G=G, v=v)
    E = 2 * G * (1 + v)
    K = 2 * G * (1 + v) / (3 * (1 - 2 * v))
    return {"E": E, "G": G, "K": K, "v": v}


def from_K_v(K: float, v: float) -> Dict[str, float]:
    validate_inputs(K=K, v=v)
    E = 3 * K * (1 - 2 * v)
    G = 3 * K * (1 - 2 * v) / (2 * (1 + v))
    return {"E": E, "G": G, "K": K, "v": v}


# ---- Función general automática ----

def compute_elastic_constants(
    E: Optional[float] = None,
    G: Optional[float] = None,
    K: Optional[float] = None,
    v: Optional[float] = None,
) -> Dict[str, float]:

    provided = {
        "E": E is not None,
        "G": G is not None,
        "K": K is not None,
        "v": v is not None,
    }

    if sum(provided.values()) != 2:
        raise ValueError("Debes proporcionar exactamente 2 variables")

    if provided["E"] and provided["G"]:
        return from_E_G(E, G)
    if provided["E"] and provided["K"]:
        return from_E_K(E, K)
    if provided["E"] and provided["v"]:
        return from_E_v(E, v)
    if provided["G"] and provided["K"]:
        return from_G_K(G, K)
    if provided["G"] and provided["v"]:
        return from_G_v(G, v)
    if provided["K"] and provided["v"]:
        return from_K_v(K, v)

    raise ValueError("Combinación no válida")


# ---- Ejemplo de uso ----
if __name__ == "__main__":
    result = compute_elastic_constants(E=210e9, v=0.3)
    print(result)