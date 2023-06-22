import re
from datetime import datetime
from sqlalchemy.orm import Session, sessionmaker
from models import LogEntry, Base
from sqlalchemy import create_engine
from config_manager import ConfigManager
import pytz
log_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - (.*?) \[(.*?)\] "(.*?)" (\d{3}) (\d*|-) "(.*?)" "(.*?)"'
log_line_regex = re.compile(log_pattern)




timestamp_format = "%d/%b/%Y:%H:%M:%S %z"

def insert_log_entry(log_entry, session):
    log_entry_model = LogEntry(
        ip=log_entry["ip"],
        identity=log_entry["identity"],
        time=log_entry["time"],
        request=log_entry["request"],
        status=log_entry["status"],
        size=log_entry["size"],
        referer=log_entry["referer"],
        user_agent=log_entry["user_agent"],
    )
    session.add(log_entry_model)
    session.commit()








def parse_log_line(line):
    match = log_line_regex.match(line)
    if match is None:
        return None

    ip, identity, timestamp_str, request, status, size_str, referer, user_agent = match.groups()
    timestamp = datetime.strptime(timestamp_str, timestamp_format)
    timestamp = timestamp.astimezone(pytz.timezone('US/Pacific'))

    timestamp = datetime.strptime(timestamp_str, timestamp_format)
    size = int(size_str) if size_str != "-" else 0

    return {
        "ip": ip,
        "identity": identity,
        "time": timestamp,
        "request": request,
        "status": status,
        "size": size,
        "referer": referer,
        "user_agent": user_agent,
    }





with open("access.log", "r") as f:
    for line in f:
        log_entry = parse_log_line(line)
        print(log_entry)


if __name__ == "__main__":
    config_manager = ConfigManager("config.json")
    db_url = config_manager.get_database_url()
    engine = create_engine(db_url)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    log_file_path = config_manager.get_log_file_path()
    parse_log_line(log_file_path, session)
