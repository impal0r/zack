# zack
 A 16-bit computer in logisim! <br>
 This project was intended as an educational resource, and I undertook it to better understand the workings of a cpu. It has a simple architecture with a hardwired decoder (which is unfortunately slightly messy), and simple IO for demonstration comprised of a keyboard, text output, and a 16x16 LED matrix - all built-in logisim components. As an educational resource it is of course not guaranteed to be fully functional by any measure.

## Requirements
 - **Logisim** - I have used version 2.7.1 (the last version, as the main branch of logisim is sadly no longer maintained)
 - **Python 3** (if you want to program zack, as the assember is a python script) - I have been using python 3.7

## How to run Zack:
 - Open computer.circ with Logisim
 - Load a .mem program into the RAM (right-click on the RAM -> Load image -> select mem file -> Open)
 - Set the clock speed to the fastest possible (Simulate -> Tick Frequency -> 4.1KHz)
 - Press Ctrl-K to start/stop the clock
 - Left-click the keyboard in Poke mode to pass input to the simulated computer

Note: I have not found a way to overclock Logisim, but my computer can't handle Zack at 4K Hz anyway and it works well enough
 
 ## How to program Zack:
 - Copy the file userDefineLang.xml to Notepad++'s user defined language directory, which on Windows 10 is `%AppData%\Roaming\Notepad++\`
 - Note: if you have already defined custom languages yourself please don't overwrite your own file, but merge the XML structure
 - Create a .src file in the root of this project and open it in your favourite text editor, for example Notepad++
 - Right-click on the words 'Normal text file' in the bottom left of the Notepad++ window and select 'Zack Assembly' as the language to get syntax highlighting
 - Add `Z1.0 prog` as the first line in your file (or `Z1.0 bios` if you're writing another BIOS)
 - Add `#INCLUDE define.src` as the next line - define.src contains names for the BIOS functions (don't do this if you're writing another BIOS!), so this step is optional but recommended
 - Write assembly code using the syntax and instructions in assemble.txt and instr.txt; see other .src files for examples
 - Assemble to a .mem or .rom file using `> python assemble.py [filename] [options]`. This produces a memory image file in logisim's special format
 - If you are writing another BIOS, load the .rom file into Zack's ROM module (the top one). Otherwise leave the ROM alone and load your .mem file into the box below, the RAM. If you left-click a component in edit mode, the type (eg. ROM or RAM) will show on the left.
 - Caution: Zack does not use a standard calling convention, so the BIOS routines take parameters and return values in different registers. Each routine states its specifications separately in comments - see bios.src. I'm sorry it ended up this way.

Please refer to assemble.txt, instr.txt and bios.txt for further documentation.

## Credits:
 - Me
 - Inspiration from Meng Xuan Xia at https://cs.mcgill.ca/~mxia3/2018/03/15/XYT-CPU-a-8-bit-built-from-scratch-in-Logisim/
