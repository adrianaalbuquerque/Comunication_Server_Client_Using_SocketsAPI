#!/usr/bin/env python3
import socket
import os
import sys
import time
import multiprocessing

TAM_MSG = 4096 # Tamanho do bloco de mensagem
HOST = '0.0.0.0' # IP do Servidor
PORT = 40000 # Porta que o Servidor escuta

def processa_msg_cliente(msg, con, cliente):
	msg = msg.decode()
	print('Cliente', cliente, 'enviou', msg)
	msg = msg.split()
	if msg[0].upper() == 'GET':
		nome_arq = " ".join(msg[1:])
		print('Arquivo solicitado:', nome_arq)
		try:
			status_arq = os.stat(nome_arq)
			con.send(str.encode('+OK {}\n'.format(status_arq.st_size)))
			arq = open(nome_arq, "rb")
			while True:
				dados = arq.read(TAM_MSG)
				if not dados: break
				con.send(dados)
		except Exception as e:
			con.send(str.encode('-ERR {}\n'.format(e)))
		return True
	elif msg[0].upper() == 'LIST':
		lista_arq = os.listdir('.')
		con.send(str.encode('+OK {}\n'.format(len(lista_arq))))
		for nome_arq in lista_arq:
			if os.path.isfile(nome_arq):
				status_arq = os.stat(nome_arq)
				con.send(str.encode('arq: {} - {:.1f}KB\n'.format(nome_arq, status_arq.st_size/1024)))
			elif os.path.isdir(nome_arq):
				con.send(str.encode('dir: {}\n'.format(nome_arq)))
			else:
				con.send(str.encode('esp: {}\n'.format(nome_arq)))
		return True
	elif msg[0].upper() == 'CRIAR':
		print('Tentando criar novo contato: ', msg[1])
		nome_arquivo_contato = msg[1] + '.txt'
		if os.path.exists(nome_arquivo_contato):
			con.send(str.encode('-ERR O contato já existe\n'))
			return True
		else:
			#criando novo arquivo de contato
			os.close(os.open(nome_arquivo_contato, os.O_CREAT))
			print('Novo contato criado: ', nome_arquivo_contato)
			con.send(str.encode('+OK\n'))
			return True
	elif msg[0].upper() == 'ESCREVER':
		print('Tentando adicionar número ao contato: ', msg[1])
		lock.acquire()
		try:
			nome_arquivo_contato = msg[1] + '.txt'
			if not os.path.exists(nome_arquivo_contato):
				con.send(str.encode('-ERR O contato não existe\n'))
				return True
			f = open(nome_arquivo_contato, "a")
			f.write(msg[2]+'\n')
			time.sleep(1)
			f.close()
			print('Número adicionado!')
			con.send(str.encode('+OK\n'))
			return True
		except Exception as e:
			print(e)
			con.send(str.encode('-ERR FATAL\n'))
			return False
		finally:
			lock.release()
		return True
	elif msg[0].upper() == 'LER':
		try:
			nome_arquivo_contato = msg[1] + '.txt'
			if not os.path.exists(nome_arquivo_contato):
				con.send(str.encode('-ERR O contato não existe\n'))
				return True
			f = open(nome_arquivo_contato, "r")
			numeros_telefones = f.readlines()
			f.close()
			i = 1
			telefones_mensagem = '+OK\n'
			for telefone in numeros_telefones:
				telefone = telefone.replace('\n', '')
				telefones_mensagem += 'telefone {}: {}\n'.format(i, telefone)
				i += 1
			telefones_mensagem += '+FIM'
			con.sendall(str.encode(telefones_mensagem))
			return True
		except Exception as e:
			print(e)
			con.send(str.encode('-ERR FATAL\n'))
			return False
		return True
	elif msg[0].upper() == 'QUIT':
		con.send(str.encode('+OK\n'))
		return False
def processa_cliente(con, cliente):
	print('Cliente conectado', cliente)
	while True:
		msg = con.recv(TAM_MSG)
		if not msg or not processa_msg_cliente(msg, con, cliente): break
	con.close()
	print('Cliente desconectado', cliente)

lock = multiprocessing.Lock()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv = (HOST, PORT)
sock.bind(serv)
sock.listen(50)
while True:
	try:
		con, cliente = sock.accept()
	except: break
	if os.fork() == 0:
		sock.close()
		processa_cliente(con, cliente)
		break
	else:
		con.close()

sock.close()
