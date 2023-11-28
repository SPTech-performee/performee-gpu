import pyodbc

# Configuração da conexão
server = '3.215.254.176'
database = 'model'
username = 'cruduser'
password = 'UsuarioCrud@12345'
driver = '{SQL Server}'  # Certifique-se de ter o driver apropriado instalado

# Cadeia de conexão
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Conectar ao SQL Server
try:
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()

except pyodbc.Error as ex:
    print(f"Erro de conexão: {ex}")
