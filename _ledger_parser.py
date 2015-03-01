import pyparsing
from collections import namedtuple
from pyparsing import (ParserElement, OneOrMore, ZeroOrMore, Word, nums,
                       alphas, alphanums, delimitedList, Group, Combine,
                       SkipTo, Optional, Literal,
                       restOfLine, LineStart, LineEnd, StringEnd)

__all__ = ['load_ledger']


CurrencyAmount = namedtuple('CurrencyAmount', 'currency amount')

ws = ' \t'
ParserElement.setDefaultWhitespaceChars(ws)

EOL = LineEnd().suppress()
SOL = LineStart().leaveWhitespace()
blankline = SOL + LineEnd()

noIndentation = SOL + ~Word(ws).leaveWhitespace().suppress()
indentation = SOL + Word(ws).leaveWhitespace().suppress()

date = Combine(Word(nums, exact=4) + '-' +
               Word(nums, exact=2) + '-' +
               Word(nums, exact=2))

description = SkipTo(';' | EOL)

accountName = SkipTo(Literal('  ') | Literal(';') | Literal('\n'))
currency = Word(alphas + '£$')
number = Word(nums + '-.,')
amount = currency('currency') + number('value')
postingLine = (indentation +
               accountName('account') +
               Optional(amount)('amount') + restOfLine + EOL)
postings = OneOrMore(Group(postingLine))

transaction = (date('date') +
               description('description') + EOL +
               Group(postings)('postings'))

# # Single statements
# keyword = Word(alphanums)
# singleValue = restOfLine
# singleValue.setParseAction(lambda tokens: tokens[0].strip())
# valueList = delimitedList(Word(alphas))
# value = Group(valueList) ^ singleValue
# oneLineStatement = keyword("keyword") + value("value") + EOL

# # If statements
# nonIndentedLine = noIndentation + restOfLine() + EOL
# indentedLine = indentation + oneLineStatement
# indentedBody = OneOrMore(indentedLine)

# ifConditions = (restOfLine() + EOL +
#                 ZeroOrMore(nonIndentedLine))
# ifConditions.setParseAction(lambda tokens: [t for t in tokens if t])

# ifStatement = ("if" +
#                Group(ifConditions)("conditions") +
#                Group(indentedBody)("body"))

# Main parser
body = OneOrMore(Group(transaction) | EOL)
parser = body + StringEnd()
parser.setDebug()
parser.ignore(blankline)
parser.ignore('#' + restOfLine)
parser.ignore(';' + restOfLine)


def convert_transaction(transaction):
    t = transaction.asDict()
    t['postings'] = [p.asDict() for p in t['postings']]
    for p in t['postings']:
        p['amount'] = CurrencyAmount(p['amount']['currency'],
                                     p['amount']['value'])
    return t


def load_ledger(filename):
    transactions = []
    f = None
    close = False
    try:
        if isinstance(filename, str):
            f = open(filename, 'r')
            close = True
        else:
            f = filename
        for transaction in parser.parseFile(f):
            transactions.append(convert_transaction(transaction))
    except pyparsing.ParseException as err:
        print(err.line)
        print(" "*(err.column-1) + "^")
        print(err)
    finally:
        if close:
            f.close()
    return transactions
