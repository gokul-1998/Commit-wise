import unittest

from gai.providers.reviewer import review_staged_changes


class ReviewerTests(unittest.TestCase):
    def test_review_flags_missing_tests_and_password_risk(self):
        result = review_staged_changes(
            ["app/services/user.py"],
            "+ password = request.json['password']\n+ except:\n",
        )

        self.assertFalse(result.security)
        self.assertFalse(result.tests)
        self.assertTrue(any("No test updates" in s.message for s in result.suggestions))
        self.assertTrue(any("password" in s.message.lower() for s in result.suggestions))

    def test_non_source_files_do_not_require_tests(self):
        result = review_staged_changes(
            ["Dockerfile", ".env.example", ".dockerignore"],
            "+ FROM python:3.12\n+ ENV DEBUG=1\n",
        )

        self.assertTrue(result.tests)
        self.assertFalse(any("No test updates" in s.message for s in result.suggestions))
        self.assertTrue(any("configuration" in s.fix.lower() for s in result.suggestions))


if __name__ == "__main__":
    unittest.main()
