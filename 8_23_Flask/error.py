# from flask import Flask,abort
#
# app = Flask(__name__)
# @app.route('/error')
# def error():
#     abort(404)
#
# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, abort, render_template, make_response

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=400):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code


@app.errorhandler(InvalidUsage)
def invalid_usage(error):
    response = make_response(error.message)
    response.status_code = error.status_code
    return response
@app.route('/exception')
def exception():
    raise InvalidUsage('No privilege to access the resource', status_code=403)


if __name__ == "__main__":
    app.run(debug=True)