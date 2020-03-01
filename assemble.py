#Custom assembler for Zack-v1
import re, sys

#---------------------------------- CONSTANTS ----------------------------------

HELP = '''
Assembles an assembly file to memory image for Zack-v1, as defined in
assemble.txt
Usage: assemble [options] file1 [file2 ...]\n
Assembly options:
   -raw         Assembles all files completely raw
   -bios        Assembles all files completely raw (to put in ROM)
   -prog        Assembles all files as a program (to put in RAM)
By default, will use file headers to determine behaviour for each file.\n
Other options:
   -rle         Compresses the output file(s) with run-length encoding
   -printlabels Displays all the labels in the file and their addresses
                at the end. Useful for debugging, or to get BIOS or OS
                function addresses
   -help        Displays this message
'''

REGS = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'SP':7}
#         name   : code  #operands  dest  src1  src2  imm
INSTRS = {'NOP'  : (0,   0,         0,    0,    0,    0),
          'HLT'  : (1,   0,         0,    0,    0,    0),
          'LDI'  : (8,   2,         1,    0,    0,    2),
          'LDAI' : (9,   2,         1,    0,    0,    2),
          'STI'  : (10,  2,         0,    0,    1,    2),
          'LDA'  : (17,  2,         1,    0,    2,    0),
          'STO'  : (18,  2,         0,    2,    1,    0),
          'PUSH' : (19,  1,         0,    0,    1,    0),
          'MOV'  : (20,  2,         1,    2,    0,    0),
          'ADD'  : (24,  3,         1,    2,    3,    0),
          'SUB'  : (25,  3,         1,    2,    3,    0),
          'AND'  : (26,  3,         1,    2,    3,    0),
          'OR'   : (27,  3,         1,    2,    3,    0),
          'NAND' : (28,  3,         1,    2,    3,    0),
          'NOR'  : (29,  3,         1,    2,    3,    0),
          'XOR'  : (30,  3,         1,    2,    3,    0),
          'CMP'  : (31,  2,         0,    1,    2,    0),
          'INC'  : (32,  1,         1,    1,    0,    0),
          'DEC'  : (33,  1,         1,    1,    0,    0),
          'NEG'  : (34,  1,         1,    0,    1,    0),
          'INV'  : (35,  1,         1,    0,    1,    0),
          'REM'  : (40,  2,         0,    1,    2,    0),
          'MULC' : (41,  3,         1,    2,    3,    0),
          'DIVD' : (42,  3,         1,    2,    3,    0),
          'DIVC' : (43,  3,         1,    2,    3,    0),
          'MUL'  : (44,  3,         1,    2,    3,    0),
          'DIV'  : (45,  3,         1,    2,    3,    0),
          'SHL'  : (48,  3,         1,    2,    3,    0),
          'SHR'  : (49,  3,         1,    2,    3,    0),
          'SAR'  : (50,  3,         1,    2,    3,    0),
          'ROL'  : (51,  3,         1,    2,    3,    0),
          'ROR'  : (52,  3,         1,    2,    3,    0),
          'JMPI' : (96,  1,         0,    0,    0,    1),
          'JZI'  : (97,  1,         0,    0,    0,    1),
          'JNZI' : (98,  1,         0,    0,    0,    1),
          'JGI'  : (99,  1,         0,    0,    0,    1),
          'JLI'  : (100, 1,         0,    0,    0,    1),
          'JAI'  : (101, 1,         0,    0,    0,    1),
          'JBI'  : (102, 1,         0,    0,    0,    1),
          'JMP'  : (104, 1,         0,    0,    1,    0),
          'JZ'   : (105, 1,         0,    0,    1,    0),
          'JNZ'  : (106, 1,         0,    0,    1,    0),
          'JG'   : (107, 1,         0,    0,    1,    0),
          'JL'   : (108, 1,         0,    0,    1,    0),
          'JA'   : (109, 1,         0,    0,    1,    0),
          'JB'   : (110, 1,         0,    0,    1,    0),
          'CALL' : (120, 1,         0,    0,    0,    1),
          'RET'  : (121, 0,         0,    0,    0,    0),
          'CALLR': (122, 1,         0,    0,    1,    0),
          'POP'  : (123, 1,         1,    0,    0,    0),
          }

