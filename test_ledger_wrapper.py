from contextlib import contextmanager
import unittest
from tempfile import NamedTemporaryFile

SAMPLE_TRANSACTION = """
2014-09-01 Description with multiple words
    assets:bank account  £-10.15
    expenses:misc
"""

SAMPLE_TRANSACTION_SPLIT = """
2014-09-01 Description with multiple words
    assets:bank account  £-10.15
    expenses:misc  £1.25
    expenses:other
"""


class TestLedger(unittest.TestCase):
    def _make_ledger(self, ledger_file=None):
        from ledger_wrapper import Ledger
        return Ledger(ledger_file)

    @contextmanager
    def _temp_ledger_file(self, contents):
        with NamedTemporaryFile() as f:
            f.write(contents.encode('utf8'))
            f.flush()
            yield self._make_ledger(f.name)

    def test_find_works(self):
        with self._temp_ledger_file(SAMPLE_TRANSACTION) as l:
            self.assertIsNotNone(
                l.find_transaction(acct="assets:bank account",
                                   desc="Description",
                                   amt=-10.15))

    def test_find_all_fields_must_match(self):
        with self._temp_ledger_file(SAMPLE_TRANSACTION) as l:

            self.assertIsNone(
                l.find_transaction(acct="wrong account",
                                   desc="Description",
                                   amt=-10.15))
            self.assertIsNone(
                l.find_transaction(acct="assets:bank account",
                                   desc="foo",
                                   amt=-10.15))
            self.assertIsNone(
                l.find_transaction(acct="assets:bank account",
                                   desc="Description",
                                   amt=3.00))

    def test_find_amount_sign_must_match(self):
        # (1) SAMPLE_TRANSACTION
        with self._temp_ledger_file(SAMPLE_TRANSACTION) as l:
            self.assertIsNotNone(
                l.find_transaction(acct="assets:bank account",
                                   desc="Description",
                                   amt=-10.15))
            self.assertIsNone(
                l.find_transaction(acct="assets:bank account",
                                   desc="Description",
                                   amt=10.15))

        # (2) SAMPLE_TRANSACTION_SPLIT
        with self._temp_ledger_file(SAMPLE_TRANSACTION_SPLIT) as l:
            self.assertIsNotNone(
                l.find_transaction(acct="assets:bank account",
                                   desc="Description",
                                   amt=-10.15))
            self.assertIsNone(
                l.find_transaction(acct="assets:bank account",
                                   desc="Description",
                                   amt=10.15))


if __name__ == '__main__':
    unittest.main()
