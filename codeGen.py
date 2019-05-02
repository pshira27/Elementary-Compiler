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
def print_error(error_str, show_line=True):
    if show_line:
        print("ERROR : %s At line %d" % (error_str, lexer.lineno))
    else:
        print("ERROR : %s" % error_str)
    sys.exit(1)

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
    if tuple is not None:
        print("-", tuple[1])
        if (tuple[0] == "Start") or (tuple[0] == "Statement"): 
            curTuple = tuple[1]
            return curTuple[0].upper()
        else: #Found an error or EoF
            print("Found an EoF")
            return "BREAK"
        

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
    strVal += ", " + ptr
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

def addData(varName, value, arr=""):
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
        print_error("Error!, Duplicate var is declared")
    else:
        global_var.append(var_name)
        if assign is None:
            asmdata += var_name + " dq " + value + "\n"
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
        elif temp[0] == "IF":
            print("")
        else:
            print("I think something went wrong :T")

def operation_routine(stm):
    print("operation_routine")

def expression_routine(stm):
    print("expression_routine")
    var = stm[1]
    opt = stm[2]
    if var in global_var or var[1] in global_var:
        if opt == "=":
            assign_val = stm[3]
            if type(var) == tuple:
                var_name = var[1]
                index_arr = var[3]
            else:
                var_name = var
        elif opt == "++":
            if type(var) == tuple:
                var_name = var[1]
                index_arr = var[3]
                addText("mov rax, [%s + %s * 8]" % (var_name, index_arr))
                addText("inc rax")
                addText("mov [%s + %s * 8], rax" % (var_name, index_arr))
            else:
                var_name = var
                addText("mov rax, [%s]" % var_name)
                addText("inc rax")
                addText("mov [%s], rax" % var_name)
        elif opt == "--":
            if type(var) == tuple:
                var_name = var[1]
                index_arr = var[3]
                addText("mov rax, [%s + %s * 8]" % (var_name, index_arr))
                addText("dec rax")
                addText("mov [%s + %s * 8], rax" % (var_name, index_arr))
            else:
                var_name = var
                addText("mov rax, [%s]" % var_name)
                addText("dec rax")
                addText("mov [%s], rax" % var_name)
        else:
            pass
            

def print_routine(stm):
    print("-> print_routine")
    text = stm[1]
    if "%d" in text or "%x" in text:
        print()
    else:
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

def if_routine(stm):
    global global_if_counter
    global_if_counter += 1
    stm_inside = stm[2]
    cmp_inside = stm[1]
    exit_c = global_if_counter

    print(stm_inside)
    addComment("----  If %s " % global_if_counter)
    # CMP routine
    cmp_routine(cmp_inside)
    try:
        getElse = stm[3]
        if getElse[0] == "else":
            statement_main(getElse)
        else:
            if_routine(getElse)
    except:
        pass
    #------------
    statement_main(stm_inside)
    addText("_L%d:" % exit_c)
    addComment("---- Exit ----")
    addText()
    
def cmp_routine(stm, exit=None):
    index_arr = 0
    var_a = stm[1]
    var_b = stm[3]
    cmp_type = stm[2]
    if exit == None:
        exit_l = global_if_counter
    else:
        exit_l = exit

    try:
        var_a = int(var_a)
    except:
        pass
    try:
        var_b = int(var_b)
    except:
        pass

    if type(var_a) == tuple:
        var_name = var_a[1]
        index_arr = var_a[3]
        addText("mov rax, [%s + %s * 8]" % (var_name, index_arr))
    elif type(var_a) == str:
        var_name = var_a
        addText("mov rax, [%s]" % var_name)
    else:
        var_name = var_a
        addText("mov rax, %s" % var_name)

    if type(var_b) == tuple:
        var_name = var_b[1]
        index_arr = var_b[3]
        addText("mov rbx, [%s + %s * 8]" % (var_name, index_arr))
    elif type(var_b) == str:
        var_name = var_b
        addText("mov rbx, [%s]" % var_name)
    else:
        var_name = var_b
        addText("mov rbx, %s" % var_name)

    addText("cmp rax, rbx")
    if cmp_type == "==":
        addText("jne _L%d" % exit_l)
    elif cmp_type == ">":
        addText("jle _L%d" % exit_l)
    elif cmp_type == ">=":
        addText("jl _L%d" % exit_l)
    elif cmp_type == "<":
        addText("jge _L%d" % exit_l)
    elif cmp_type == "<=":
        addText("jg _L%d" % exit_l)
    addComment()

def whileloop_routine(stm):
    global global_if_counter
    loop_c = global_if_counter
    exit_c = loop_c + 1

    cmp_inside = stm[1]
    stm_inside = stm[2]

    addText("_L%d:" % loop_c)
    global_if_counter += 1
    cmp_routine(cmp_inside)
    global_if_counter += 1
    statement_main(stm_inside)
    addText("jmp _L%d" % loop_c)
    addText("_L%d:" % exit_c)

def do_routine(stm):
    global global_if_counter
    global global_if_counter
    loop_c = global_if_counter
    exit_c = loop_c + 1

    cmp_inside = stm[3]
    stm_inside = stm[1]

    addText("_L%d:" % loop_c)
    global_if_counter += 1
    statement_main(stm_inside)
    cmp_routine(cmp_inside, exit_c)
    addText("jmp _L%d" % loop_c)
    addText("_L%d:" % exit_c)


#------------------------------------ ASM init
addData("_fmin", '"%ld", 0')
addComment("Start Program")
addText("push rbp")
addText()

#------------------------------------ Main is here
def statement_main(tuple):
    if tuple is not None:
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
                whileloop_routine(stateTuple)
            elif state == "DO":
                do_routine(stateTuple)
            elif state == "IF":
                if_routine(stateTuple)

            #Next STM
            try:
                currentTuple = currentTuple[2]
            except:
                break
            print("-----------------------------")