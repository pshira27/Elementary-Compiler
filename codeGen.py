import sys

#Global Var

lexer = None

asmheader = ("DEFAULT REL\n" +
             "extern printf\n" +
             "extern fflush\n" +
             "global main\n")
asmdata = 'section .data\n'
asmtext = "section .text\n" + "main:\n"
asmleave = 'xor rax, rax\npop rbp\nret\n'

fflush_label = "fflush"

empty_str = '""'
str_prefix = "_STR"
global_str_counter = 0
global_str = {}
global_var = []
global_if_counter = 0

reg_order = ["rcx", "rdx", "r8", "r9"]

#------------------------------------ Get Set Add Function
def getHeader():
    global asmheader
    return asmheader
def getData():
    global asmdata
    return asmdata
def getText():
    global asmtext
    return asmtext
def getLeave():
    global asmleave
    return asmleave

def getFunction(tuple):
    print("-", tuple[1])
    if tuple[0] is not "Start": #Found an error or EoF
        print("Found an EoF")
        return "BREAK"
    else:
        curTuple = tuple[1]
        return curTuple[0].upper()

def get_var(symbol):
    if symbol in global_var:
        return symbol
    print("Use of undeclare variable %s" % symbol)

def get_str(text):
    if text not in global_str:
        declare_string(text)
    return global_str[text]

def getMultival(stm):
    ptr = stm
    strVal = ""
    strVal += ptr[1] 
    ptr = ptr[2]
    while(ptr[0] == "MultiValue"):
        strVal += ", " + ptr[1]
        ptr = ptr[2]
    return strVal

def getListval(stm):
    _stm = stm
    listVal = []
    listVal.append(_stm[0])
    if type(_stm) == tuple:
        while(True):
            if type(_stm[1]) != tuple:
                listVal.append(_stm[1])
                break
            else:
                _stm = _stm[1]
                listVal.append(_stm[0])
    return listVal

def addData(varName, value):
    global asmdata
    asmdata += "%s db %s\n" % (varName, value)

def addText(cmd = ""):
    global asmtext
    asmtext += cmd + "\n"

def addComment(cmd = ""):
    global asmtext
    asmtext += ";" + cmd +"\n"
#------------------------------------ Declare Function
def declare_string(text):
    global global_str_counter
    if text not in global_str:
        asm_symbol = str_prefix + str(global_str_counter)
        global_str[text] = asm_symbol
        _text = ''
        if '\\n' in text:
            texts = text.replace('"', '').split('\\n')
            for t in texts:
                if t:
                    _text += '"' + t + '", 10,'
            _text += ' 0'
        else:
            _text = text + ', 0'
        addData(asm_symbol, _text)
        global_str_counter += 1

def declare_var(var_name, value, assign=None):
    global global_var
    global asmdata

    if var_name in global_var:
        print("Error!, Duplicate var is declared")
    else:
        global_var.append(var_name)
        if assign is None:
            addData(var_name, value)
        elif assign == "arrayDup":
            asmdata += var_name + " times " + str(value) + " dq 0" + "\n"

#------------------------------------ Function routine
def declacration_routine(stm):
    #print("visited declacration_routine")
    print(type(stm[2]))
    if type(stm[2]) is not tuple: #Default
        if stm[1] == "string":
            declare_var(stm[2],"'             $', 0")
        else:
            declare_var(stm[2],"0")
    else:
        temp = stm[2]
        print(temp)
        print(temp[0])
        if temp[0] == "ArrayDeclaration":
            declare_var(temp[1], temp[3], "arrayDup")
        elif temp[0] == "ArrayMultiAssign":
            name = temp[1]
            arrValue = getMultival(temp[5])
            declare_var(name, arrValue)
        elif temp[0] == "AssignConstant":
            if type(temp[3]) == tuple:      #Need operation routine
                operation_routine(temp[3])
            else:
                declare_var(temp[1], temp[3])
        elif temp[0] == "AssignString":
            print("sth")
        else:
            print("I think something went wrong :T")

def operation_routine(stm):
    print("operation_routine")

def expression_routine(stm):
    print("expression_routine")

def print_routine(stm):
    print("-> print_routine")
    text = stm[1]
    if "%d" in text or "%x" in text:
        lists = getListval(stm[2])
        print(lists)

    texts = get_str(text)
    addText("mov rcx, %s" % texts)
    addText("call printf")
    addText("xor %s, %s" % (reg_order[0], reg_order[0]))
    addText("call " + fflush_label)
    addText()

def println_routine(stm):
    _stm = list(stm)
    print("-> println_routine")
    texts = '"' + stm[1].replace('"', '') + "\\n"+'"'
    _stm[1] = texts
    print_routine(tuple(_stm))

#------------------------------------ ASM init
addData("_fmin", '"%ld", 0')
addComment("- Start Here")
addText("push rbp")
addText()

#------------------------------------ Main is here
def statement_main(tuple):
    currentTuple = tuple
    while(True):
        state = getFunction(currentTuple)
        stateTuple = currentTuple[1]
        print("",state)
        if state == "BREAK":
            addText("")
            addComment("terminate program")
            addText(asmleave)
            break
        elif state == "DECLARATION":
            print("")
            declacration_routine(stateTuple)
        elif state == "EXPRESSION":
            print("")
            expression_routine(stateTuple)
        elif state == "PRINT":
            print("")
            print_routine(stateTuple)
        elif state == "PRINTLN":
            print("")
            println_routine(stateTuple)
        elif state == "FORLOOP":
            print("")
        elif state == "WHILELOOP":
            print("")

        #Next STM
        currentTuple = currentTuple[2]
        print("-----------------------------")