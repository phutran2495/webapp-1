import unittest
import bcrypt
import main
import unittest


class TestStringMethods(unittest.TestCase):
    # test function to test equality of two value
    def test(self):
        # error message in case if test case got failed
        message = "First value and second value are not equal !"
        # assertEqual() to check equality of first & second value
        self.assertEqual(main.validate_user("Edward123!"), "ok")


if __name__ == '__main__':
    unittest.main()