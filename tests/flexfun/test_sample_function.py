# (C) 2024 GoodData Corporation
from flexfun.sample_function import SampleFlexFunction


def test_sample_function1(flexfun_parameters):
    fun = SampleFlexFunction.create()
    result = fun.call(flexfun_parameters, None, {})

    assert result is not None
