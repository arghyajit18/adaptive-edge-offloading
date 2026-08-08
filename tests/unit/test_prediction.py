import pytest
from adaptive_engine.prediction.moving_average import MovingAverageForecaster
from adaptive_engine.prediction.exp_smoothing import ExpSmoothingForecaster
def test_moving_average():
    f = MovingAverageForecaster(window=3)
    for v in 10,20,30:
        f.update(v)
    assert f.predict() == 20.0
    f.update(40)
    assert f.predict() == 30.0
def test_exp_smoothing():
    f = ExpSmoothingForecaster(alpha=0.5)
    f.update(100)
    assert f.predict() == 100
    f.update(200)
    assert f.predict() == 150
