#!/usr/bin/env python3
"""
Автоматическое исправление подключения WSL → Windows PostgreSQL
Запускать из WSL при проблемах с подключением
"""

import subprocess
import sys
import os
import re

def run_wsl(cmd, shell=True):
    """Выполнить команду в WSL"""
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def run_powershell(cmd):
    """Выполнить команду в PowerShell (админ) через wsl.exe"""
    full_cmd = f'powershell.exe -Command "{cmd}"'
    return run_wsl(full_cmd)

def get_wsl_gateway():
    """Получить WSL gateway IP"""
    stdout, _, _ = run_wsl("ip route | grep default | awk '{print $3}'")
    return stdout.strip()

def test_postgres_connection(host, port=5432, timeout=5):
    """Проверить подключение к PostgreSQL"""
    test_script = f'''
import psycopg2
conn = psycopg2.connect(host="{host}", port={port}, dbname="finam_predictor", user="postgres", password="1289", connect_timeout={timeout})
print("OK")
conn.close()
'''
    stdout, stderr, code = run_wsl(f'python3 -c "{test_script}"')
    return code == 0 and "OK" in stdout

def fix_hyperv_firewall():
    """Отключить Hyper-V firewall"""
    print("🔧 Отключение Hyper-V firewall...")
    stdout, stderr, code = run_powershell(
        "Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -Enabled False"
    )
    if code == 0:
        print("✅ Hyper-V firewall отключен")
        return True
    else:
        print(f"❌ Ошибка: {stderr}")
        return False

def fix_port_proxy():
    """Настроить port proxy"""
    print("🔧 Настройка port proxy...")
    # Удалить старое
    run_powershell("netsh interface portproxy delete v4tov4 listenport=5432")
    # Создать новое
    stdout, stderr, code = run_powershell(
        "netsh interface portproxy add v4tov4 listenport=5432 listenaddress=0.0.0.0 connectport=5432 connectaddress=127.0.0.1"
    )
    if code == 0:
        print("✅ Port proxy настроен")
        return True
    else:
        print(f"❌ Ошибка: {stderr}")
        return False

def update_env_file(host):
    """Обновить .env файл"""
    env_path = ".env"
    if not os.path.exists(env_path):
        print(f"⚠️ Файл {env_path} не найден")
        return False
    
    with open(env_path, "r") as f:
        content = f.read()
    
    # Обновить DB_HOST
    new_content = re.sub(r"DB_HOST=.*", f"DB_HOST={host}", content)
    
    with open(env_path, "w") as f:
        f.write(new_content)
    
    print(f"✅ .env обновлен: DB_HOST={host}")
    return True

def main():
    print("=" * 60)
    print("🔧 Диагностика WSL → Windows PostgreSQL")
    print("=" * 60)
    
    # 1. Получить WSL gateway
    gateway = get_wsl_gateway()
    print(f"📡 WSL Gateway IP: {gateway}")
    
    # 2. Проверить подключение
    print(f"\n🔍 Проверка подключения к {gateway}:5432...")
    if test_postgres_connection(gateway):
        print("✅ Подключение работает! Ничего делать не нужно.")
        return 0
    
    print("❌ Подключение не работает. Запускаю исправление...")
    
    # 3. Проверить WSL PostgreSQL
    stdout, _, _ = run_wsl("sudo service postgresql status 2>/dev/null || echo 'inactive'")
    if "active" in stdout:
        print("⚠️ WSL PostgreSQL запущен! Останавливаю...")
        run_wsl("sudo service postgresql stop")
        run_wsl("sudo systemctl disable postgresql")
        print("✅ WSL PostgreSQL остановлен и отключен")
    
    # 4. Отключить Hyper-V firewall
    fix_hyperv_firewall()
    
    # 5. Настроить port proxy
    fix_port_proxy()
    
    # 6. Обновить .env
    update_env_file(gateway)
    
    # 7. Проверить снова
    print(f"\n🔍 Повторная проверка подключения к {gateway}:5432...")
    if test_postgres_connection(gateway):
        print("✅ Подключение восстановлено!")
        return 0
    else:
        print("❌ Подключение всё ещё не работает.")
        print("\n💡 Дополнительные шаги:")
        print("   1. Убедитесь что Windows PostgreSQL запущен:")
        print("      PowerShell: Get-Service postgresql-x64-17")
        print("   2. Проверьте pg_hba.conf:")
        print('      code "C:\\Program Files\\PostgreSQL\\17\\data\\pg_hba.conf"')
        print("   3. Добавьте: host all all 0.0.0.0/0 scram-sha-256")
        return 1

if __name__ == "__main__":
    sys.exit(main())