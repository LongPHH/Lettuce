from flask import Flask, render_template, request
from ledis import Ledis
# render template is for Jinja Template
# requests is for handling inputs and outputs
# flask allow easy interaction with HTML dynamically

app = Flask(__name__)

commands = []
ledis = Ledis()


def parse_command(command):
    command_lst = command.strip().split(' ')  # removing white space with strip()
    cmd = command_lst[0]

    if cmd == "SET":
        result = ledis.SET(command_lst[1], command_lst[2:])
    elif cmd == "GET":
        result = ledis.GET(command_lst[1])
    elif cmd == "SADD":
        result = ledis.SADD(command_lst[1], command_lst[2:])
    elif cmd == "SREM":
        result = ledis.SREM(command_lst[1], command_lst[2:])
    elif cmd == "SMEMBERS":
        result = ledis.SMEMBERS(command_lst[1])
    elif cmd == "SINTER":
        result = ledis.SINTER(command_lst[1:])
    elif cmd == "KEYS":
        result = ledis.KEYS()
    elif cmd == "DEL":
        result = ledis.DEL(command_lst[1])
    elif cmd == "EXPIRE":
        result = ledis.EXPIRE(command_lst[1], command_lst[2])
    elif cmd == "TTL":
        result = ledis.TTL(command_lst[1])
    elif cmd == "SAVE":
        result = ledis.SAVE()
    elif cmd == "RESTORE":
        result = ledis.RESTORE()
    else:
        result = "INVALID INPUT"

    while len(commands) > 12:
        commands.pop(0)

    return result



@app.route("/", methods=['post', 'get'])  # access website when go to /

def home():
    if request.method == 'POST':
        command = request.form.get('command')  # getting commands
        commands.append(command)

        response = parse_command(command)  # calling parse_command to execute commands
        commands.append(response)

    return render_template("home.html", commands=commands)  # show the user the page with updated commands/response


if __name__ == "__main__":
    app.run(debug=True)
