from flask import Flask, url_for, request, render_template, redirect, session, make_response
import time

app = Flask(__name__)


@app.route('/login', methods=['POST', 'GET'])
def login():
    response = None
    if request.method == 'POST':
        if request.form['user'] == 'admin':
            session['user'] = request.form['user']
            response = make_response('Admin login successfully!')
            response.set_cookie('login_time', time.strftime('%Y-%m-%d %H:%M:%S'))
        ...
    else:
        if 'user' in session:
            login_time = request.cookies.get('login_time')
            response = make_response('Hello %s,you logged in on %s' % (session['user'], login_time))
        ...
    return response


app.secret_key = '123456'
if __name__ == "__main__":
    app.run(debug=True)
