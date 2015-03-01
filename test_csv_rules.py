import unittest
import re
from io import StringIO


test_rules_file_contents = """
skip 2
fields date, description, amount, balance
currency £
account1 assets:bank

# Cash withdrawals
if
LINK
ATM
  account2 assets:cash

# Put cheque number in ()s
if [0-9]{6}
  description ({description})
"""


class RulesTest(unittest.TestCase):
    def _make_rules(self, rules_file=None):
        from csv_rules import Rules
        return Rules(rules_file)

    def test_rules_are_matched_against_description(self):
        rules = self._make_rules()
        rules.add('PATTERN', account2='account')
        self.assertNotEqual(rules.match('Description containing PATTERN'),
                            rules.defaults)
        self.assertEqual(rules.match('Description that does not match'),
                         rules.defaults)

    def test_defaults_are_overriden_by_rules(self):
        rules = self._make_rules()
        rules.set_defaults(account1='a1',
                           description='default')
        rules.add('PATTERN', account2='a2')
        rules.add('DESCRIPTION', description='new')
        self.assertEqual(rules.match('PATTERN'),
                         dict(account1='a1',
                              account2='a2',
                              description='default'))
        self.assertEqual(rules.match('DESCRIPTION'),
                         dict(account1='a1',
                              description='new'))

    def test_loads_rules_from_file(self):
        rules_file = StringIO(test_rules_file_contents)
        rules = self._make_rules(rules_file)
        self.assertEqual(
            rules.options,
            dict(skip=2,
                 fields='date description amount balance'.split()))
        self.assertEqual(
            rules.defaults,
            dict(currency='£',
                 account1='assets:bank'))
        self.assertEqual(rules.rules, [
            (re.compile('LINK'), dict(account2='assets:cash')),
            (re.compile('ATM'), dict(account2='assets:cash')),
            (re.compile('[0-9]{6}'), dict(description='({description})')),
        ])
