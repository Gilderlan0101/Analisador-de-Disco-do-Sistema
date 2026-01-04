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
