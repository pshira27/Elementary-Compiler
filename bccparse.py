import ply.yacc as yacc
import bcclex
import sys

tokens = bcclex.tokens

precedence = (
	('left', '+', '-'),
	('left', '*', '/', '%')
)

# ------------------ Start Grammar ------------------ #
def p_start(p):
	''' line	: 	Input line 
				|	EXIT empty'''
	if(not p[1] == None and not p[2] == None):
		p[0] = ("Start", p[1], p[2])
	else:
		p[0] = ("End")
	
def p_input(p):
	''' Input	:	Declaration
				| 	Expression
				| 	If_Statement
				| 	While_Loop
				| 	For_Loop
				| 	Do_While_Loop
				| 	Print_Console '''
	p[0] = p[1]
	
# ------------------ Declaration ------------------ #
def p_declarationStatement(p):
	''' Declaration 	: 	DeclarationTypeNumber IDENTIFIER_ALL ";"
						|	DeclarationTypeNumber ARRAY_MULTI_ASSIGN ";"
						| 	STRING IDENTIFIER ";"
						|	STRING STRING_ASSIGN ";" '''
	p[0] = ("Declaration", p[1], p[2])

def p_declarationNumberType(p):
	''' DeclarationTypeNumber 	: INT 
								| INT16 '''
	p[0] = p[1]
	
def p_identifierAssign(p):
	' IDENTIFIER_ASSIGN		:	IDENTIFIER "=" OperationConstant '
	p[0] = ("AssignConstant", p[1], p[2], p[3])

def p_stringAssign(p):
	''' STRING_ASSIGN		:	IDENTIFIER "=" DQ_MSG '''
	p[0] = ("AssignString", p[1], p[2], p[3])
	
def p_IdentifierArray(p):
	' IDENTIFIER_ARRAY	:	IDENTIFIER "[" ARRAY_SIZE "]" '
	p[0] = ("ArrayDeclaration", p[1], p[2], p[3], p[4])

def p_IdentifierArrayWithAssign(p):
	' ARRAY_MULTI_ASSIGN	:	IDENTIFIER "[" "]" "=" "{" MULTI_ASSIGN "}" '
	p[0] = ("ArrayMultiAssign", p[1], p[2], p[3], p[4], p[6])
	
def p_MultiAssign(p):
	''' MULTI_ASSIGN		:	CONSTANT "," MULTI_ASSIGN
							|	CONSTANT empty'''
	if(p[2] == ","):
		p[0] = ("MultiValue", p[1], p[3])
	else:
		p[0] = p[1]

def p_sizeOfArray(p):
	''' ARRAY_SIZE		:	IDENTIFIER 
						|	OperationConstant '''
	p[0] = p[1];
	
def p_operationOfConstant(p):
	''' OperationConstant	:	OperationStatement
							|	OperationStatementInBracket
							|	MinusVariable
							|	CONSTANT_ALL
							|	IDENTIFIER_ID '''
	p[0] = p[1]

def p_operationOfConstantBracket(p):
	''' OperationStatementInBracket	:	"(" OperationStatement ")" '''
	p[0] = p[2]

def p_OperationStatements(p):
	''' OperationStatement	:	OperationConstant '+' OperationConstant 
							|	OperationConstant '-' OperationConstant 
							|	OperationConstant '*' OperationConstant
							|	OperationConstant '/' OperationConstant
							|	OperationConstant '%' OperationConstant '''
	p[0] = ("Operation", p[1], p[2], p[3])
	
def p_minusVariableDeclaration(p):
	''' MinusVariable		:	OperationVarDeclare OperationConstant '''
	if(p[1] == "+"):
		p[0] = p[2]
	else:
		p[0] = ("MinusConstant", p[1], p[2])

def p_identifierAll(p):
	''' IDENTIFIER_ALL		:	IDENTIFIER_ASSIGN
							|	IDENTIFIER_ARRAY
							|	IDENTIFIER '''
	p[0] = p[1]

