
import os
import sys

class Parser:
  

    def __init__(self, file_name: str):
      
        self.current_command = ""
     
        self.current = -1
     
        self.commands = []
       
        file = open(file_name)
        for line in file:
            line = line.partition("//")[0]
            line = line.strip()
            if line:
                self.commands.append(line)
        file.close()

    def hasMoreCommands(self) -> bool:
       
        return (self.current + 1) < len(self.commands)

    def advance(self) -> None:
      
        self.current += 1
        self.current_command = self.commands[self.current]

    def commandType(self) -> str:
      
       
        arithmetic_commands = ["add", "sub", "neg",
                               "eq", "gt", "lt", "and", "or", "not"]
   
        cmd = self.current_command.split(" ")[0]
     
        if cmd in arithmetic_commands:
            return "C_ARITHMETIC"
        elif cmd == "push":
            return "C_PUSH"
        elif cmd == "pop":
            return "C_POP"
        elif cmd == "label":
            return "C_LABEL"
        elif cmd == "goto":
            return "C_GOTO"
        elif cmd == "if-goto":
            return "C_IF"
        elif cmd == "function":
            return "C_FUNCTION"
        elif cmd == "call":
            return "C_CALL"
        elif cmd == "return":
            return "C_RETURN"
        else:
            raise NameError("Unexpected Command Type")

    def arg1(self) -> str:
        """Returns the first argument of the current command. For C_ARITHMETIC returns the command itself. Should not be called for C_RETURN."""
        if self.commandType() == "C_ARITHMETIC":
            return self.current_command.split(" ")[0]
        else:
            return self.current_command.split(" ")[1]

    def arg2(self) -> int:
        """Returns the second argument of the current command. Only valid for C_PUSH, C_POP, C_FUNCTION, and C_RETURN."""
        return int(self.current_command.split(" ")[2])


