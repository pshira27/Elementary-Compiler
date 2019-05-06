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
global_if_exit = 0

reg_order = ["rcx", "rdx", "r8", "r9", "r10", "r11"]

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
    if getType(ptr) == "MultiValue":
        strVal += ptr[1] 
        ptr = ptr[2]
        while(ptr[0] == "MultiValue"):
            strVal += ", " + ptr[1]
            ptr = ptr[2]
        strVal += ", " + ptr
    else:
        strVal += ptr
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
    print(stm[2])
    if type(stm[2]) is not tuple: #Default
        if stm[1] == "string":
            declare_var(stm[2],"'$', 0")
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
            if getType(temp[3]) == "Operation":      #Need operation routine
                declare_var(temp[1], "0")
                addComment("Assign var with operation")
                operation_routine(temp[3])
                addText("mov [%s], rax" %  temp[1])
            else:
                declare_var(temp[1], temp[3])
        elif temp[0] == "AssignString":
            print("sth")
        elif temp[0] == "IF":
            print("")
        else:
            print("I think something went wrong :T")

def expression_routine(stm):
    print("expression_routine")
    var = stm[1]
    opt = stm[2]
    if var in global_var or var[1] in global_var:
        if opt == "=":
            assign_val = stm[3]
            type_assign_val = getType(assign_val)
            print(type_assign_val)
            if type_assign_val == "CONSTANT":
                var_name = var
                addText("mov rax, %s" % assign_val)
            elif type_assign_val == "ID":
                var_name = var
                addText("mov rax, [%s]" % assign_val)
            elif type_assign_val == "ArrayDeclaration":
                var_name = assign_val[1]
                index_arr = assign_val[3]
                if getType(index_arr) == "CONSTANT":
                    addText("mov rax, [%s + %s * 8]" % (var_name, index_arr))
                elif getType(index_arr) == "ID":
                    addText("mov R15, [%s]" % index_arr)
                    addText("mov rax, [%s + R15 * 8]" % (var_name))
            elif type_assign_val == "Operation":
                print("\n Enter operation via expression")
                addComment("I don't feel so good")
                # addText("xor rbx, rbx")
                # operation_routine(assign_val)
                opt = assign_val[2]
                if opt == "+":
                    addText("xor rbx, rbx")
                    operation_routine(assign_val)
                    addText("add rax, rbx")
                elif opt == "-":
                    addText("xor rbx, rbx")
                    operation_routine(assign_val)
                    addText("sub rbx, rax")
                    addText("mov rax, rbx")
                elif opt == "*":
                    addText("mov rbx, 1")
                    operation_routine(assign_val)
                    addText("imul rax, rbx")
                elif opt == "/":
                    addText("mov rbx, 1")
                    operation_routine(assign_val)
                    addText("mov r9, rax")
                    addText("mov rax, rbx")
                    addText("mov rcx, r9")
                    addText("idiv rcx")
                elif opt == "%":
                    addText("mov rbx, 1")
                    operation_routine(assign_val)
                    addText("mov r9, rax")
                    addText("mov rax, rbx")
                    addText("mov rcx, r9")
                    addText("idiv rcx")
                    addText("mov rax, rdx")
                else:
                    pass
                # noted
            if getType(var) == "ID":
                addText("mov [%s], rax" % (var))
            elif getType(var) == "ArrayDeclaration":
                var_name = var[1]
                index_arr = var[3]
                if getType(index_arr) == "CONSTANT":
                    addText("mov [%s + %s * 8], rax" % (var_name, index_arr))
                elif getType(index_arr) == "ID":
                    addText("mov R15, [%s]" % index_arr)
                    addText("mov [%s + R15 * 8], rax" % (var_name))

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
    else:
        print_error("Uses undeclaration variable")
    addText() 

