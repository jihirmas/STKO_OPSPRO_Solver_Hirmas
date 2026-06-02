class InternalTagAllocator:
    """
    Centralized allocator for tags generated during TCL export.

    It consumes the standard STKO process_info counters when available, so
    generated nodes, elements and materials do not collide with user model tags.
    """

    def __init__(self, pinfo=None):
        self.pinfo = pinfo
        self._node = self._get_counter('next_node_id', 1)
        self._element = self._get_counter('next_elem_id', 1)
        self._material = self._get_counter('next_physicalProperties_id', 1)

    def allocate_node(self) -> int:
        value = self._node
        self._node += 1
        self._set_counter('next_node_id', self._node)
        return value

    def allocate_element(self) -> int:
        value = self._element
        self._element += 1
        self._set_counter('next_elem_id', self._element)
        return value

    def allocate_uniaxial_material(self) -> int:
        value = self._material
        self._material += 1
        self._set_counter('next_physicalProperties_id', self._material)
        return value

    def _get_counter(self, name: str, fallback: int) -> int:
        if self.pinfo is None:
            return fallback
        try:
            return int(getattr(self.pinfo, name))
        except Exception:
            return fallback

    def _set_counter(self, name: str, value: int):
        if self.pinfo is None:
            return
        try:
            setattr(self.pinfo, name, int(value))
        except Exception:
            pass

