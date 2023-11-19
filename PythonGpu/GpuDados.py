import mysql.connector
import GPUtil
from datetime import datetime
import time

conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    password='sptech',
    database='performee',
)

tentativas = 4

cursor = conexao.cursor()
for tentativa in range(tentativas, 0, -1):
    ipServidor = input('Digite o IP do Servidor: ')

    buscaIp = f'select count(*) from servidor where ipServidor = "{ipServidor}"'
    cursor.execute(buscaIp)
    resultado = cursor.fetchone()  # ler o banco de dados
    valorResult = resultado[0]

    if valorResult == 0:
        print('Servidor Não encontrado!')
        tentativas -= 1
        print(f'Você tem {tentativas} tentativas!'.format(tentativas))

    else:
        print("Servidor Encontrado!")
        while True:
            buscarEmp = f'select fkEmpresa from servidor where ipServidor = "{ipServidor}"'
            cursor.execute(buscarEmp)
            empresa = cursor.fetchone()  # ler o banco de dados
            fkEmpresa = empresa[0]

            buscarDc = f'select fkDataCenter from servidor where ipServidor = "{ipServidor}"'
            cursor.execute(buscarDc)
            dataCenter = cursor.fetchone()  # ler o banco de dados
            fkDataCenter = dataCenter[0]

            print('O que deseja?')
            print('1 Cadastrar GPU')
            print('2 Inserir Leitura')
            print('3 Sair')
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
                else:
                    print("GPU desse servidor já cadastrado")


            elif opcao == 2:
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
                    time.sleep(15)

            elif opcao == 3:
                print("Saindo...")
                break
            else:
                print('Número Inválido!')



                cursor.close()
                conexao.close()