def print_routine(stm):
    print("-> print_routine", stm)
    reg_c = 1
    text = stm[1]
    # try:
    #     stm_inside = stm[2]
    #     var = stm_inside[0] # (x ,sth)
    #     if var == "ArrayDeclaration":
    #         var = stm_inside
    #     print(">> ",var, type(var))
    #     try:
    #         nxtVar = stm_inside[1]
    #     except:
    #         pass
    #     while(True):
    #         if type(var) == tuple: #ArrayDeclaration
    #             var_name = var[1]
    #             var_index = var[3]
    #             addText("mov %s, [%s + %s * 8]" % (reg_order[reg_c], var_name, var_index))
    #         else:
    #             if var == '"':
    #                 pass
    #             else:
    #                 var_name = var
    #                 addText("mov %s, [%s]" % (reg_order[reg_c], var_name))

    #         reg_c += 1

    #         if type(nxtVar) == str:
    #             var_name = nxtVar
    #             addText("mov %s, [%s]" % (reg_order[reg_c], var_name))
    #             break
    #         else:
    #             stm_inside = nxtVar
    #             var = stm_inside[0] # (x ,sth)
    #             nxtVar = stm_inside[1]
    #             reg_c += 1
    # except:
    #     pass
    try:
        print("Type: ",getType(stm[2]), type(stm[2]), len(stm[2]))
        if type(stm[2]) == tuple and len(stm[2]) == 2:   #Found Multi var
            print("Multi var routine...")
            curTuple = stm[2]
            while(type(curTuple) == tuple and len(curTuple) == 2):
                if getType(curTuple[0]) == "ID":
                    print("printing ID")
                    var_name = curTuple[0]
                    addText("mov %s, [%s]" % (reg_order[reg_c], var_name))
                elif getType(curTuple[0]) == "CONSTANT":
                    print("printing CONSTANT")
                    var_name = curTuple[0]
                    addText("mov %s, %s" % (reg_order[reg_c], var_name))
                elif getType(curTuple[0]) == "ArrayDeclaration":
                    print("printing ArrayDeclaration")
                    arrTuple = curTuple[0]
                    if getType(arrTuple[3]) == "ID":
                        print()
                        var_name = arrTuple[1]
                        var_index = arrTuple[3]
                        addText("mov R15, [%s]" % var_index)
                        addText("mov %s, [%s + R15 * 8]" % (reg_order[reg_c], var_name))
                    elif getType(arrTuple[3]) == "CONSTANT":
                        print()
                        var_name = arrTuple[1]
                        var_index = arrTuple[3]
                        addText("mov %s, [%s + %s * 8]" % (reg_order[reg_c], var_name, var_index)) 
                reg_c += 1
                curTuple = curTuple[1]
            # Last Var
            print("printing the lastest")
            if getType(curTuple) == "ID":
                print("printing ID")
                var_name = curTuple
                addText("mov %s, [%s]" % (reg_order[reg_c], var_name))
            elif getType(curTuple) == "CONSTANT":
                print("printing CONSTANT")
                var_name = curTuple
                addText("mov %s, %s" % (reg_order[reg_c], var_name))
            elif getType(curTuple) == "ArrayDeclaration":
                print("printing ArrayDeclaration")
                arrTuple = curTuple
                if getType(arrTuple[3]) == "ID":
                    print()
                    var_name = arrTuple[1]
                    var_index = arrTuple[3]
                    addText("mov R15, [%s]" % var_index)
                    addText("mov %s, [%s + R15 * 8]" % (reg_order[reg_c], var_name))
                elif getType(arrTuple[3]) == "CONSTANT":
                    print()
                    var_name = arrTuple[1]
                    var_index = arrTuple[3]
                    addText("mov %s, [%s + %s * 8]" % (reg_order[reg_c], var_name, var_index))
        else:
            if getType(stm[2]) == "ID":
                print("printing ID")
                var_name = stm[2]
                addText("mov %s, [%s]" % (reg_order[reg_c], var_name))
            elif getType(stm[2]) == "CONSTANT":
                print("printing CONSTANT")
                var_name = stm[2]
                if var_name == '"':
                    addText('mov %s, " "' % (reg_order[reg_c]))
                else:
                    addText("mov %s, %s" % (reg_order[reg_c], var_name))
            elif getType(stm[2]) == "ArrayDeclaration":
                print("printing ArrayDeclaration")
                arrTuple = stm[2]
                if getType(arrTuple[3]) == "ID":
                    print()
                    var_name = arrTuple[1]
                    var_index = arrTuple[3]
                    addText("mov R15, [%s]" % var_index)
                    addText("mov %s, [%s + R15 * 8]" % (reg_order[reg_c], var_name))
                elif getType(arrTuple[3]) == "CONSTANT":
                    print()
                    var_name = arrTuple[1]
                    var_index = arrTuple[3]
                    addText("mov %s, [%s + %s * 8]" % (reg_order[reg_c], var_name, var_index))    
    except:
        pass
    
    texts = get_str(text)
    print("getting text... ",texts)
    addComment()
    addText("mov %s, %s" % (reg_order[0], texts))
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

