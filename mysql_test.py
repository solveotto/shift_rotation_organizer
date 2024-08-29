import MySQLdb
import sshtunnel

sshtunnel.SSH_TIMEOUT = 10.0
sshtunnel.TUNNEL_TIMEOUT = 10.0

with sshtunnel.SSHTunnelForwarder(
    ('ssh.pythonanywhere.com'),
    ssh_username='solveottooren', ssh_password='UckBaGAO489v',
    remote_bind_address=('solveottooren.mysql.pythonanywhere-services.com', 3306)
) as tunnel:
    connection = MySQLdb.connect(
        user='solveottooren',
        passwd='MFW.dct7rbk3xkj5zmv',
        host='127.0.0.1', port=tunnel.local_bind_port,
        db='solveottooren$turnuser',
    )
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM points;")
    
    tables = cursor.fetchall()
    for table in tables:
        print(table[0])
    


    cursor = connection.cursor()
    cursor.execute("SELECT * FROM points;")
    
    tables = cursor.fetchall()
    for table in tables:
        print(table[0])
    
    cursor.close()



    connection.close()