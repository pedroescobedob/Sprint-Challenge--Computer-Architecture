"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.sp = 7  # stack pointer index in register
        self.reg[self.sp] = 244  # stack pointer
        self.flag = 0
        self.branchtable = {}
        self.branchtable[130] = self.LDI
        self.branchtable[71] = self.prnt
        self.branchtable[162] = self.mul
        self.branchtable[160] = self.add
        self.branchtable[1] = self.HLT
        self.branchtable[69] = self.push
        self.branchtable[70] = self.pop
        self.branchtable[17] = self.ret
        self.branchtable[80] = self.call
        self.branchtable[167] = self.compare
        self.branchtable[84] = self.jump
        self.branchtable[86] = self.JNE
        self.branchtable[85] = self.JEQ
        self.branchtable[168] = self.and_
        self.branchtable[171] = self.xor
        self.branchtable[170] = self.or_

    def load(self, path):
        """Load a program into memory."""

        address = 0

        file = open(path, "r")
        for line in file:
            if line[:8][0] == "0" or line[:8][0] == "1":
                self.ram[address] = int(line[:8], 2)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        # compare two numbers, use flag to indicate result
    
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 1
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 2
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 4

        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]

        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]

        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def register(self, op):
        if op == "CALL":
            new_pc = self.reg[self.ram_read(self.pc+1)]
            self.push(self.pc + 2)
            self.pc = new_pc
        elif op == "JMP":
            # index of the register to jump to
            reg_index = self.ram_read(self.pc + 1)
            # the value at that index
            value = self.reg[reg_index]
            # set it to pc
            self.pc = value
        elif op == "JNE":
            # if flag is clear, jump to given address
            if ~self.flag & 1:
                self.jump()
            # otherwise, continue
            else:
                self.pc += 2
        elif op == "JEQ":
            # if equal flag is set to true, jump to given address
            if self.flag & 1:
                self.jump()
            # otherwise, continue
            else:
                self.pc += 2
        else:
            raise Exception("Unsupported Register operatonion")

    def HLT(self):
        print('System exiting...')
        sys.exit(1)

    def prnt(self):
        print(self.reg[self.ram_read(self.pc + 1)])
        self.pc += 2

    def LDI(self):
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.pc + 2)
        self.pc += 3

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def push(self, value=None):
        self.reg[self.sp] -= 1  # decrement sp
        if not value:
            value = self.reg[self.ram_read(self.pc + 1)]
        self.ram_write(value, self.reg[self.sp])
        self.pc += 2

    def pop(self):
        value = self.ram_read(self.reg[self.sp])
        reg_position = self.ram_read(self.pc + 1)
        self.reg[reg_position] = value
        self.reg[self.sp] += 1  # increment sp
        self.pc += 2

    def ret(self):
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

# ALU OPERATIONS

    def add(self):
        self.alu("ADD", self.ram_read(self.pc+1), self.ram_read(self.pc+2))
        self.pc += 3

    def mul(self):
        self.alu("MUL", self.ram_read(self.pc+1), self.ram_read(self.pc+2))
        self.pc += 3

    def compare(self):
        # utilize the ALU to handle the CMP operation
        self.alu('CMP', self.ram_read(self.pc+1), self.ram_read(self.pc+2))
        self.pc += 3

    def and_(self):
        self.alu("AND", self.ram_read(self.pc+1), self.ram_read(self.pc+2))
        self.pc += 3

    def xor(self):
        self.alu('XOR', self.ram_read(self.pc+1), self.ram_read(self.pc+2))
        self.pc += 3

    def or_(self):
        self.alu('OR', self.ram_read(self.pc+1), self.ram_read(self.pc+2))
        self.pc += 3

# REGISTER OPERATIONS 

    def call(self):
        self.register("CALL")

    def jump(self):
        self.register("JMP")

    def JNE(self):
        self.register("JNE")

    def JEQ(self):
        self.register("JEQ")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        running = True
        while running:
            IR = self.ram_read(self.pc)
            if IR == 1:
                self.branchtable[IR]()
                break
            elif IR in self.branchtable:
                self.branchtable[IR]()
            else:
                print(f'unknown instruction {IR} at address {self.pc}')
                sys.exit(1)