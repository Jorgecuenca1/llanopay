import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('159.223.164.118', username='root', password='thanosoft1A.a')

script = """
import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'llanopay_project.settings'
django.setup()
from apps.accounts.models import User
from apps.wallet.models import Wallet
from decimal import Decimal

# Reset/create admin
try:
    u = User.objects.get(phone_number='+573001234567')
    u.set_password('admin1234')
    u.is_staff = True
    u.is_superuser = True
    u.is_verified = True
    u.save()
    print('Admin password reset')
except User.DoesNotExist:
    u = User.objects.create_superuser(phone_number='+573001234567', password='admin1234', first_name='Admin', last_name='NovaPay')
    print('Admin created')
w, _ = Wallet.objects.get_or_create(user=u)
w.balance_cop = Decimal('10000000')
w.balance_llo = Decimal('500')
w.save()

# Reset/create test user
try:
    u2 = User.objects.get(phone_number='+573009876543')
    u2.set_password('test1234')
    u2.is_verified = True
    u2.save()
    print('Test user password reset')
except User.DoesNotExist:
    u2 = User.objects.create_user(phone_number='+573009876543', password='test1234', first_name='Juan', last_name='Llanero')
    u2.is_verified = True
    u2.document_type = 'CC'
    u2.document_number = '1234567890'
    u2.save()
    print('Test user created')
w2, _ = Wallet.objects.get_or_create(user=u2)
w2.balance_cop = Decimal('5000000')
w2.balance_llo = Decimal('100')
w2.save()

for u in User.objects.all():
    print(f'  {u.phone_number} staff={u.is_staff} verified={u.is_verified} has_pw={u.has_usable_password()}')
"""

sftp = ssh.open_sftp()
with sftp.open('/opt/novapay/setup_users.py', 'w') as f:
    f.write(script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('docker exec novapay_backend python /code-backend/setup_users.py', timeout=20)
print(stdout.read().decode().strip())
err = stderr.read().decode().strip()
if err:
    print('ERR:', err[:500])

# Test login
stdin, stdout, stderr = ssh.exec_command(
    """curl -s -X POST http://127.0.0.1:8005/api/v1/auth/login/ -H 'Content-Type: application/json' -d '{"phone_number":"+573009876543","password":"test1234"}'""",
    timeout=10)
resp = stdout.read().decode().strip()
print(f'Login test: {resp[:100]}')

# Test web
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -o /dev/null -w "%{http_code}" https://nova.jorgecuenca.com/app/', timeout=10)
print(f'Web: {stdout.read().decode().strip()}')

ssh.close()
print('DONE')
