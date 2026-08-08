class ExpSmoothingForecaster:
    def __init__(self, alpha: float = 0.3):
        self._alpha = alpha
        self._level: float | None = None

    def update(self, value: float) -> None:
        if self._level is None:
            self._level = value
        else:
            self._level = self._alpha * value + (1 - self._alpha) * self._level

    def predict(self) -> float:
        return self._level or 0.0

    def recent_mae(self, actual: list[float]) -> float:
        if not actual:
            return float("inf")
        level = None
        errors = []
        for a in actual:
            pred = level if level is not None else a
            errors.append(abs(pred - a))
            level = a if level is None else self._alpha * a + (1 - self._alpha) * level
        return sum(errors) / len(errors)
