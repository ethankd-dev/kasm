import os
import decimal
import sys

line = ""
linenumber = 0
end = False
mode = 0
instruction_memory = [False] * 2048  # keeps track of if a memory location is assigned to something else
memory_lines = []
data_memory = [False] * 1024
subprocess_names = []
file = open("output.bin", "w")
user_defined_tokens = {

}
k86_tokens = {
    "JMP": "0000",
    "JZ": "0001",
    "JNZ": "0010",
    "JC": "0011",
    "JNC": "0100",
    "JGT": "0101",
    "JLT": "0110",
    "JO": "0111",
    "JNO": "1000",
    "JP": "1001",
    "JNP": "1010",
    "ADD": "11110000",
    "SUB": "11110001",
    "MULT": "11110010",
    "DIV": "11110011",
    "AND": "11110100",
    "OR": "11110101",
    "XOR": "11110110",
    "SHL": "11110111",
    "SHR": "11111000",
    "ROL": "11111001",
    "ROR": "11111010",
    "LOADR": "11111011",
    "SWAP": "11111100",
    "CMP": "11111101",
    "TEST": "11111110",
    "ADDI": "111111110000",
    "SUBI": "111111110001",
    "MULTI": "111111110010",
    "DIVI": "111111110011",
    "LOADI": "111111110100",
    "LOADM": "111111110101",
    "LOADA": "111111110110",
    "STORE": "111111110111",
    "CLEAR": "111111111000",
    "NOT": "111111111001",
    "NEG": "111111111010",
    "PUSH": "111111111011",
    "POP": "111111111100",
    "RET": "111111111101",
    "PRINT": "111111111110",
    "SKIPZ": "1111111111110000",
    "SKIPNZ": "1111111111110001",
    "SKIPC": "1111111111110010",
    "SKIPNC": "1111111111110011",
    "SKIPGT": "1111111111110100",
    "SKIPLT": "1111111111110101",
    "SKIPO": "1111111111110110",
    "SKIPNO": "1111111111110111",
    "SKIPP": "1111111111111000",
    "SKIPNP": "1111111111111001",
    "INPUT": "1111111111111100",
    "NOP": "1111111111111101",
    "SYS": "1111111111111110",
    "HALT": "1111111111111111"}
registers = {
    "R0": "0000",
    "R1": "0001",
    "R2": "0010",
    "R3": "0011",
    "R4": "0100",
    "R5": "0101",
    "R6": "0110",
    "R7": "0111",
    "R8": "1000",
    "R9": "1001",
    "R10": "1010",
    "R11": "1011",
    "R12": "1100",
    "R13": "1101",
    "R14": "1110",
    "R15": "1111",

}


# remember to rename the registers above


def run(filename):
    global line
    global linenumber
    global end
    global mode
    with open(filename, "r") as reader:
        for line in reader:
            linenumber += 1
            line = line.strip()
            temp = line.split("#")  # makes '#' into the comment character
            tempstr = temp[0]
            lineargs = tempstr.split()
            if len(lineargs) > 0:
                if lineargs[0] == ".data":
                    mode = 1
                elif lineargs[0] == ".code":
                    mode = 2
                else:
                    parse(lineargs)
    index=0
    for line in memory_lines:
        if not isdigit(line[4:]):
            if line[4:] in subprocess_names:
                memory_lines[index] = line[0:4]+subprocess_names[line[4:]]
        index+=1
    for i in memory_lines:
        file.write(i)


