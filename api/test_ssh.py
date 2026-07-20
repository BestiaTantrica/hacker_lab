import paramiko
try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname='129.80.73.248', username='ubuntu', key_filename='/home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/llave_oci', timeout=5)
    stdin, stdout, stderr = client.exec_command('ls -la /home/ubuntu/plataforma_operativa/resultados/')
    print('--- RESULTADOS OCI-1 ---')
    print(stdout.read().decode())
except Exception as e:
    print('Error SSH:', e)
