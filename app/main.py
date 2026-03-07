import sdl2.ext
import sys
import ctypes
from time import sleep
from app.chip8 import CHIP8
from logging import getLogger


logger = getLogger(__name__)

window: sdl2.SDL_Window = None
renderer: sdl2.SDL_Renderer = None
texture: sdl2.SDL_Texture = None

cpu = None

keymap = [
    sdl2.SDL_SCANCODE_X,
    sdl2.SDL_SCANCODE_1,
    sdl2.SDL_SCANCODE_2,
    sdl2.SDL_SCANCODE_3,
    sdl2.SDL_SCANCODE_Q,
    sdl2.SDL_SCANCODE_W,
    sdl2.SDL_SCANCODE_E,
    sdl2.SDL_SCANCODE_A,
    sdl2.SDL_SCANCODE_S,
    sdl2.SDL_SCANCODE_D,
    sdl2.SDL_SCANCODE_Z,
    sdl2.SDL_SCANCODE_C,
    sdl2.SDL_SCANCODE_4,
    sdl2.SDL_SCANCODE_R,
    sdl2.SDL_SCANCODE_F,
    sdl2.SDL_SCANCODE_V,
]

def init():
    global window, renderer, texture
    if sdl2.ext.init():
        raise "SDL Initialization Failed!"
    
    window = sdl2.SDL_CreateWindow(b"CHIP8", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, 1024, 512, 0)
    if not window:
        raise "Window Creation Failed!"
    
    renderer = sdl2.SDL_CreateRenderer(window, -1, 0)
    if not renderer:
        raise "SDL Renderer Initialization Failed!"
    
    texture = sdl2.SDL_CreateTexture(renderer, sdl2.SDL_PIXELFORMAT_RGB888, sdl2.SDL_TEXTUREACCESS_STREAMING, 64, 32)
    if not texture:
        raise "SDL texture Creation Failed!"

def deinit():
    sdl2.SDL_DestroyWindow(window)
    sdl2.SDL_Quit()

def load_ROM(filename):
    with open(filename, "rb") as file:
        rom = file.read()
    for i, byte in enumerate(rom):
        cpu.memory[0x200 + i] = byte
    
def main():
    global cpu
    init()
    
    cpu = CHIP8()
    cpu.init()
    
    if len(sys.argv) < 2:
        logger.warning("NO ROM GIVEN!\n")
        return
    
    
    try:
        load_ROM(sys.argv[1])
    except:
        raise
    
    keep_open = True
    event = sdl2.SDL_Event()
    while keep_open:
        while sdl2.SDL_PollEvent(event) > 0:
            if event.type == sdl2.SDL_QUIT:
                keep_open = False
            if event.type == sdl2.SDL_KEYDOWN:
                i = 0
                while i < 16:
                    if event.key.keysym.scancode == keymap[i]:
                        cpu.keys[i] = 1
                    i += 1
            if event.type ==  sdl2.SDL_KEYUP:
                i = 0
                while i < 16:
                    if event.key.keysym.scancode == keymap[i]:
                        cpu.keys[i] = 0
                    i += 1
        for _ in range(10):
            cpu.cycle()
        
        sdl2.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255)
        sdl2.SDL_RenderClear(renderer)
        
        pixels = ctypes.c_void_p()
        pitch = ctypes.c_int()
        
        sdl2.SDL_LockTexture(texture, None, ctypes.byref(pixels), ctypes.byref(pitch))
        
        pixels_ptr = ctypes.cast(pixels, ctypes.POINTER(ctypes.c_uint32))
        
        for i, g in enumerate(cpu.graphics):
            pixels_ptr[i] = 0xFFFFFFFF if g else 0x00000000
            
        
        sdl2.SDL_UnlockTexture(texture)
        
        _ = sdl2.SDL_RenderCopy(renderer, texture, None, None)
        _ = sdl2.SDL_RenderPresent(renderer)
        
        sdl2.SDL_Delay(16)
    
    deinit()


if __name__ == "__main__":
    main()
