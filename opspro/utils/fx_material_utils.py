"""
fx_material_utils.py
--------------------
Utility helpers for :class:`PyMpc.FxMaterial`:

- :func:`fx_material_to_dict`  – serialize an FxMaterial to a plain dict (JSON-safe)
- :func:`fx_material_from_dict` – deserialize an FxMaterial from such a dict
- :func:`edit_fx_material`     – open FxMaterialDialog and return the edited copy
                                  (or a fresh one when *material* is ``None``)
"""

from PyMpc import (
    FxMaterial, 
    FxColor, 
    FxMaterialVisibilityOptions, 
    FxColoringMode,
    FxTexturingMode,
    FxShaderSessionType
)


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

def fx_material_to_dict(mat: FxMaterial) -> dict:
    """
    Serialize *mat* to a plain dict with only JSON-compatible types.

    The ``visibilityOptionsOverride`` entry is ``None`` when no override is set.
    """
    vop = None
    if mat.hasVisibilityOptionsOverride:
        ov = mat.visibilityOptionsOverride
        vop = {
            'faces':     bool(ov.faces),
            'edges':     bool(ov.edges),
            'meshEdges': bool(ov.meshEdges),
            'vertices':  bool(ov.vertices),
        }

    def _color(c):
        return {'r': float(c.r), 'g': float(c.g), 'b': float(c.b)}

    return {
        'diffuse':                   _color(mat.diffuse),
        'specular':                  _color(mat.specular),
        'shininess':                 float(mat.shininess),
        'transparency':              float(mat.transparency),
        'backFaceReduction':         float(mat.backFaceReduction),
        'transparencyOnlyOnFaces':   bool(mat.transparencyOnlyOnFaces),
        'edgeColor':                 _color(mat.edgeColor),
        'pointColor':                _color(mat.pointColor),
        'meshEdgeColorReduction':    float(mat.meshEdgeColorReduction),
        'coloringMode':              int(mat.coloringMode),
        'lineWidth':                 float(mat.lineWidth),
        'pointSize':                 float(mat.pointSize),
        'textureMode':               int(mat.textureMode),
        'textureOnlyOnFaces':        bool(mat.textureOnlyOnFaces),
        'textureClamp':              bool(mat.textureClamp),
        'polygonStipple':            int(mat.polygonStipple),
        'additionalPolygonOffset':   float(mat.additionalPolygonOffset),
        'lighting':                  bool(mat.lighting),
        'lightingOnlyOnFaces':       bool(mat.lightingOnlyOnFaces),
        'depthTest':                 bool(mat.depthTest),
        'shaderSession':             int(mat.shaderSession),
        'visibilityOptionsOverride': vop,
    }


def fx_material_from_dict(data: dict) -> FxMaterial:
    """
    Deserialize an FxMaterial from a dict produced by :func:`fx_material_to_dict`.

    Unknown / missing keys fall back to the default ``FxMaterial`` values.
    """
    mat = FxMaterial()

    def _color(d):
        return FxColor(float(d['r']), float(d['g']), float(d['b']))

    diffuse = data.get('diffuse', None)
    if diffuse is not None:
        mat.diffuse = _color(diffuse)
    specular = data.get('specular', None)
    if specular is not None:
        mat.specular = _color(specular)
    shininess = data.get('shininess', None)
    if shininess is not None:
        mat.shininess = float(shininess)
    transparency = data.get('transparency', None)
    if transparency is not None:
        mat.transparency = float(transparency)
    backFaceReduction = data.get('backFaceReduction', None)
    if backFaceReduction is not None:
        mat.backFaceReduction = float(backFaceReduction)
    transparencyOnlyOnFaces = data.get('transparencyOnlyOnFaces', None)
    if transparencyOnlyOnFaces is not None:
        mat.transparencyOnlyOnFaces = bool(transparencyOnlyOnFaces)
    edgeColor = data.get('edgeColor', None)
    if edgeColor is not None:
        mat.edgeColor = _color(edgeColor)
    pointColor = data.get('pointColor', None)
    if pointColor is not None:
        mat.pointColor = _color(pointColor)
    meshEdgeColorReduction = data.get('meshEdgeColorReduction', None)
    if meshEdgeColorReduction is not None:
        mat.meshEdgeColorReduction = float(meshEdgeColorReduction)
    coloringMode = data.get('coloringMode', None)
    if coloringMode is not None:
        mat.coloringMode = FxColoringMode(coloringMode)
    lineWidth = data.get('lineWidth', None)
    if lineWidth is not None:
        mat.lineWidth = float(lineWidth)
    pointSize = data.get('pointSize', None)
    if pointSize is not None:
        mat.pointSize = float(pointSize)
    textureMode = data.get('textureMode', None)
    if textureMode is not None:
        mat.textureMode = FxTexturingMode(textureMode)
    textureOnlyOnFaces = data.get('textureOnlyOnFaces', None)
    if textureOnlyOnFaces is not None:
        mat.textureOnlyOnFaces = bool(textureOnlyOnFaces)
    textureClamp = data.get('textureClamp', None)
    if textureClamp is not None:
        mat.textureClamp = bool(textureClamp)
    polygonStipple = data.get('polygonStipple', None)
    if polygonStipple is not None:
        mat.polygonStipple = int(polygonStipple)
    additionalPolygonOffset = data.get('additionalPolygonOffset', None)
    if additionalPolygonOffset is not None:
        mat.additionalPolygonOffset = float(additionalPolygonOffset)
    lighting = data.get('lighting', None)
    if lighting is not None:
        mat.lighting = bool(lighting)
    lightingOnlyOnFaces = data.get('lightingOnlyOnFaces', None)
    if lightingOnlyOnFaces is not None:
        mat.lightingOnlyOnFaces = bool(lightingOnlyOnFaces)
    depthTest = data.get('depthTest', None)
    if depthTest is not None:
        mat.depthTest = bool(depthTest)
    shaderSession = data.get('shaderSession', None)
    if shaderSession is not None:
        mat.shaderSession = FxShaderSessionType(shaderSession)

    vop = data.get('visibilityOptionsOverride', None)
    if vop is not None:
        ov = FxMaterialVisibilityOptions(
            bool(vop.get('faces',     True)),
            bool(vop.get('edges',     True)),
            bool(vop.get('meshEdges', True)),
            bool(vop.get('vertices',  True)),
        )
        mat.visibilityOptionsOverride = ov

    return mat


# ---------------------------------------------------------------------------
# Interactive editing
# ---------------------------------------------------------------------------

def edit_fx_material(material: FxMaterial = None):
    """
    Open ``FxMaterialDialog`` for interactive editing.

    Parameters
    ----------
    material : FxMaterial or None
        Existing material to edit.  Pass ``None`` to create a fresh one.

    Returns
    -------
    FxMaterial or None
        A new ``FxMaterial`` instance with the user's changes, or ``None``
        if the dialog was cancelled.
    """
    import PyMpc
    # editFxMaterial is a C++ function registered in export_fx.cpp.
    # It opens FxMaterialDialog modally (parent = QApplication::activeWindow())
    # and returns a copy of the accepted material, or None on cancel.
    return PyMpc.editFxMaterial(material)
