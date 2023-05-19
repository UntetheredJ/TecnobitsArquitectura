
import sys, re

A_COMMAND = 'A'
C_COMMAND = 'C'
L_COMMAND = 'L'

class Parser:
    """Lee un comando en lenguaje assembly, lo parsea y provee acceso a los componentes
     del comando. Además, elimina los espacios en blanco y los comentarios"""

    def __init__(self, filepath):
        """Abre el archivo y se prepara para parsear"""
        try:
            with open(filepath, 'r') as f:
                self.commands = list(filter(len,
                                            [re.sub('//.*$', '', l).strip() for l in f]))
        except FileNotFoundError:
            print("Could not find %s" % (filepath))

    def hasMoreCommands(self):
        return len(self.commands) > 0

    def next(self):
        """Lee el siguiente comando del input y lo convierte en el comando actual.
         Se llama únicamente si hasMoreCommands() es true."""
        self.command = self.commands.pop(0)

    def commandType(self):
        """Retorna el tipo de comando:
        * A_COMMAND para @Xxx donde Xxx es un número decimal o un símbolo
        * C_COMMAND para dest=comp;jump
        * L_COMMAND (pseudo-command) para (Xxx) donde Xxx es un símbolo"""
        if self.command[0] == '@':
            return A_COMMAND
        elif self.command[0] == '(' and self.command[-1] == ')':
            return L_COMMAND
        return C_COMMAND

    def symbol(self):
        """Retorna el decimal o símbolo Xxx del comando actual @Xxx o
        (Xxx). Se llama cuando commandType() es A_COMMAND o
        L_COMMAND"""
        return self.command.strip('@()')

    def dest(self):
        """Retorna el mnemónico de destino en el comando C actual
        Se llama solo cuando commandType() es C_COMMAND"""
        if '=' not in self.command:
            return ''
        return self.command.split('=')[0]

    def comp(self):
        return self.command.split('=')[-1].split(';')[0]

    def jump(self):
        """Retorna el mnemónico de salto en el comando C actual.
        Se llama solo cuando commandType() es C_COMMAND"""
        if ';' not in self.command:
            return ''
        return self.command.split('=')[-1].split(';')[-1]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python Parser.py FILE")
    else:
        print("Running parser")
    for arg in sys.argv[1:]:
        p = Parser(arg)
        while p.hasMoreCommands():
            p.next()
            print("Symbol: %s, instruction: %s, dest: %s, comp: %s, jump: %s"
                  % (p.symbol(), p.commandType(), p.dest(), p.comp(), p.jump()))
