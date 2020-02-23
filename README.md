# zack
 A 16-bit computer in logisim!
 Works with Logisim 2.7.1 (the last version, the main branch of logisim is sadly no longer maintained)
 Scripts are written in Python 3

How to use Zack:
 - Open computer.circ with Logisim
 - Load a .mem program into the RAM (right-click on the RAM -> Load image -> select mem file -> Open)
 - Set the clock speed to the fastest possible (Simulate -> Tick Frequency -> 4.1KHz)
 - Press Ctrl-K to start/stop the clock
 - Left-click the keyboard in Poke mode to pass input to the simulated computer

Please refer to assemble.txt, instr.txt and bios.txt for further documentation.

Note: I have not yet found a way to overclock Logisim, but my computer can't simulate Zack at 4K Hz anyway and it works well enough :D

Credits:
 - Me
 - Inspiration from Meng Xuan Xia at https://cs.mcgill.ca/~mxia3/2018/03/15/XYT-CPU-a-8-bit-built-from-scratch-in-Logisim/
