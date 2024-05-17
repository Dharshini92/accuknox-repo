import hvac
import time

vault = hvac.Client(
    url='https://vault.accuknox.com:8200/',
    token='YOUR_VAULT_TOKEN'
)

def read_secret(vault, secret_path):
    read_response = vault.secrets.kv.v2.read_secret_version(
        path=secret_path,
        mount_point='vault-hello-test',
        raise_on_deleted_version=True
    )
    secret_value = read_response['data']['data']
    return secret_value

def write_secret(vault, secret_path, secret_value):
    try:
        # Write the secret to the destination path/engine
        vault.secrets.kv.v2.create_or_update_secret(
            path=secret_path,
            mount_point='vault-hello-test1',
            secret=secret_value
        )
        print("Secret migrated successfully - ", secret_path)
    except Exception as e:
        print("Some error occurred in writing secret", e)

def migrate_secrets():
    # Retrieve all secrets from the old path/engine
    secret_paths = vault.secrets.kv.v2.list_secrets(
        path="/",
        mount_point='vault-hello-test'
    )['data']['keys']
    
    for secret_path in secret_paths:
        secret_value = read_secret(vault, secret_path)
        write_secret(vault, secret_path, secret_value)

def monitor_and_migrate():
    while True:
        migrate_secrets()
        time.sleep(60)  # Check every 60 seconds

# Start monitoring and migrating secrets
monitor_and_migrate()
