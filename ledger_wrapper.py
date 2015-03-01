import subprocess
import logging


class LedgerError(Exception):
    pass


class Ledger:
    def __init__(self, ledger_file=None):
        self.ledger_file = ledger_file

    def _run_ledger(self, args):
        cmdline = ['hledger']
        if self.ledger_file:
            cmdline += ['-f', self.ledger_file]
        cmdline += args
        try:
            result = subprocess.check_output(cmdline)
        except subprocess.CalledProcessError as err:
            logging.error("Error calling hledger [ret {}]. Command line: {}"
                          .format(err.returncode, cmdline))
            raise LedgerError("Error calling hledger")
        result = result.decode('utf8')
        return result

    def find_transaction(self, **query):
        # Need to use reg not print command: matches postings rather
        # than whole transactions.
        args = ['reg']
        for k, v in query.items():
            if k == 'amt':
                v = '{:+f}'.format(v)
            args.append('{}:{}'.format(k, v))
        result = self._run_ledger(args)
        if result:
            return result
        else:
            return None
