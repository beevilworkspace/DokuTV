import unittest
from dokutv.domain import DomainError, InvalidVideoError, ScheduleError


class TestDomainExceptions(unittest.TestCase):

    def test_exception_inheritance(self):
        self.assertTrue(issubclass(InvalidVideoError, DomainError))
        self.assertTrue(issubclass(ScheduleError, DomainError))

    def test_raising_domain_exceptions(self):
        with self.assertRaises(DomainError):
            raise InvalidVideoError("Invalid video test")

        with self.assertRaises(DomainError):
            raise ScheduleError("Invalid schedule test")


if __name__ == "__main__":
    unittest.main()
