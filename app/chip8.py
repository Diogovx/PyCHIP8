from ctypes import c_uint16, c_uint8, c_int32
import random
from time import time


class CHIP8():
    def __init__(self):
        self.opcode = c_uint16()
        self.memory = (c_uint8 * 4096)()
        self.graphics = (c_uint8 * (64 * 32))()
        self.registers = (c_uint8 * 16)()
        self.index = c_uint16()
        self.program_counter = c_uint16()
        
        self.delay_timer = c_uint8()
        self.sound_timer = c_uint8()
        
        self.stack = (c_uint16 * 16)()
        self.sp = c_uint16()
        
        self.keys = (c_uint8 * 16)()
        
        self.chip8_fontset = (c_uint8 * 80)( 
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        )
    
    def init(self):
        random.seed(time())
        
        self.program_counter.value = 0x200
        self.opcode.value = 0
        self.index.value = 0
        self.sp.value = 0
        self.delay_timer.value = 0
        self.sound_timer.value = 0
        
        for i in range(len(self.graphics)):
            self.graphics[i] = 0
        for i in range(len(self.memory)):
            self.memory[i] = 0
        for i in range(len(self.stack)):
            self.stack[i] = 0
        for i in range(len(self.registers)):
            self.registers[i] = 0
        for i in range(len(self.keys)):
            self.keys[i] = 0
        
        for i, value in enumerate(self.chip8_fontset):
            self.memory[i] = value

    def increment_pc(self):
        self.program_counter.value += 2
    
    def cycle(self):
        self.opcode = self.memory[self.program_counter] << 8 | self.memory[self.program_counter + 1]
        
        # X000
        first = self.opcode >> 12
        
        match first:
            case 0x0:
                if self.opcode == 0x00E0:
                    for i in range(len(self.graphics)):
                        self.graphics[i] = 0
                elif self.opcode == 0X00EE:
                    self.sp -= 1
                    self.program_counter = self.stack[self.sp]
                self.increment_pc()
            case 0x1:
                self.program_counter = self.opcode & 0x0FFF
            case 0x2:
                self.stack[self.sp] = self.program_counter
                self.sp += 1
                self.program_counter = self.opcode & 0x0FFF
            case 0x3:
                x = (self.opcode & 0x0F00) >> 8

                if self.registers[x] == self.opcode & 0x00FF:
                    self.increment_pc()
                
                self.increment_pc()
            case 0x4:
                x = (self.opcode & 0x0F00) >> 8

                if self.registers[x] != self.opcode & 0x00FF:
                    self.increment_pc()
                
                self.increment_pc()
            case 0X5:
                x = (self.opcode & 0x0F00) >> 8
                y = (self.opcode & 0x00F0) >> 4
                

                if self.registers[x] == self.registers[y]:
                    self.increment_pc()
                
                self.increment_pc()
            case 0x6:
                x = (self.opcode & 0x0F00) >> 8
                #self.registers[x] = @truncate(u8, self.opcode & 0X00FF)
                self.registers[x] = c_uint8(self.opcode & 0X00FF)
                self.increment_pc()
            case 0x7:
                #@setRuntimeSafety(false)
                x = (self.opcode & 0x0F00) >> 8
                #self.registers[x] += @truncate(u8, self.opcode & 0X00FF)
                self.registers[x] += c_uint8(self.opcode & 0X00FF)
                self.increment_pc()
            case 0x8:
                x = (self.opcode & 0x0F00) >> 8
                y = (self.opcode & 0x00F0) >> 4
                m = self.opcode & 0x000F
                
                match m:
                    case 0:
                        self.registers[x] = self.registers[y]
                    case 1:
                        self.registers[x] |= self.registers[y]
                    case 2:
                        self.registers[x] &= self.registers[y]
                    case 3:
                        self.registers[x] ^= self.registers[y]
                    case 4:
                        #setRunTimeSafety(false)
                        sum: c_uint16 = self.registers[x]
                        sum += self.registers[y]
                        
                        self.registers[0xF] = 1 if sum > 255 else 0
                        #self.registers[x] = @truncate(u8, sum & 0x00FF)
                        self.registers[x] = c_uint8(sum & 0x00FF)
                    case 5:
                        #setRunTimeSafety(false)
                        self.registers[0xF] = 1 if self.registers[x] > self.registers[y] else 0
                        self.registers[x] -= self.registers[y]
                    case 6:
                        self.registers[0xF] = self.registers & 1
                        self.registers[x] >>= 1
                    case 7:
                        #setRunTimeSafety(false)
                        self.registers[0xF] = 1 if self.registers[y] > self.registers[x] else 0
                        self.registers[x] = self.registers[y] - self.registers[x]
                    case 14:
                        
                        self.registers[0xF] = 1 if self.registers[x] & 0x80 != 0 else 0
                        self.registers[x] <<= 1
                    
                self.increment_pc()
            case 0x9:
                x = (self.opcode & 0x0F00) >> 8
                y = (self.opcode & 0x00F0) >> 4
                

                if self.registers[x] != self.registers[y]:
                    self.increment_pc()
                
                self.increment_pc()
            case 0xA:
                self.index = self.opcode & 0x0FFF
                self.increment_pc()
            case 0xB:
                #self.program_counter = (self.opcode & 0x0FFF) + @intCast(u16, self.registers[0])
                self.program_counter = (self.opcode & 0x0FFF) + c_uint16(self.registers[0])
            case 0xC:
                x = (self.opcode & 0x0F00) >> 8
                kk = self.opcode & 0x00FF
                
                #self.registers[x] = @truncate(u8 ,@intCast(u32,cstd.rand()) & kk)
                self.registers[x] = c_uint8(c_int32(random.random()) & kk)
                self.increment_pc()
            