def parse(lineargs):
    global linenumber
    if mode == 1:
        if len(lineargs) != 2:
            raise Exception(
                f"Error at line {linenumber}:  Variable declarations in the .data section must be 2 arguments: a "
                f"token and a value.")
        else:
            if lineargs[0] in k86_tokens or lineargs[0] in registers:
                raise Exception(f"Error at line {linenumber}:  Provided token is a K86 token.")
            if lineargs[0] in user_defined_tokens:
                raise Exception(f"Error at line {linenumber}:  Duplicate token.")
            else:
                memalloc(lineargs[0], lineargs[1])
    if mode == 2:
        match lineargs[0]:
            case "JMP":
                jump_type(lineargs[0],lineargs[1])
            case "JZ":
                jump_type(lineargs[0], lineargs[1])
            case "JNZ":
                jump_type(lineargs[0], lineargs[1])
            case "JC":
                jump_type(lineargs[0], lineargs[1])
            case "JNC":
                jump_type(lineargs[0], lineargs[1])
            case "JGT":
                jump_type(lineargs[0], lineargs[1])
            case "JLT":
                jump_type(lineargs[0], lineargs[1])
            case "JO":
                jump_type(lineargs[0], lineargs[1])
            case "JNO":
                jump_type(lineargs[0], lineargs[1])
            case "JP":
                jump_type(lineargs[0], lineargs[1])
            case "JNP":
                jump_type(lineargs[0], lineargs[1])
            case "ADD":
                two_register(lineargs[0], lineargs[1], lineargs[2])
            case "SUB":
                two_register(lineargs[0], lineargs[1], lineargs[2])
            case "MULT":
                two_register(lineargs[0], lineargs[1], lineargs[2])
            case "DIV":
                two_register(lineargs[0], lineargs[1], lineargs[2])
            case "AND":
                two_register(lineargs[0], lineargs[1], lineargs[2])
            case "OR":
                two_register(lineargs[0], lineargs[1], lineargs[2])
            case "XOR":
                two_register(lineargs[0], lineargs[1], lineargs[2])
            case "SHL":
                shifters(lineargs[0], lineargs[1], lineargs[2])
            case "SHR":
                shifters(lineargs[0], lineargs[1], lineargs[2])
            case "ROL":
                shifters(lineargs[0], lineargs[1], lineargs[2])
            case "ROR":
                shifters(lineargs[0], lineargs[1], lineargs[2])
            case "LOADR":
                two_register(lineargs[0], lineargs[1], lineargs[2])
            case "SWAP":
                two_register(lineargs[0], lineargs[1], lineargs[2])
            case "CMP":
                two_register(lineargs[0], lineargs[1], lineargs[2])
            case "TEST":
                two_register(lineargs[0], lineargs[1], lineargs[2])
            case "ADDI":
                immediate_type(lineargs[0], lineargs[1], lineargs[2])
            case "SUBI":
                immediate_type(lineargs[0], lineargs[1], lineargs[2])
            case "MULTI":
                immediate_type(lineargs[0], lineargs[1], lineargs[2])
            case "DIVI":
                immediate_type(lineargs[0], lineargs[1], lineargs[2])
            case "LOADI":
                immediate_type(lineargs[0], lineargs[1], lineargs[2])
            case "LOADM":
                two_word_memory_type(lineargs[0], lineargs[1], lineargs[2])
            case "LOADA":
                two_word_memory_type(lineargs[0], lineargs[1], lineargs[2])
            case "STORE":
                two_word_memory_type(lineargs[0], lineargs[1], lineargs[2])
            case "CLEAR":
                one_operand(lineargs[0], lineargs[1])
            case "NOT":
                one_operand(lineargs[0], lineargs[1])
            case "NEG":
                one_operand(lineargs[0], lineargs[1])
            case "PUSH":
                one_operand(lineargs[0], lineargs[1])
            case "POP":
                one_operand(lineargs[0], lineargs[1])
            case "RET":
                one_operand(lineargs[0], lineargs[1])
            case "PRINT":
                one_operand(lineargs[0], lineargs[1])
            case "SKIPZ":
                no_operand(lineargs[0])
            case "SKIPNZ":
                no_operand(lineargs[0])
            case "SKIPC":
                no_operand(lineargs[0])
            case "SKIPNC":
                no_operand(lineargs[0])
            case "SKIPGT":
                no_operand(lineargs[0])
            case "SKIPLT":
                no_operand(lineargs[0])
            case "SKIPO":
                no_operand(lineargs[0])
            case "SKIPNO":
                no_operand(lineargs[0])
            case "SKIPP":
                no_operand(lineargs[0])
            case "SKIPNP":
                no_operand(lineargs[0])
            case "INPUT":
                no_operand(lineargs[0])
            case "NOP":
                no_operand(lineargs[0])
            case "SYS":
                no_operand(lineargs[0])
            case "HALT":
                no_operand(lineargs[0])
            case _:
                if len(lineargs)==1 and lineargs[0][len(lineargs)] == ':':
                    subprocess_names[lineargs[0][0:len(lineargs)-1]] = get_next_instr_addr()



def get_next_instr_addr():
    index=0
    while instruction_memory:
        index+=1
    return format(index, f'0{12}b')

    # if mode == 2: #will be used for code section
    # need a way to get the subprocess names at the start here
    #maybe mode 2 is parsing thru everything and finding subprocess names, the jumps and stuff just check if the name is in the file, append the name to the end of the binary, reiterate thu the file, replacing the names with an actual value
    #Need to do that, then go thru the output file, replace any instances of a subprocess name, cause u will change the jumps and stuff to just putting down the name ie,jmp location= 0000location, then needs to be changed after the location is determined when assigning everything pc location
    # so step 1, do .data, step 2, go thru all the code and find subprocess names that exist, store in array, step 3, go thru code section, if anything references a subprocess name, put it in the string if it exists, if it doesnt, yell at them, then go thru output.txt, replace any subprocess name with the actual instruction mem address and store new output in filename.bin and delete output


