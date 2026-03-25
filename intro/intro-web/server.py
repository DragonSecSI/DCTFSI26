import flask
import subprocess

app = flask.Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    response = ""
    if flask.request.method == 'POST':
        host = flask.request.form['host'].strip()
        if not host:
            response = "No host provided."
        else:
            try:
                result = subprocess.run(f"ping -c 4 '{host}'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    response = f"{result.stdout}"
                else:
                    response = f"An error occurred while pinging"
            except Exception:
                response = f"An error occurred"
    return flask.render_template_string('''
        <h1>Welcome to PAAS (Ping As A Service)</h1>
        <form action="/" method="post">
            <input type="text" name="host" placeholder="Enter host to ping" required>
            <button type="submit">Ping</button>
        </form>
        <pre>{{ response }}</pre>
    ''', response=response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
