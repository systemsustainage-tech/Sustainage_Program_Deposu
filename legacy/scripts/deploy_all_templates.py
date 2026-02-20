import paramiko
import os

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'
remote_base = '/var/www/sustainage'

files_to_deploy = [
    ('c:/SUSTAINAGESERVER/web_app.py', 'web_app.py'),
    ('c:/SUSTAINAGESERVER/templates/carbon.html', 'templates/carbon.html'),
    ('c:/SUSTAINAGESERVER/templates/energy.html', 'templates/energy.html'),
    ('c:/SUSTAINAGESERVER/templates/waste.html', 'templates/waste.html'),
    ('c:/SUSTAINAGESERVER/templates/water.html', 'templates/water.html'),
    ('c:/SUSTAINAGESERVER/templates/biodiversity.html', 'templates/biodiversity.html'),
    ('c:/SUSTAINAGESERVER/templates/sdg.html', 'templates/sdg.html'),
    ('c:/SUSTAINAGESERVER/templates/gri.html', 'templates/gri.html'),
    ('c:/SUSTAINAGESERVER/templates/social.html', 'templates/social.html'),
    ('c:/SUSTAINAGESERVER/templates/governance.html', 'templates/governance.html'),
    ('c:/SUSTAINAGESERVER/templates/governance_edit.html', 'templates/governance_edit.html'),
    ('c:/SUSTAINAGESERVER/templates/csrd.html', 'templates/csrd.html'),
    ('c:/SUSTAINAGESERVER/templates/taxonomy.html', 'templates/taxonomy.html'),
    ('c:/SUSTAINAGESERVER/templates/taxonomy_edit.html', 'templates/taxonomy_edit.html'),
    ('c:/SUSTAINAGESERVER/templates/economic.html', 'templates/economic.html'),
    ('c:/SUSTAINAGESERVER/templates/issb.html', 'templates/issb.html'),
    ('c:/SUSTAINAGESERVER/templates/iirc.html', 'templates/iirc.html'),
    ('c:/SUSTAINAGESERVER/templates/tcfd.html', 'templates/tcfd.html'),
    ('c:/SUSTAINAGESERVER/templates/tnfd.html', 'templates/tnfd.html'),
    ('c:/SUSTAINAGESERVER/templates/supply_chain.html', 'templates/supply_chain.html'),
    ('c:/SUSTAINAGESERVER/templates/esg.html', 'templates/esg.html'),
    ('c:/SUSTAINAGESERVER/templates/cbam.html', 'templates/cbam.html'),
    ('c:/SUSTAINAGESERVER/templates/cdp.html', 'templates/cdp.html')
]

def deploy():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, username=username, password=password)
        sftp = ssh.open_sftp()
        
        for local_path, remote_rel_path in files_to_deploy:
            remote_path = f"{remote_base}/{remote_rel_path}"
            print(f"Uploading {local_path} to {remote_path}...")
            try:
                sftp.put(local_path, remote_path)
                print("Success.")
            except Exception as e:
                print(f"Failed to upload {local_path}: {e}")
        
        print("Restarting sustainage.service...")
        stdin, stdout, stderr = ssh.exec_command('systemctl restart sustainage.service')
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("Deploy complete.")
        sftp.close()
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == '__main__':
    deploy()