def p_identifierID(p):
	''' IDENTIFIER_ID		:	IDENTIFIER_ARRAY
							|	IDENTIFIER '''
	p[0] = p[1]
	
def p_constantAll(p):
	''' CONSTANT_ALL		:	CONSTANT
							|	IDENTIFIER '''
	p[0] = p[1]
	
def p_constantDecOrHex(p):
	''' CONSTANT			:	CONSTANT10
							|	CONSTANT16 '''
	p[0] = p[1]

def p_incrementAndDecrement(p):
	''' INC_DEC_OPRERATOR	:	INC_OP
							|	DEC_OP '''
	p[0] = p[1]
	
def p_operationVariableDeclaration(p):
	''' OperationVarDeclare	:	"+"
							|	"-" '''
	p[0] = p[1]

# ------------------ Expression ------------------ #
def p_expressionStatement(p):
	''' Expression 		: 	IDENTIFIER_ID "=" OperationConstant ";"
						|	IDENTIFIER_ID "=" DQ_MSG ";"
						|	ARRAY_MULTI_ASSIGN empty ";"
						| 	IDENTIFIER_ID INC_DEC_OPRERATOR ";"
						| 	INC_DEC_OPRERATOR IDENTIFIER_ID ";" '''
	if(p[2] == "="):
		p[0] = ("Expression", p[1], p[2], p[3])
	elif(p[2] == None):
		p[0] = p[1];
	else:
		p[0] = ("Expression", p[1], p[2])

	
# ------------------ If Else Statement ------------------ #
def p_ifStatement(p):
	' If_Statement	:	IF "(" Compare_Expreession ")" "{" statements "}" Elif_Else '
	if(not p[8] == None):
		p[0] = ("if", p[3], p[6], p[8])
	else:
		p[0] = ("if", p[3], p[6])
		
def p_ElifStatement(p):
	' Elif_Statement	:	ELIF "(" Compare_Expreession ")" "{" statements "}" Elif_Else '
	if(not p[8] == None):
		p[0] = ("elif", p[3], p[6], p[8])
	else:
		p[0] = ("elif", p[3], p[6])
		
def p_ElseStatement(p):
	' Else_Statement	:	ELSE "{" statements "}" '
	p[0] = ("else", p[3])
	
def p_Statement(p):
	''' statements		:	empty empty
						|	Declaration statements
						|	Expression statements
						|	If_Statement statements
						|	While_Loop statements
						|	For_Loop statements
						|	Do_While_Loop statements
						|	Print_Console statements '''
	if(not p[1] == None and not p[2] == None):
		p[0] = ("Statement", p[1], p[2])
	elif(not p[1] == None and p[2] == None):
		p[0] = ("Statement", p[1])
	else:
		pass
	
def p_elseifStatement(p):
	''' Elif_Else		:	empty
						|	Elif_Statement
						|	Else_Statement '''
	p[0] = p[1];
	
def p_compareExpressionStatement(p):
	''' Compare_Expreession		:	OperationConstant Compare_Operator OperationConstant '''
	p[0] = ("Compare", p[1], p[2], p[3])
	
def p_compareOperator(p):
	''' Compare_Operator	:	L_OP
							|	G_OP
							|	LE_OP
							|	GE_OP
							|	EQ_OP
							|	NE_OP '''
	p[0] = p[1];

# ------------------ While Loop ------------------ #
def p_whileLoop(p):
	''' While_Loop	:	WHILE "(" Compare_Expreession ")" "{" statements "}" '''
	p[0] = ("WhileLoop", p[3], p[6])
	
