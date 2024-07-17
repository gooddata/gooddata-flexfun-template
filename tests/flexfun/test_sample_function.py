# (C) 2024 GoodData Corporation
from flexfun.sample_function import SampleFlexFunction


def test_sample_function1():
    fun = SampleFlexFunction.create()
    result = fun.call({}, None, {})

    assert result is not None
