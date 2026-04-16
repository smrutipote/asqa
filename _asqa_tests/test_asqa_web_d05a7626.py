import pytest
import sys
import os

# Add the repo directory to Python path to import modules
sys.path.insert(0, '/repo')

def divide(a, b):
    return a / b

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_divide_by_zero_with_float():
    with pytest.raises(ZeroDivisionError):
        divide(5.5, 0.0)

def test_divide_by_zero_negative_numerator():
    with pytest.raises(ZeroDivisionError):
        divide(-8, 0)

def test_divide_normal_case():
    result = divide(10, 2)
    assert result == 5.0

def test_divide_float_result():
    result = divide(7, 2)
    assert result == 3.5