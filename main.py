import asyncio
import os
import os.path
from typing import *

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from requests import request

from src.backup.config import COMMAND_REGISTRY, SCOPES, Colors


class OptionsInLine:
    """Initial program display.
    This class displays all available command-line options.
    """

    def __init__(self) -> None:
        self.commands_in_line()

    def commands_in_line(self) -> None:
        """List all available commands."""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*50}{Colors.RESET}")
        print(
            f'{Colors.CYAN}{Colors.BOLD}      GOOGLE DRIVE BACKUP MANAGER{Colors.RESET}'
        )
        print(f"{Colors.CYAN}{Colors.BOLD}{'='*50}{Colors.RESET}\n")

        COMMAND_REGISTRY_COPY = COMMAND_REGISTRY.copy()
        for index, command in enumerate(COMMAND_REGISTRY_COPY, start=1):
            cmd_name, cmd_desc = command.values()
            print(
                f'{Colors.GREEN}{index:2}. {Colors.BOLD}{cmd_name:<15}{Colors.RESET}{Colors.YELLOW}-{Colors.RESET} {cmd_desc}'
            )

        print(f"\n{Colors.CYAN}{'─'*50}{Colors.RESET}")
        print(
            f"{Colors.MAGENTA}💡 Dica:{Colors.RESET} Use {Colors.BOLD}'init'{Colors.RESET} para autenticar pela primeira vez"
        )
        print(f"{Colors.CYAN}{'─'*50}{Colors.RESET}\n")


class RunCommands(OptionsInLine):
    def __init__(self) -> None:
        super().__init__()

    async def input_field(self) -> None:
        """Handle user command input."""
        while True:
            try:
                print(
                    f'{Colors.BLUE}╭─({Colors.GREEN}backup-manager{Colors.BLUE})─[{Colors.WHITE}~{Colors.BLUE}]{Colors.RESET}'
                )
                entry = str(
                    input(f'{Colors.BLUE}╰─{Colors.BOLD}${Colors.RESET} > ')
                ).strip()

                if entry.startswith('backup --all'):
                    print(
                        f'\n{Colors.YELLOW}⚠️  Fazendo backup de todos os arquivos...{Colors.RESET}'
                    )
                    print(
                        f'{Colors.YELLOW}   Isso pode remover arquivos do armazenamento local.{Colors.RESET}\n'
                    )

                elif entry.startswith('backup -f'):
                    print(f'\n{Colors.CYAN}📤 UPLOAD DE ARQUIVO{Colors.RESET}')
                    print(f"{Colors.CYAN}{'─'*30}{Colors.RESET}")
                    current_dir = os.getcwd()
                    print(
                        f'{Colors.WHITE}Diretório atual: {Colors.GREEN}{current_dir}{Colors.RESET}'
                    )

                    file_path = str(
                        input(
                            f'\n{Colors.WHITE}📁 Caminho do arquivo: {Colors.RESET}'
                        )
                    ).strip()
                    mime_type_file = str(
                        input(
                            f'{Colors.WHITE}📝 Tipo MIME (opcional): {Colors.RESET}'
                        )
                    ).strip()

                    if mime_type_file == '':
                        mime_type_file = None

                    print(
                        f'\n{Colors.YELLOW}⏳ Enviando arquivo...{Colors.RESET}'
                    )
                    await Commands().upload(
                        file_path=file_path, mime_type=mime_type_file
                    )

                elif entry.startswith('backup --list'):
                    print(
                        f'\n{Colors.CYAN}📋 LISTANDO ARQUIVOS DO GOOGLE DRIVE{Colors.RESET}'
                    )
                    print(f"{Colors.CYAN}{'─'*40}{Colors.RESET}")
                    await Commands().list()

                elif entry.startswith('backup --delete'):
                    print(f'\n{Colors.RED}🗑️  EXCLUIR ARQUIVO{Colors.RESET}')
                    print(f"{Colors.RED}{'─'*25}{Colors.RESET}")
                    await Commands().list()
                    print(
                        f'\n{Colors.YELLOW}⚠️  Atenção: Esta ação é irreversível!{Colors.RESET}'
                    )
                    id_file = str(
                        input(
                            f'\n{Colors.WHITE}🔑 ID do arquivo para excluir: {Colors.RESET}'
                        )
                    ).strip()
                    await Commands().delete_file(file_Id=id_file)

                elif entry.startswith('init'):
                    print(
                        f'\n{Colors.CYAN}🔐 INICIALIZANDO AUTENTICAÇÃO{Colors.RESET}'
                    )
                    print(f"{Colors.CYAN}{'─'*35}{Colors.RESET}")
                    await Commands().authorization_user()

                elif entry in ['exit', 'quit', 'q']:
                    print(f'\n{Colors.GREEN}👋 Até logo!{Colors.RESET}\n')
                    break

                elif entry == 'clear' or entry == 'cls':
                    os.system('clear')
                    self.commands_in_line()

                elif entry.startswith('mkdir'):
                    os.system('clear')
                    name_folder = str(input(f'{Colors.YELLOW} name folder> '))
                    await Commands().create_folder(folder_name=name_folder)

                elif entry.startswith('backup --download'):
                    # Downloads of files
                    os.system('clear')
                    await Commands().list()
                    get_file = str(input('ID do arquivo no drive> '))

                    await Commands().download_file(real_file_id=get_file)

                elif entry == '':
                    continue

                elif entry.startswith('pwd'):
                    os.system('pwd')

                else:
                    print(
                        f'\n{Colors.RED}❌ Comando não reconhecido: {entry}{Colors.RESET}'
                    )
                    print(
                        f'{Colors.YELLOW}📝 Comandos disponíveis:{Colors.RESET}'
                    )
                    self.commands_in_line()

            except KeyboardInterrupt:
                print(f'\n\n{Colors.GREEN}👋 Até logo!{Colors.RESET}\n')
                break
            except Exception as e:
                print(f'\n{Colors.RED}❌ Erro: {e}{Colors.RESET}')


