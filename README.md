# PyCHIP8: A CHIP-8 Emulator Written in Python

## Idea

The goal of this project is to build a simple CHIP-8 emulator written in Python capable of running classic CHIP-8 ROMs.
The emulator implements the CHIP-8 virtual machine, including memory, registers, stack, graphics, timers, and input handling.

The project was created mainly for learning purposes, exploring how emulators work internally and how low-level systems can be reproduced in a high-level language like Python.

## Features

- CHIP-8 CPU implementation
- 16 general-purpose registers
- Stack and subroutine support
- SDL2 rendering
- Keyboard input mapping
- ROM loading
- Support for most CHIP-8 opcodes

## Technologies Used

- Python 3
- PySDL2 (graphics and input)

## How to Run

1. Install dependencies
    Install Python and the required libraries:

    ```bash
    pip install pysdl2 pysdl2-dll 
    ```

    If you are using **uv**, you can run:

    ```bash
    uv sync 
    ```

2. Run the emulator
    Execute the program passing a CHIP-8 ROM as argument:

    ```bash
    python -m app.main path/to/rom.ch8 
    ```

    Example:

    ```bash
    python -m app.main roms/IBM Logo.ch8 
    ```

    If the ROM path contains spaces, remember to use quotes:

    ```bash
    python -m app.main "roms/IBM Logo.ch8" 
    ```

## Screenshot

![CHIP8 screensjot](./assets/Screenshot_3.png)

## Next Steps

Possible improvements for the emulator:

[ ] Create a UI

Read it in pt-br:
[README](./README-pt-br.md)
