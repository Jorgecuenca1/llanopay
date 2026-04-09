"""
Deploy NovaPay to production server via SSH + SFTP (paramiko).
Uploads project files directly, then runs docker-compose.
Server: 159.223.164.118  Domain: nova.jorgecuenca.com
"""
import paramiko
import os
import time
import stat

HOST = '159.223.164.118'
USER = 'root'
PASSWORD = 'thanosoft1A.a'
DOMAIN = 'nova.jorgecuenca.com'
PROJECT_DIR = '/opt/novapay'
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

# Files/dirs to upload (relative to project root)
UPLOAD_DIRS = ['apps', 'llanopay_project', 'templates', 'static']
UPLOAD_FILES = [
    'manage.py', 'requirements.txt', 'Dockerfile',
    'docker-compose.yml', '.env.example',
]


def ssh_exec(ssh, cmd, timeout=300):
    """Execute a command via SSH and return output."""
    print(f"  > {cmd[:150]}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    if out.strip():
        for line in out.strip().split('\n')[:20]:
            print(f"    {line}")
    if err.strip() and exit_code != 0:
        for line in err.strip().split('\n')[:10]:
            print(f"    [WARN] {line}")
    return out, err, exit_code


def sftp_upload_dir(sftp, local_path, remote_path):
    """Recursively upload a directory via SFTP."""
    try:
        sftp.stat(remote_path)
    except FileNotFoundError:
        sftp.mkdir(remote_path)

    for item in os.listdir(local_path):
        local_item = os.path.join(local_path, item)
        remote_item = remote_path + '/' + item

        # Skip pycache, .venv, .git, .idea, __pycache__, node_modules, build
        if item in ('__pycache__', '.venv', '.git', '.idea', 'node_modules',
                     'build', '.dart_tool', 'flutter_app', 'db.sqlite3',
                     '.env', '*.pyc', '*.pdf'):
            continue
        if item.endswith('.pyc') or item.endswith('.pdf'):
            continue

        if os.path.isdir(local_item):
            sftp_upload_dir(sftp, local_item, remote_item)
        else:
            print(f"    Uploading: {remote_item}")
            sftp.put(local_item, remote_item)


def deploy():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    print("Connected!\n")

    # 1. Install Docker if not present
    print("=" * 60)
    print("STEP 1: Ensuring Docker is installed")
    print("=" * 60)
    _, _, code = ssh_exec(ssh, 'docker --version')
    if code != 0:
        print("  Installing Docker...")
        ssh_exec(ssh, 'apt-get update -qq && apt-get install -y -qq docker.io docker-compose', timeout=300)
        ssh_exec(ssh, 'systemctl enable docker && systemctl start docker')
    else:
        print("  Docker already installed")

    # Ensure docker-compose
    _, _, code = ssh_exec(ssh, 'docker-compose --version')
    if code != 0:
        ssh_exec(ssh, 'apt-get install -y -qq docker-compose', timeout=120)

    # 2. Upload project files
    print("\n" + "=" * 60)
    print("STEP 2: Uploading project files")
    print("=" * 60)
    ssh_exec(ssh, f'mkdir -p {PROJECT_DIR}')

    sftp = ssh.open_sftp()

    # Upload single files
    for f in UPLOAD_FILES:
        local_f = os.path.join(LOCAL_DIR, f)
        if os.path.exists(local_f):
            remote_f = f'{PROJECT_DIR}/{f}'
            print(f"    Uploading: {remote_f}")
            sftp.put(local_f, remote_f)

    # Upload directories
    for d in UPLOAD_DIRS:
        local_d = os.path.join(LOCAL_DIR, d)
        if os.path.isdir(local_d):
            print(f"  Uploading directory: {d}/")
            sftp_upload_dir(sftp, local_d, f'{PROJECT_DIR}/{d}')

    sftp.close()
    print("  Upload complete!")

    # 3. Stop existing containers
    print("\n" + "=" * 60)
    print("STEP 3: Stopping existing containers (if any)")
    print("=" * 60)
    ssh_exec(ssh, f'cd {PROJECT_DIR} && docker-compose down 2>/dev/null || true')
    # Also stop any conflicting containers on ports 80/443
    ssh_exec(ssh, 'docker stop novapay_https novapay_backend 2>/dev/null || true')
    ssh_exec(ssh, 'docker rm novapay_https novapay_backend 2>/dev/null || true')

    # 4. Build and start
    print("\n" + "=" * 60)
    print("STEP 4: Building and starting containers")
    print("=" * 60)
    ssh_exec(ssh, f'cd {PROJECT_DIR} && docker-compose build 2>&1', timeout=600)
    print("  Build complete. Starting services...")
    ssh_exec(ssh, f'cd {PROJECT_DIR} && docker-compose up -d 2>&1', timeout=120)

    print("\n  Waiting for services to initialize (20s)...")
    time.sleep(20)

    # 5. Check status
    print("\n" + "=" * 60)
    print("STEP 5: Checking container status")
    print("=" * 60)
    ssh_exec(ssh, f'cd {PROJECT_DIR} && docker-compose ps')
    ssh_exec(ssh, 'docker logs novapay_backend --tail 30 2>&1')

    # 6. Create superuser + test data
    print("\n" + "=" * 60)
    print("STEP 6: Creating superuser and test data")
    print("=" * 60)
    create_data = r'''
import django, os
os.environ["DJANGO_SETTINGS_MODULE"] = "llanopay_project.settings"
django.setup()
from apps.accounts.models import User
from apps.wallet.models import Wallet
# Superuser / admin
if not User.objects.filter(phone_number="+573001234567").exists():
    u = User.objects.create_superuser(phone_number="+573001234567", password="admin1234", first_name="Admin", last_name="NovaPay")
    Wallet.objects.get_or_create(user=u, defaults={"balance_cop": 10000000, "balance_llo": 500})
    print("Admin created")
else:
    print("Admin exists")
# Test user
if not User.objects.filter(phone_number="+573009876543").exists():
    u2 = User.objects.create_user(phone_number="+573009876543", password="test1234", first_name="Juan", last_name="Llanero")
    u2.is_verified = True
    u2.document_type = "CC"
    u2.document_number = "1234567890"
    u2.save()
    Wallet.objects.get_or_create(user=u2, defaults={"balance_cop": 5000000, "balance_llo": 100})
    print("Test user created")
else:
    print("Test user exists")
'''
    ssh_exec(ssh, f'''docker exec novapay_backend python -c "{create_data.strip()}"''')

    # 7. Verify
    print("\n" + "=" * 60)
    print("STEP 7: Final verification")
    print("=" * 60)
    ssh_exec(ssh, 'curl -s -o /dev/null -w "Backend: %{http_code}\\n" http://127.0.0.1:8005/app/')
    ssh_exec(ssh, f'curl -s -o /dev/null -w "HTTPS: %{{http_code}}\\n" -k https://{DOMAIN}/ 2>/dev/null || echo "HTTPS portal initializing (1-2 min for SSL cert)..."')

    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print(f"""
    Web Platform:     https://{DOMAIN}/app/
    Admin Dashboard:  https://{DOMAIN}/dashboard/
    API Docs:         https://{DOMAIN}/api/docs/

    Admin Login:      +573001234567 / admin1234
    Test User:        +573009876543 / test1234

    Note: SSL cert takes 1-2 min to provision on first deploy.
    """)

    ssh.close()


if __name__ == '__main__':
    deploy()
