class DimensionMode:
    TWO_D = '2D'
    THREE_D = '3D'
    ALL = (TWO_D, THREE_D)

    @classmethod
    def normalize(cls, value: str) -> str:
        value = str(value).strip().upper()
        if value not in cls.ALL:
            raise ValueError(f'Unsupported dimension mode: {value}')
        return value

