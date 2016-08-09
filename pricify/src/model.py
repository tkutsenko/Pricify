import graphlab
import re
import string
import graphlab.aggregate as agg
import os
from graphlab.toolkits.cross_validation import shuffle

DATA_PATH = "../../data/"
WEB_APP_DATA_PATH = '../data/'
topics_number = 100


def read_data():
    # Load image analysis datasets.
    # Data was reduced to 6 categories in 3 groups: phones, home
    # (Furniture, Household, Home & Garden), apparel
    # (Baby & Kids, Clothing & Shoes).

    phones_set = graphlab.load_sframe(DATA_PATH + 'phones_with_ids')
    home_set = graphlab.load_sframe(DATA_PATH + 'home_with_ids')
    apparel_set = graphlab.load_sframe(DATA_PATH + 'apparel_with_ids')

    return phones_set, home_set, apparel_set


def save_prices(sf, name):
    data = sf[['id', 'price']]
    data.save(DATA_PATH + name)


def features(sf):
    features_lst = ['id', 'category_id', 'category_name', 'count_words',
                    'tfidf', 'image', 'deep_features', 'price']

    # Make price float from string
    sf['price'] = sf['price'].astype(float)
    # Remove outliers
    sf = sf[sf['price'] < 1500]

    # Add count_words feature
    sf = count_words(sf)

    # TF-IDF (term frequency - inverse document frequency)
    sf['tfidf'] = graphlab.text_analytics.tf_idf(sf['count_words'])

    return sf.select_columns(features_lst)


def count_words(sf):
    # Combine words from title and description
    sf['words'] = sf['title'] + ' ' + sf['description']
    # Remove punctuation
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    sf['words'] = sf['words'].apply(lambda x: regex.sub('', x))
    # Ttransforms row into an ordered list of strings that represents the a
    # simpler version of the Penn-Tree-Bank-style (PTB-style) tokenization
    sf['words'] = graphlab.text_analytics.tokenize(sf['words'])

    # Bag-of-words
    sf['count_words'] = graphlab.text_analytics.count_words(sf['words'])
    # Text cleaning. Remove stop words.
    sf['count_words'] = sf['count_words'].dict_trim_by_keys(graphlab.text_analytics.stopwords(), exclude=True)
    return sf


def tf_idf_vectorizer(sf, dataset_name):
    encoder = graphlab.feature_engineering.TFIDF('count_words')
    encoder = encoder.fit(sf)
    encoder.save(WEB_APP_DATA_PATH + 'vectorizer_' + dataset_name)


def topic_model(sf, dataset_name):
    # Used Topic models from GraphLab Create to generate topic by title and
    # description
    model = graphlab.topic_model.create(sf['count_words'],
                                        num_topics=topics_number,
                                        num_iterations=100)

    # Save model to the web application
    model.save(WEB_APP_DATA_PATH + 'topic_model_' + dataset_name)

    # Add topic fields
    sf = add_topic_fields(sf, model)
    return sf


def add_topic_fields(sf, model):
    sf['topic'] = model.predict(sf['count_words'])
    for i in xrange(topics_number):
        sf['topic_' + str(i)] = sf['topic'].apply(lambda x:
                                                  (1 if int(x) == i else 0))
    return sf


def image_deep_features(file_path, deep_learning_model):
    img = graphlab.Image(file_path)
    image_sf = graphlab.SFrame({'image': [img]})
    image_sf['deep_features'] = deep_learning_model.extract_features(image_sf)
    return image_sf


# Create a model
def nearest_neighbors(sf, name):
    model = graphlab.nearest_neighbors.create(sf,
                                              features=model_features(sf),
                                              label='id')
    model.save(WEB_APP_DATA_PATH + 'similar_images_for_' + name)
    return model


# Create a model
def random_forest_model(sf, name):
    model = graphlab.random_forest_regression.create(sf,
                                                     target='price',
                                                     features=model_features(sf),
                                                     max_depth=3)

    model.save(WEB_APP_DATA_PATH + 'random_forest_regression_for_' + name)
    return model


# Create a model
def gradient_boosted_regression_trees_model(sf, name):
    model = graphlab.boosted_trees_regression.create(sf,
                                                     target='price',
                                                     features=model_features(sf),
                                                     max_iterations=20,
                                                     max_depth=3)

    model.save(WEB_APP_DATA_PATH + 'boosted_trees_regression_for_' + name)
    return model


def model_features(sf):
    # 'deep_features','tfidf','topic_0','topic_1','topic_2', ...
    return list(set(sf.column_names()) -
                set(['id', 'category_id', 'category_name', 'count_words',
                     'image', 'price', 'topic']))


# Nearest Neighbors models to classify categiry by image, title and description
def nearest_neighbors_categiry_classifier(sf, name):
    model = graphlab.nearest_neighbors.create(sf,
                                              features=['deep_features',
                                                        'count_words'],
                                              label='id')

    model.save(WEB_APP_DATA_PATH + 'nearest_neighbors_categiry_for_' + name)
    return model


# Model to classify categiry by image, title and description
def category_classifier(sf):
    model = graphlab.boosted_trees_classifier.create(sf,
                                                     target='category_name',
                                                     features=['deep_features',
                                                               'count_words'],
                                                     max_iterations=20,
                                                     max_depth=3)

    model.save(WEB_APP_DATA_PATH + 'boosted_trees_category_classifier')
    return model


def run_and_save_model():
    models_lst = read_data()
    models_lst = [features(model) for model in models_lst]
    phones_set, home_set, apparel_set = models_lst

    set_dict = {'phones': phones_set, 'home': home_set, 'apparel': apparel_set}

    for dataset_name, dataset in set_dict.iteritems():
        dataset = topic_model(dataset, dataset_name)
        nearest_neighbors(dataset, dataset_name)
        random_forest_model(dataset, dataset_name)
        gradient_boosted_regression_trees_model(dataset, dataset_name)
        nearest_neighbors_categiry_classifier(dataset, dataset_name)
        tf_idf_vectorizer(dataset, dataset_name)
        save_prices(dataset, dataset_name + "_s")

    image_set = phones_set.append(home_set).append(apparel_set)
    shuffle(image_set, random_seed=0)
    category_classifier(image_set)


if __name__ == '__main__':
    run_and_save_model()
