from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QInputDialog, QLabel, QWidget, QTextEdit, QMainWindow, QMessageBox, QCheckBox
from config_manager import ConfigManager
from log_parser import  parse_log_line
from models import Base, LogEntry
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import sys
from sqlalchemy import func
from PyQt5.QtWidgets import QDateEdit, QCalendarWidget
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QDateEdit
from PyQt5.QtCore import QDate
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog
from datetime import datetime, timedelta
from pytz import timezone
import subprocess
from sqlalchemy.exc import SQLAlchemyError
import os
class LogViewerApp(QMainWindow):
    def __init__(self, session, config_manager):
        super().__init__()
        self.session = session
        self.config_manager = config_manager
        self.setWindowTitle("Log Viewer")
        self.setGeometry(300, 300, 1000, 600)

        self.log_display = QTextEdit(self)
        self.log_display.setGeometry(20, 100, 1000, 600)

        self.show_logs_button = QPushButton("Show Logs", self)
        self.show_logs_button.move(20, 20)
        self.show_logs_button.clicked.connect(self.show_log)

        self.group_by_ip_checkbox = QCheckBox("IP", self)
        self.group_by_ip_checkbox.move(120, 20)
        self.group_by_ip_checkbox.resize(150, 20) 

        self.group_by_date_checkbox = QCheckBox("Date", self)
        self.group_by_date_checkbox.move(220, 20)
        self.group_by_date_checkbox.resize(150, 20)  

        self.group_by_date_range_checkbox = QCheckBox("Date Range", self)
        self.group_by_date_range_checkbox.move(320, 20)
        self.group_by_date_range_checkbox.resize(200, 20)


        self.parse_button = QPushButton("Parse",self)
        self.parse_button.move(520, 20)
        self.parse_button.clicked.connect(self.parse_log)


        self.filter_button = QPushButton("Filter", self)
        self.filter_button.move(620, 20)
        self.filter_button.clicked.connect(self.filter)

        self.cron_button = QPushButton("Cron", self)
        self.cron_button.move(720, 20)
        self.cron_button.clicked.connect(self.schedule_task)

    
       




    

    def filter(self):
        result_texts = []
        if self.group_by_ip_checkbox.isChecked():
            result_texts.append(self.group_by_ip())
        if self.group_by_date_checkbox.isChecked():
            result_texts.append(self.group_by_date())
        if self.group_by_date_range_checkbox.isChecked():
            result_texts.append(self.group_by_date_range())
        
            
        result_text = "\n\n".join(result_texts)
        self.log_display.setText(result_text)
        
    
    def schedule_task(self):
        time, okPressed = QInputDialog.getText(self, "Введите времяч", "Формат: ЧЧ:ММ")
        if okPressed:
         try:
                datetime.strptime(time, '%H:%M')  
                script_path = r"C:/Путь/к/вашему/файлу/log_parser.py"  # Здесь укажите путь к скрипту, который будет выполяться каждый день
                task_name = "MyTask"  # Название задачи
                command = f'schtasks /Create /SC DAILY /TN {task_name} /TR "python {script_path}" /ST {time}'
                subprocess.call(command, shell=True)
         except  ValueError:
            QMessageBox.critical(self, "Input Error", "Invalid time format!")
    
    def parse_log(self):
        try:
            log_file_path = self.config_manager.get_log_file_path()
            if not os.path.exists(log_file_path):
                QMessageBox.critical(self, "File Error", f"Log file {log_file_path} does not exist.")
                return
            
            with open(log_file_path, "r") as f:
                for line in f:
                    log_entry_dict = parse_log_line(line)
                    if log_entry_dict:
                        log_entry = LogEntry(**log_entry_dict)
                        self.session.add(log_entry)
                self.session.commit()
            self.log_display.setText("Log file parsed and inserted to database successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", "An unexpected error occurred: " + str(e))

    def show_log(self):
        try:
            log_entry = self.session.query(LogEntry).all()
            log_text = ""
            for log in log_entry:
              log_text += f"ID: {log.id}, IP: {log.ip}, Identity: {log.identity}, User: {log.user}, Time: {log.time}, Request: {log.request}, Status: {log.status}, Size: {log.size}, Referer: {log.referer}, User Agent: {log.user_agent}\n"
            self.log_display.setText(log_text)
        except SQLAlchemyError as e:
            self.session.rollback()
            QMessageBox.critical(self, "Database Error", "A database error occurred: " + str(e))
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", "An unexpected error occurred: " + str(e))
       
    
    def group_by_ip(self):
        logs = self.session.query(LogEntry.ip, func.count(LogEntry.ip)).group_by(LogEntry.ip).all()
        return "\n".join(f"IP: {log[0]}, Count: {log[1]}" for log in logs)

    def group_by_date(self):
        logs = self.session.query(func.date(LogEntry.time), func.count(func.date(LogEntry.time))).group_by(func.date(LogEntry.time)).all()
        return "\n".join(f"Date: {log[0]}, Count: {log[1]}" for log in logs)

    def group_by_date_range(self):
        start_date_str, okPressed1 = QInputDialog.getText(self, "Input Start Date", "Format: YYYY-MM-DD")
        end_date_str, okPressed2 = QInputDialog.getText(self, "Input End Date", "Format: YYYY-MM-DD")

        if okPressed1 and okPressed2:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            
                local_tz = timezone('Etc/GMT+7')  
                start_date = local_tz.localize(start_date).astimezone(timezone('Etc/GMT-7'))
                end_date = local_tz.localize(end_date + timedelta(days=1)).astimezone(timezone('Etc/GMT-7')) 

                logs = (self.session.query(LogEntry)
                       .filter(LogEntry.time.between(start_date, end_date))
                       .order_by(LogEntry.time).all())
            
                result_text = f"Logs between {start_date_str} and {end_date_str}:\n"
                for log in logs:
                 result_text += f"ID: {log.id}, IP: {log.ip}, Identity: {log.identity}, User: {log.user}, Time: {log.time}, Request: {log.request}, Status: {log.status}, Size: {log.size}, Referer: {log.referer}, User Agent: {log.user_agent}\n"
            
                return result_text

            except ValueError:
             QMessageBox.critical(self, "Input Error", "Invalid date format!")
        else:
            QMessageBox.critical(self, "Input Error", "Invalid date format!")
        return ""

def setup_database(config_manager):
    try:
        database_uri = config_manager.get_database_url()
        engine = create_engine(database_uri)
        Base.metadata.create_all(engine)
    except SQLAlchemyError as e:
        QMessageBox.critical(None, "Database Error", "A database error occurred: " + str(e))
    except Exception as e:
        QMessageBox.critical(None, "Unexpected Error", "An unexpected error occurred: " + str(e))

    
    
def main():
    app = QApplication(sys.argv)
    config_manager = ConfigManager("config.json")
    db_url = config_manager.get_database_url()

    setup_database(config_manager)
    
    try:
        engine = create_engine(db_url)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        viewer = LogViewerApp(session, config_manager)
        viewer.show()
    except SQLAlchemyError as e:
        QMessageBox.critical(None, "Database Error", "A database error occurred: " + str(e))
        return
    except Exception as e:
        QMessageBox.critical(None, "Unexpected Error", "An unexpected error occurred: " + str(e))

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
