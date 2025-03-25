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
            # if reader.tell() == os.fstat(reader.fileno()).st_size:
            #    end = True
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
                # user_defined_tokens[lineargs[0]] = lineargs[1]
                memalloc(lineargs[0], lineargs[1])
    #if mode ==2:



    # if mode == 2: #will be used for code section
    # need a way to get the subprocess names at the start here
    #maybe mode 2 is parsing thru everything and finding subprocess names, the jumps and stuff just check if the name is in the file, append the name to the end of the binary, reiterate thu the file, replacing the names with an actual value
    #Need to do that, then go thru the output file, replace any instances of a subprocess name, cause u will change the jumps and stuff to just putting down the name ie,jmp location= 0000location, then needs to be changed after the location is determined when assigning everything pc location
    # so step 1, do .data, step 2, go thru all the code and find subprocess names that exist, store in array, step 3, go thru code section, if anything references a subprocess name, put it in the string if it exists, if it doesnt, yell at them, then go thru output.txt, replace any subprocess name with the actual instruction mem address and store new output in filename.bin and delete output


def memalloc(token, value):
    # print(token)
    finalval = ""

    if value == "?":
        value = "0"
        finalval = to_signed_binary(0)  # Default value as signed 16-bit binary
    elif value.startswith("0x"):  # Hexadecimal value
        finalval = to_signed_binary(int(value, 16))
    elif value.isdigit() or (value[0] == "-" and value[1:].isdigit()):  # Decimal value
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
    # print(finalval)  # write load and store here instead
    loadi("R0", value)
    store("R0", index)

    return finalval  # Return the final signed binary value


def to_signed_binary(number):
    number = int(number)  # Ensure it's an integer
    if number < 0:
        number = (1 << 16) + number  # Convert to two's complement
    return format(number & 0xFFFF, f'0{16}b')  # Ensure 16-bit binary representation


def jmp(op1):
    if op1 in user_defined_tokens:

        memory_lines.append(k86_tokens["JMP"] + op1)
    else:
        temp = format(op1, f'0{12}b')
        memory_lines.append(k86_tokens["JMP"] + temp)
    index = 0
    while instruction_memory[index]:
        index += 1
    instruction_memory[index] = True


# def jz(op1):

# def jnz(op1):

# def jc(op1):

# def jnc(op1):

# def jgt(op1):

# def jlt(op1):

# def jo(op1):

# def jno(op1):

# def jp(op1):

# def jnp(op1):


# 2 operand
# def add(op1, op2):

# def sub(op1, op2):

# def mult(op1, op2):

# def div(op1, op2):

# def and(op1, op2):

# def or(op1, op2):

# def xor(op1, op2):

# def shl(op1, op2):

# def shr(op1, op2):

# def rol(op1, op2):

# def ror(op1, op2):

# def loadr(op1, op2):

# def swap(op1, op2):

# def cmp(op1, op2):

# def test(op1, op2):

# section 3
# def addi(op1, op2):

# def subi(op1, op2):

# def multi(op1, op2):

# def divi(op1, op2):

def loadi(op1, op2):
    if op1 in registers:
        memory_lines.append(k86_tokens["LOADI"] + registers[op1] + "\n")
        memory_lines.append(to_signed_binary(op2) + "\n")
    else:
        raise Exception(f"Invalid format at line {linenumber}.")
    index = 0
    while instruction_memory[index]:
        index += 1
    instruction_memory[index] = True
    instruction_memory[index + 1] = True


def loadm(op1, op2):
    if op1 in registers:
        memory_lines.append(k86_tokens["LOADM"] + registers[op1] + "\n")
        if op2 in user_defined_tokens:
            memory_lines.append(user_defined_tokens[op2] + "\n")
        else:
            memory_lines.append(to_signed_binary(op2) + "\n")
        index = 0
        while instruction_memory[index]:
            index += 1
        instruction_memory[index] = True
        instruction_memory[index + 1] = True
    else:
        raise Exception(f"Invalid format at line {linenumber}.")

