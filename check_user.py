import os
import sys
import typing as t

from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSON_SORT_KEYS'] = False

def count_connection(username: str) -> int:
    command = 'ps -u %s' % username
    result = os.popen(command).readlines()

    return len([line for line in result if 'sshd' in line])


def get_expiration_date(username: str) -> t.Optional[str]:
    command = 'chage -l %s' % username
    result = os.popen(command).readlines()

    for line in result:
        line = list(map(str.strip, line.split(':')))
        if line[0].lower() == 'account expires' and line[1] != 'never':
            return datetime.strptime(line[1], '%b %d, %Y').strftime('%d/%m/%Y')

    return None


def get_expiration_days(date: str) -> int:
    if not isinstance(date, str) or date.lower() == 'never' or not isinstance(date, str):
        return -1

    return (datetime.strptime(date, '%d/%m/%Y') - datetime.now()).days


def get_time_online(username: str) -> t.Optional[str]:
    command = 'ps -u %s -o etime --no-headers' % username
    result = os.popen(command).readlines()
    return result[0].strip() if result else None


@app.route('/check/<string:username>')
def check_user(username):
    try:
        count = count_connection(username)
        expiration_date = get_expiration_date(username)

        return jsonify(
            {
                'username': username,
                'count_connection': count,
                'expiration_date': expiration_date,
                'expiration_days': get_expiration_days(expiration_date),
                'time_online': get_time_online(username),
            }
        )
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(sys.argv[1]) if len(sys.argv) > 1 else 2095,
    )