class CodeWriter:
    

    def __init__(self, file_name: str):
    
       
        self.file = open(file_name, "w")
       
        self.file_name = ""

        self.function_name = "OS"
      
        self.label_counter = 0
        
        self.symbols = {
           
            "add": "M=D+M",
            "sub": "M=M-D",
            "and": "M=D&M",
            "or": "M=D|M",
            "neg": "M=-M",
            "not": "M=!M",
            "eq": "D;JEQ",
            "gt": "D;JGT",
            "lt": "D;JLT",
          
            "local": "@LCL",
            "argument": "@ARG",
            "this": "@THIS",
            "that": "@THAT",
            "constant": "",
            "static": "",
            "pointer": "@3",
            "temp": "@5"
        }

    def write_init(self):
       
        output = []
   
        output.append("@256")
        output.append("D=A")
        output.append("@SP")
        output.append("M=D")
        self.write_to_file(output)
    
        self.write_function("OS", 0)
       
        self.write_call("Sys.init", 0)

    def set_file_name(self, file_name: str):
        """Informs the codewriter about the file being processed."""
        self.file_name = file_name

    def comment(self, input: str):
        """Writes a comment with the given input."""
        self.write_to_file(["// " + input], False)

    def write_arithmetic(self, command: str):
        """Writes the assembly code for a given arithmetic vm command."""
        output = []
        if command in ["add", "sub", "and", "or"]:
           
            output.append("@SP")
            output.append("AM=M-1")
            output.append("D=M")
            
            output.append("@SP")
            output.append("A=M-1")
         
            output.append(self.symbols[command])
        elif command in ["neg", "not"]:
         
            output.append("@SP")
            output.append("A=M-1")
            output.append(self.symbols[command])
        elif command in ["eq", "gt", "lt"]:
            jump_label = "CompLabel" + str(self.label_counter)
            self.label_counter += 1
       
            output.append("@SP")
            output.append("AM=M-1")
            output.append("D=M")
            
            output.append("@SP")
            output.append("A=M-1")
           
            output.append("D=M-D")
           
            output.append("M=-1")
           
            output.append("@" + jump_label)
         
           
            output.append(self.symbols[command])
            
            output.append("@SP")
            output.append("A=M-1")
            output.append("M=0")
    
            output.append("(" + jump_label + ")")
        else:
            raise NameError("Unexpected Arithmetic Command")

       
        self.write_to_file(output)

    def write_push_pop(self, command: str, segment: str, index: int):
        """Writes the push and pop code for a given vm command."""
        output = []
        if command == "C_PUSH":
            if segment == "constant":
                output.append("@" + str(index))
                output.append("D=A")
                output.append("@SP")
                output.append("AM=M+1")
                output.append("A=A-1")
                output.append("M=D")
            elif segment in ["local", "argument", "this", "that", "temp", "pointer"]:
             
                output.append("@" + str(index))
                output.append("D=A")
              
                if segment == "temp" or segment == "pointer":
                    output.append(self.symbols[segment])
                else:
         
                    output.append(self.symbols[segment])
                    output.append("A=M")
             
                output.append("A=D+A")
         
                output.append("D=M")
            
                output.append("@SP")
                output.append("A=M")
                output.append("M=D")
           
                output.append("@SP")
                output.append("M=M+1")
            elif segment == "static":
                
                output.append("@" + self.file_name + "." + str(index))
 
                output.append("D=M")
   
                output.append("@SP")
                output.append("A=M")
                output.append("M=D")
      
                output.append("@SP")
                output.append("M=M+1")
            else:
                raise NameError("Unexpected Push Segment")
        elif command == "C_POP":
            if segment == "constant":
             
                raise NameError("Cannot Pop Constant Segment")
            elif segment in ["local", "argument", "this", "that", "temp", "pointer"]:
          
                output.append("@" + str(index))
                output.append("D=A")
       
                if segment == "temp" or segment == "pointer":
                    output.append(self.symbols[segment])
                else:
        
                    output.append(self.symbols[segment])
                    output.append("A=M")
    
                output.append("D=D+A")

                output.append("@R13")
                output.append("M=D")

                output.append("@SP")
                output.append("AM=M-1")
                output.append("D=M")
          
                output.append("@R13")
                output.append("A=M")
                output.append("M=D")
            elif segment == "static":
             
                output.append("@SP")
                output.append("AM=M-1")
                output.append("D=M")
              
                output.append("@" + self.file_name + "." + str(index))
          
                output.append("M=D")
            else:
                raise NameError("Unexpected Pop Segment")
        else:
            raise NameError("Unexpected Command Type")

     
        self.write_to_file(output)

    def write_label(self, label: str):
        """Writes the aseembly label."""
        label_name = self.function_name + "$" + label
        output = []
        output.append("(" + label_name + ")")
        self.write_to_file(output)

    def write_goto(self, label: str):
        """Writes unconditional jump to the given label."""
        label_name = self.function_name + "$" + label
        output = []
        output.append("@" + label_name)
        output.append("0;JMP")
        self.write_to_file(output)

    def write_if(self, label: str):
        """Writes conditional jump to the given label."""
        label_name = self.function_name + "$" + label
        output = []
      
        output.append("@SP")
        output.append("AM=M-1")
        output.append("D=M")
     
        output.append("@" + label_name)
        output.append("D;JNE")
        self.write_to_file(output)

    def write_function(self, function_name: str, num_vars: int):
        """Writes the function definition in assembly."""
        output = []
        self.function_name = function_name
        output.append("(" + self.function_name + ")")
        self.write_to_file(output)
        for _ in range(num_vars):
            self.write_push_pop("C_PUSH", "constant", 0)

    def write_call(self, function_name: str, num_args: int):
        """Writes the necessary assembly code to call a function."""
       
        return_label = self.function_name + "$ret." + str(self.label_counter)
        self.label_counter += 1
       
        output = []
      
        output.append("@" + return_label)
        output.append("D=A")
        output.append("@SP")
        output.append("A=M")
        output.append("M=D")
        output.append("@SP")
        output.append("M=M+1")
        
        for segment in ["LCL", "ARG", "THIS", "THAT"]:
            output.append("@" + segment)
            output.append("D=M")
            output.append("@SP")
            output.append("A=M")
            output.append("M=D")
            output.append("@SP")
            output.append("M=M+1")
  
        output.append("@SP")
        output.append("D=M")
        output.append("@5")
        output.append("D=D-A")
        output.append("@" + str(num_args))
        output.append("D=D-A")
        output.append("@ARG")
        output.append("M=D")
   
        output.append("@SP")
        output.append("D=M")
        output.append("@LCL")
        output.append("M=D")
      
        output.append("@" + function_name)
        output.append("0;JMP")
  
        output.append("(" + return_label + ")")
        self.write_to_file(output)

    def write_return(self):
        """Writes the return code of a function call."""
        
        output = []
       
        output.append("@LCL")
        output.append("D=M")
        output.append("@R13")
        output.append("M=D")
   
        output.append("@5")
        output.append("A=D-A")
        output.append("D=M")
        output.append("@R14")
        output.append("M=D")
       
        output.append("@SP")
        output.append("AM=M-1")
        output.append("D=M")
        output.append("@ARG")
        output.append("A=M")
        output.append("M=D")
     
        output.append("@ARG")
        output.append("D=M+1")
        output.append("@SP")
        output.append("M=D")
        
        for segment in ["THAT", "THIS", "ARG", "LCL"]:
            output.append("@R13")
            output.append("AM=M-1")
            output.append("D=M")
            output.append("@" + segment)
            output.append("M=D")
        
        output.append("@R14")
        output.append("A=M")
        output.append("0;JMP")
        self.write_to_file(output)

    def write_to_file(self, output: list, new_line=True):
        """Writes a given list of output."""
        
        if new_line:
            output.append("")
        
        for line in output:
            print(line, file=self.file)

    def close(self):
        """Closes the output file."""
        self.file.close()