def if_routine(stm, ifelse=False):
    global global_if_counter
    global global_if_exit

    global_if_counter += 1
    stm_inside = stm[2]
    cmp_inside = stm[1]
    exit_c = global_if_counter
    exit_l = global_if_exit
    print(stm_inside)
    addComment("----  If %s " % global_if_counter)
    # CMP routine
    cmp_routine(cmp_inside)
    global_if_exit += 1
    statement_main(stm_inside)
    if ifelse:
        addText("ex_%d:" % (exit_l - 1))   #jmp global_exit
        addComment()
    addText("jmp ex_%d" % exit_l)
    addText("_L%d:" % exit_c)
    try:                                    #Have Else - Elif stm
        getElse = stm[3]
        print(getElse[0])
        if getElse[0] == "else":
            addComment("Else-routine")
            statement_main(getElse[1])
            addText("ex_%d:" % exit_l)
        elif getElse[0] == "elif":
            if_routine(getElse, True)
    except:
        addText("ex_%d:" % exit_l)
        pass
    #------------
    addComment()
    
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
        if getType(var_a) == "Operation":
            print()
            operation_routine(var_a)
        elif getType(var_a) == "ArrayDeclaration":
            var_name = var_a[1]
            index_arr = var_a[3]
            if getType(index_arr) == "CONSTANT":
                addText("mov rax, [%s + %s * 8]" % (var_name, index_arr))
            elif getType(index_arr) == "ID":
                addText("mov R15, [%s]" % index_arr)
                addText("mov rax, [%s + R15 * 8]" % (var_name))
    elif type(var_a) == str:
        var_name = var_a
        addText("mov rax, [%s]" % var_name)
    else:
        var_name = var_a
        addText("mov rax, %s" % var_name)

    if type(var_b) == tuple:
        if getType(var_b) == "Operation":
            print()
            addText("mov R14, rax")
            operation_routine(var_b)
            addText("mov rbx, rax")
            addText("mov rax, rbx")
        elif getType(var_a) == "ArrayDeclaration":
            var_name = var_b[1]
            index_arr = var_b[3]
            if getType(index_arr) == "CONSTANT":
                addText("mov rbx, [%s + %s * 8]" % (var_name, index_arr))
            elif getType(index_arr) == "ID":
                addText("mov R15, [%s]" % index_arr)
                addText("mov rbx, [%s + R15 * 8]" % (var_name))
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

def forloop_routine(stm):
    global global_if_counter
    loop_c = global_if_counter
    exit_c = loop_c + 1

    if stm[2] == "int":
        addComment("Start FOR-declaration")
        declar_tuple = ('Declaration', 'int', stm[3])
        exp_tuple = ('Expression', stm[3], '=', stm[4])
        declacration_routine(declar_tuple)
        expression_routine(exp_tuple)
        cmp_inside = stm[5]
        opt_inside = stm[6]
        stm_inside = stm[7]
        addComment()
    elif type(stm[2]) == str:
        addComment("Start FOR-expression")
        exp_tuple = ('Expression', stm[2], '=', stm[3])
        expression_routine(exp_tuple)
        cmp_inside = stm[4]
        opt_inside = stm[5]
        stm_inside = stm[6]
        addComment()

    addText("_L%d:" % loop_c)
    global_if_counter += 1
    print(cmp_inside, opt_inside)
    cmp_routine(cmp_inside)
    global_if_counter += 1
    statement_main(stm_inside)
    if opt_inside[0] == "IncrementOrDecrement":
        exp_tuple2 = ('Expression', opt_inside[1], opt_inside[2])
        expression_routine(exp_tuple2)
    addText("jmp _L%d" % loop_c)
    addText("_L%d:" % exit_c)

#------------------------------------ Operation routine
def getType(o):
    if type(o) == tuple:
        otype = o[0]
    elif o in global_var:
        otype = 'ID'
    else:
        otype = 'CONSTANT'
    return otype

