from textx import metamodel_from_file
import sys

# Validate that a filename argument was passed
try :
    assert(sys.argv[1])
except :
    raise TypeError("Missing argument for program filename")

# Current state of all variables
state = {}

def eval_print(print_stmt) :
    values = print_stmt.values
    for i in values:
        if isinstance(i, str) and i in state:
            print(state[i], end = '')
            
        else:
            print(i, end = '')
    print()

def eval_create(create_stmt):
    if create_stmt.var not in state:
        if create_stmt.value == None:
            state[create_stmt.var] = None
        else:
            state[create_stmt.var] = eval_expr(create_stmt.value)
    else:
        raise Exception("Cannot create new variable with the same name as an existing variable")
    
def eval_assign(assign_stmt):
    if assign_stmt.var in state:
        state[assign_stmt.var] = eval_expr(assign_stmt.value)
    else:
        raise Exception("Variable not found")
    
def eval_factor(factor_stmt):
    if isinstance(factor_stmt.value, str):
        if factor_stmt.value in state:
            return state[factor_stmt.value]
        else:
            raise Exception("Variable not found", factor_stmt.value)
    else:
        return factor_stmt.value
    
def eval_term(term_stmt):
    if term_stmt.operation == None:
        return eval_factor(term_stmt.factor1)
    else:
        match term_stmt.operation:
            case '*':
                return eval_factor(term_stmt.factor1) * eval_term(term_stmt.factor2)
            case '/':
                return eval_factor(term_stmt.factor1) / eval_term(term_stmt.factor2)
            case '%':
                return eval_factor(term_stmt.factor1) % eval_term(term_stmt.factor2)
    
def eval_expr(expr):
    if expr.operation == None:
        return eval_term(expr.term1)
    else:
        match expr.operation:
            case '+':
                return eval_term(expr.term1) + eval_expr(expr.term2)
            case '-':
                return eval_term(expr.term1) - eval_expr(expr.term2)
    
def eval_if(if_block):
    comparison = False
    for if_stmt in if_block.ifs:
        value1 = eval_expr(if_stmt.value1)
        value2 = eval_expr(if_stmt.value2)
    
        match if_stmt.comparison:
            case 'equal to':
                comparison = True if value1 == value2 else False
            case 'not equal to':
                comparison = True if value1 != value2 else False
            case 'less than':
                comparison = True if value1 < value2 else False
            case 'greater than':
                comparison = True if value1 > value2 else False
            case 'less than or equal to':
                comparison = True if value1 <= value2 else False
            case 'greater than or equal to':
                comparison = True if value1 >= value2 else False

        if comparison:
            interpret(if_stmt)
            break
    if not comparison and if_block.elses != None:
        interpret(if_block.elses)

def eval_for(for_stmt):
    state[for_stmt.var] = get_value(for_stmt.range_start)

    for state[for_stmt.var] in range(eval_expr(for_stmt.range_start), eval_expr(for_stmt.range_end) + 1):
        interpret(for_stmt)


def get_value(var):
    if isinstance(var, str) and var in state:
        return state[var]
    else:
        return var

def interpret(model):
    for stmt in model.statements:
        match stmt.__class__.__name__:
            case 'Print':
                eval_print(stmt)
            case 'Create':
                eval_create(stmt)
            case 'Assign':
                eval_assign(stmt)
            case 'If':
                eval_if(stmt)
            case 'For':
                eval_for(stmt)

# Load metamodel
verbose_mm = metamodel_from_file('verbose.tx')

# Load model
program = verbose_mm.model_from_file(sys.argv[1])

interpret(program)