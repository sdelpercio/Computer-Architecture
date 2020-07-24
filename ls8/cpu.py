"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = True
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0
        self.ir = 0
        self.fl = 0b00000000
        
        self.branchtable = {}
        self.branchtable[0b00000001] = self.HLT 
        self.branchtable[0b10000010] = self.LDI              
        self.branchtable[0b01000111] = self.PRN
        self.branchtable[0b10100000] = self.ADD
        self.branchtable[0b10100010] = self.MUL 
        self.branchtable[0b01000101] = self.PUSH 
        self.branchtable[0b01000110] = self.POP
        self.branchtable[0b01010000] = self.CALL
        self.branchtable[0b00010001] = self.RET
        self.branchtable[0b10100111] = self.CMP
        self.branchtable[0b01010100] = self.JMP
        self.branchtable[0b01010101] = self.JEQ
        self.branchtable[0b01010110] = self.JNE
        
    ## Instructions ##
    def HLT(self): ## 'Halt', stop running
        self.running = False
    def LDI(self): ## 'Loading Data', store value in register 
        reg_index = self.ram[self.pc + 1]
        load = self.ram[self.pc + 2]
        self.reg[reg_index] = load
        self.pc += 1 + (self.ir >> 6)
    def PRN(self): ## 'Print', prints value in a register
        reg_index = self.ram[self.pc + 1]
        print(self.reg[reg_index])
        self.pc += 1 + (self.ir >> 6)
    def ADD(self): ## 'Add', adds two values in registers
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('ADD', operand_a, operand_b)
        self.pc += 1 + (self.ir >> 6)
    def MUL(self): ## 'Multiply', multiplies two values in registers
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('MUL', operand_a, operand_b)
        self.pc += 1 + (self.ir >> 6)
    def PUSH(self): ## 'Push', copies value from register and pushes onto stack
        self.reg[7] -= 1
        sp = self.reg[7]
        reg_index = self.ram[self.pc + 1]
        value = self.reg[reg_index]
        self.ram[sp] = value
        self.pc += 1 + (self.ir >> 6)
    def POP(self): ## 'Pop', copies the value at top of stack into a given register
        sp = self.reg[7]
        value = self.ram[sp]
        reg_index = self.ram[self.pc + 1]
        self.reg[reg_index] = value
        self.reg[7] += 1
        self.pc += 1 + (self.ir >> 6)
    def CALL(self): ## 'Call', moves the pc to an address in ram to call a function
        reg_index = self.ram[self.pc + 1]
        address = self.reg[reg_index]
        return_address = self.pc + 2
        # push return address onto stack
        self.reg[7] -= 1
        sp = self.reg[7]
        self.ram[sp] = return_address
        # set pc to called func
        self.pc = address
    def RET(self): ## 'Return', moves program counter back after finishing subroutine
        # pop return address
        sp = self.reg[7]
        return_address = self.ram[sp]
        self.reg[7] += 1
        # set pc
        self.pc = return_address
    def CMP(self): ## 'Compare', Compares values in two registers
        reg_A = self.ram[self.pc + 1]
        reg_B = self.ram[self.pc + 2]
        self.alu('CMP', reg_A, reg_B)
        self.pc += 1 + (self.ir >> 6)
    def JMP(self): ## 'Jump', set the pc to an address stored in a register
        reg_index = self.ram[self.pc + 1]
        next_index = self.reg[reg_index]
        self.pc = next_index
    def JEQ(self): ## 'Jump if equal', If flag is set to equal, jump to stored address
        if self.fl == 1:
            reg_index = self.ram[self.pc + 1]
            next_index = self.reg[reg_index]
            self.pc = next_index
        else:
            self.pc += 1 + (self.ir >> 6)
    def JNE(self): ## 'Jump if not equal'
        if (self.fl & 0b00000001) == 0:
            reg_index = self.ram[self.pc + 1]
            next_index = self.reg[reg_index]
            self.pc = next_index
        else:
            self.pc += 1 + (self.ir >> 6)
            
            
        
    def ram_read(self, index):
        """Returns the value stored at an index in RAM"""
        return self.ram[index]
    
    def ram_write(self, value, index):
        """Writes a value to an index in RAM"""
        self.ram[index] = value

    def load(self):
        """Load a program into memory."""

        address = 0
        program = []
        
        # check for program to run and filename
        if len(sys.argv) < 2:
            print("Please pass in a second filename: python3 ./ls8/ls8.py second_filename.py")
            sys.exit()
            
        filename = sys.argv[1]
        # read file, get instructions, append to program
        try:
            with open(f'ls8/examples/{filename}') as f:
                for line in f:
                    split_line = line.split('#')[0]
                    command = split_line.strip()
                    if command == '':
                        continue
                    program.append(int(command, 2))
        except FileNotFoundError:
            print(f'{sys.argv[0]}: {sys.argv[1]} file was not found')
            sys.exit()

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            else:
                self.fl = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # enter a loop
        while self.running:
            # read memory address at program counter (pc)
            # store that into instruction register (ir)
            self.ir = self.ram_read(self.pc)
        
            # check if the ir matches any cases
            try:
                self.branchtable[self.ir]()
            except KeyError:
                print('LS8 does not support this operation')
                print(f'ir = {self.ir}')
                sys.exit()
        
