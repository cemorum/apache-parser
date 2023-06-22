import configparser
import json

class ConfigManager:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = json.load(f)

    def get_database_url(self):
        db_config = self.config['database']
        return f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['name']}"

    def get_log_file_path(self):
        return self.config['log_file_path']
    