#----------------------------------- FUNCTIONS ---------------------------------

def get_extension(filename):
    i = filename.rfind('.')
    if i == len(filename)-1: i = 0
    return filename[i+1:]

def strip_extension(filename):
    i = filename.rfind('.')
    if i < 0: i = len(filename)
    return filename[:i]

def printerror(error, line):
    print("Line "+str(line)+": "+error, file=sys.stderr)

def inline_to_int(number, recurse=None):
    '''Converts an inline constant to a 16-bit integer'''
    if recurse is None:
        recurse = inline_to_int
    
    #is it a character?
    if len(number)==3 and number[0]==number[2]=="'":
        if number[1]=='\x00': return ord(' ')
        num = ord(number[1])
        if num > 256: raise ValueError #zack doesn't support unicode
        return num
    elif len(number)==4 and number[0]==number[3]=="'" and number[1]=='\\':
        return ord(eval(number))

    #base + offset
    if '+' in number:
        if number.count('+') > 1:
            raise ValueError
        number = number.split('+')
        number1 = recurse(number[0])
        number2 = recurse(number[1])
        return (number1 + number2) & 0xffff #discard bits beyond 16

    #number immediates: (sign)/(base)/number
    match = re.match('(-?)(0d|0x|0b|0o)?([0-9A-Fa-f]+)$', number)
    if match:
        base = 10
        if match.group(2): #if we have specified the base
            base = {'0b':2, '0o':8, '0d':10, '0x':16}[match.group(2)]
        #convert to int - this could raise ValueError
        number = int(match.group(3), base)
        number &= 0xffff #discard bits beyond 16
        if match.group(1): #negative: convert to 2's complement
            number = 65536 - number
        return number
    else:
        raise ValueError

def parse_immediate(imm, i, words, labels, unresolved_labels):
    '''
    Parses an immediate (which could refer to a label) and returns the 16-bit word,
    updating labels accordingly, or raises ValueError if immediate is invalid.
    -> word:int
    '''
    #is it inline?
    try:
        return inline_to_int(imm, recurse=(
            lambda num,i=i,w=words,l=labels,u=unresolved_labels: parse_immediate(num,i,w,l,u)) )
    except ValueError:
        #is it a label?
        if imm in labels:
            return labels[imm]
        elif imm.isalnum() and imm[0].isalpha():
            unresolved_labels.append((len(words),imm,i))#index and name in unresolved
            return 0 #add placeholder 0 to memory
        else: #invalid label
            raise ValueError

def get_mem(filename):
    '''-> ('mem...', length_in_memory_words)
    Assuming logisim raw format'''
    with open(filename) as file:
        file.readline() #remove first line (the 'magic bytes')
        lines = [] #final list to return
        word_count = 0 #count up memory words as well
        for line in file:
            #ignore comments and strip whitespace
            #note: this also removes trailing \n
            line = line[:line.find('#')].strip()
            if line: #is not ''
                lines.append(line) #line is sth useful so add to list
                #count up memory words line represents
                for word in line.split():
                    word = word.split('*')
                    #if there is a *, add multiplier, which comes first, to ctr
                    if len(word) == 2:
                        word_count += int(word[0])
                    #otherwise just add one
                    else:
                        word_count += 1

    return ('\n'.join(lines), word_count)

def smart_replace(name, value, string):
    '''-> (new_string, number_of_subs_made)'''
    return re.subn(r'(\s|^|\+)'+name+r'([:,\s]|$|\+)',
                   r'\g<1>'+value+r'\2',
                   string)

