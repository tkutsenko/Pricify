from flask import Flask, request, render_template, redirect, url_for, send_from_directory, session
import graphlab
import re, string
import graphlab.aggregate as agg
import os
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage
from pricify import load_models
from src.model import count_words, image_deep_features

# This is the path to the upload directory
UPLOAD_FOLDER = 'public/uploads/'
# These are the extension that we are accepting to be uploaded
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

# Initialize the Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
PORT = 5000

# Sessions variables are stored client side, on the users browser
# the content of the variables is encrypted, so users can't
# actually see it. They could edit it, but again, as the content
# wouldn't be signed with this hash key, it wouldn't be valid
# You need to set a scret key (random text) and keep it secret
app.secret_key = 'z7XdA3Cov8JCg4F~7qRK2QB7ZK?939XyzI'


DATA = []
TIMESTAMP = []

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    title = str(unicode(request.form['product_title']).encode('ascii', 'ignore'))
    description = str(unicode(request.form['product_description']).encode('ascii', 'ignore'))
    session['title'] = title
    session['description'] = description

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
        return redirect(url_for('predict_price', filename=filename))
        #redirect(url_for('.do_foo', messages=messages))


# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/price')
def predict_price():
    title = session['title']
    description = session['description']

    #Build dataframe to vectorize input data
    sf = graphlab.SFrame({'title' : [title], 'description' : [description]})
    sf = count_words(sf)
    filename = app.config['UPLOAD_FOLDER'] + request.args['filename']
    sf = sf.join(image_deep_features(filename, deep_learning_model), how='left')

    #Define category
    category = boosted_trees_category_classifier.predict(sf, output_type='class')[0]

    #Define data class
    

    # #Build dataframe to vectorize input data
    # df = pd.DataFrame([data], index=[0])
    #
    # #Predict for one line of data
    # predict, probably = predict_for_input(df, model, pickles)
    #
    # #Store data into global variable
    # print probably, predict
    # name = "{0}".format(df['name'][0])
    # DATA.append(([name, probably, predict]))
    #
    # #DATA.append(json.dumps(request.json, sort_keys=True, indent=4, separators=(',', ': ')))
    # TIMESTAMP.append(time.time())
    return render_template('price.html')


# This route will clear the variable sessions
# This functionality can come handy for example when we logout
# a user from our app and we want to clear its information
@app.route('/clear')
def clearsession():
    # Clear the session
    session.clear()
    # Redirect the user to the main page
    return redirect(url_for('index'))


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
    boosted_trees_category_classifier, topic_model_phones, topic_model_apparel, \
    topic_model_home, boosted_trees_regression_for_phones, boosted_trees_regression_for_apparel, \
    boosted_trees_regression_for_home, similar_images_for_phones, similar_images_for_apparel_train, \
    similar_images_for_home, deep_learning_model = load_models()

    # Start Flask app
    app.run(host='0.0.0.0', port=PORT, debug=True)
