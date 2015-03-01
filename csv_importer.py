import re
import csv
from datetime import datetime
from csv_rules import Rules
from ledger_wrapper import Ledger


class Transaction:
    def __init__(self, date, account1, account2, amount, currency,
                 description="", balance=None, code=None):
        self.date = date
        self.account1 = account1
        self.account2 = account2
        self.amount = amount
        self.currency = currency
        self.description = description
        self.balance = balance
        self.code = code

    def __str__(self):
        assertion = ''
        if self.balance is not None:
            assertion = " = {}{}".format(self.currency, self.balance)
        maybe_code = ' ({})'.format(self.code) if self.code else ''
        return "{}{} {}\n    {}  {}{:.02f}{}\n    {}  {}{:.02f}".format(
            self.date, maybe_code, self.description,
            self.account1, self.currency, self.amount, assertion,
            self.account2, self.currency, -self.amount)


REQUIRED_FIELDS = set([
    'date',
    'description',
    'account1',
    'account2',
    'amount',
])


def read_transactions_from_csv(filename, rules):
    def field(name, line):
        i = list(rules.options['fields']).index(name)
        return line[i]
    with open(filename, 'r') as f:
        for i in range(rules.options.get('skip', 0)):
            f.readline()
        reader = csv.reader(f)
        for line_list in reader:
            line = {}
            for i, fieldname in enumerate(rules.options['fields']):
                line[i] = line[fieldname] = line_list[i]

            # The * looks like a reconciled transaction so don't allow
            # it at start of descriptions.
            # TODO: should probably strip any non-alphanum chars
            desc = line['description'].lstrip('*')

            match = rules.match(desc)
            if 'date' not in match:
                match['date'] = field('date', line)
            if 'amount' not in match:
                try:
                    match['amount'] = float(field('amount', line))
                except ValueError:
                    pass
            if 'balance' not in match:
                try:
                    match['balance'] = float(field('balance', line))
                except ValueError:
                    pass
            if 'description' not in match:
                match['description'] = desc
            missing_keys = REQUIRED_FIELDS.difference(match.keys())
            if missing_keys:
                raise RuntimeError("Required field missing: {}"
                                   .format(missing_keys))

            # Do string formatting with CSV fields
            for k in match:
                if isinstance(match[k], str):
                    match[k] = match[k].format(**line)

            t = Transaction(match['date'],
                            match['account1'],
                            match['account2'],
                            match['amount'],
                            match['currency'],
                            match['description'],
                            match.get('balance', None),
                            match.get('code', None))
            yield t


def escape(s):
    for c in '.*?+^$[]()':
        s = s.replace(c, '\\' + c)
    return s


def deduplicate_transactions(transactions, ledger):
    for t in transactions:
        existing = ledger.find_transaction(
            date=t.date,
            desc=escape(t.description),
            acct=t.account1,
            amt=t.amount,
            cur=t.currency)
        if not existing:
            yield t


def print_transactions(filename, rules, existing_ledger=None):
    transactions = read_transactions_from_csv(filename, rules)
    if existing_ledger:
        ledger = Ledger(existing_ledger)
        transactions = deduplicate_transactions(transactions, ledger)
    print("; Converted from {}\n; [{}]\n"
          .format(filename, datetime.now().replace(microsecond=0)))
    for t in transactions:
        print(t)
        print()


if __name__ == "__main__":
    import sys
    rules = Rules(sys.argv[1])
    if len(sys.argv) > 3:
        existing_ledger = sys.argv[3]
    else:
        existing_ledger = None
    print_transactions(sys.argv[2], rules, existing_ledger)