def preprocess(raw_lines, defined_names = {}):
    '''Removes comments, and evaluates preprocessor statements and macros
    -> (lines[], names{}, error) for assembler'''
    names = defined_names
    lines = [] #('LINE etc', original_line_number)
    error = 0

    macro = ctr_name = None
    macro_value = macro_start = 0
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        i += 1
        ii = i+1 #if we use i line nos in errors will be one off (we stripped the header on line 1)
        #ignore comments and strip whitespace
        line = line[:line.find(';')].strip() #note: this removes the trailing \n
        #ignore empty lines
        if not line:
            continue

        #evaluate #DEFINE and #UNDEF before we replace names
        if line.upper().startswith('#DEFINE '):
            line = line.split()
            try:
                name = line[1]
                if name.isalnum() and name[0].isalpha():
                    value = ' '.join(line[2:])
                    value = value.replace('\\n','\n').replace('\\\\','\\')
                    names[name] = value
                else:
                    printerror('Preprocessor Error: Invalid name '+name,ii)
                    error = 1
            except IndexError:
                printerror('Preprocessor Error: Expected name and value'
                           'after #DEFINE statement',ii)
                error = 1
            continue
        if line.upper().startswith('#UNDEF '):
            line = line.split()
            try:
                name = line[1]
            except IndexError:
                printerror('Preprocessor Error: Expected name after #UNDEF', ii)
            try:
                del names[name]
            except KeyError:
                pass
            continue

        #evaluate names from the #DEFINE directive
        #(replace recursively until there are none left)
        names_left = True
        while names_left:
            names_left = False
            for name in names:
                line, numsubs = smart_replace(name, names[name], line)
                if numsubs > 0: names_left = True
        #make sure separate lines are processed separately
        if '\n' in line:
            lines2 = [l+'\n' for l in line.split('\n')]
            #note i has already been incremented
            raw_lines = raw_lines[:i-1]+lines2+raw_lines[i:]
            line = lines2[0][:-1]

        split = line.split()
        #find preprecessor directives(starting with #)
        if line[0]=='#':

            if split[0].upper()=='#INCLUDE': #include a src /*or mem*/ file
                if len(split) > 1:
                    filename = split[1]
                    ext = get_extension(filename)
                    try:
                        if ext == 'src':
                            with open(filename,'r') as include_file:
                                lines2 = include_file.readlines()
                            #check file header
                            first_line = lines2.pop(0).strip().split()
                            if (len(first_line)!=2 or first_line[0][0]!='Z' or
                                first_line[1] not in ('bios', 'raw', 'prog')):
                                printerror('Error: Invalid file header',ii)
                                error = 1
                            elif first_line[0][1:] not in ('1','1.0'):
                                print('Error: Zack version'+first_line[0][1:]+
                                      'not supported',ii)
                                error = 1
                            #properly process the file
                            lines2, names2, error = preprocess(lines2, defined_names=names) 
                            #add processed lines and names from file
                            lines.extend([(line2[0], i) for line2 in lines2])
                            names.update(names2)
                        elif ext == 'mem':
                            #raise FileNotFoundError if file not exist
                            f = open(filename,'r'); f.close()
                            lines.append(('INCLUDE '+filename,ii))
                        else:
                            printerror('Preprocessor Error: Could not include '
                                       +filename+': file type not supported',ii)
                            error = 1
                    except FileNotFoundError:
                        printerror('Preprocessor Error: File '+filename
                                   +' does not exist',ii)
                        error = 1
                else:
                    printerror('Preprocessor Error: Expected filename'
                               'after #INCLUDE statement',ii)
                    error = 1

            elif split[0].upper()=='#REPLN':
                #duplicates a single line n times (shorter)
                if len(split) < 3:
                    printerror('Preprocessor Error: Expected number of repeats',ii)
                    error = 1
                else:
                    try:
                        macro_value = int(split[1])
                        if macro_value > 0:
                            line2 = ' '.join(split[2:])+'\n'
                            lines2, names2, error = preprocess((line2,))
                            names.update(names2)
                            lines2 = [(line2[0],i) for line2 in lines2]
                            for j in range(macro_value):
                                lines.extend(lines2)
                        else:
                            printerror('Preprocessor Error: repeats must be at least 1',ii)
                            error = 1
                    except ValueError:
                        printerror('Preprocessor Error: Expected number of repeats',ii)
                        error = 1
            elif split[0].upper()=='#REPEAT':
                #duplicates chunk n times, optionally with a counter
                if macro is None:
                    try:
                        macro_value = int(split[1])
                    except (IndexError, ValueError):
                        printerror('Preprocessor Error: Expected number of repeats',ii)
                        error = 1
                    if macro_value < 1: #check number of repeats if positive
                        printerror('Preprocessor Error: repeats must be at least 1',ii)
                        error = 1
                    if len(split) > 3: #check for too many arguments
                        printerror('Preprocessor Error: too many arguments after #REPEAT',ii)
                        error = 1
                    if len(split) == 3: #we have a counter
                        if split[2].isalnum() and split[2][0].isalpha():
                            ctr_name = split[2]
                            names[ctr_name] = 'ctr'
                        else: #check counter name is valid
                            printerror('Preprocessor Error: Invalid '
                                       'counter name', ii)
                            error = 1
                    if not error: #if it's still good do the macro
                        macro = 'repeat'
                        macro_start = len(lines) #-> start of lines to rep
                else:
                    printerror('Preprocessor Error: Cannot nest macros',ii)
                    error = 1
            elif split[0].upper()=='#ENDM':
                if macro is None:
                    printerror('Preprocessor Error: ENDM statement should be'
                               ' after a macro start',ii)
                    error = 1
                else:
                    if ctr_name is None:
                        lines.extend(lines[macro_start:]*(macro_value-1))
                    else:
                        #2d list: we append in columns, then read in rows
                        #         for increased speed (hopefully)
                        extra_lines = [[] for j in range(macro_value-1)]
                        for j in range(macro_start, len(lines)):
                            for k in range(macro_value-1):
                                #note smart_replace calls re.subn,
                                #which returns (new_str, num_subs_made)
                                extra_lines[k].append((
                                 smart_replace('ctr', str(k+1), lines[j][0])[0],
                                 lines[j][1]))
                            lines[j] = (smart_replace('ctr', '0', lines[j][0])[0],
                                        lines[j][1])
                        for ll in extra_lines:
                            lines.extend(ll)
                        del extra_lines
                    del names[ctr_name]
                    macro = ctr_name = None

            else:
                printerror('Preprocessor Error: Invalid statement',ii)
                error = 1
        else: #don't add preprocessor directives to list for assembler
            #finally add the processed line to the final list
            lines.append((line, ii))

    return (lines, names, error)


