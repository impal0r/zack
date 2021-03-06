# zack
 An experimental 16-bit computer implemented in logisim. <br>
 The aim of this project was to build a computer processor from the ground up using logical components. Zack has a relatively simple RISC architecture with a hardwired decoder, and is connected to memory-mapped IO for demonstration: a keyboard, console output, and a 16x16 LED matrix, which are all built-in logisim components.

### Requirements
 - **Logisim** - I have used version 2.7.1 (the last version, as the main branch of logisim is sadly no longer maintained)
 - **Python 3** for programming Zack, as the assembler is written as a Python 3.7 script

## Running Zack:
 - Open computer.circ with Logisim
 - Load a `.mem` program into the RAM (right-click on the RAM -> Load image -> select `.mem` file -> Open)
 - Set the clock speed to the fastest possible (Simulate -> Tick Frequency -> 4.1KHz)
 - Press Ctrl-K to start/stop the clock
 - Left-click the keyboard in Poke mode to pass input to the simulated computer
 
## Programming Zack:
Programs for Zack are written as `.src` files, using a custom assembly language defined in `assemble.txt` and `instr.txt`. They are compiled using the `assemble.py` assembler, producing a hexadecimal file (or memory image) with the extension `.mem`. Such an image can be loaded and run in Zack by following the steps under "Running Zack".

The assembly language definition is based on Intel syntax. The assembler supports single-line comments, labels (which you can jump to or call), defining constants in memory, basic arithmetic expressions (eg. `0xf100+'a'`), and some preprocessor macros including `#include` and `#define` statements. It does not support any arithmetic expressions beyond single addition, and does not support strings like some fully-fledged modern assemblers.

For examples, please have a look the `.src` files in the project, especially `maze2.src` and `noughts-crosses.src`.

Note that the routines defined in the "BIOS" and programs in this project don't use a standard calling convention, so they take arguments and return values in different registers. This allows for multiple return values and some micro-optimisation, but makes the code a little more confusing. Each function documents which registers it takes each argument and returns each value in where it is defined, using a comment.

### Notepad++ syntax highlighting
If you use Notepad++ to write code for this model computer, you can follow the following steps to get syntax highlighting in your .src files:
1. Download the file userDefineLang.xml
2. Find where your installation of Notepad++ keeps userDefineLand.xml, which on Windows 10 is `%AppData%\Roaming\Notepad++\`
3. If you have not defined any custom languages yourself, you can replace your file with the one you downloaded. Otherwise, you need to merge the XML structure of the files so that you don't lose your custom languages.
4. Now when you create a `.src` file in Notepad++, right-click on 'Normal text file' in the bottom left, and you should be able to select 'Zack Assembly'. This will get you syntax highlighting when writing .src files.

### .src file syntax
 - The first line should always be `Z1.0 prog`
 - Preprocessor macros start with a `#`. `#INCLUDE define.src` gives you names for BIOS functions so you don't have to put explicit memory addresses in your code.
 - Single-line comments start with a `;` and are ignored by the assembler.
 - Every program has an entry point, which is defined with the label `ENTRY:`
 - Every program should either HALT or keep running in a loop. If execution passes the end of your program the processor will start executing empty memory, which is an infinite NOP sled, and 0x0000 is the opcode for NOP.

### Assembling source code
Open a command window, and run `python assemble.py filename.src`. This should produce a `.mem` file of the same name as the source.

To test the program, follow the steps under Running Zack, and select the `.mem` file you just created.

### The "BIOS"
The "BIOS" contains setup code that is run each time Zack starts (it sets the stack pointer and prints a welcome message), and defines some useful functions to interface with the IO of the model computer. Its source code is contained in `bios.src`, and the machine code in `bios.rom` is autosaved by Logisim (thanks to the persistency of the ROM element), so doesn't need to be loaded every time Zack is opened.

If anyone decides they want to write another version of the BIOS, they should be aware of the following:

 - The BIOS is limited to the size of the ROM, which is 256 words (memory is word-, not byte- addressable, and each instruction is a word long).
 - Execution always begins at address `0x0000`, or at the start of the memory. The first thing in `bios.src`, not including the mandatory first line and comments, is the startup code.
 - The assembler, when it assembles 'user-mode' programs, assumes the convention of the current bios in the way it detects and loads programs.
 - The source code of the bios is different to that of a normal program. Its first line is `Z1.0 bios` to indicate that it should be assembled differently - this means that the assembler will not look for an `ENTRY:` label, and will produce an output that can be loaded into the ROM rather than the RAM of the model computer, in the form of a `.rom` file.
 - To test a new BIOS, you need to manually load the corresponding `.rom` file into the ROM of the model computer using Logisim's GUI. The new BIOS will then be saved in the model computer on closing Logisim, and you will need to manually replace the original BIOS if you want it back.

Please refer to assemble.txt, instr.txt and bios.txt for further documentation.

## Credits:
 - I derived some inspiration from Meng Xuan Xia at https://cs.mcgill.ca/~mxia3/2018/03/15/XYT-CPU-a-8-bit-built-from-scratch-in-Logisim/
