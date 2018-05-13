import os

from flask import send_from_directory
from flask import Flask, render_template, request
from flask import redirect, url_for, after_this_request
from werkzeug.utils import secure_filename

import sys
sys.path.insert(0, r'/media/anton/Ubuntu/GitWorkDir/JobsScheduler/Model')
import algorithms

UPLOAD_FOLDER = '/media/anton/Ubuntu/GitWorkDir/JobsScheduler/tmp/'
ALLOWED_EXTENSIONS = set(['txt'])
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solution')
def solution():

    if request.args.get('choice') == 'permutation':

        #######################################################
        data = algorithms.read_file(UPLOAD_FOLDER + '/input_data')
        jobs = data[0]
        machines_quantity = data[1]
        opt = algorithms.optimal(jobs, machines_quantity)
        schedule = algorithms.spt_algorithm(jobs, machines_quantity)
        algorithms.write_file("/home/anton/csvfile.csv", schedule, opt)
        print(schedule)
        print()
        schedule = algorithms.swapping_method(schedule, len(jobs))
        print(schedule)
        print()
        #print(opt, max_len(schedule, machines_quantity)[1])
        algorithms.write_file("/home/anton/csvfile.csv", schedule, opt)
        ########################################################
        @after_this_request
        def remove_file(response):
            if os.path.isfile("/home/anton/csvfile.csv"):
                os.remove("/home/anton/csvfile.csv")
            return response

        return send_from_directory('/home/anton', 'csvfile.csv')
    if request.args.get('choice') == 'another':
        ########################################################
        data = algorithms.read_file(UPLOAD_FOLDER + '/input_data')
        jobs = data[0]
        machines_quantity = data[1]
        opt = algorithms.optimal(jobs, machines_quantity)
        schedule = algorithms.spt_algorithm(jobs, machines_quantity)
        algorithms.write_file("/home/anton/csvfile.csv", schedule, opt)
        print(schedule)
        print()
        schedule = algorithms.genetic_algorithm(schedule, len(jobs), opt)
        print(schedule)
        print()
        #print(opt, max_len(schedule, machines_quantity)[1])
        algorithms.write_file("/home/anton/csvfile.csv", schedule, opt)
        ########################################################
        @after_this_request
        def remove_file(response):
            if os.path.isfile("/home/anton/csvfile.csv"):
                os.remove("/home/anton/csvfile.csv")
            return response
        return send_from_directory('/home/anton', 'csvfile.csv')
    return render_template('solution.html')

@app.route('/about')
def about():
    return  render_template('about.html')
@app.route('/task')
def task():
    return  render_template('task.html')


@app.route('/generation')
def Generation():
    if request.args.get('choice') == 'permutation':
        #######################################################
        data = algorithms.random_inicialisation()
        jobs = data[0]
        machines_quantity = data[1]
        opt = algorithms.optimal(jobs, machines_quantity)
        schedule = algorithms.spt_algorithm(jobs, machines_quantity)
        algorithms.write_file("/home/anton/csvfile.csv", schedule, opt)
        print(schedule)
        print()
        schedule = algorithms.swapping_method(schedule, len(jobs))
        print(schedule)
        print()
        #print(opt, max_len(schedule, machines_quantity)[1])
        algorithms.write_file("/home/anton/csvfile.csv", schedule, opt)
        ########################################################
        @after_this_request
        def remove_file(response):
            if os.path.isfile("/home/anton/csvfile.csv"):
                os.remove("/home/anton/csvfile.csv")
            return response
        return send_from_directory('/home/anton', 'csvfile.csv')
    if request.args.get('choice') == 'another':
        ########################################################
        data = algorithms.random_inicialisation()
        jobs = data[0]
        machines_quantity = data[1]
        opt = algorithms.optimal(jobs, machines_quantity)
        schedule = algorithms.spt_algorithm(jobs, machines_quantity)
        algorithms.write_file("/home/anton/csvfile.csv", schedule, opt)
        print(schedule)
        print()
        schedule = algorithms.genetic_algorithm(schedule, len(jobs), opt)
        print(schedule)
        print()
        #print(opt, max_len(schedule, machines_quantity)[1])
        algorithms.write_file("/home/anton/csvfile.csv", schedule, opt)
        ########################################################
        @after_this_request
        def remove_file(response):
            if os.path.isfile("/home/anton/csvfile.csv"):
                os.remove("/home/anton/csvfile.csv")
            return response
        return send_from_directory('/home/anton', 'csvfile.csv')
    return render_template('generation.html')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/download', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            #filename = secure_filename(file.filename)
            filename = "input_data"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('solution'))
            #return render_template('solution.html')
    return 'Не правильний формат файлу, завантажте правильний файл'

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(port=5000)
