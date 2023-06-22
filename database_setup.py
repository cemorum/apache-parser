from sqlalchemy import create_engine
from config_manager import ConfigManager
from models import Base


config = ConfigManager('config.ini')
database_uri = config.get_database_uri()

engine = create_engine(database_uri)

Base.metadata.create_all(engine)