def operation_routine(stm, count = 0):
    print("operation_routine")
    a = stm[1]
    b = stm[3]
    if getType(a) == "Operation" and getType(b) != "Operation":
        a = stm[1]
        b = stm[3]
    elif getType(b) == "Operation" and getType(a) != "Operation":
        a = stm[3]
        b = stm[1]
    else:
        a = stm[1]
        b = stm[3]
    opt = stm[2]
    if opt == "+":
        plus_routine(a,b,count)
    elif opt == "-":
        minus_routine(a,b,count)
    elif opt == "*":
        multiply_routine(a,b,count)
    elif opt == "/":
        divide_routine(a,b,count)
    elif opt == "%":
        mod_routine(a,b,count)
    else:
        print_error("ERROR unknown operation")
    
def plus_routine(a, b, count=0):
    a_type = getType(a)
    b_type = getType(b)
    addComment("plus_routine")
    if a_type == 'CONSTANT':
        if count == 0:
            addText("mov rax, %s" % a)
        else:
            addText("add rax, " + a)
    elif a_type == 'ID':
        get_var(a)
        if count == 0:
            addText("mov rax, [%s]" % a)
        else:
            addText("add rax, [%s]" % a)
    elif a_type == 'ArrayDeclaration':
        a_name = a[1]
        a_index = a[3]
        if getType(a_index) == "CONSTANT":
            if count == 0:
                addText("mov rax, [%s + %s * 8]" % (a_name, a_index))
            else:
                addText("add rax, [%s + %s * 8]" % (a_name, a_index))
        elif getType(a_index) == "ID":
            if count == 0:
                addText("mov R15, [%s]" % a_index)
                addText("mov rax, [%s + R15 * 8]" % (a_name))
            else:
                addText("mov R15, [%s]" % a_index)
                addText("add rax, [%s + R15 * 8]" % (a_name))
        else:
            print_error("Error array A index is invalid")
    elif a_type == "Operation":
        operation_routine(a, count)
    else:
        print_error("ERROR AT - A - IN PLUS ROUTINE")

    if count == 0 and b_type == "Operation":
        addText("mov rbx, rax")
        addText("xor rax, rax")
    else:
        count += 1

    if b_type == 'CONSTANT':
        addText("add rax, " + b)
    elif b_type == 'ID':
        get_var(b)
        addText("add rax, [%s]" % b)
    elif b_type == 'ArrayDeclaration':
        b_name = b[1]
        b_index = b[3]
        if getType(b_index) == "CONSTANT":
            addText("add rax, [%s + %s * 8]" % (b_name, b_index))
        elif getType(a_index) == "ID":
            addText("mov R15, [%s]" % b_index)
            addText("add rax, [%s + R15 * 8]" % (b_name))
        else:
            print_error("Error array B index is invalid")
    elif b_type == "Operation":
        operation_routine(b, count)
    else:
        print_error("ERROR AT - B - IN PLUS ROUTINE")

def minus_routine(a, b, count=0):
    a_type = getType(a)
    b_type = getType(b)
    addComment("minus_routine")
    if a_type == 'CONSTANT':
        if count == 0:
            addText("mov rax, %s" % a)
        else:
            addText("sub rax, " + a)
    elif a_type == 'ID':
        get_var(a)
        if count == 0:
            addText("mov rax, [%s]" % a)
        else:
            addText("sub rax, [%s]" % a)
    elif a_type == 'ArrayDeclaration':
        a_name = a[1]
        a_index = a[3]
        if getType(a_index) == "CONSTANT":
            if count == 0:
                addText("mov rax, [%s + %s * 8]" % (a_name, a_index))
            else:
                addText("sub rax, [%s + %s * 8]" % (a_name, a_index))
        elif getType(a_index) == "ID":
            if count == 0:
                addText("mov R15, [%s]" % a_index)
                addText("mov rax, [%s + R15 * 8]" % (a_name))
            else:
                addText("mov R15, [%s]" % a_index)
                addText("sub rax, [%s + R15 * 8]" % (a_name))
        else:
            print_error("Error array A index is invalid")
    elif a_type == "Operation":
        operation_routine(a, count)
    else:
        print_error("ERROR AT - A - IN MINUS ROUTINE")

    if count == 0 and b_type == "Operation":
        addText("mov rbx, rax")
        addText("xor rax, rax")
    else:
        count += 1

    if b_type == 'CONSTANT':
        addText("sub rax, " + b)
    elif b_type == 'ID':
        get_var(b)
        addText("sub rax, [%s]" % b)
    elif b_type == 'ArrayDeclaration':
        b_name = b[1]
        b_index = b[3]
        if getType(b_index) == "CONSTANT":
            addText("sub rax, [%s + %s * 8]" % (b_name, b_index))
        elif getType(b_index) == "ID":
            addText("mov R15, [%s]" % b_index)
            addText("sub rax, [%s + R15 * 8]" % (b_name))
        else:
            print_error("Error array B index is invalid")
    elif b_type == "Operation":
        operation_routine(b, count)
    else:
        print_error("ERROR AT - B - IN MINUS ROUTINE")