def assemble(lines, bios): #bios = whether we are assembling a bios or program
    '''Assembles instructions to memory words
    -> (words:list[int], error:bool)'''
    if bios:
        words = []
        adr_ctr = 0
    else:
        words = [0] #placeholder for entry pointer
        adr_ctr = 513 #start of main memory +1 because entry ptr
    labels = {}
    unresolved = [] #(index_in_words, 'labelname', line_number)
    if not bios:
        unresolved.append((0, 'ENTRY', 0))
    include_mems = [] #('mem...', mem_length)

    error = 0
    for line, i in lines:
        #find labels
        colon = line.find(':')
        if colon == 0:
            printerror("SyntaxError: expexted label before ':'", i)
            error = 1
            continue
        if colon > 0:
            label = line[:colon]
            if label.isalnum() and label[0].isalpha():
                if label in labels:
                    printerror("Error: repeated label '"+label+"'", i)
                    error = 1
                    continue
                labels[label] = adr_ctr #point to where we currently are
            else:
                printerror("SyntaxError: invalid label '"+label+"'", i)
                error = 1
                continue
            line = line[colon+1:].strip()
        #do nothing if line was empty but for a label
        if not line: continue

        #check for constant ' ' used (it would be split)
        if '\x00' in line: #check first for null as we will use it
            printerror("SyntaxError: invalid syntax", i)
            error = 1
            continue
        space = line.find("' '")
        if space >= 0:
            line = line[:space+1]+"\x00"+line[space+2:] #replace space with null
        #get instruction and operands
        line = re.split(' |, ', line)
        if line[0] not in INSTRS:
            if line[0] == 'CONST': #special keyword CONST: just add immediate
                #parse immediate (labels autoupdated)
                try:
                    word = parse_immediate(line[1], i, words, labels, unresolved)
                    words.append(word)
                    adr_ctr += 1
                except ValueError:
                    printerror("Error: invalid immediate '"+imm+"'", i)
                    error = 1
                continue
            elif line[0] == 'INCLUDE': #special keyword: include mem file
                #add memory to list
                include_mem, length = get_mem(line[1])
                include_mems.append((include_mem, length))
                #increase address by correct amount
                adr_ctr += length
                #add placeholder to words, which points to this mem
                #the fact that this is negative indicates a special pointer
                words.append(-len(include_mems))
                continue
            else:
                printerror("Error: invalid instruction '"+line[0]+"'", i)
            error = 1
            continue
        instr = INSTRS[line[0]]
        #check correct number of operands
        if instr[1] != len(line)-1:
            printerror("Error: "+line[0]+" takes "+str(instr[1])+" operands", i)
            error = 1
            continue

        #assemble instruction word
        try:
            word = instr[0] << 9
            if instr[2]:
                word += REGS[line[instr[2]]] << 6
            if instr[3]:
                word += REGS[line[instr[3]]] << 3
            if instr[4]:
                word += REGS[line[instr[4]]]
            words.append(word)
            adr_ctr += 1
        except (IndexError, KeyError):
            printerror("Error: invalid operands", i)
            error = 1
            continue
        #add immediate as well if required
        if instr[5]:
            imm = line[instr[5]]
            #parse_immediate will update labels if required
            try:
                word = parse_immediate(imm, i, words, labels, unresolved)
                words.append(word)
                adr_ctr += 1
            except ValueError:
                printerror("Error: invalid immediate '"+imm+"'", i)
                error = 1
                continue

    #resolve unresolved labels
    if printlabels:
        from pprint import pprint
        pprint(labels)
    while unresolved:
        label = unresolved.pop(0)
        if label[1] in labels:
            #add because placeholder will normally be 0,
            #but in a 'base+offset' imm, base or offset may be a label and the other
            #will be added to words, so the label part is added on here
            #(actually both may be labels, and both added together here)
            words[label[0]] += labels[label[1]]
        elif label[1]=='ENTRY':
            printerror("Error: Expected ENTRY label", i) #i is the last line
            error = 1
        else:
            printerror("Error: invalid label '"+label[1]+"'", label[2])
            error = 1

    return (words, include_mems, error)

