
import GPUtil
from datetime import datetime
import time
import logging
import socket
import requests

import MySql
import SqlServer

webhook_url = "https://hooks.slack.com/services/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"

logging.basicConfig(filename='log_performee_gpu.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

tentativas = 6

vezestentada = 1

hostname = socket.gethostname()

ipUser = socket.gethostbyname(hostname)

cursor = MySql.conexao.cursor()

cursorServer = SqlServer.cursor



print("""
+------------------------------------+
|   Bem vindo ao \033[1;34mPerformee\033[m GPU!      |""")
for tentativa in range(tentativas, 0, -1):
    ipServidor = input("""+------------------------------------+
Digite o IP do Servidor: """)

    buscaIp = f"select count(*) from servidor where ipServidor = '{ipServidor}'"
    cursorServer.execute(buscaIp)
    resultado = cursorServer.fetchone()  # ler o banco de dados
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
            buscarEmp = f"select fkEmpresa from servidor where ipServidor = '{ipServidor}'"
            cursorServer.execute(buscarEmp)
            empresa = cursorServer.fetchone()  # ler o banco de dados
            fkEmpresa = empresa[0]

            buscarDc = f"select fkDataCenter from servidor where ipServidor = '{ipServidor}'"
            cursorServer.execute(buscarDc)
            dataCenter = cursorServer.fetchone()  # ler o banco de dados
            fkDataCenter = dataCenter[0]

            fkEmpresaLocal = ""
            fkDataCenterLocal = ""

            #Verificando se tem os dados cadastrado no banco local

            slcServer = f"SELECT COUNT(*) FROM Servidor where IpServidor = '{ipServidor}'"
            cursor.execute(slcServer)
            verificacaoIp = cursor.fetchone()[0]

            slcEmail = f"SELECT email FROM Empresa where idEmpresa = {fkEmpresa}"
            cursorServer.execute(slcEmail)
            emailEmpr = cursorServer.fetchone()[0]

            slcCnpj = f"SELECT cnpj FROM Empresa where idEmpresa = {fkEmpresa}"
            cursorServer.execute(slcCnpj)
            cnpjEmp = cursorServer.fetchone()[0]

            slcNome = f"SELECT nome FROM DataCenter where idDataCenter = {fkDataCenter}"
            cursorServer.execute(slcNome)
            nomeDc = cursorServer.fetchone()[0]

            slcTamanho = f"SELECT tamanho FROM DataCenter where idDataCenter = {fkDataCenter}"
            cursorServer.execute(slcTamanho)
            tamanhoDc = cursorServer.fetchone()[0]

            # Se o IP já existir
            if verificacaoIp != 0:
                # Obter informações relacionadas ao servidor
                fkEmpLocal = f"SELECT fkEmpresa FROM Servidor where IpServidor = '{ipServidor}'"
                cursor.execute(fkEmpLocal)
                fkEmpresaLocal = cursor.fetchone()[0]
                fkDcLocal = f"SELECT fkDataCenter FROM Servidor where IpServidor = '{ipServidor}'"
                cursor.execute(fkDcLocal)
                fkDataCenterLocal = cursor.fetchone()[0]
            else:

                # Verificar se a empresa já existe
                emailE = f"SELECT COUNT(*) FROM Empresa where email = '{emailEmpr}'"
                cursor.execute(emailE)
                emailEmprL = cursor.fetchone()[0]

                cnpjE = f"SELECT COUNT(*) FROM Empresa where cnpj = '{cnpjEmp}'"
                cursor.execute(cnpjE)
                cnpjEmprL = cursor.fetchone()[0]

                # Verificar se o DataCenter já existe
                dcE = f"SELECT COUNT(*) FROM DataCenter where nome = '{nomeDc}'"
                cursor.execute(dcE)
                nomeDcL = cursor.fetchone()[0]

                tamanhoE = f"SELECT COUNT(*) FROM DataCenter where tamanho = {tamanhoDc}"
                cursor.execute(tamanhoE)
                tamanhoDcL = cursor.fetchone()[0]

                # Se a empresa não existir, inserir uma nova
                if emailEmprL == 0 and cnpjEmprL == 0:

                    razaoE = f"SELECT razaoSocial FROM Empresa where idEmpresa = {fkEmpresa}"
                    cursorServer.execute(razaoE)
                    razaoSocial = cursorServer.fetchone()[0]

                    nomeFE = f"SELECT nomeFantasia FROM Empresa where idEmpresa = {fkEmpresa}"
                    cursorServer.execute(nomeFE)
                    nomeFantasia = cursorServer.fetchone()[0]

                    telE = f"SELECT telefone FROM Empresa where idEmpresa = {fkEmpresa}"
                    cursorServer.execute(telE)
                    telefone = cursorServer.fetchone()[0]

                    inserirEmpresa = f"INSERT INTO Empresa(razaoSocial, nomeFantasia, cnpj, email, telefone) VALUES ('{razaoSocial}','{nomeFantasia}','{cnpjEmp}','{emailEmpr}',{telefone})"
                    cursor.execute(inserirEmpresa)
                    MySql.conexao.commit()

                    # Obter o ID da nova empresa
                    fkEmL = f"SELECT idEmpresa FROM Empresa where email = '{emailEmpr}' and cnpj = '{cnpjEmp}'"
                    cursor.execute(fkEmL)
                    fkEmpresaLocal = cursor.fetchone()[0]
                else:
                    # Obter o ID da empresa existente
                    fkEpL = f"SELECT idEmpresa FROM Empresa where email = '{emailEmpr}' and cnpj = '{cnpjEmp}'"
                    cursor.execute(fkEpL)
                    fkEmpresaLocal = cursor.fetchone()[0]

                # Se o DataCenter não existir, inserir um novo
                if nomeDcL == 0 and tamanhoDcL == 0:
                    insertDc = f"INSERT INTO DataCenter(nome, tamanho, fkEmpresa) VALUES ('{nomeDc}',{tamanhoDc},{fkEmpresaLocal})"
                    cursor.execute(insertDc)
                    MySql.conexao.commit()

                    # Obter o ID do novo DataCenter
                    fkDcL = f"SELECT idDataCenter FROM DataCenter where nome = '{nomeDc}' and tamanho = {tamanhoDc}"
                    cursor.execute(fkDcL)
                    fkDataCenterLocal = cursor.fetchone()[0]
                else:
                    # Obter o ID do DataCenter existente
                    fkDcL = f"SELECT idDataCenter FROM DataCenter where nome = '{nomeDc}' and tamanho = {tamanhoDc}"
                    cursor.execute(fkDcL)
                    fkDataCenterLocal = cursor.fetchone()[0]

                # Obter informações relacionadas ao servidor
                hostL = f"SELECT hostname FROM Servidor where IpServidor = '{ipServidor}'"
                cursorServer.execute(hostL)
                hostnameL = cursorServer.fetchone()[0]

                sisL = f"SELECT sisOp FROM Servidor where IpServidor = '{ipServidor}'"
                cursorServer.execute(sisL)
                sisOpL = cursorServer.fetchone()[0]

                atL = f"SELECT ativo FROM Servidor where IpServidor = '{ipServidor}'"
                cursorServer.execute(atL)
                ativoL = cursorServer.fetchone()[0]

                # Inserir o novo servidor
                insertServer = f"INSERT INTO Servidor(ipServidor, hostname, sisOp, ativo, fkEmpresa, fkDataCenter) VALUES ('{ipServidor}','{hostnameL}','{sisOpL}',{ativoL},{fkEmpresaLocal},{fkDataCenterLocal})"
                cursor.execute(insertServer)
                MySql.conexao.commit()

            print("""+------------------------------------+
| 1) Cadastrar GPU                   |
| 2) Inserir Dados GPU               |
| 3) Sair                            |
+------------------------------------+""")
            opcao = int(input('Escolha a opção: '))

            if opcao == 1:
                verificarGpuS = f"select count(*) from Componente where tipo = 'GPU' and fkServidor = '{ipServidor}'"
                cursorServer.execute(verificarGpuS)
                verificacaoS = cursorServer.fetchone()  # ler o banco de dados
                gpuExistS = verificacaoS[0]

                verificarGpu = f"select count(*) from Componente where tipo = 'GPU' and fkServidor = '{ipServidor}'"
                cursor.execute(verificarGpu)
                verificacao = cursor.fetchone()  # ler o banco de dados
                gpuExist = verificacao[0]

                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    modelo = gpu.name
                    capacidadeTotal = gpu.memoryTotal

                if gpuExistS == 0:
                    print('Cadastrando GPU....')
                    insertGpu = (f"insert into Componente (tipo, modelo, capacidadeTotal, fkMedida, fkEmpresa, fkDataCenter, "
                                 f"fkServidor) values ('GPU', '{modelo}','{capacidadeTotal}', 3, {fkEmpresa}, {fkDataCenter}, "
                                 f"'{ipServidor}')")
                    cursorServer.execute(insertGpu)
                    cursorServer.commit()
                    print("\033[1;32mGPU Cadastrada Com Sucesso!\033[m")
                    logging.info(
                        f' Usuário do IP {ipUser}, hostName: {hostname}. Cadastrou a GPU do servidor de IP: {ipServidor} com sucesso!')

                else:
                    print("\033[1;33mGPU já cadastrada nesse servidor!\033[m")
                    logging.info(
                        f' Usuário do IP {ipUser}, hostName: {hostname}. Tentou cadastrar a GPU do servidor de IP: {ipServidor}, mas já existe GPU cadastrada')

                if gpuExist == 0:
                    print('Cadastrando GPU Local....')
                    insertGpu = (f"insert into Componente (tipo, modelo, capacidadeTotal, fkMedida, fkEmpresa, fkDataCenter, "
                                 f"fkServidor) values ('GPU', '{modelo}','{capacidadeTotal}', 3, {fkEmpresaLocal}, {fkDataCenterLocal}, "
                                 f"'{ipServidor}')")
                    cursor.execute(insertGpu)
                    MySql.conexao.commit()

                else:
                    print("\033[1;33mGPU Local já cadastrada nesse servidor!\033[m")


            elif opcao == 2:

                logging.info(
                    f' Usuário do IP {ipUser}, hostName: {hostname}. iniciou o processo inserção de dados da GPU do servidor de IP: {ipServidor}')

                while True:
                    dataHoraAtual = datetime.now()
                    pegaridComponente = f"select idComponente from Componente where tipo = 'GPU' and fkServidor = '{ipServidor}'"
                    cursorServer.execute(pegaridComponente)
                    idComp = cursorServer.fetchone()  # ler o banco de dados
                    fkComponente = idComp[0]

                    pegaridComponenteL = f"select idComponente from Componente where tipo = 'GPU' and fkServidor = '{ipServidor}'"
                    cursor.execute(pegaridComponenteL)
                    idCompL = cursor.fetchone()  # ler o banco de dados
                    fkComponenteLocal = idCompL[0]

                    gpus = GPUtil.getGPUs()
                    for gpu in gpus:
                        uso = gpu.load * 100
                        temp = gpu.temperature

                    print("inserindo dados da GPU")
                    insertLeituraGpu = (f"insert into Leitura (dataLeitura, emUso, temperatura, fkMedidaTemp, fkEmpresa, "
                                        f"fkDataCenter, fkServidor, fkComponente) values (GETDATE(), ROUND({uso}, "
                                        f"2), ROUND({temp}, 2), 5, {fkEmpresa}, {fkDataCenter},'{ipServidor}', "
                                        f"{fkComponente})")
                    cursorServer.execute(insertLeituraGpu)
                    cursorServer.commit()

                    insertLeituraGpuLocal = (
                        f"insert into Leitura (dataLeitura, emUso, temperatura, fkMedidaTemp, fkEmpresa, "
                        f"fkDataCenter, fkServidor, fkComponente) values ('{dataHoraAtual}', ROUND({uso}, "
                        f"2), ROUND({temp}, 2), 5, {fkEmpresaLocal}, {fkDataCenterLocal},'{ipServidor}', "
                        f"{fkComponenteLocal})")
                    cursor.execute(insertLeituraGpuLocal)  # executa o script do banco
                    MySql.conexao.commit()  # edita o banco de dados

                    mediaGpu = f"""SELECT ROUND(AVG(emUso), 2) AS media_ultimas_10_leituras
FROM (
    SELECT TOP 10 emUso
    FROM Leitura AS l
    JOIN Componente AS c ON c.idComponente = l.fkComponente
    WHERE c.tipo = 'GPU' AND l.fkServidor = '{ipServidor}'
    ORDER BY l.idLeitura DESC
) AS ultimas_leituras"""
                    cursorServer.execute(mediaGpu)
                    gpuUso = cursorServer.fetchone()
                    mediaUsoGpu = gpuUso[0]

                    media_temperatura_gpu = f"""SELECT ROUND(AVG(temperatura), 2) AS media_ultimas_10_leituras
FROM (
    SELECT TOP 10 temperatura
    FROM Leitura AS l
    JOIN Componente AS c ON c.idComponente = l.fkComponente
    WHERE c.tipo = 'GPU' AND l.fkServidor = '{ipServidor}'
    ORDER BY l.idLeitura DESC
) AS ultimas_leituras"""
                    cursorServer.execute(media_temperatura_gpu)
                    temperaturaGpu = cursorServer.fetchone()[0]

                    leitura = f"""SELECT TOP 1 idLeitura
FROM Leitura AS l
JOIN Componente AS c ON c.idComponente = l.fkComponente
WHERE c.tipo = 'GPU' AND l.fkServidor = '{ipServidor}'
ORDER BY l.idLeitura DESC
"""
                    cursorServer.execute(leitura)
                    leituraFk = cursorServer.fetchone()
                    fkLeitura = leituraFk[0]

                    leituraL = f'SELECT idLeitura FROM leitura AS l JOIN componente AS c ON c.idComponente = l.fkComponente WHERE c.tipo = "GPU" AND l.fkServidor = {ipServidor} ORDER BY l.idLeitura DESC LIMIT 1'
                    cursor.execute(leituraL)
                    leituraFkL = cursor.fetchone()
                    fkLeituraLocal = leituraFkL[0]

                    if mediaUsoGpu >= 85:
                        descricao = f"Alerta de Risco. Servidor {ipServidor}: A utilização da GPU esteve constantemente acima de 85%, nas últimas 10 verificação. Pode ocorrer travamentos! Média de utilização: {mediaUsoGpu}%"

                        tipo = "Em risco"

                        insertAlerta = (
                            f"insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values (GETDATE(), '{tipo}', '{descricao}', {fkEmpresa}, {fkDataCenter}, '{ipServidor}', {fkComponente}, {fkLeitura})")
                        cursorServer.execute(insertAlerta)  # executa o script do banco
                        cursorServer.commit()

                        insertAlertaLocal = (
                            f"insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values (now(), '{tipo}', '{descricao}', {fkEmpresaLocal}, {fkDataCenterLocal}, '{ipServidor}', {fkComponenteLocal}, {fkLeituraLocal})")
                        cursor.execute(insertAlertaLocal)  # executa o script do banco
                        MySql.conexao.commit()


                        alerta = {"text": descricao}
                        response = requests.post(webhook_url, json=alerta)

                        logging.critical(
                            f' Usuário do IP {ipUser}, hostName: {hostname}. Teve {descricao}')

                    elif mediaUsoGpu >= 66 and mediaUsoGpu <= 84:
                        descricao = f"Alerta de Cuidado. Servidor {ipServidor}: A utilização da GPU esteve constantemente entre 66% a 84%, nas últimas 10 verificação. Pode ocorrer lentidão! Média de utilização: {mediaUsoGpu}%"

                        tipo = "Cuidado"

                        insertAlerta = (
                            f"insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values (GETDATE(), '{tipo}', '{descricao}', {fkEmpresa}, {fkDataCenter}, '{ipServidor}', {fkComponente}, {fkLeitura})")
                        cursorServer.execute(insertAlerta)  # executa o script do banco
                        cursorServer.commit()

                        insertAlertaLocal = (
                            f"insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values (now(), '{tipo}', '{descricao}', {fkEmpresaLocal}, {fkDataCenterLocal}, '{ipServidor}', {fkComponenteLocal}, {fkLeituraLocal})")
                        cursor.execute(insertAlertaLocal)  # executa o script do banco
                        MySql.conexao.commit()

                        alerta = {"text": descricao}
                        response = requests.post(webhook_url, json=alerta)

                        logging.warning(
                            f' Usuário do IP {ipUser}, hostName: {hostname}. Teve {descricao}')
                    else:
                        descricao = f"Alerta Estável. Servidor {ipServidor}: A utilização da GPU está abaixo 66%, nas últimas 10 verificação. A utilização! Média de utilização: {mediaUsoGpu}%"

                        tipo = 'Estável'

                        insertAlerta = (
                            f"insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values (GETDATE(), '{tipo}', '{descricao}', {fkEmpresa}, {fkDataCenter}, '{ipServidor}', {fkComponente}, {fkLeitura})")
                        cursorServer.execute(insertAlerta)  # executa o script do banco
                        cursorServer.commit()

                        insertAlertaLocal = (
                            f"insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values (now(), '{tipo}', '{descricao}', {fkEmpresaLocal}, {fkDataCenterLocal}, '{ipServidor}', {fkComponenteLocal}, {fkLeituraLocal})")
                        cursor.execute(insertAlertaLocal)  # executa o script do banco
                        MySql.conexao.commit()

                        alerta = {"text": descricao}
                        response = requests.post(webhook_url, json=alerta)


                    if temperaturaGpu > 39:
                        descricao2 = f"Alerta de Risco. Servidor {ipServidor}: A temperatura da GPU está acima de 39°C, nas últimas 10 verificação. Risco de Super Aquecimento! Média de temperatura: {temperaturaGpu}°C"

                        tipo = "Em risco"

                        insertAlerta = (
                            f"insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values (GETDATE(), '{tipo}', '{descricao2}', {fkEmpresa}, {fkDataCenter}, '{ipServidor}', {fkComponente}, {fkLeitura})")
                        cursorServer.execute(insertAlerta)  # executa o script do banco
                        cursorServer.commit()

                        insertAlertaLocal = (
                            f"insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values (now(), '{tipo}', '{descricao2}', {fkEmpresaLocal}, {fkDataCenterLocal}, '{ipServidor}', {fkComponenteLocal}, {fkLeituraLocal})")
                        cursor.execute(insertAlertaLocal)  # executa o script do banco
                        MySql.conexao.commit()

                        alerta = {"text": descricao2}
                        response = requests.post(webhook_url, json=alerta)

                        logging.critical(
                            f' Usuário do IP {ipUser}, hostName: {hostname}. Teve {descricao}')
                    elif temperaturaGpu >= 35 and temperaturaGpu <= 39:
                        descricao2 = f"Alerta de Cuidado. Servidor {ipServidor}: A temperatura da GPU está entre 35°C a 39°C, nas últimas 10 verificação. Pode ocorrer aquecimento! Média de temperatura: {temperaturaGpu}°C"

                        tipo = "Cuidado"

                        insertAlerta = (
                            f"insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values (GETDATE(), '{tipo}', '{descricao2}', {fkEmpresa}, {fkDataCenter}, '{ipServidor}', {fkComponente}, {fkLeitura})")
                        cursorServer.execute(insertAlerta)  # executa o script do banco
                        cursorServer.commit()

                        insertAlertaLocal = (
                            f"insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values (now(), '{tipo}', '{descricao2}', {fkEmpresaLocal}, {fkDataCenterLocal}, '{ipServidor}', {fkComponenteLocal}, {fkLeituraLocal})")
                        cursor.execute(insertAlertaLocal)  # executa o script do banco
                        MySql.conexao.commit()

                        alerta = {"text": descricao2}
                        response = requests.post(webhook_url, json=alerta)

                        logging.critical(
                            f' Usuário do IP {ipUser}, hostName: {hostname}. Teve {descricao}')
                    else:
                        descricao2 = f"Alerta Estável. Servidor {ipServidor}: A temperatura da GPU está abaixo de 35°C, nas últimas 10 verificação. Temperatura está OK! Média de temperatura: {temperaturaGpu}°C"

                        tipo = "Estável"

                        insertAlerta = (
                            f"insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values (GETDATE(), '{tipo}', '{descricao2}', {fkEmpresa}, {fkDataCenter}, '{ipServidor}', {fkComponente}, {fkLeitura})")
                        cursorServer.execute(insertAlerta)  # executa o script do banco
                        cursorServer.commit()

                        insertAlertaLocal = (
                            f"insert into Alerta(dataAlerta, tipo, descricao, fkEmpresa, fkDataCenter, fkServidor, fkComponente, fkLeitura) values (now(), '{tipo}', '{descricao2}', {fkEmpresaLocal}, {fkDataCenterLocal}, '{ipServidor}', {fkComponenteLocal}, {fkLeituraLocal})")
                        cursor.execute(insertAlertaLocal)  # executa o script do banco
                        MySql.conexao.commit()

                        alerta = {"text": descricao2}
                        response = requests.post(webhook_url, json=alerta)

                    time.sleep(10)

            elif opcao == 3:
                print("Saindo...")
                break
            else:
                print('Número Inválido!')

                cursor.close()
                MySql.conexao.close()