def multiply_routine(a, b, count=0):
    a_type = getType(a)
    b_type = getType(b)
    addComment("multiply_routine")
    if a_type == 'CONSTANT':
        if count == 0:
            addText("mov rax, %s" % a)
        else:
            addText("imul rax, " + a)
    elif a_type == 'ID':
        get_var(a)
        if count == 0:
            addText("mov rax, [%s]" % a)
        else:
            addText("imul rax, [%s]" % a)
    elif a_type == 'ArrayDeclaration':
        a_name = a[1]
        a_index = a[3]
        if getType(a_index) == "CONSTANT":
            if count == 0:
                addText("mov rax, [%s + %s * 8]" % (a_name, a_index))
            else:
                addText("imul rax, [%s + %s * 8]" % (a_name, a_index))
        elif getType(a_index) == "ID":
            if count == 0:
                addText("mov R15, [%s]" % a_index)
                addText("mov rax, [%s + R15 * 8]" % (a_name))
            else:
                addText("mov R15, [%s]" % a_index)
                addText("imul rax, [%s + R15 * 8]" % (a_name))
        else:
            print_error("Error array A index is invalid")
    elif a_type == "Operation":
        operation_routine(a, count)
    else:
        print_error("ERROR AT - A - IN MULITIPLY ROUTINE")

    if count == 0 and b_type == "Operation":
        addText("mov rbx, rax")
        addText("xor rax, rax")
    else:
        count += 1

    if b_type == 'CONSTANT':
        addText("imul rax, " + b)
    elif b_type == 'ID':
        get_var(b)
        addText("imul rax, [%s]" % b)
    elif b_type == 'ArrayDeclaration':
        b_name = b[1]
        b_index = b[3]
        if getType(b_index) == "CONSTANT":
            addText("imul rax, [%s + %s * 8]" % (b_name, b_index))
        elif getType(b_index) == "ID":
            addText("mov R15, [%s]" % b_index)
            addText("imul rax, [%s + R15 * 8]" % (b_name))
        else:
            print_error("Error array B index is invalid")
    elif b_type == "Operation":
        operation_routine(b, count)
    else:
        print_error("ERROR AT - B - IN MULITIPLY ROUTINE")

def divide_routine(a, b, count=0):
    a_type = getType(a)
    b_type = getType(b)
    addComment("divide_routine")
    addText('xor rdx, rdx')
    if a_type == 'CONSTANT':
        if count == 0:
            addText("mov rax, %s" % a)
        else:
            addText("mov rcx, " + a)
            addText("idiv rcx")
    elif a_type == 'ID':
        get_var(a)
        if count == 0:
            addText("mov rax, [%s]" % a)
        else:
            addText("mov rcx, [%s]" % a)
            addText("idiv rcx")
    elif a_type == 'ArrayDeclaration':
        a_name = a[1]
        a_index = a[3]
        if getType(a_index) == "CONSTANT":
            if count == 0:
                addText("mov rax, [%s + %s * 8]" % (a_name, a_index))
            else:
                addText("mov rcx, [%s + %s * 8]" % (a_name, a_index))
                addText("idiv rcx")
        elif getType(a_index) == "ID":
            if count == 0:
                addText("mov R15, [%s]" % a_index)
                addText("mov rax, [%s + R15 * 8]" % (a_name))
            else:
                addText("mov R15, [%s]" % a_index)
                addText("mov rcx, [%s + R15 * 8]" % (a_name))
                addText("idiv rcx")
        else:
            print_error("Error array A index is invalid")
    elif a_type == "Operation":
        operation_routine(a, count)
    else:
        print_error("ERROR AT - A - IN DIVIDE ROUTINE")

    if count == 0 and b_type == "Operation":
        addText("mov rbx, rax")
        addText("xor rax, rax")
    else:
        count += 1
    addText('xor rdx, rdx')

    if b_type == 'CONSTANT':
        addText("mov rcx, " + b)
        addText("idiv rcx")
    elif b_type == 'ID':
        get_var(b)
        addText("mov rcx, [%s]" % b)
        addText("idiv rcx")
    elif b_type == 'ArrayDeclaration':
        b_name = b[1]
        b_index = b[3]
        if getType(b_index) == "CONSTANT":
            addText("mov rcx, [%s + %s * 8]" % (b_name, b_index))
            addText("idiv rcx")
        elif getType(b_index) == "ID":
            addText("mov R15, [%s]" % b_index)
            addText("mov rcx, [%s + R15 * 8]" % (b_name))
            addText("idiv rcx")
        else:
            print_error("Error array A index is invalid")
    elif b_type == "Operation":
        operation_routine(b, count)
    else:
        print_error("ERROR AT - B - IN DIVIDE ROUTINE")