class Commands(RunCommands):
    def __init__(self) -> None:
        super().__init__()
        self.creds = None

    async def start(self):
        await self.input_field()

    async def authorization_user(self) -> None:
        """Handle user authorization with Google Drive API."""
        if os.path.exists('token.json'):
            print(f'{Colors.GREEN}✅ Autenticação verificada.{Colors.RESET}')
            self.creds = Credentials.from_authorized_user_file(
                'token.json', SCOPES
            )

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print(
                    f'{Colors.YELLOW}🔄 Atualizando token de acesso...{Colors.RESET}'
                )
                self.creds.refresh(Request())
            else:
                print(
                    f'{Colors.CYAN}🌐 Iniciando autenticação...{Colors.RESET}'
                )
                print(
                    f'{Colors.YELLOW}⚠️  Uma janela do navegador será aberta para autorização.{Colors.RESET}'
                )
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
            print(
                f'{Colors.GREEN}✅ Autenticação concluída com sucesso!{Colors.RESET}'
            )
        else:
            print(f'{Colors.GREEN}✅ Já autenticado!{Colors.RESET}')

        print(f"{Colors.CYAN}{'─'*35}{Colors.RESET}\n")

    async def list(self) -> None:
        """List files from Google Drive."""
        try:
            await self.authorization_user()
            service = build('drive', 'v3', credentials=self.creds)

            results = (
                service.files()
                .list(
                    pageSize=20,
                    fields='nextPageToken, files(id, name, size, modifiedTime)',
                )
                .execute()
            )

            items = results.get('files', [])

            if not items:
                print(
                    f'{Colors.YELLOW}📭 Nenhum arquivo encontrado no Google Drive.{Colors.RESET}'
                )
                return

            print(
                f'\n{Colors.GREEN}📁 Total de arquivos: {len(items)}{Colors.RESET}\n'
            )
            print(f"{Colors.CYAN}{'─'*70}{Colors.RESET}")
            print(
                f"{Colors.BOLD}{'NOME':<40} {'ID':<25} {'MODIFICAÇÃO':<10}{Colors.RESET}"
            )
            print(f"{Colors.CYAN}{'─'*70}{Colors.RESET}")

            for item in items:
                name = (
                    item['name'][:38] + '...'
                    if len(item['name']) > 38
                    else item['name']
                )
                file_id = item['id'] if len(item['id']) > 22 else item['id']
                modified = (
                    item.get('modifiedTime', 'N/A')[:10]
                    if 'modifiedTime' in item
                    else 'N/A'
                )
                print(
                    f'{Colors.WHITE}{name:<40} {Colors.CYAN}{file_id} {Colors.YELLOW}{modified:<10}{Colors.RESET}'
                )

            print(f"{Colors.CYAN}{'─'*70}{Colors.RESET}\n")

        except HttpError as error:
            print(
                f'{Colors.RED}❌ Erro ao listar arquivos: {error}{Colors.RESET}'
            )

    async def delete_file(self, file_Id: str) -> None:
        """Remove files from Google Drive."""
        try:
            await self.authorization_user()
            service = build('drive', 'v3', credentials=self.creds)

            # Get file info before deletion
            file_info = (
                service.files().get(fileId=file_Id, fields='name').execute()
            )
            file_name = file_info.get('name', 'Arquivo desconhecido')

            print(f'\n{Colors.YELLOW}⚠️  Confirmar exclusão:{Colors.RESET}')
            print(
                f'{Colors.RED}   Arquivo: {Colors.BOLD}{file_name}{Colors.RESET}'
            )
            print(f'{Colors.RED}   ID: {file_Id}{Colors.RESET}')

            confirm = (
                input(
                    f"\n{Colors.YELLOW}❓ Digite 'SIM' para confirmar: {Colors.RESET}"
                )
                .strip()
                .upper()
            )

            if confirm == 'SIM':
                service.files().delete(fileId=file_Id).execute()
                print(
                    f"{Colors.GREEN}✅ Arquivo '{file_name}' excluído com sucesso!{Colors.RESET}"
                )
            else:
                print(f'{Colors.YELLOW}⏹️  Exclusão cancelada.{Colors.RESET}')

        except HttpError as error:
            print(
                f'{Colors.RED}❌ Erro ao excluir arquivo: {error}{Colors.RESET}'
            )
        except Exception as e:
            print(f'{Colors.RED}❌ Erro: {e}{Colors.RESET}')

    async def upload(self, file_path: str, mime_type: str = None) -> None:
        """Upload a file to Google Drive."""
        try:
            if not os.path.exists(file_path):
                print(
                    f'{Colors.RED}❌ Arquivo não encontrado: {file_path}{Colors.RESET}'
                )
                return

            await self.authorization_user()
            service = build('drive', 'v3', credentials=self.creds)

            # Auto-detect MIME type
            if not mime_type:
                import mimetypes

                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'

            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            print(f'\n{Colors.CYAN}📊 Informações do arquivo:{Colors.RESET}')
            print(
                f'{Colors.WHITE}   Nome: {Colors.GREEN}{file_name}{Colors.RESET}'
            )
            print(
                f'{Colors.WHITE}   Tamanho: {Colors.GREEN}{file_size:,} bytes{Colors.RESET}'
            )
            print(
                f'{Colors.WHITE}   Tipo MIME: {Colors.GREEN}{mime_type}{Colors.RESET}'
            )
            print(f'{Colors.YELLOW}⏳ Enviando...{Colors.RESET}')

            file_metadata = {'name': file_name}

            with open(file_path, 'rb') as file_data:
                media = MediaIoBaseUpload(
                    file_data, mimetype=mime_type, resumable=True
                )
                file = (
                    service.files()
                    .create(body=file_metadata, media_body=media, fields='id')
                    .execute()
                )

            print(
                f'{Colors.GREEN}✅ Upload concluído com sucesso!{Colors.RESET}'
            )
            print(
                f"{Colors.CYAN}🔗 ID do arquivo: {Colors.BOLD}{file.get('id')}{Colors.RESET}\n"
            )

        except HttpError as error:
            print(f'{Colors.RED}❌ Erro no upload: {error}{Colors.RESET}')
        except Exception as e:
            print(f'{Colors.RED}❌ Erro inesperado: {e}{Colors.RESET}')

    async def create_folder(self, folder_name: str) -> str:
        """Create folder in drive"""

        try:
            await self.authorization_user()
            service = build('drive', 'v3', credentials=self.creds)

            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
            }

            file = (
                service.files()
                .create(body=file_metadata, fields='id')
                .execute()
            )
            print(f"{Colors.GREEN}  FOLDER ID: {file.get('id')}")

            return file.get('id')

        except HttpError as error:
            print(f' {Colors.RED}  An error occourred: {error}')

    async def download_file(self, real_file_id: str):
        """Downloads a file
        Args:
            real_file_id: ID of the file to download
        Returns : IO object with location.

        Load pre-authorized user credentials from the environment.
        TODO(developer) - See https://developers.google.com/identity
        for guides on implementing OAuth2 for the application.
        """

        import io

        try:

            await self.authorization_user()
            service = build('drive', 'v3', credentials=self.creds)

            # Get basename of file
            file_metadata = service.files().get(fileId=real_file_id).execute()
            file_name = file_metadata['name']

            print(
                f'{Colors.CYAN} Baixando o arquivo {Colors.GREEN}{file_name}{Colors.RESET}'
            )

            download_path = str(input('Onde deseja salva o arquivo ?: '))
            if download_path == '':
                download_path = os.getcwd()

            # Create absolute path
            file_path = os.path.join(download_path, file_name)

            count = 1

            orinal_name, extension = os.path.splitext(file_path)
            while os.path.exists(file_path):
                new_name = f'{orinal_name}_{count}_{extension}'
                file_path = os.path.join(download_path, new_name)

                count += 1

            # Save file or folder
            request = service.files().get_media(fileId=real_file_id)
            with open(file_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False

                while not done:
                    status, done = downloader.next_chunk()

                    if status:
                        print(
                            f'{Colors.YELLOW} Progresso: {int(status.progress())}%{Colors.RESET}'
                        )

            print(
                f'{Colors.GREEN} Download concluído com sucesso!{Colors.RESET}'
            )
            print(
                f'{Colors.CYAN} arquvo salvo em:{Colors.RESET}{Colors.BOLD}{file_path}'
            )

            return file_path

        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

        except Exception:
            return None


if __name__ == '__main__':
    try:
        test = Commands()
        asyncio.run(test.start())
    except KeyboardInterrupt:
        print(
            f'\n{Colors.GREEN}👋 Programa encerrado pelo usuário.{Colors.RESET}\n'
        )
