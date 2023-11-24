import mysql.connector
import GPUtil
from datetime import datetime
import time
import logging
import socket
import requests

webhook_url = "https://hooks.slack.com/services/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"



logging.basicConfig(filename='log_performee_gpu.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    password='sptech',
    database='performee',
)

tentativas = 6
vezestentada = 1


hostname = socket.gethostname()


ipUser = socket.gethostbyname(hostname)

cursor = conexao.cursor()

print("""
+------------------------------------+
|   Bem vindo ao \033[1;34mPerformee\033[m GPU!.     |""")
for tentativa in range(tentativas, 0, -1):
    ipServidor = input("""+------------------------------------+
Digite o IP do Servidor: """)

    buscaIp = f'select count(*) from servidor where ipServidor = "{ipServidor}"'
    cursor.execute(buscaIp)
    resultado = cursor.fetchone()  # ler o banco de dados
    valorResult = resultado[0]

    if valorResult == 0:
        print('\033[1;31mServidor não encontrado!\033[m')
        tentativas -= 1
        if tentativas == 0:
            logging.info(
                f' Usuário do IP {ipUser}, hostName: {hostname}. Esgotou o número máximo de tentativas para acessar o servidor! e o Python foi encerrado')
            print('Acabou suas tentativas! Volte mais tarde')


        else:
            print(f'Você tem \033[1;31m{tentativas}\033[m tentativas!'.format(tentativas))
            logging.info(f' Usuário do IP {ipUser}, hostName: {hostname}. Tentou acessar um servidor inexistente pela {vezestentada} vez!')
            vezestentada += 1

    else:
        print("\033[1;32mServidor Encontrado!\033[m")
        logging.info(
            f' Usuário do IP {ipUser}, hostName: {hostname}. Acessou o Servidor de IP: {ipServidor} com Sucesso!')

        while True:
            buscarEmp = f'select fkEmpresa from servidor where ipServidor = "{ipServidor}"'
            cursor.execute(buscarEmp)
            empresa = cursor.fetchone()  # ler o banco de dados
            fkEmpresa = empresa[0]

            buscarDc = f'select fkDataCenter from servidor where ipServidor = "{ipServidor}"'
            cursor.execute(buscarDc)
            dataCenter = cursor.fetchone()  # ler o banco de dados
            fkDataCenter = dataCenter[0]

            print("""+------------------------------------+
| 1) Cadastrar GPU                   |
| 2) Inserir Dados GPU               |
| 3) Sair                            |
+------------------------------------+""")
            opcao = int(input('Escolha a opção: '))


            gpus = GPUtil.getGPUs()

            for gpu in gpus:
                modelo = gpu.name
                capacidadeTotal = gpu.memoryTotal
                uso = gpu.load * 100
                temp = gpu.temperature

            if opcao == 1:
                verificarGpu = f'select count(*) from Componente where tipo = "GPU" and fkServidor = "{ipServidor}"'
                cursor.execute(verificarGpu)
                verificacao = cursor.fetchone()  # ler o banco de dados
                gpuExist = verificacao[0]

                if gpuExist == 0:
                    print('Cadastrando GPU....')
                    insertGpu = (f'insert into Componente (tipo, modelo, capacidadeTotal, fkMedida, fkEmpresa, fkDataCenter, '
                                 f'fkServidor) values ("GPU", "{modelo}","{capacidadeTotal}", 3, {fkEmpresa}, {fkDataCenter}, '
                                 f'"{ipServidor}")')
                    cursor.execute(insertGpu)
                    print("\033[1;32mGPU Cadastrada Com Sucesso!\033[m")
                    logging.info(
                        f' Usuário do IP {ipUser}, hostName: {hostname}. Cadastrou a GPU do servidor de IP: {ipServidor} com sucesso!')

                else:
                    print("\033[1;33mGPU já cadastrada nesse servidor!\033[m")
                    logging.info(
                        f' Usuário do IP {ipUser}, hostName: {hostname}. Tentou cadastrar a GPU do servidor de IP: {ipServidor}, mas já existe GPU cadastrada')



            elif opcao == 2:

                logging.info(
                    f' Usuário do IP {ipUser}, hostName: {hostname}. iniciou o processo inserção de dados da GPU do servidor de IP: {ipServidor}')

                while True:
                    dataHoraAtual = datetime.now()
                    pegaridComponente = f'select idComponente from Componente where tipo = "GPU" and fkServidor = "{ipServidor}"'
                    cursor.execute(pegaridComponente)
                    idComp = cursor.fetchone()  # ler o banco de dados
                    fkComponente = idComp[0]

                    print("inserindo dados da GPU")
                    insertLeituraGpu = (f'insert into Leitura (dataLeitura, emUso, temperatura, fkMedidaTemp, fkEmpresa, '
                                        f'fkDataCenter, fkServidor, fkComponente) values ("{dataHoraAtual}", format({uso}, '
                                        f'2), format({temp}, 2), 5, {fkEmpresa}, {fkDataCenter},"{ipServidor}", '
                                        f'{fkComponente})')
                    cursor.execute(insertLeituraGpu) # executa o script do banco
                    conexao.commit()  # edita o banco de dados

                    mediaGpu = f'SELECT ROUND(AVG(emUso), 2) AS media_ultimas_10_leituras FROM (SELECT emUso FROM leitura AS l JOIN componente AS c ON c.idComponente = l.fkComponente WHERE c.tipo = "GPU" AND l.fkServidor = "{ipServidor}" ORDER BY l.idLeitura DESC LIMIT 10 ) AS ultimas_leituras'
                    cursor.execute(mediaGpu)
                    gpuUso = cursor.fetchone()
                    mediaUsoGpu = gpuUso[0]

                    media_temperatura_gpu = f'SELECT ROUND(AVG(temperatura), 2) AS media_ultimas_10_leituras FROM (SELECT temperatura FROM leitura AS l JOIN componente AS c ON c.idComponente = l.fkComponente WHERE c.tipo = "GPU" AND l.fkServidor = "{ipServidor}" ORDER BY l.idLeitura DESC LIMIT 10) AS ultimas_leituras'
                    cursor.execute(media_temperatura_gpu)
                    temperaturaGpu = cursor.fetchone()[0]

                    leitura = f'SELECT idLeitura FROM leitura AS l JOIN componente AS c ON c.idComponente = l.fkComponente WHERE c.tipo = "GPU" AND l.fkServidor = {ipServidor} ORDER BY l.idLeitura DESC LIMIT 1'
                    cursor.execute(leitura)
                    leituraFk = cursor.fetchone()
                    fkLeitura = leituraFk[0]
                    #
                    if mediaUsoGpu >= 85:
                        descricao = f"Alerta de Risco. Servidor {ipServidor}: A utilização da GPU esteve constantemente acima de 85%, nas últimas 10 verificação. Pode ocorrer travamentos! Média de utilização: {mediaUsoGpu}%"

                        tipo = "Em risco"

                        insertAlerta = (
                            f'insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values ("{dataHoraAtual}", "{tipo}", "{descricao}", {fkEmpresa}, {fkDataCenter}, "{ipServidor}", {fkComponente}, {fkLeitura})')
                        cursor.execute(insertAlerta)  # executa o script do banco
                        conexao.commit()

                        alerta = {"text": descricao}
                        response = requests.post(webhook_url, json=alerta)

                        logging.critical(
                            f' Usuário do IP {ipUser}, hostName: {hostname}. Teve {descricao}')

                    elif mediaUsoGpu >= 66 and mediaUsoGpu <= 84:
                        descricao = f"Alerta de Cuidado. Servidor {ipServidor}: A utilização da GPU esteve constantemente entre 66% a 84%, nas últimas 10 verificação. Pode ocorrer lentidão! Média de utilização: {mediaUsoGpu}%"

                        tipo = "Cuidado"

                        insertAlerta = (
                            f'insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values ("{dataHoraAtual}", "{tipo}", "{descricao}", {fkEmpresa}, {fkDataCenter}, "{ipServidor}", {fkComponente}, {fkLeitura})')
                        cursor.execute(insertAlerta)  # executa o script do banco
                        conexao.commit()

                        alerta = {"text": descricao}
                        response = requests.post(webhook_url, json=alerta)

                        logging.warning(
                            f' Usuário do IP {ipUser}, hostName: {hostname}. Teve {descricao}')
                    else:
                        descricao = f"Alerta Estável. Servidor {ipServidor}: A utilização da GPU está abaixo 66%, nas últimas 10 verificação. A utilização! Média de utilização: {mediaUsoGpu}%"

                        tipo = 'Estável'

                        insertAlerta = (
                            f'insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values ("{dataHoraAtual}", "{tipo}", "{descricao}", {fkEmpresa}, {fkDataCenter}, "{ipServidor}", {fkComponente}, {fkLeitura})')
                        cursor.execute(insertAlerta)  # executa o script do banco
                        conexao.commit()

                        alerta = {"text": descricao}
                        response = requests.post(webhook_url, json=alerta)


                    if temperaturaGpu > 39:
                        descricao2 = f"Alerta de Risco. Servidor {ipServidor}: A temperatura da GPU está acima de 39°C, nas últimas 10 verificação. Risco de Super Aquecimento! Média de temperatura: {temperaturaGpu}°C"

                        tipo = "Em risco"

                        insertAlerta = (
                            f'insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values ("{dataHoraAtual}", "{tipo}", "{descricao2}", {fkEmpresa}, {fkDataCenter}, "{ipServidor}", {fkComponente}, {fkLeitura})')
                        cursor.execute(insertAlerta)  # executa o script do banco
                        conexao.commit()

                        alerta = {"text": descricao2}
                        response = requests.post(webhook_url, json=alerta)

                        logging.critical(
                            f' Usuário do IP {ipUser}, hostName: {hostname}. Teve {descricao}')
                    elif temperaturaGpu >= 35 and temperaturaGpu <= 39:
                        descricao2 = f"Alerta de Cuidado. Servidor {ipServidor}: A temperatura da GPU está entre 35°C a 39°C, nas últimas 10 verificação. Pode ocorrer aquecimento! Média de temperatura: {temperaturaGpu}°C"

                        tipo = "Cuidado"

                        insertAlerta = (
                            f'insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values ("{dataHoraAtual}", "{tipo}", "{descricao2}", {fkEmpresa}, {fkDataCenter}, "{ipServidor}", {fkComponente}, {fkLeitura})')
                        cursor.execute(insertAlerta)  # executa o script do banco
                        conexao.commit()

                        alerta = {"text": descricao2}
                        response = requests.post(webhook_url, json=alerta)

                        logging.critical(
                            f' Usuário do IP {ipUser}, hostName: {hostname}. Teve {descricao}')
                    else:
                        descricao2 = f"Alerta Estável. Servidor {ipServidor}: A temperatura da GPU está abaixo de 35°C, nas últimas 10 verificação. Temperatura está OK! Média de temperatura: {temperaturaGpu}°C"

                        tipo = "Estável"

                        insertAlerta = (
                            f'insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values ("{dataHoraAtual}", "{tipo}", "{descricao2}", {fkEmpresa}, {fkDataCenter}, "{ipServidor}", {fkComponente}, {fkLeitura})')
                        cursor.execute(insertAlerta)  # executa o script do banco
                        conexao.commit()

                        alerta = {"text": descricao2}
                        response = requests.post(webhook_url, json=alerta)

                    time.sleep(15)

            elif opcao == 3:
                print("Saindo...")
                break
            else:
                print('Número Inválido!')

                cursor.close()
                conexao.close()
