import requests
import os


def main():
    base_settings_dir = '/etc/rspet/'
    if not os.path.exists(base_settings_dir):
        os.makedirs(base_settings_dir)

    plugin_dir = os.path.join(base_settings_dir, 'plugins')
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir)

    client_plugin_dir = os.path.join(plugin_dir, 'client')
    if not os.path.exists(client_plugin_dir):
        os.makedirs(client_plugin_dir)

    conf = requests.get('https://rspet.github.io/config.json')
    with open(("/etc/rspet/config.json"), 'w') as cfile:
        cfile.write(conf.text)

    os.chmod(base_settings_dir, 0o777)
    for root, dirs, files in os.walk(base_settings_dir):
        for momo in dirs:
            os.chmod(os.path.join(root, momo), 0o777)
        for momo in files:
            os.chmod(os.path.join(root, momo), 0o666)

    log_dir = '/var/log/rspet/'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    os.chmod(log_dir, 0o777)
