import pyparsing
from pyparsing import (ParserElement, OneOrMore, ZeroOrMore, Word,
                       alphas, alphanums, delimitedList, Group,
                       restOfLine, LineStart, LineEnd, StringEnd)

__all__ = ['load_rules']

ws = ' \t'
ParserElement.setDefaultWhitespaceChars(ws)

EOL = LineEnd().suppress()
SOL = LineStart().leaveWhitespace()
blankline = SOL + LineEnd()

noIndentation = SOL + ~Word(ws).leaveWhitespace().suppress()
indentation = SOL + Word(ws).leaveWhitespace().suppress()

# Single statements
keyword = Word(alphanums)
value = restOfLine
value.setParseAction(lambda tokens: tokens[0].strip())
oneLineStatement = keyword("keyword") + value("value") + EOL

# If statements
nonIndentedLine = noIndentation + restOfLine() + EOL
indentedLine = indentation + Group(oneLineStatement)
indentedBody = OneOrMore(indentedLine)

ifConditions = (restOfLine() + EOL +
                ZeroOrMore(nonIndentedLine))
ifConditions.setParseAction(lambda tokens: [t for t in tokens if t])

ifStatement = ("if" +
               Group(ifConditions)("conditions") +
               indentedBody("body"))

# Main parser
body = OneOrMore(Group(ifStatement | oneLineStatement | EOL))
parser = body + StringEnd()
parser.ignore(blankline)
parser.ignore('#' + restOfLine)


def load_rules(filename):
    options = {}
    rules = []
    f = None
    close = False
    try:
        if isinstance(filename, str):
            f = open(filename, 'r')
            close = True
        else:
            f = filename
        for statement in parser.parseFile(f):
            if 'keyword' in statement:
                if hasattr(statement.value, 'asList'):
                    value = statement.value.asList()
                else:
                    value = statement.value
                options[statement.keyword] = value
            elif 'conditions' in statement:
                rules.append((statement.conditions.asList(),
                              statement.body.asList()))
    except pyparsing.ParseException as err:
        print(err.line)
        print(" "*(err.column-1) + "^")
        print(err)
    finally:
        if close:
            f.close()
    return options, rules
