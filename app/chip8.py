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
        pc = self.program_counter.value
        self.opcode.value = self.memory[pc] << 8 | self.memory[pc + 1]
        
        # X000
        first = self.opcode.value >> 12
        
        match first:
            case 0x0:
                if self.opcode.value == 0x00E0:
                    for i in range(len(self.graphics)):
                        self.graphics[i] = 0
                elif self.opcode.value == 0X00EE:
                    self.sp.value -= 1
                    self.program_counter.value = self.stack[self.sp.value]
                self.increment_pc()
            case 0x1:
                self.program_counter.value = self.opcode.value & 0x0FFF
            case 0x2:
                self.stack[self.sp] = self.program_counter.value
                self.sp.value += 1
                self.program_counter.value = self.opcode.value & 0x0FFF
            case 0x3:
                x = (self.opcode.value & 0x0F00) >> 8

                if self.registers[x] == self.opcode.value & 0x00FF:
                    self.increment_pc()
                
                self.increment_pc()
            case 0x4:
                x = (self.opcode.value & 0x0F00) >> 8

                if self.registers[x] != self.opcode.value & 0x00FF:
                    self.increment_pc()
                
                self.increment_pc()
            case 0X5:
                x = (self.opcode.value & 0x0F00) >> 8
                y = (self.opcode.value & 0x00F0) >> 4
                

                if self.registers[x] == self.registers[y]:
                    self.increment_pc()
                
                self.increment_pc()
            case 0x6:
                x = (self.opcode.value & 0x0F00) >> 8
                self.registers[x] = self.opcode.value & 0X00FF
                self.increment_pc()
            case 0x7:
                x = (self.opcode.value & 0x0F00) >> 8
                self.registers[x] = (self.registers[x] + (self.opcode.value & 0X00FF)) & 0xFF
                self.increment_pc()
            case 0x8:
                x = (self.opcode.value & 0x0F00) >> 8
                y = (self.opcode.value & 0x00F0) >> 4
                m = self.opcode.value & 0x000F
                
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
                        sum_val = self.registers[x] + self.registers[y]
                        
                        self.registers[0xF] = 1 if sum_val > 255 else 0
                        #self.registers[x] = @truncate(u8, sum & 0x00FF)
                        self.registers[x] = sum_val & 0x00FF
                    case 5:
                        #setRunTimeSafety(false)
                        self.registers[0xF] = 1 if self.registers[x] > self.registers[y] else 0
                        self.registers[x] -= self.registers[y]
                    case 6:
                        self.registers[0xF] = self.registers[x] & 1
                        self.registers[x] >>= 1
                    case 7:
                        #setRunTimeSafety(false)
                        self.registers[0xF] = 1 if self.registers[y] > self.registers[x] else 0
                        self.registers[x] = self.registers[y] - self.registers[x]
                    case 14:
                        self.registers[0xF] = 1 if self.registers[x] & 0x80 != 0 else 0
                        self.registers[x] = (self.registers[x] << 1) & 0xFF
                    
                self.increment_pc()
            case 0x9:
                x = (self.opcode.value & 0x0F00) >> 8
                y = (self.opcode.value & 0x00F0) >> 4
                

                if self.registers[x] != self.registers[y]:
                    self.increment_pc()
                
                self.increment_pc()
            case 0xA:
                self.index.value = self.opcode.value & 0x0FFF
                self.increment_pc()
            case 0xB:
                self.program_counter = (self.opcode.value & 0x0FFF) + self.registers[0]
            case 0xC:
                x = (self.opcode.value & 0x0F00) >> 8
                kk = self.opcode.value & 0x00FF
                
                random_byte = random.randint(0, 255)
                self.registers[x] = random_byte & kk
                self.increment_pc()
            case 0xD:
                self.registers[0xF] = 0
                xx = (self.opcode.value & 0x0F00) >> 8
                yy = (self.opcode.value & 0x00F0) >> 4
                nn = self.opcode.value & 0x000F
                
                regX = self.registers[xx]
                regY = self.registers[yy]
                
                y = 0
                while y < nn:
                    pixel = self.memory[self.index.value + y]
                    x = 0
                    while x < 8:
                        msb = 0x80
                        
                        if pixel & (msb >> x) != 0 :
                            tX = (regX + x) % 64
                            tY = (regY + y) % 32
                            idx = tX + tY * 64
                            
                            self.graphics[idx] ^= 1
                            
                            if  self.graphics[idx] == 0:
                                self.registers[0xF] = 1
                            
                        x = x + 1
                    y = y + 1
                self.increment_pc()
            case 0xE:
                x = (self.opcode.value & 0x0F00) >> 8
                kk = self.opcode.value & 0x00FF
                
                if kk == 0x9E:
                    if self.keys[self.registers[x]] == 1:
                        self.increment_pc()
                elif kk == 0xA1:
                    if self.keys[self.registers[x]] != 1:
                        self.increment_pc()
                
                self.increment_pc()
            case 0xF:
                x = (self.opcode.value & 0x0F00) >> 8
                kk = self.opcode.value & 0x00FF
                
                if kk == 0x07:
                    self.registers[x] == self.delay_timer.value
                elif kk == 0x0A:
                    key_pressed = False
                    
                    for i, v in enumerate(self.keys):
                        if v != 0:
                            self.registers[x] = i
                            key_pressed = True
                            break
                    if not key_pressed:
                        return
                elif kk == 0x15:
                    self.delay_timer.value = self.registers[x]
                elif kk == 0x18:
                    self.sound_timer.value = self.registers[x]
                elif kk == 0x1E:
                    self.index.value = self.index.value + self.registers[x]
                elif kk == 0x29:
                    if self.registers[x] < 16:
                        self.index.value = self.registers[x] * 0x5
                elif kk == 0x33:
                    self.memory[self.index.value] = self.registers[x] // 100
                    self.memory[self.index.value + 1] = (self.registers[x] // 10) % 10
                    self.memory[self.index.value + 2] = self.registers[x] % 10
                elif kk == 0x55:
                    i = 0
                    while i <= x:
                        self.memory[self.index.value + i] = self.registers[i]
                        i += 1
                elif kk == 0x65:
                    i = 0
                    while i <= x:
                        self.registers[i] = self.memory[self.index.value + i]
                        i += 1
                    
                
                self.increment_pc()