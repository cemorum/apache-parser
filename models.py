from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
Base = declarative_base()
engine = create_engine('mysql+pymysql://username:password@host/database_name')
Session = sessionmaker(bind=engine)
session = Session()
class LogEntry(Base):
    __tablename__ = 'log_entries'

    id = Column(Integer, primary_key=True)
    ip = Column(String(15))  
    identity = Column(String(50))  
    user = Column(String(50))
    time = Column(DateTime)
    request = Column(String(500))
    status = Column(String(3))
    size = Column(Integer)
    referer = Column(String(500))
    user_agent = Column(String(500))

    def __repr__(self):
        return f"<LogEntry(ip='{self.ip}', time='{self.time}', request='{self.request}')>"
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
        

