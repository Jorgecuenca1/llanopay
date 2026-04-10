"""Create superuser and test data on server, verify HTTPS."""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('159.223.164.118', username='root', password='thanosoft1A.a')

# Create init script on server
init_script = """
import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'llanopay_project.settings'
django.setup()
from apps.accounts.models import User
from apps.wallet.models import Wallet

if not User.objects.filter(phone_number='+573001234567').exists():
    u = User.objects.create_superuser(phone_number='+573001234567', password='admin1234', first_name='Admin', last_name='NovaPay')
    Wallet.objects.get_or_create(user=u, defaults={'balance_cop': 10000000, 'balance_llo': 500})
    print('Admin created')
else:
    print('Admin exists')

if not User.objects.filter(phone_number='+573009876543').exists():
    u2 = User.objects.create_user(phone_number='+573009876543', password='test1234', first_name='Juan', last_name='Llanero')
    u2.is_verified = True
    u2.document_type = 'CC'
    u2.document_number = '1234567890'
    u2.save()
    Wallet.objects.get_or_create(user=u2, defaults={'balance_cop': 5000000, 'balance_llo': 100})
    print('Test user created')
else:
    print('Test user exists')
"""

# Write script to server
sftp = ssh.open_sftp()
with sftp.open('/opt/novapay/init_data.py', 'w') as f:
    f.write(init_script)
sftp.close()

# Execute inside container
stdin, stdout, stderr = ssh.exec_command(
    'docker exec novapay_backend python /code-backend/init_data.py',
    timeout=30
)
print('Init data:', stdout.read().decode().strip())
err = stderr.read().decode().strip()
if err:
    print('Errors:', err[:500])

# Check HTTPS
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" -k https://nova.jorgecuenca.com/app/',
    timeout=15
)
print('HTTPS status:', stdout.read().decode().strip())

# Check HTTP
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8005/app/',
    timeout=10
)
print('Backend status:', stdout.read().decode().strip())

ssh.close()
print('Done!')