#--------------------------------- MAIN PROGRAM --------------------------------

#check for command line flags
OVERRIDE_FORMAT = 0
if '-bios' in sys.argv:
    OVERRIDE_FORMAT = 1
    bios = True
    final_ext = '.rom'
    sys.argv.remove('-bios')
if '-raw' in sys.argv:
    if OVERRIDE_FORMAT:
        print('Error: Cannot specify more than one assembly option '
              'to override file headers.')
        sys.exit(1)
    OVERRIDE_FORMAT = 1
    bios = True
    final_ext = '.mem'
    sys.argv.remove('-raw')
if '-prog' in sys.argv:
    if OVERRIDE_FORMAT:
        print('Error: Cannot specify more than one assembly option '
              'to override file headers.')
        sys.exit(1)
    OVERRIDE_FORMAT = 1
    bios = False
    final_ext = '.mem'
    sys.argv.remove('-prog')

rle = False
printlabels = False
if '-rle' in sys.argv:
    rle = True
    sys.argv.remove('-rle')
if '-printlabels' in sys.argv:
    printlabels = True
    sys.argv.remove('-printlabels')

#validate argv and/or print help
if (len(sys.argv)==1 or '-help' in sys.argv or '--help' in sys.argv
    or '/?' in sys.argv):
    print(HELP)
    sys.exit(0)

