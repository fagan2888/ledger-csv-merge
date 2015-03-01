import re
from _rules_parser import load_rules


ALLOWED_FIELDS = [
    'date',
    'date2',
    'status',
    'code',
    'description',
    'comment',
    'account1',
    'account2',
    'currency',
    'amount',
    'amount-in',
    'amount-out',
]


class Rules:
    def __init__(self, rules_file=None):
        self.rules = []
        self.options = {}
        self.defaults = {}
        if rules_file is not None:
            self.load(rules_file)

    def load(self, rules_file):
        options, rules = load_rules(rules_file)

        for opt, value in options.items():
            if opt in ALLOWED_FIELDS:
                self.defaults[opt] = value
            else:
                if opt == 'skip':
                    value = int(value)
                elif opt == 'fields':
                    value = [x.strip() for x in value.split(',')]
                self.options[opt] = value

        for patterns, body in rules:
            for pattern in patterns:
                self.add(pattern, **dict(body))

    def set_defaults(self, **kw):
        for k, v in kw.items():
            self.defaults[k] = v

    def add(self, pattern, **actions):
        assert set(actions.keys()).difference(ALLOWED_FIELDS) == set([])
        self.rules.append((re.compile(pattern), actions))

    def match(self, description):
        result = dict(self.defaults)
        for pattern, actions in self.rules:
            if pattern.search(description):
                result.update(actions)
                return result
        return result
