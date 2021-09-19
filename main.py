import re
import numpy as np
from PIL import Image
from flask import Flask, request, render_template, url_for, jsonify, send_from_directory
from werkzeug.utils import redirect, secure_filename


def hex_to_rgb(value):
    h = value.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


UPLOAD_FOLDER = '/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST' and 'text' in request.form and 'file' in request.files:
        uploading_file = request.files['file']
        if uploading_file and allowed_file(uploading_file.filename):
            hex_colour = request.form['text']
            if re.match(r'#[0-9A-Fa-f]{6}', hex_colour):
                filename = secure_filename(uploading_file.filename)
                uploading_file.save(uploading_file.filename)
                colour_rgb = hex_to_rgb(hex_colour)
                im = np.array(Image.open(filename).convert('RGB'))
                result = np.count_nonzero(np.all(im == colour_rgb, axis=2))
                black_pixels = np.count_nonzero(np.all(im == [0, 0, 0], axis=2))
                while_pixels = np.count_nonzero(np.all(im == [255, 255, 255], axis=2))
                if black_pixels > while_pixels:
                    solution = 'black pixels more than white'
                else:
                    solution = 'white pixels more than black'
                # return redirect(url_for('uploaded_file', filename=filename))
                return jsonify({'1.number of hex pixels': result,
                                '2.black pixels': black_pixels,
                                '3.white pixels': while_pixels,
                                '4.solution': solution})
            else:
                return jsonify({'message': 'hex not valid'})
        else:
            return jsonify({'message': 'file not valid'})
    return jsonify({'message': 'file not upload'})


@app.route('/<filename>')  # что-то не так?!
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    app.run(debug=True)