#assemble programs
for program in sys.argv[1:]:
    #open file for reading
    try:
        in_file = open(program,'r')
    except FileNotFoundError:
        print("Program file '",program,"' not found.",sep='',file=sys.stderr)
        continue
    #setup
    print('Assembling',program,'...')
    raw_lines = in_file.readlines()
    in_file.close()
    error = 0
    #check file header
    first_line = raw_lines.pop(0).strip().split()
    if len(first_line)!=2 or first_line[0][0]!='Z' or first_line[1] not in 'bios raw prog':
        print('Error: Invalid file header',file=sys.stderr)
        error = 1
    elif first_line[0][1:] not in ('1','1.0'):
        print('Error: Zack version', first_line[0][1:], 'not supported',file=sys.stderr)
        error = 1
    elif not OVERRIDE_FORMAT:
        f = first_line[1]
        if f=='bios':
            bios = True
            final_ext = '.rom'
        elif f=='raw':
            bios = True
            final_ext = '.mem'
        elif f=='prog':
            bios = False
            final_ext = '.mem'
        else:
            print('Error: Invalid file header',file=sys.stderr)
            error = 1

    #preprocess file
    if not error:
        lines, names, error = preprocess(raw_lines)
    #assemble instructions
    if not error:
        words, include_mems, error = assemble(lines, bios)
    #if there was an error, don't make an output file
    if error:
        print('Assembly of',program,'unsuccessful')
        continue

    #finally format and write words to memory image file
    progname = strip_extension(program)
    out_name = progname + final_ext
    with open(out_name, 'w') as out_file:
        out_file.write('v2.0 raw')
        if not bios:
            out_file.write('\n512*0')

        if rle: #set up loop variables
            prev_word = None
            run_count = 0
            line_len = 81 #max is 80
            words.append(0) #add extra word as we only write prev_word to file
        else: #init counter
            i = 0
        words_index = 0
        for words_index in range(len(words)):
            word = words[words_index]
            if word<0: #this is an include pointer from an INCLUDE *.mem
                #write the included memory to output
                mem = include_mems[~word] # ~word = -word-1
                out_file.write('\n'+mem[0]+'\n')
                if not(rle or words_index==len(words)-1):
                    #line up next words
                    i += mem[1]
                    rem = i%16
                    out_file.write( ' '*(5*rem + int(rem>7)) )
            elif rle: #run length encoding: check for runs and encode them
                if prev_word is None: #skip first word
                    prev_word = word
                    continue
                if word == prev_word: #we have a run
                    run_count += 1
                    continue
                else:
                    if run_count: #write finished run to file
                        mem_str = str(run_count+1) + '*' + '{:x}'.format(prev_word)
                        run_count = 0
                    else: #no run, just write memory words sequentially
                        mem_str = '{:x}'.format(prev_word)
                    line_len += len(mem_str) + 1 #+1 for space
                    if line_len > 80: #write on new line if line too long
                        out_file.write('\n')
                        line_len = len(mem_str)
                    else: out_file.write(' ')
                out_file.write(mem_str)
            else: #just write regular memory words sequentially
                # make everything look nice
                if not i%16: out_file.write('\n')
                elif not i%4: out_file.write('  ')
                else: out_file.write(' ')
                # write value in hex
                out_file.write(f'{word:04x}')
                i += 1
            #keep track of previous word for run length encoding
            if rle: prev_word = word
        out_file.write('\n')

    print('Assembled',program,'to',out_name+'!')

