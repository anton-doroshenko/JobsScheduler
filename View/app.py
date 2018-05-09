import os

from flask import send_from_directory
from flask import Flask, render_template, request
from flask import redirect, url_for
from werkzeug.utils import secure_filename

import sys
sys.path.insert(0, r'/media/anton/Ubuntu/GitWorkDir/JobsScheduler/Model')
import algorithms

UPLOAD_FOLDER = '/media/anton/Ubuntu/GitWorkDir/untitled/tmp/'
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
        #jobs = np.array([(1, 12),(2, 14), (3, 15), (4, 12), (5, 16),
        #                 (6, 12), (7, 12), (8, 23), (9, 13), (10, 15),
        #                 (11, 21), (12, 23), (13, 24), (14, 12), (15, 29)],
        #                dtype=[('index', '<i4'), ('time', '<i4')])

        #machines_quantity = 4
        #opt = math.ceil(np.sum(jobs['time']) / machines_quantity)
        schedule = algorithms.spt_algorithm(jobs, machines_quantity)
        print(schedule)
        print()
        schedule = algorithms.swapping_method(schedule, len(jobs))
        print(schedule)
        print()
        #print(opt, max_len(schedule, machines_quantity)[1])
        algorithms.write_file("/home/anton/csvfile.csv", schedule)
        ########################################################

        return send_from_directory('/home/anton', 'csvfile.csv')
    if request.args.get('choice') == 'another':
        pass
        #return send_from_directory('C:/Users/User/PycharmProjects/untitled/static', 'task.docx')
    return render_template('solution.html')

@app.route('/about')
def about():
    return  render_template('about.html')
@app.route('/task')
def task():
    return  render_template('task.html')

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
    app.run()