def loada(op1, op2):
    if op1 in registers:
        memory_lines.append(k86_tokens["LOADA"] + registers[op1] + "\n")
        if op2 in user_defined_tokens:
            memory_lines.append(user_defined_tokens[op2] + "\n")
        else:
            memory_lines.append(to_signed_binary(op2) + "\n")
        index = 0
        while instruction_memory[index]:
            index += 1
        instruction_memory[index] = True
        instruction_memory[index + 1] = True
    else:
        raise Exception(f"Invalid format at line {linenumber}.")

def store(op1, op2):
    if op1 in registers:
        memory_lines.append(k86_tokens["STORE"] + registers[op1] + "\n")
        if op2 in user_defined_tokens:
            memory_lines.append(user_defined_tokens[op2] + "\n")
        else:
            memory_lines.append(to_signed_binary(op2) + "\n")
        index = 0
        while instruction_memory[index]:
            index += 1
        instruction_memory[index] = True
        instruction_memory[index + 1] = True
    else:
        raise Exception(f"Invalid format at line {linenumber}.")


def clear(op1):
    if op1 in registers:
        memory_lines.append(k86_tokens["CLEAR"]+registers[op1])
        setinstrmem1()
    else:
        raise Exception(f"Invalid format at line {linenumber}.")

def notinst(op1):
    if op1 in registers:
        memory_lines.append(k86_tokens["NOT"]+registers[op1])
        setinstrmem1()
    else:
        raise Exception(f"Invalid format at line {linenumber}.")

def neg(op1):
    if op1 in registers:
        memory_lines.append(k86_tokens["NEG"]+registers[op1])
        setinstrmem1()
    else:
        raise Exception(f"Invalid format at line {linenumber}.")

def push(op1):
    if op1 in registers:
        memory_lines.append(k86_tokens["PUSH"]+registers[op1])
        setinstrmem1()
    else:
        raise Exception(f"Invalid format at line {linenumber}.")

def pop(op1):
    if op1 in registers:
        memory_lines.append(k86_tokens["POP"]+registers[op1])
        setinstrmem1()
    else:
        raise Exception(f"Invalid format at line {linenumber}.")

def ret(op1):
    if op1 in registers:
        memory_lines.append(k86_tokens["RET"]+registers[op1])
        setinstrmem1()
    else:
        raise Exception(f"Invalid format at line {linenumber}.")

def print(op1):
    if op1 in registers:
        memory_lines.append(k86_tokens["PRINT"]+registers[op1])
        setinstrmem1()
    else:
        raise Exception(f"Invalid format at line {linenumber}.")



# section 4
def skipz():
    memory_lines.append(k86_tokens["SKIPZ"])
    setinstrmem1()


def skipnz():
    memory_lines.append(k86_tokens["SKIPNZ"])
    setinstrmem1()


def skipc():
    memory_lines.append(k86_tokens["SKIP"])
    setinstrmem1()


def skipnc():
    memory_lines.append(k86_tokens["SKIPNC"])
    setinstrmem1()


def skipgt():
    memory_lines.append(k86_tokens["SKIPGT"])
    setinstrmem1()


def skiplt():
    memory_lines.append(k86_tokens["SKIPLT"])
    setinstrmem1()


def skipo():
    memory_lines.append(k86_tokens["SKIPO"])
    setinstrmem1()


def skipno():
    memory_lines.append(k86_tokens["SKIPNO"])
    setinstrmem1()


def skipp():
    memory_lines.append(k86_tokens["SKIPP"])
    setinstrmem1()


def skipnp():
    memory_lines.append(k86_tokens["SKIPNP"])
    setinstrmem1()


def inputms():
    memory_lines.append(k86_tokens["INPUT"])
    setinstrmem1()


def nop():
    memory_lines.append(k86_tokens["NOP"])
    setinstrmem1()


def syscall():
    memory_lines.append(k86_tokens["SYS"])
    setinstrmem1()


def halt():
    memory_lines.append(k86_tokens["HALT"])
    setinstrmem1()


def setinstrmem1():
    index = 0
    while instruction_memory[index]:
        index += 1
    instruction_memory[index] = True


def main():
    if len(sys.argv) != 2:  # Check if arguments were passed
        print(f"Usage: kasm [file name]")
    else:
        run(sys.argv[1])


if __name__ == "__main__":
    main()
