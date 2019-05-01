import ply.lex as lex
tokens = [
		'INT16',
		'INT',
		'IDENTIFIER',
		'CONSTANT10', 
		'CONSTANT16',
		'INC_OP', 
		'DEC_OP', 
		'DQ_MSG',
        'EQ_OP', 
		'L_OP', 
		'G_OP',
		'LE_OP', 
		'GE_OP', 
		'NE_OP'
		]

reserved = {
	'string': 'STRING',
	'for': 'FOR',
	'do': 'DO',
	'while': 'WHILE',
    'if': 'IF',
	'elif' : 'ELIF',
    'else': 'ELSE',
	
    'print': 'PRINT',
	'println': 'PRINT_LN',
}

tokens += reserved.values()

t_ignore = ' \t\v\n\f'
t_INC_OP = r'\+\+'
t_DEC_OP = r'--'
t_LE_OP = r'<='
t_GE_OP = r'>='
t_L_OP = r'<'
t_G_OP = r'>'
t_EQ_OP = r'=='
t_NE_OP = r'!='

t_DQ_MSG = r'\"(\\.|[^"\\])*\"'


literals = [
			'{', '}', 
			'[', ']',
			'(', ')',
			'=',
			',',
			'+',
			'-',
			'*',
			'/',
			'%',
			';',
			'"']
 
def t_COMMENT(t):
    r'/\*(.|\n)*?\*/'
    pass

# Comment (C++-Style)
def t_CPPCOMMENT(t):
    r'//.*\n'
    pass

def t_INT16(t):
	r'[iI][nN][tT]16'
	t.type = 'INT16'
	return t
	
def t_INT(t):
	r'[iI][nN][tT]'
	t.type = 'INT'
	return t	

def t_IDENTIFIER(t):
    r'[a-zA-Z_]+[0-9a-zA-Z]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    return t
	
def t_CONSTANT16(t):
    r'[a-fA-F0-9]+[hH]'
    t.value = str(t.value)
    t.type = 'CONSTANT16'
    return t	
	
def t_CONSTANT10(t):
    r'[0-9]+'
    t.value = str(t.value)
    t.type = 'CONSTANT10'
    return t
	


def t_error(t):
    print('Illegal character')
    t.lexer.skip(1)

lexer = lex.lex()