def main():
    """Arranges the parsing and code conversion of a Virtual Machine file."""

    
    if len(sys.argv) != 2:
        print("Error: No input file is found.")
        print("Usage: python " + __file__ + " [file.vm] | [directory]")
        return

  
    input_files = []
    input_path = sys.argv[1]

    if os.path.isfile(input_path) and input_path[-3:] == ".vm":
        input_files.append(input_path)
        output_file_name = input_path[:-3] + ".asm"
   
    elif os.path.isdir(input_path):
      
        if input_path[-1:] == "/":
            input_path = input_path[:-1]
   
        for file_name in os.listdir(input_path):
            if file_name[-3:] == ".vm":
                input_files.append(input_path + "/" + file_name)
       
        if len(input_files) == 0:
            raise NameError("No Input File Found")
        output_file_name = input_path + ".asm"
    else:
        raise NameError("Unknown Input Path")

    
    code_writer = CodeWriter(output_file_name)


    code_writer.comment("Bootstrap Code")
    code_writer.write_init()

   
    for input_file_name in input_files:
       
        file_name = input_file_name.split("/")[-1][:-3]
        code_writer.set_file_name(file_name)

       
        parser = Parser(input_file_name)

      
        while parser.hasMoreCommands():
            parser.advance()
            
            code_writer.comment(parser.current_command)
           
            command_type = parser.commandType()
            if command_type == "C_ARITHMETIC":
              
                code_writer.write_arithmetic(parser.arg1())
            elif command_type in ["C_PUSH", "C_POP"]:
              
                segment = parser.arg1()
                index = parser.arg2()
                code_writer.write_push_pop(command_type, segment, index)
            elif command_type == "C_LABEL":
               
                code_writer.write_label(parser.arg1())
            elif command_type == "C_GOTO":
               
                code_writer.write_goto(parser.arg1())
            elif command_type == "C_IF":
            
                code_writer.write_if(parser.arg1())
            elif command_type == "C_FUNCTION":
           
                function_name = parser.arg1()
                num_vars = parser.arg2()
                code_writer.write_function(function_name, num_vars)
            elif command_type == "C_CALL":
            
                function_name = parser.arg1()
                num_args = parser.arg2()
                code_writer.write_call(function_name, num_args)
            elif command_type == "C_RETURN":
               
                code_writer.write_return()
            else:
                raise NameError("Unsupported Command Type")

   
    code_writer.close()


if __name__ == "__main__":
    main()