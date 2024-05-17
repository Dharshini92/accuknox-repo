import requests
import json

# Vault configuration
vault_url = 'https://vault.accuknox.com:8200'
token = "hvs.CAESIFGzcrnd31QBXhQFLG6pu0wIoW_OuSyLaNsWIXcGh2U2Gh4KHGh2cy43MURuN2YxaklrYjk2d3FIQWlnMDd2M2o"
source_engine = 'vault-hello-test'
destination_engine = 'vault-hello-test1'

# Headers for Vault API requests
headers = {
    'X-Vault-Token': token
}

def list_secrets(engine):
    """List all secrets in the given secret engine."""
    url = f"{vault_url}/v1/{engine}/metadata?list=true"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    try:
        return response.json().get('data', {}).get('keys', [])
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from {url}: {e}")
        return []

def read_secret(engine, secret_path):
    """Read a secret from the given secret engine."""
    url = f"{vault_url}/v1/{engine}/data/{secret_path}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    try:
        return response.json().get('data', {}).get('data', {})
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from {url}: {e}")
        return {}

def write_secret(engine, secret_path, secret_data):
    """Write a secret to the given secret engine."""
    url = f"{vault_url}/v1/{engine}/data/{secret_path}"
    data = {
        'data': secret_data
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    try:
        response.json()
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from {url}: {e}")

def migrate_secrets(source_engine, destination_engine):
    """Migrate secrets from source_engine to destination_engine."""
    try:
        secrets = list_secrets(source_engine)
        if not secrets:
            print("No secrets found or failed to list secrets.")
            return
        for secret in secrets:
            # Handle directory paths by recursively listing and migrating them
            if secret.endswith('/'):
                sub_secrets = list_secrets(f"{source_engine}/{secret}")
                for sub_secret in sub_secrets:
                    secret_path = f"{secret}{sub_secret}"
                    secret_data = read_secret(source_engine, secret_path)
                    if secret_data:
                        write_secret(destination_engine, secret_path, secret_data)
                        print(f"Successfully migrated secret: {secret_path}")
                    else:
                        print(f"Failed to read secret: {secret_path}")
            else:
                secret_data = read_secret(source_engine, secret)
                if secret_data:
                    write_secret(destination_engine, secret, secret_data)
                    print(f"Successfully migrated secret: {secret}")
                else:
                    print(f"Failed to read secret: {secret}")
    except requests.RequestException as e:
        print(f"HTTP request error: {e}")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == '__main__':
    migrate_secrets(source_engine, destination_engine)