# ------------------ For Loop ------------------ #
def p_forLoop(p):
	''' For_Loop			:	FOR "(" DeclarationTypeNumber IDENTIFIER "=" OperationConstant ";" Compare_Expreession ";" IDENTIFIER_ALL_ASSIGN ")" "{" statements "}"
							|	FOR "(" DeclarationTypeNumber IDENTIFIER "=" OperationConstant ";" Compare_Expreession ";" For_Loop_Crement ")" "{" statements "}"
							|	FOR "(" IDENTIFIER "=" OperationConstant ";" Compare_Expreession ";" IDENTIFIER_ALL_ASSIGN ")" "{" statements "}"
							|	FOR "(" IDENTIFIER "=" OperationConstant ";" Compare_Expreession ";" For_Loop_Crement ")" "{" statements "}" '''
	if(p[4] == "="):
		p[0] = ("ForLoop", 'for', p[3], p[5], p[7], p[9], p[12])
	else:
		p[0] = ("ForLoop", 'for', p[3], p[4], p[6], p[8], p[10], p[13])

def p_IdentifierAllAssign(p):
	''' IDENTIFIER_ALL_ASSIGN	:	IDENTIFIER_ID "=" CONSTANT_ALL '+' IDENTIFIER_ID
								|	IDENTIFIER_ID "=" CONSTANT_ALL '-' IDENTIFIER_ID 
								|	IDENTIFIER_ID "=" CONSTANT_ALL '*' IDENTIFIER_ID
								|	IDENTIFIER_ID "=" CONSTANT_ALL '/' IDENTIFIER_ID 
								|	IDENTIFIER_ID "=" CONSTANT_ALL '%' IDENTIFIER_ID 
								|	IDENTIFIER_ID "=" IDENTIFIER_ID '+' CONSTANT_ALL
								|	IDENTIFIER_ID "=" IDENTIFIER_ID '-' CONSTANT_ALL 
								|	IDENTIFIER_ID "=" IDENTIFIER_ID '*' CONSTANT_ALL
								|	IDENTIFIER_ID "=" IDENTIFIER_ID '/' CONSTANT_ALL 
								|	IDENTIFIER_ID "=" IDENTIFIER_ID '%' CONSTANT_ALL '''
	p[0] = ("AssignValue", p[1], p[3], p[4], p[5])

def p_forLoopCrements(p):
	''' For_Loop_Crement	:	IDENTIFIER INC_DEC_OPRERATOR
							|	INC_DEC_OPRERATOR IDENTIFIER '''
	p[0] = ("IncrementOrDecrement", p[1], p[2])

# ------------------ Do While Loop ------------------ #
def p_doWhileLoop(p):
	''' Do_While_Loop	:	DO "{" statements "}" WHILE "(" Compare_Expreession ")" ";" '''
	p[0] = ("do", p[3], 'while', p[7])

# ------------------ Print ------------------ #
def p_printConsole(p):
	''' Print_Console		:	PRINT "(" DQ_MSG ")" ";"
							|	PRINT "(" DQ_MSG Print_Value ")" ";"
							|	PRINT_LN "(" DQ_MSG ")" ";"
							|	PRINT_LN "(" DQ_MSG Print_Value ")" ";"	
							|	PRINT_LN "(" empty empty ")" ";" '''
	if(p[4] == ")"):
		p[0] = (p[1], p[3])
	elif(p[3] == None):
		p[0] = ("newline", p[1], p[2], p[3])
	else:
		p[0] = (p[1], p[3], p[4])
	
def p_printValue(p):
	''' Print_Value			:	empty empty empty
							|	"," IDENTIFIER_ID Print_Value
							|	"," CONSTANT Print_Value
							|	"," DQ_MSG Print_Value '''
	if(not p[3] == None):
		p[0] = (p[2], p[3])
	else:
		p[0] = (p[2]);
		

# ------------------ Main ------------------ #

def p_empty(p):
    'empty :'
    pass

def p_exit(p):
	'EXIT :'
	pass

def p_error(p):
    if p:
        if p.value == '\n':
            print("Syntax error at line %d" % p.lineno)
        else:
            print("Syntax error at '%s' at line %d" %
                (p.value, p.lexer.lineno))
    else:
        print("Syntax error at EOF")
    sys.exit(1)

start = 'line'
parser = yacc.yacc()


def parse(s, debug=False):
    return parser.parse(s, tracking=True, debug=debug)
	
	