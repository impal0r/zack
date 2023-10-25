# zack

![Screenshot of Zack in logisim](/images/zack.PNG)

 Zack is an demonstration of a 16-bit RISC computer implemented in logisim. It includes a custom instruction set, with an assembler written in Python3 to convert code to bytecode in Logisim-format memory files. Deafult programs: noughts-and-crosses (aka. tic-tac-toe), a maze game, and some test programs.
 
 Zack uses a hardwired decoder (no microcode), a 2-bit internal phase counter, and hardwired registers, and is connected to some memory-mapped IO (keyboard, text console, and a 16x16 LED matrix - all built-in logisim components). It has a ROM module containing the "bios", and a RAM module into which programs must be manually loaded.
 
 The reason this project exists is an educational one: by building everything from the ground up, including designing my own instruction set, processor, IO layout, and assembly compiler, I learned a lot about the details and edge cases of this kind of system design, and hope to make something more complicated in the future.
 
### Possible future improvements:
 - Write a test suite for the instruction set
 - Remake the whole thing better:
 - https://github.com/hneemann/Digital can be clocked much faster than logisim, and is still currently maintained (as of 2022), so if I go ahead and make a second version I'll very likely switch from logisim to Digital
 - Either implement RISC-V in the next version, or write a C compiler, so that it can be easily used by more people

### Requirements
 - **Logisim** - I have used version 2.7.1 (the last version, as the main branch of logisim is no longer maintained)
 - **Python 3** - the assembler is a Python 3.7 script

## Running Zack:
 - Open computer.circ with Logisim
 - Load a `.mem` program into the RAM (right-click on the RAM -> Load image -> select `.mem` file -> Open)
 - The most interesting programs are `hello.mem`, `noughts-crosses.mem`, and `maze2.mem` (which is an optimised version of `maze.mem`)
 - Set the clock speed to the fastest possible (Simulate -> Tick Frequency -> 4.1KHz)
 - Press Ctrl-K to start/stop the clock
 - Left-click the keyboard in Poke mode to pass input to the simulated computer
 
## Programming Zack:
Documentation formatted as fixed-width text is found in the files `instr.txt`, `assemble.txt` and `bios.txt`. This was written by me a few years ago when I wasn't as good at writing documentation, so I apologise in advance both for the formatting and for the style. Also, all the example programs have source code, and  `bios.src` and `maze2.src` in particular contain a lot of explananatory comments, and `noughts-crosses.src` also uses a lot of the features.

Programs for Zack are written as `.src` files, using a custom assembly language described in `assemble.txt` and `instr.txt`. They are compiled using the `assemble.py` assembler, producing a file with the extension `.mem`, which can be read by Logisim so it can be loaded into Zack's memory module.

The custom assembly language is based on Intel syntax. The assembler supports single-line comments, labels (which you can jump to or call), defining constants in memory, basic arithmetic expressions (eg. `0xf100+'a'`), and some preprocessor macros including `#include` and `#define` statements. It does not support any arithmetic expressions beyond single addition, and does not support strings like modern assemblers.

Note that the routines defined in the "BIOS" and programs in this project don't use a single standard calling convention, so they take arguments and return values in different registers. This allows for multiple return values and some micro-optimisation, but makes the code a little more confusing. I would normally avoid doing this, but Logisim has a very slow clock speed and I was frustrated. Each function documents which registers it uses, and the calling convention, in comments.

### Notepad++ syntax highlighting
I have included a Notepad++ user defined language file, `userDefineLang.xml`, which allows Notepad++ to properly syntax highlight `.src` files.
1. Download the file `userDefineLang.xml`
2. Find where your installation of Notepad++ keeps userDefineLand.xml, which on Windows 10 is `%AppData%\Roaming\Notepad++\`
3. If you have not defined any custom languages yourself, you can replace your file with the one from this repository. Otherwise, *you need to merge the XML structure of the files so that you don't lose your own custom languages*.
4. Create or open a `.src` file in Notepad++, right-click on 'Normal text file' in the bottom left corner, and you should be able to select 'Zack Assembly'. This should enable the custom syntax highlighting for all `.src` files.

### .src file syntax
 - The first line should always be `Z1.0 prog`
 - Preprocessor macros start with a `#`. `#INCLUDE define.src` gives you names for BIOS functions so you don't have to put explicit memory addresses in your code.
 - Single-line comments start with a `;` and are ignored by the assembler.
 - Every program has an entry point, which is defined with the label `ENTRY:`
 - Every program should either HALT or keep running in a loop. If execution passes the end of your program the processor will start executing empty memory, which is an infinite NOP sled, and 0x0000 is the opcode for NOP.

### Assembling source code
Open a command or terminal window, and run `python assemble.py [filename].src` in the project directory. If there are no errors this will create (or overwrite by default) the file `[filename].mem`.

To test the program, follow the steps under Running Zack, and select the `.mem` file you just created.

### The "BIOS"
The idea of the "bios" is to contain setup code that is run each time Zack starts. Actually the only setup needed is to set the stack pointer, but the BIOS also prints a welcome message. The bios also contains some useful IO functions. Its source code is contained in `bios.src`, and the machine code in `bios.rom` is autosaved by Logisim (thanks to the persistency of the ROM element), so doesn't need to be loaded every time Zack is opened.

If anyone decides they want to write another version of the BIOS, they should be aware of the following:

 - The BIOS is limited to the size of the ROM, which is 256 words (memory is word-, not byte- addressable, and each instruction is a word long. A word is two bytes).
 - Execution always begins at address `0x0000`, or at the start of the memory. The first thing in `bios.src`, not including the mandatory first line and comments, is the startup code.
 - The assembler, when it assembles 'user-mode' programs, assumes the convention of the current bios in the way it detects and loads programs. This is that the address of the entry point of the program is found at 0x0200 (at the start or RAM), or if no program is loaded the value at 0x0200 will be all zeroes by default (a NULL).
 - The source code of the bios is different to that of a normal program. Its first line is `Z1.0 bios` to indicate that it should be assembled differently - this means that the assembler will not look for an `ENTRY:` label, and will produce an output that can be loaded into the ROM rather than the RAM of the model computer, in the form of a `.rom` file.
 - To test a new BIOS, you need to manually load the corresponding `.rom` file into the ROM of the model computer using Logisim's GUI. The new BIOS will then be saved in the model computer on closing Logisim, and you will need to manually replace the original BIOS if you want it back.

More documentation found in assemble.txt, instr.txt and bios.txt.

## Credits:
 - I derived some inspiration from Meng Xuan Xia at https://cs.mcgill.ca/~mxia3/2018/03/15/XYT-CPU-a-8-bit-built-from-scratch-in-Logisim/
