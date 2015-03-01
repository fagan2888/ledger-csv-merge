from datetime import datetime
from glob import glob
import re


def get_last_run():
    with open('last-run-date', 'r') as f:
        return datetime.strptime('%Y-%m-%d', f.read())


def get_statements_since(date):
    for statement in glob('Statements/Statement_CURRENT*.csv'):
        m = re.search(r'_([0-9-]+)\.csv$', statement, re.I)
        print(statement)

