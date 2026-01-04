
# If modifying these scopes, delete the file token.json.
# Then run python3 main.py and type 'init'. in terminal
SCOPES = ['https://www.googleapis.com/auth/drive']


# Registro central de comandos do sistema.
# Os comandos listados aqui são carregados automaticamente na CLI ao iniciar o programa.
COMMAND_REGISTRY = [
    {'command': 'init', 'description': 'Realizar login no google drive.'},
    {
        'command': 'backup --all',
        'description': 'Realiza o backup de todas as pastas configuradas.',
    },
    {
        'command': 'backup -f <files>',
        'description': 'Realiza o backup de arquivos ou pastas específicas.',
    },
    {
        'command': 'backup --list',
        'description': 'Lista todos os arquivos armazenados na nuvem.',
    },
    {
        'command': 'backup --delete <files>',
        'description': 'Remove um arquivo específico da nuvem.',
    },

    {
        'command': 'mkdir', 
        'description': 'Cria uma pasta no drive.'
    },
]

# Códigos de cores ANSI
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Cores de texto
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Cores de fundo
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


