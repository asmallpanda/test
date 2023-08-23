from flask import Flask, url_for, request, render_template, redirect, session

app = Flask(__name__)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.form['user'] == 'admin':
            session['user'] = request.form['user']
            return 'Admin login successfully!'
        else:
            return 'No such user!'
    if 'user' in session:
        return 'Hello %s!' % session['user']
    else:
        title = request.args.get('title', 'Default')
        return render_template('login.html', title=title)


@app.route('/logout',)
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


app.secret_key = '123456'

if __name__ == "__main__":
    app.run(debug=True)
