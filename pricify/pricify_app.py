from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import graphlab
import re, string
import graphlab.aggregate as agg
import os
from werkzeug import secure_filename

# This is the path to the upload directory
UPLOAD_FOLDER = 'public/uploads'
# These are the extension that we are accepting to be uploaded
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

# Initialize the Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
PORT = 5000

DATA = []
TIMESTAMP = []

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        return redirect(url_for('uploaded_file', filename=filename))

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



# home page
# @app.route('/')
# def index():
#     return '''
#         <!DOCTYPE html>
#         <html>
#             <head>
#                 <meta charset="utf-8">
#                 <title>Pricify</title>
#             </head>
#           <body>
#             <!-- page content -->
#             <h1>See prices for your stuff.</h1>
#             <p>
#                 Model to define price for your garage sale.
#             </p>
#             <p>
#                 <a href="/submit">Check price</a>
#             </p>
#           </body>
#         </html>
#         '''
#
# # Form page to submit text
# @app.route('/submit')
# def submission_page():
#     return '''
#         <h3>We try to predict price.</h3>
#         <form action="/predict" method='POST' >
#             <p>
#                 <label>Input product title:</label>
#                 <input type="text" name="product_title" />
#             </p>
#             <p>
#                 <label>Input product description:</label>
#                 <textarea rows="10" cols="45" name="product_description"></textarea></p>
#             </p>
#             <input type="submit" />
#         </form>
#         '''
#
# @app.route('/upload', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('uploaded_file', filename=filename))
#     return '''
#     <!doctype html>
#     <title>Upload new File</title>
#     <h1>Upload new File</h1>
#     <form action="" method=post enctype=multipart/form-data>
#       <p><input type=file name=file>
#          <input type=submit value=Upload>
#     </form>
#     '''
# from flask import send_from_directory
#
# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'],
#                                filename)
#
# # My word counter app
# @app.route('/predict', methods=['POST'] )
# def word_counter():
#     word = str(request.form['user_input'])
#     topic = model.predict(vectorizer.transform([word]))
#     proba = model.predict_proba(vectorizer.transform([word]))
#     page = 'We think that word {0} is from {1} topic.'
#     return page.format(word, topic[0])
#
#
#
# @app.route('/score', methods=['POST'])
# def score():
#
#     #get data from  request
#     data = request.json
#
#     #Build dataframe to vectorize input data
#     df = pd.DataFrame([data], index=[0])
#
#     #Predict for one line of data
#     predict, probably = predict_for_input(df, model, pickles)
#
#     #Store data into global variable
#     print probably, predict
#     name =  "{0}".format(df['name'][0])
#     DATA.append(([name, probably, predict]))
#
#     #DATA.append(json.dumps(request.json, sort_keys=True, indent=4, separators=(',', ': ')))
#     TIMESTAMP.append(time.time())
#     return ""
#
#
# @app.route('/check')
# def check():
#     line1 = "Number of data points: {0}".format(len(DATA))
#     if DATA and TIMESTAMP:
#         print DATA
#         dt = datetime.fromtimestamp(TIMESTAMP[-1])
#         data_time = dt.strftime('%Y-%m-%d %H:%M:%S')
#         line2 = "Latest datapoint received at: {0}".format(data_time)
#         line3 = DATA[-1]
#         output = "{0}\n\n{1}\n\n{2}".format(line1, line2, line3)
#     else:
#         output = line1
#     return output, 200, {'Content-Type': 'text/css; charset=utf-8'}
#
# @app.route('/dashboard')
# def dashboard():
#     if DATA:
#         return render_template('table.html', data=DATA)
#     else:
#         return ""

if __name__ == '__main__':
    #model = load_models()

    # Start Flask app
    app.run(host='0.0.0.0', port=PORT, debug=True)
