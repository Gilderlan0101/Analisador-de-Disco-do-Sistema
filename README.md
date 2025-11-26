# Analisador-de-Disco-do-Sistema
Script "plug-and-play" que verifica automaticamente o tamanho total de múltiplos diretórios (ex: /home/) e exibe os resultados em formatos legíveis (KB, MB, GB). Ponto de partida eficiente para monitorar o uso do armazenamento do sistema


Requisitos:
```
pip install python-dotenv

USER_ROOT="seu_usuario_root" 

```


```



import os
import logging
import math

from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_subdirectories(root_dir: str) -> list[str]:
    """
    Lists all immediate subdirectories within a root directory.
    """
    # Initialize list to store the directory paths
    dir_list = []

    # Check if the root directory exists before trying to scan
    if not os.path.isdir(root_dir):
        logging.error(f"The root directory does not exist: {root_dir}")
        return []

    logging.info(f"Searching for folders inside: {root_dir}")

    # scandir is more efficient than listdir + isdir
    with os.scandir(root_dir) as entries:
        for entry in entries:
            # entry.is_dir() checks if it's a directory (and not a file)
            if entry.is_dir():
                # entry.path is already the full path
                dir_list.append(entry.path)

    return dir_list


def format_file_size(bytes_size):
    """
    Formats a size in bytes into a human-readable unit of measure (B, KB, MB, GB, TB, etc.).
    """
    if bytes_size == 0:
        return '0 B'

    # Define the units of measurement
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

    # Calculate the logarithm base 1024 to find the correct unit index
    i = int(math.floor(math.log(bytes_size, 1024)))

    # Limit the index to avoid errors if the number is too large for defined units
    i = min(i, len(units) - 1)

    # Calculate the formatted size
    formatted_size = round(bytes_size / (1024**i), 2)
    unit = units[i]

    return f'TOTAL: {formatted_size} {unit}'


def get_folder_size(paths: list[str]) -> str:
    """Find all folders belonging to the root user and determine their total size."""

    total_file = 0

    try:

        # Checking beforehand if the path is a directory.
        for current_path in paths:
            path_isdir = os.path.isdir(current_path)

            if path_isdir:

                logging.info(
                    f'Performing a query in the directory: [{os.path.basename(current_path)}]'
                )

                for dirpath, dirnames, filenames in os.walk(current_path):
                    for file in filenames:
                        fp = os.path.join(dirpath, file)

                        try:
                            # Add the file size to the total starting at zero.
                            total_file += os.path.getsize(fp)
                        except OSError as e:
                            logging.error(
                                f'Error when trying to access directory. [{current_path}]  ERRO: {str(e)}'
                            )
                            continue

            else:
                logging.info(f'Invalid path or not a directory {current_path}')

        return format_file_size(total_file)

    except Exception as e:
        logging.error(
            f'Fatal error while attempting to verify directory sizes. ERRO: {str(e)}'
        )
        raise e



path = get_subdirectories(f'/home/{os.getenv('USER_ROOT')}')
total = get_folder_size(paths=path)
print(total)
```

#Saida
```
TOTAL: 36.20 GB
```