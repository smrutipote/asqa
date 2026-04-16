import pytest
import sys
import os

# Add the repo directory to the Python path to import modules
sys.path.insert(0, '/repo')

def divide(a, b):
    return a / b

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_divide_normal_case():
    result = divide(10, 2)
    assert result == 5.0

def test_divide_negative_numbers():
    result = divide(-10, 2)
    assert result == -5.0

def test_divide_float_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(3.14, 0)

def test_divide_zero_by_number():
    result = divide(0, 5)
    assert result == 0.0