from adaptive_engine.prediction.exp_smoothing import ExpSmoothingForecaster
from adaptive_engine.prediction.moving_average import MovingAverageForecaster


class ForecasterSelector:
    def __init__(self, window: int = 20, eval_interval: int = 50):
        self._window = window
        self._eval_interval = eval_interval
        self._tick = 0
        self.forecasters: dict[str, dict] = {}

    def _ensure(self, name: str):
        if name not in self.forecasters:
            self.forecasters[name] = {
                "ma": MovingAverageForecaster(window=self._window),
                "es": ExpSmoothingForecaster(alpha=0.3),
                "best": None,
            }

    def update(self, metrics: dict) -> None:
        for k, v in metrics.items():
            self._ensure(k)
            self.forecasters[k]["ma"].update(v)
            self.forecasters[k]["es"].update(v)
        self._tick += 1
        if self._tick % self._eval_interval == 0:
            self._reevaluate()

    def _reevaluate(self) -> None:
        for _name, bag in self.forecasters.items():
            ma_pred = bag["ma"].predict()
            es_pred = bag["es"].predict()
            last_val = bag["ma"]._samples[-1] if bag["ma"]._samples else 0
            bag["best"] = (
                bag["ma"] if abs(ma_pred - last_val) < abs(es_pred - last_val) else bag["es"]
            )

    def predict_all(self) -> dict:
        out = {}
        for name, bag in self.forecasters.items():
            forecaster = bag["best"] or bag["ma"]
            out[name] = forecaster.predict()
        return out
