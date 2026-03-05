import sdl2.ext
from time import sleep

window: sdl2.SDL_Window = None
renderer: sdl2.SDL_Renderer = None
texture: sdl2.SDL_Texture = None


def init():
    if sdl2.ext.init():
        raise "SDL Initialization Failed!"
    
    window = sdl2.SDL_CreateWindow("CHIP8", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, 1024, 512, 0)
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
    sdl2.SDL_QUIT

def main():
    
    try:
        init()
    
    finally:
        deinit()
    
    keep_open = True
    while keep_open:
        #TODO Emulator Cycle
        e: sdl2.SDL_Event = None
        while sdl2.SDL_PollEvent(e) > 0:
            match type(e):
                case sdl2.SDL_QUIT:
                    keep_open = False
        
        _ = sdl2.SDL_RenderClear(renderer)
        
        #TODO Build Texture
        
        _ = sdl2.SDL_RenderCopy(renderer, texture, None, None)
        _ = sdl2.SDL_RenderPresent(renderer)
        
        sleep(16 * 1000 * 1000)


if __name__ == "__main__":
    main()
