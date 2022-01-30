from flask import Flask, render_template, url_for, request, send_from_directory
import random, threading, webbrowser
import pathlib

from resources.student_resource import StudentResource


app = Flask(__name__)


@app.route('/', methods = ['GET', 'POST'])
def index():
    error = None
    message = ""
    success = None

    # Check whether data has been submitted
    if request.method == 'POST':
        # Get submitted data
        school_url = request.form.get('school_url')
        batch = request.form.get('batch')
        username = request.form.get('username')
        password = request.form.get('password')

        # Create a dict with the submitted data
        payload = {
            "school_url": school_url,
            "batch": batch,
            "username": username,
            "password": password
        }

        # Pass the payload to the student resource class
        student_resource = StudentResource(payload = payload)
        response = student_resource.get_students()
        if not response.status:
            error = response.message
            message = response.message
        else:
            success = True
            message = response.message
            file_name = "student_data.xlsx"
            return send_from_directory(pathlib.Path().resolve(), file_name, as_attachment = True)
            # return redirect(url_for('/'), 200,)
    return render_template('index.html', error = error, message = message, success = success)


if __name__ == '__main__':
    port = 5000 + random.randint(0, 999)
    # url = "http://127.0.0.1:5000"
    # threading.Timer(1.25, lambda: webbrowser.open(url)).start()
    app.run(debug = True, port = 5000)

