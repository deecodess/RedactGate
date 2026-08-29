import unittest

from redactgate.parsers import validate_format


class ParserTests(unittest.TestCase):
    def test_validates_json_success(self) -> None:
        result = validate_format("json", '{"email":"[REDACTED_EMAIL]","status":200}')
        self.assertTrue(result["passed"])

    def test_validates_json_failure(self) -> None:
        result = validate_format("json", '{"email":')
        self.assertFalse(result["passed"])

    def test_validates_csv_failure_for_inconsistent_rows(self) -> None:
        result = validate_format("csv", "id,email\n1,a@example.com,extra\n")
        self.assertFalse(result["passed"])

    def test_text_format_needs_no_structural_validation(self) -> None:
        result = validate_format("txt", "plain text")
        self.assertTrue(result["passed"])


if __name__ == "__main__":
    unittest.main()

