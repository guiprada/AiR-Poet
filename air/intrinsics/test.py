import unittest
from air.intrinsics.intrinsics import (
    adder, subtracter, multiplier, divider,
    add, subtract, multiply, divide,
    modulus, exponent, floor_divide,
    less_than, less_than_or_equal, greater_than, greater_than_or_equal, equal, not_equal,
    is_number, is_null, not_fn,
    OPERATOR_DICT, OPERATOR_LIST,
)


class TestArithmeticVariadic(unittest.TestCase):

    def test_adder_zero_args(self):
        self.assertEqual(adder(), 0)

    def test_adder_one_arg(self):
        self.assertEqual(adder(5), 5)

    def test_adder_many(self):
        self.assertEqual(adder(1, 2, 3, 4), 10)

    def test_subtracter_zero_args_raises(self):
        with self.assertRaises(TypeError):
            subtracter()

    def test_subtracter_one_arg_negation(self):
        self.assertEqual(subtracter(5), -5)
        self.assertEqual(subtracter(-3), 3)

    def test_subtracter_two_args(self):
        self.assertEqual(subtracter(10, 3), 7)

    def test_subtracter_chain(self):
        self.assertEqual(subtracter(10, 3, 2), 5)

    def test_multiplier_zero_args(self):
        self.assertEqual(multiplier(), 1)

    def test_multiplier_chain(self):
        self.assertEqual(multiplier(2, 3, 4), 24)

    def test_divider_basic(self):
        self.assertAlmostEqual(divider(10, 2), 5.0)

    def test_divider_zero_divisor_raises(self):
        with self.assertRaises(ZeroDivisionError):
            divider(1, 0)


class TestArithmeticBinary(unittest.TestCase):

    def test_add(self):
        self.assertEqual(add(3, 4), 7)

    def test_subtract(self):
        self.assertEqual(subtract(10, 3), 7)

    def test_multiply(self):
        self.assertEqual(multiply(3, 4), 12)

    def test_divide(self):
        self.assertAlmostEqual(divide(7, 2), 3.5)

    def test_divide_by_zero_raises(self):
        with self.assertRaises(ValueError):
            divide(1, 0)

    def test_modulus(self):
        self.assertEqual(modulus(10, 3), 1)

    def test_exponent(self):
        self.assertEqual(exponent(2, 10), 1024)

    def test_floor_divide(self):
        self.assertEqual(floor_divide(7, 2), 3)

    def test_floor_divide_by_zero_raises(self):
        with self.assertRaises(ValueError):
            floor_divide(5, 0)


class TestComparison(unittest.TestCase):

    def test_less_than(self):
        self.assertTrue(less_than(1, 2))
        self.assertFalse(less_than(2, 1))

    def test_less_than_or_equal(self):
        self.assertTrue(less_than_or_equal(2, 2))

    def test_greater_than(self):
        self.assertTrue(greater_than(3, 2))

    def test_greater_than_or_equal(self):
        self.assertTrue(greater_than_or_equal(3, 3))

    def test_equal(self):
        self.assertTrue(equal(42, 42))
        self.assertFalse(equal(1, 2))

    def test_not_equal(self):
        self.assertTrue(not_equal(1, 2))


class TestTypePredicates(unittest.TestCase):

    def test_is_number_int(self):
        self.assertTrue(is_number(42))

    def test_is_number_float(self):
        self.assertTrue(is_number(3.14))

    def test_is_number_string(self):
        self.assertFalse(is_number("hello"))

    def test_is_number_none(self):
        self.assertFalse(is_number(None))

    def test_is_null_none(self):
        self.assertTrue(is_null(None))

    def test_is_null_zero(self):
        self.assertFalse(is_null(0))

    def test_is_null_false(self):
        self.assertFalse(is_null(False))

    def test_not_fn_true(self):
        self.assertFalse(not_fn(True))

    def test_not_fn_false(self):
        self.assertTrue(not_fn(False))

    def test_not_fn_zero(self):
        self.assertTrue(not_fn(0))


class TestOperatorDict(unittest.TestCase):

    def test_operator_dict_plus(self):
        self.assertEqual(OPERATOR_DICT['+'](3, 4), 7)

    def test_operator_dict_minus_binary(self):
        self.assertEqual(OPERATOR_DICT['-'](10, 3), 7)

    def test_operator_dict_minus_unary(self):
        self.assertEqual(OPERATOR_DICT['-'](5), -5)

    def test_operator_dict_minus_zero_raises(self):
        with self.assertRaises(TypeError):
            OPERATOR_DICT['-']()

    def test_operator_dict_star(self):
        self.assertEqual(OPERATOR_DICT['*'](3, 4), 12)

    def test_operator_dict_floor_div(self):
        self.assertEqual(OPERATOR_DICT['//'](7, 2), 3)

    def test_operator_list_contains_all(self):
        for op in ['+', '-', '*', '/', '//', '%', '^', '<', '<=', '>', '>=', '==', '!=']:
            self.assertIn(op, OPERATOR_LIST)


if __name__ == '__main__':
    unittest.main()
