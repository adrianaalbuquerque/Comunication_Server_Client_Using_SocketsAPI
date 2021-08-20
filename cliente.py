import socket
import sys
import os

TAM_MSG = 4096 # Tamanho do bloco de mensagem
HOST = '127.0.0.1' # IP do Servidor
PORT = 40000 # Porta que o Servidor escuta

#--------------------------------------------------------- Cores ----------------------------------------------------

cor = ('\033[m', '\033[1;41m', '\033[1;42m', '\033[1;43m', '\033[1;44m', '\033[1;45m', '\033[1;97;46m', '\033[1;47m', '\033[7m' , '\033[1;97;103m', '\033[1;97;104m', '\033[1;97;102m', '\033[1;97;40m', '\033[1;100m', '\033[1;101m', '\033[1;97;105m', '\033[1;97;106m', '\033[1;31m', '\033[1;32m', '\033[1;33m', '\033[1;34m', '\033[1;35m', '\033[1;36m', '\033[1;37m', '\033[1;97m', '\033[1;93m', '\033[1;94m', '\033[1;92m', '\033[1;40m', '\033[1;90m', '\033[1;91m', '\033[1;95m', '\033[1;96m', '\033[1;30m')

def linha(tam=55):
  return '-' * tam

def cabecalho(txt, corz):
    print(linha())
    print(f'{cor[corz]}{txt.center(55)}{cor[0]}')
    print(linha())

# ----------------------------------------------------------------------------------------------------------------------

def decode_cmd_usr(cmd_usr):
    cmd_map = {
        'exit': 'quit',
        'ls': 'list',
        'down': 'get',
        'ler': 'ler',
        'criar': 'criar',
        'escrever': 'escrever',
    }

    tokens = cmd_usr.split()
    if tokens[0].lower() in cmd_map:
        tokens[0] = cmd_map[tokens[0].lower()]
        return " ".join(tokens)
    else:
        return False
if len(sys.argv) > 1:
    HOST = sys.argv[1]


cabecalho('LISTA TELEFÔNICA', 15)

cabecalho('MENU PRINCIPAL', 0)

print(f'\n{cor[25]}{"[CRIAR]":>10}{cor[0]} - {cor[26]}Adicionar nome de um novo contato{cor[0]}\n{cor[25]}{"[ESCREVER]":>10}{cor[0]} - {cor[26]}Inserir número em um contato específico{cor[0]}\n{cor[25]}{"[LER]":>10}{cor[0]} - {cor[26]}Exibir número(s) de telefone de um contato{cor[0]}\n{cor[25]}{"[LS]":>10}{cor[0]} - {cor[26]}Listar arquivos dos contatos{cor[0]}\n{cor[25]}{"[DOWN]":>10}{cor[0]} - {cor[26]}Baixar arquivo de um contato específico{cor[0]}\n')

cabecalho('INSTRUÇÕES', 14)

print(f"{cor[17]} CRIAR nome_do_contato \n ESCREVER nome_do_contato numero_do_contato \n LER nome_do_contato \n {cor[0]}")

print(linha())

print('Servidor:', HOST+':'+str(PORT))
serv = (HOST, PORT)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(serv)
print('Para encerrar use EXIT, CTRL+D ou CTRL+C\n')
while True:
    try:
        cmd_usr = input('BTP> ')
    except:
        cmd_usr = 'EXIT'
    cmd = decode_cmd_usr(cmd_usr)
    if not cmd:
        print('Comando indefinido:', cmd_usr)
    else:
        sock.send(str.encode(cmd))
        dados = sock.recv(TAM_MSG)
        if not dados: break
        msg_status = dados.decode().split('\n')[0]
        dados = dados[len(msg_status)+1:]
        if msg_status == '-ERR FATAL':
            print('Houve um problema grave ao tentar realizar a última operação no servidor, encerrando conexão...')
            break
        print(msg_status)
        cmd = cmd.split()
        cmd[0] = cmd[0].upper()
        if cmd[0] == 'QUIT':
            break
        elif cmd[0] == 'LIST':
            num_arquivos = int(msg_status.split()[1])
            dados = dados.decode()
            while True:
                arquivos = dados.split('\n')
                residual = arquivos[-1] # último sem \n fica para próxima
                for arq in arquivos[:-1]:
                    print(arq)
                    num_arquivos -= 1
                if num_arquivos == 0: break
                dados = sock.recv(TAM_MSG)
                if not dados: break
                dados = residual + dados.decode()
        elif cmd[0] == 'GET':
            nome_arq = " ".join(cmd[1:])
            print('Recebendo:', nome_arq)
            arq = open(nome_arq, "wb")
            tam_arquivo = int(msg_status.split()[1])
            while True:
                arq.write(dados)
                tam_arquivo -= len(dados)
                if tam_arquivo == 0: break
                dados = sock.recv(TAM_MSG)
                if not dados: break
            arq.close()
        elif cmd[0] == 'LER':
            dados = dados.decode()
            if '-ERR' in msg_status:
              print(dados)
            else:
              while not '+FIM' in dados:
                  residual = sock.recv(TAM_MSG)
                  dados += residual.decode()
              print(f'Esses são os números de telefone de {cmd[1]}')
              print(dados)  
        elif cmd[0] == 'CRIAR':
            if msg_status == "+OK":
                print('Contato criado com sucesso')
            else:
                print('Houve um problema ao tentar criar novo contato')
        elif cmd[0] == 'ESCREVER':
            if msg_status == "+OK":
                print('Número adicionado com sucesso')
            else:                
                print('Houve um problema ao adicionar novo número')

sock.close()