def mod_routine(a, b, count=0):
    a_type = getType(a)
    b_type = getType(b)
    addComment("mod_routine")
    addText('xor rdx, rdx')
    if a_type == 'CONSTANT':
        if count == 0:
            addText("mov rax, %s" % a)
        else:
            addText("mov rcx, " + a)
            addText("idiv rcx")
            addText("mov rax, rdx")
    elif a_type == 'ID':
        get_var(a)
        if count == 0:
            addText("mov rax, [%s]" % a)
        else:
            addText("mov rcx, [%s]" % a)
            addText("idiv rcx")
            addText("mov rax, rdx")
    elif a_type == 'ArrayDeclaration':
        a_name = a[1]
        a_index = a[3]
        if getType(a_type) == "CONSTANT":
            if count == 0:
                addText("mov rax, [%s + %s * 8]" % (a_name, a_index))
            else:
                addText("mov rcx, [%s + %s * 8]" % (a_name, a_index))
                addText("idiv rcx")
                addText("mov rax, rdx")
        elif getType(a_type) == "ID":
            if count == 0:
                addText("mov R15, [%s]" % a_index)
                addText("mov rax, [%s + R15 * 8]" % (a_name))
            else:
                addText("mov R15, [%s]" % a_index)
                addText("mov rcx, [%s + R15 * 8]" % (a_name))
                addText("idiv rcx")
                addText("mov rax, rdx")
        else:
            print_error("Error array A index is invalid")
    elif a_type == "Operation":
        operation_routine(a, count)
    else:
        print_error("ERROR AT - A - IN MOD ROUTINE")

    if count == 0 and b_type == "Operation":
        addText("mov rbx, rax")
        addText("xor rax, rax")
    else:
        count += 1
    addText('xor rdx, rdx')

    if b_type == 'CONSTANT':
        addText("mov rcx, " + b)
        addText("idiv rcx")
        addText("mov rax, rdx")
    elif b_type == 'ID':
        get_var(b)
        addText("mov rcx, [%s]" % b)
        addText("idiv rcx")
        addText("mov rax, rdx")
    elif b_type == 'ArrayDeclaration':
        b_name = b[1]
        b_index = b[3]
        if getType(b_index) == "CONSTANT":
            addText("mov rcx, [%s + %s * 8]" % (b_name, b_index))
            addText("idiv rcx")
            addText("mov rax, rdx")
        elif getType(b_index) == "ID":
            addText("mov R15, [%s]" % b_index)
            addText("mov rcx, [%s + R15 * 8]" % (b_name))
            addText("idiv rcx")
            addText("mov rax, rdx")
        else:
            print_error("Error array B index is invalid")
    elif b_type == "Operation":
        operation_routine(b, count)
    else:
        print_error("ERROR AT - B - IN MOD ROUTINE")


#------------------------------------ ASM init
addData("_fmin", '"%ld", 0')
addText("push rbp")
addText()
addComment("Start Program")
addText()

#------------------------------------ Main is here
def statement_main(tuple, s=None):
    if tuple is not None:
        currentTuple = tuple
        while(True):
            state = getFunction(currentTuple)
            stateTuple = currentTuple[1]
            print("",state)
            if state == "BREAK":
                addText("")
                if s != None:
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
                forloop_routine(stateTuple)
            elif state == "WHILELOOP":
                whileloop_routine(stateTuple)
            elif state == "DO":
                do_routine(stateTuple)
            elif state == "IF":
                if_routine(stateTuple)
            elif state == "NEWLINE":
                print("")
                nl_tuple = ('" "')
                println_routine(nl_tuple)
            #Next STM
            try:
                currentTuple = currentTuple[2]
            except:
                break
            print("-----------------------------")