def memalloc(token, value):
    finalval = ""

    if value == "?":
        value = "0"
        finalval = to_signed_binary(0)  # Default value as signed 16-bit binary
    elif value.startswith("0x"):  # Hexadecimal value
        finalval = to_signed_binary(int(value, 16))
    elif isdigit(value) or (value[0] == "-" and isdigit(value[1:])):  # Decimal value
        finalval = to_signed_binary(int(value))
    else:
        raise Exception(f"Invalid value format: {value}")
    index = 0
    while data_memory[index]:
        index += 1
        if index == 2047:
            raise Exception("Out of data memory!")
    data_memory[index] = True
    index = index + 2048  # puts it in the data memory zone
    user_defined_tokens[token] = format(index, f'0{12}b')
    immediate_type("LOADI","R0",value)
    two_word_memory_type("STORE", "R0",index)

    return finalval  # Return the final signed binary value


def to_signed_binary(number):
    number = int(number)  # Ensure it's an integer
    if number < 0:
        number = (1 << 16) + number  # Convert to two's complement
    return format(number & 0xFFFF, f'0{16}b')  # Ensure 16-bit binary representation

def jump_type(instruction_code, op1):
    if isdigit(op1):
        temp = format(op1, f'0{12}b')
        memory_lines.append(k86_tokens[instruction_code] + temp)
    else:
        memory_lines.append(k86_tokens[instruction_code] + op1)
    setinstrmem1()


# 2 operand
def two_register(instruction_code,op1,op2): #handles add,sub,mult,div,and,or,xor,loadr,swap,cmp,test
    if ',' in op1:
        op1=op1[0:op1.find(',')]
    if op1 in registers and op2 in registers:
        memory_lines.append(k86_tokens[instruction_code]+registers[op1]+registers[op2])
    else:
        raise Exception(f"Invalid format at line {linenumber}.")
    setinstrmem1()

def shifters(instruction_code,op1,op2): #handles shl,shr,rol,ror
    if ',' in op1:
        op1=op1[0:op1.find(',')]
    if op1 in registers and isdigit(op2):
        memory_lines.append(k86_tokens[instruction_code]+registers[op1]+format(op2, f'0{4}b'))
    else:
        raise Exception(f"Invalid format at line {linenumber}.")
    setinstrmem1()


# section 3
def immediate_type(instruction_code, op1, op2): #handles addi, subi, multi, divi, loadi
    if ',' in op1:
        op1=op1[0:op1.find(',')]
    if op1 in registers:
        memory_lines.append(k86_tokens[instruction_code] + registers[op1] + "\n")
        memory_lines.append(to_signed_binary(op2) + "\n")
    else:
        raise Exception(f"Invalid format at line {linenumber}.")
    index = 0
    while instruction_memory[index]:
        index += 1
    instruction_memory[index] = True
    instruction_memory[index + 1] = True

def two_word_memory_type(instruction_code, op1, op2): #handles loadm, loada, store
    if ',' in op1:
        op1=op1[0:op1.find(',')]
    if op1 in registers:
        memory_lines.append(k86_tokens[instruction_code] + registers[op1] + "\n")
        if isdigit(op2):
            memory_lines.append("0000"+format(op2, f'0{12}b')+ "\n")
        else:
            memory_lines.append("0000"+ op2 + "\n")
        index = 0
        while instruction_memory[index]:
            index += 1
        instruction_memory[index] = True
        instruction_memory[index + 1] = True
    else:
        raise Exception(f"Invalid format at line {linenumber}.")


def one_operand(instruction_code, op1): #handles clear, not, neg, push, pop, ret, and print
    if op1 in registers:
        memory_lines.append(k86_tokens[instruction_code]+registers[op1])
        setinstrmem1()
    else:
        raise Exception(f"Invalid format at line {linenumber}.")


# section 4
def no_operand(instruction_code): #handles the skips, input, nop, sys, halt
    memory_lines.append(k86_tokens[instruction_code])
    setinstrmem1()



def setinstrmem1():
    index = 0
    while instruction_memory[index]:
        index += 1
    instruction_memory[index] = True
def isdigit(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def main():
    if len(sys.argv) != 2:  # Check if arguments were passed
        print(f"Usage: kasm [file name]")
    else:
        run(sys.argv[1])


if __name__ == "__main__":
    main()
