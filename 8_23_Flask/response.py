from flask import Flask,url_for,request,render_template,redirect,session,make_response
app = Flask(__name__)
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        ...
    if 'user' in session:
        ...
    else:
        title = request.args.get('title', 'Default')
        response = make_response(render_template('login.html', title=title), 200)
        response.headers['key'] = 'value'
        return response
if __name__ == "__main__":
    app.run(debug=True)