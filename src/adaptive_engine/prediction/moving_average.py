from collections import deque


class MovingAverageForecaster:
    def __init__(self, window: int = 10):
        self._window = window
        self._samples: deque[float] = deque(maxlen=window)

    def update(self, value: float) -> None:
        self._samples.append(value)

    def predict(self) -> float:
        if not self._samples:
            return 0.0
        return sum(self._samples) / len(self._samples)

    def recent_mae(self, actual: list[float]) -> float:
        if not actual:
            return float("inf")
        preds = [self.predict() for _ in actual]
        return sum(abs(p - a) for p, a in zip(preds, actual, strict=False)) / len(actual)
