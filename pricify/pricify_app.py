from flask import Flask, request, render_template, redirect, url_for, send_from_directory, session
import graphlab
import re, string
import graphlab.aggregate as agg
import os
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage
from pricify import load_models, load_data
from src.model import count_words, image_deep_features, add_topic_fields

# This is the path to the upload directory
UPLOAD_FOLDER = 'static/uploads/'
IMAGES_FOLDER = 'static/images/'
# These are the extension that we are accepting to be uploaded
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

# Initialize the Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGES_FOLDER'] = IMAGES_FOLDER
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
    if category == 'Cell Phones':
        topic_model = topic_model_phones
        price_model = boosted_trees_regression_for_phones
        neighbors_model = similar_images_for_phones
        vectorizer = vectorizer_phones
        data = phones
        category_name = 'phones'
    elif category in ['Furniture', 'Household', 'Home & Garden']:
        topic_model = topic_model_home
        price_model = boosted_trees_regression_for_home
        neighbors_model = similar_images_for_home
        vectorizer = vectorizer_home
        data = home
        category_name = 'home'
    else: # 'Baby & Kids', 'Clothing & Shoes'
        topic_model = topic_model_apparel
        price_model = boosted_trees_regression_for_apparel
        neighbors_model = similar_images_for_apparel
        vectorizer = vectorizer_apparel
        data = apparel
        category_name = 'apparel'

    #Add topic fields
    sf = add_topic_fields(sf, topic_model)

    #Add TF-IDF
    transformed_sf = vectorizer.transform(sf)
    sf['tfidf'] = transformed_sf['count_words']

    #Predict price
    price = round(price_model.predict(sf)[0])

    #Find nearest_neighbors
    neighbors = neighbors_model.query(sf, k = 5)
    neighbors = neighbors.groupby(key_columns='query_label', operations={"neighbours":agg.CONCAT("reference_label")})
    neighbors_lst = neighbors['neighbours'][0]

    similar_offers = data.filter_by(neighbors_lst, 'id')
    similar_offers['image_path'] = similar_offers['id'].apply(lambda x: app.config['IMAGES_FOLDER'] + category_name + "/" + str(x) + '.jpg')
    return render_template('price.html', price = price, category = category, image = filename, offers = similar_offers)


# This route will clear the variable sessions
# This functionality can come handy for example when we logout
# a user from our app and we want to clear its information
@app.route('/clear')
def clearsession():
    # Clear the session
    session.clear()
    # Redirect the user to the main page
    return redirect(url_for('index'))


if __name__ == '__main__':
    boosted_trees_category_classifier, topic_model_phones, topic_model_apparel, \
    topic_model_home, vectorizer_phones, vectorizer_apparel, vectorizer_home, \
    boosted_trees_regression_for_phones, boosted_trees_regression_for_apparel, \
    boosted_trees_regression_for_home, similar_images_for_phones, similar_images_for_apparel, \
    similar_images_for_home, deep_learning_model = load_models()

    phones, home, apparel = load_data()

    # Start Flask app
    app.run(host='0.0.0.0', port=PORT, debug=True)
