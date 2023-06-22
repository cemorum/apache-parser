from flask import Flask, request, jsonify
from models import LogEntry, session
from sqlalchemy import func
from datetime import datetime

app = Flask(__name__)

@app.route('/logs', methods=['GET'])
def get_logs():
    api_key = request.headers.get('x-api-key')

    if api_key != '12345iii':
        return jsonify({'error': 'Invalid API key'}), 403

    group_by_ip = request.args.get('group_by_ip')
    group_by_date = request.args.get('group_by_date')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    result = {}

    if group_by_ip:
        logs = session.query(LogEntry.ip, func.count(LogEntry.ip)).group_by(LogEntry.ip).all()
        result['group_by_ip'] = {log[0]: log[1] for log in logs}

    if group_by_date:
        logs = session.query(func.date(LogEntry.time), func.count(func.date(LogEntry.time))).group_by(func.date(LogEntry.time)).all()
        result['group_by_date'] = {str(log[0]): log[1] for log in logs}

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        logs = session.query(LogEntry).filter(LogEntry.time.between(start_date, end_date)).all()
        result['logs'] = [log.to_dict() for log in logs]

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)