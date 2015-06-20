#!/usr/bin/env python

import os.path
import time
import click
import logging
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from csv_importer import Rules, get_transactions


class Merger:
    def __init__(self, ledger_file, rules_file, yes_append, csv_files):
        self._ledger_file = ledger_file
        self._rules_file = rules_file
        self._yes_append = yes_append
        self._csv_files = csv_files
        self._observer = None

        def on_rules_modified(event):
            print()
            self.reload()
            self.print_transactions()
            self._prompt_append(wait=False)
        self._event_handler = PatternMatchingEventHandler([rules_file])
        self._event_handler.on_modified = on_rules_modified
        self._observer = Observer()
        self._observer.schedule(self._event_handler,
                                os.path.dirname(rules_file))

    def __del__(self):
        if self._observer and self._observer.is_alive():
            self._observer.stop()
            self._observer.join()

    def _prompt_append(self, wait=True):
        click.secho('\nLedger file: %s' % self._ledger_file, fg='yellow')
        click.secho('Append these transactions to Ledger file?',
                    fg='yellow', nl=False)
        if wait:
            return click.confirm('')
        else:
            click.secho(' [y/N]: ', nl=False)
            return

    def reload(self):
        print('\rReloading...\n')
        rules = Rules(self._rules_file)
        self.transactions = []
        self.unknown = []

        for csv_file in self._csv_files:
            click.secho('>>> {}'.format(csv_file), fg='blue')
            ts = []
            self.transactions.append((csv_file, ts))
            for t in get_transactions(csv_file, rules, self._ledger_file):
                print(t)
                print()
                ts.append(t)
                if t.account2 == 'expenses:unknown':
                    self.unknown.append(t)

    def print_transactions(self):
        if not any(x for (_, x) in self.transactions):
            click.secho('No new transactions found')
            return False

        if self.unknown:
            click.secho('{} transactions with unknown account:'
                        .format(len(self.unknown)), fg='yellow')
            for t in self.unknown:
                click.secho('   {}: {} (£{:0.2f})'
                            .format(t.date, t.description, t.amount))

    def main(self):
        self.reload()
        if self.print_transactions() is False:
            return

        self._observer.start()
        if self._ledger_file and (self._yes_append or self._prompt_append()):
            print('Appending...', end=' ')
            now = datetime.now().replace(microsecond=0)
            with open(self._ledger_file, 'ta') as f:
                for filename, txns in self.transactions:
                    print('; Converted from {}'.format(filename), file=f)
                    print('; [{}]\n'.format(now), file=f)
                    for t in txns:
                        print(str(t) + '\n', file=f)
            print('done')


@click.command()
@click.option('-f', '--ledger-file', type=click.Path(exists=True),
              help='Ledger file')
@click.option('-r', '--rules-file', type=click.Path(exists=True),
              help='hledger-compatible rules file')
@click.option('-y', '--yes-append', default=False, is_flag=True,
              help='don\'t ask for confirmation to append to Ledger file')
@click.argument('csv_files', type=click.Path(), nargs=-1)
def main(ledger_file, rules_file, yes_append, csv_files):
    m = Merger(ledger_file, rules_file, yes_append, csv_files)
    m.main()
