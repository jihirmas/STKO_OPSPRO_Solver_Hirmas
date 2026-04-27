import math


class StrainHistoryParameters:
    def __init__(
        self,
        num_cyc,
        num_divisions,
        target_strain,
        scale_pos,
        scale_neg,
        num_cyc_editable,
        custom_history_vector=None,
    ):
        self.num_cycles = num_cyc
        self.num_divisions = num_divisions
        self.target_strain = target_strain
        self.scale_pos = scale_pos
        self.scale_neg = scale_neg
        self.num_cycles_editable = num_cyc_editable
        self.custom_history_vector = custom_history_vector or []


def _reference_value_at(vector, index):
    if hasattr(vector, 'referenceValueAt'):
        return vector.referenceValueAt(index)
    return vector[index]


def _discretize(num_divisions, values):
    if not values:
        return []
    xmin = min(values)
    xmax = max(values)
    dx = (xmax - xmin) / max(num_divisions, 1)
    result = [values[0]]
    if abs(dx) > 1.0e-16:
        for i in range(1, len(values)):
            delta = values[i] - values[i - 1]
            nsteps = max(1, int(math.ceil(abs(delta / dx))))
            step = delta / nsteps
            current = values[i - 1]
            for _ in range(nsteps):
                current += step
                result.append(current)
    return result


class StrainHistoryReference:
    def __init__(self):
        self.strain = []

    def getDefaultParams(self):
        return StrainHistoryParameters(1, 10, 0.0, 1.0, 1.0, False)

    def build(self, params):
        vector = params.custom_history_vector
        self.strain = [_reference_value_at(vector, i) for i in range(len(vector))]


class StrainHistoryCustom:
    def __init__(self):
        self.strain = []

    def getDefaultParams(self):
        return StrainHistoryParameters(1, 10, 0.0, 1.0, 1.0, True)

    def build(self, params):
        vector = params.custom_history_vector
        points = [0.0]
        for i in range(len(vector)):
            value = _reference_value_at(vector, i)
            if i == 0 and value == 0:
                continue
            if value > 0:
                value *= params.scale_pos
            elif value < 0:
                value *= params.scale_neg
            points.append(value)
        self.strain = _discretize(params.num_divisions, points)


class StrainHistoryCyclicAsymmetric:
    def __init__(self):
        self.strain = []

    def getDefaultParams(self):
        return StrainHistoryParameters(1, 10, 0.0, 1.0, 1.0, True)

    def build(self, params):
        target = params.target_strain
        scale_pos = params.scale_pos
        scale_neg = params.scale_neg
        if target < 0.0:
            scale_pos, scale_neg = scale_neg, scale_pos
        points = [0.0]
        for _ in range(max(1, params.num_cycles)):
            points.append(target * scale_pos)
            points.append(0.0)
        self.strain = _discretize(params.num_divisions, points)


class StrainHistoryCyclicAsymmLinearIncreasing:
    def __init__(self):
        self.strain = []

    def getDefaultParams(self):
        return StrainHistoryParameters(3, 10, 0.0, 1.0, 1.0, True)

    def build(self, params):
        target = params.target_strain
        cycles = max(1, params.num_cycles)
        scale_pos = params.scale_pos
        scale_neg = params.scale_neg
        if target < 0.0:
            scale_pos, scale_neg = scale_neg, scale_pos
        points = [0.0]
        for i in range(cycles):
            current = target / cycles * (i + 1)
            points.append(current * scale_pos)
            points.append(0.0)
        self.strain = _discretize(params.num_divisions, points)


class StrainHistoryCyclicEN12512:
    def __init__(self):
        self.strain = []

    def getDefaultParams(self):
        return StrainHistoryParameters(11, 10, 0.0, 1.0, 1.0, False)

    def build(self, params):
        target = params.target_strain
        scale_pos = params.scale_pos
        scale_neg = params.scale_neg
        if target < 0.0:
            scale_pos, scale_neg = scale_neg, scale_pos

        def make_cycles(strain, count):
            values = []
            for _ in range(count):
                values.append(strain * scale_pos)
                values.append(-strain * scale_neg)
            return values

        points = [0.0]
        points += make_cycles(target / 4.0, 1)
        points += make_cycles(target / 2.0, 1)
        points += make_cycles(target, 3)
        points += make_cycles(2.0 * target, 3)
        points += make_cycles(4.0 * target, 3)
        self.strain = _discretize(params.num_divisions, points)


class StrainHistoryCyclicSymmetric:
    def __init__(self):
        self.strain = []

    def getDefaultParams(self):
        return StrainHistoryParameters(1, 10, 0.0, 1.0, 1.0, True)

    def build(self, params):
        target = params.target_strain
        scale_pos = params.scale_pos
        scale_neg = params.scale_neg
        if target < 0.0:
            scale_pos, scale_neg = scale_neg, scale_pos
        points = [0.0]
        for _ in range(max(1, params.num_cycles)):
            points.append(target * scale_pos)
            points.append(-target * scale_neg)
        points.append(0.0)
        self.strain = _discretize(params.num_divisions, points)


class StrainHistoryCyclicSymmLinearIncreasing:
    def __init__(self):
        self.strain = []

    def getDefaultParams(self):
        return StrainHistoryParameters(3, 10, 0.0, 1.0, 1.0, True)

    def build(self, params):
        target = params.target_strain
        cycles = max(1, params.num_cycles)
        scale_pos = params.scale_pos
        scale_neg = params.scale_neg
        if target < 0.0:
            scale_pos, scale_neg = scale_neg, scale_pos
        points = [0.0]
        for i in range(cycles):
            current = target / cycles * (i + 1)
            points.append(current * scale_pos)
            points.append(-current * scale_neg)
        points.append(0.0)
        self.strain = _discretize(params.num_divisions, points)


class StrainHistoryMonotonic:
    def __init__(self):
        self.strain = []

    def getDefaultParams(self):
        return StrainHistoryParameters(1, 100, 0.0, 1.0, 1.0, False)

    def build(self, params):
        target = params.target_strain
        scale_pos = params.scale_pos
        scale_neg = params.scale_neg
        if target < 0.0:
            scale_pos, scale_neg = scale_neg, scale_pos
        self.strain = _discretize(params.num_divisions, [0.0, target * scale_pos])


class StrainHistoryFactory:
    supportedTypes = {
        'CyclicAsymmetric': StrainHistoryCyclicAsymmetric,
        'CyclicAsymmLinearIncreasing': StrainHistoryCyclicAsymmLinearIncreasing,
        'CyclicEN12512': StrainHistoryCyclicEN12512,
        'CyclicSymmetric': StrainHistoryCyclicSymmetric,
        'CyclicSymmLinearIncreasing': StrainHistoryCyclicSymmLinearIncreasing,
        'Monotonic': StrainHistoryMonotonic,
        'Custom': StrainHistoryCustom,
        'ReferenceCurveHistory': StrainHistoryReference,
    }

    @staticmethod
    def getTypes():
        return list(StrainHistoryFactory.supportedTypes.keys())

    @staticmethod
    def make(class_name):
        if class_name not in StrainHistoryFactory.supportedTypes:
            raise ValueError('Unsupported strain history "{}"'.format(class_name))
        return StrainHistoryFactory.supportedTypes[class_name]()
