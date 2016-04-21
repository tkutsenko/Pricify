import graphlab
import re, string
import graphlab.aggregate as agg
import os
from graphlab.toolkits.cross_validation import shuffle

DATA_PATH = "../data/"
WEB_APP_DATA_PATH = '../pricify/data/'

def read_data():
    #Load image analysis datasets.
    #Data was reduced to 6 categories in 3 groups: phones, home (Furniture, Household, Home & Garden), apparel (Baby & Kids, Clothing & Shoes) This dataset is already split into a training set and test set (80/20).

    phones_train = graphlab.load_sframe(DATA_PATH + 'phones_train')
    phones_test = graphlab.load_sframe(DATA_PATH + 'phones_test')
    home_train = graphlab.load_sframe(DATA_PATH + 'home_train')
    home_test = graphlab.load_sframe(DATA_PATH + 'home_test')
    apparel_train = graphlab.load_sframe(DATA_PATH + 'apparel_train')
    apparel_test = graphlab.load_sframe(DATA_PATH + 'apparel_test')

    return phones_train, phones_test, home_train, home_test, apparel_train, apparel_test

def features(sf):
    features_lst = ['id', 'category_id', 'category_name', 'count_words', 'tfidf', 'image', 'deep_features','price']

    # Make price float from string
    sf['price'] = sf['price'].astype(float)
    #Remove outliers
    sf = sf[sf['price'] < 1500]

    # Combine words from title and description
    sf['words'] = sf['title'] + ' ' + sf['description']
    # Remove punctuation
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    sf['words'] = sf['words'].apply(lambda x: regex.sub('', x))
    #Ttransforms row into an ordered list of strings that represents the a simpler version of the
    #Penn-Tree-Bank-style (PTB-style) tokenization
    sf['words'] = graphlab.text_analytics.tokenize(sf['words'])

    #Bag-of-words
    sf['count_words'] = graphlab.text_analytics.count_words(sf['words'])
    #Text cleaning. Remove stop words.
    sf['count_words'] = sf['count_words'].dict_trim_by_keys(graphlab.text_analytics.stopwords(), exclude=True)
    #TF-IDF (term frequency - inverse document frequency)
    sf['tfidf'] = graphlab.text_analytics.tf_idf(sf['count_words'])

    return sf.select_columns(features_lst)

def topic_model(sf, dataset_name):
    #Used Topic models from GraphLab Create to generate topic by title and description
    topics_number = 100
    model = graphlab.topic_model.create(sf['count_words'], num_topics=topics_number, num_iterations=100)

    #Save model to the web application
    model.save(WEB_APP_DATA_PATH + 'topic_model_' + dataset_name)

    #Add topic fields
    sf['topic'] = model.predict(sf['count_words'])
    for i in  xrange(topics_number):
        sf['topic_' + str(i)] = sf['topic'].apply(lambda x: (1 if int(x) == i else 0))
    return sf

# Create a model.
def nearest_neighbors(sf, name):
    model = graphlab.nearest_neighbors.create(sf,
                                              features=model_features(sf),
                                              label='id')
    model.save(WEB_APP_DATA_PATH + 'similar_images_for_' + name)
    return model

# Create a model.
def random_forest_model(sf, name):
    model = graphlab.random_forest_regression.create(sf, target='price',
                                          features=model_features(sf),
                                          #max_iterations = 20,
                                          max_depth =  3
                                          )

    model.save(WEB_APP_DATA_PATH + 'random_forest_regression_for_' + name)
    return model

# Create a model.
def  gradient_boosted_regression_trees_model(sf, name):
    model = graphlab.boosted_trees_regression.create(sf, target='price',
                                          features=model_features(sf),
                                          max_iterations = 20,
                                          max_depth =  3
                                          )

    model.save(WEB_APP_DATA_PATH + 'boosted_trees_regression_for_' + name)
    return model

def model_features(sf):
    #'deep_features','tfidf','topic_0','topic_1','topic_2', ...
    return list(set(
                  sf.column_names()) - \
                  set(['id', 'category_id', 'category_name', 'count_words', 'image', 'price', 'topic']
                ))


# Model to classify categiry by image, title and description
def nearest_neighbors_categiry_classifier(sf, name):
    model = graphlab.nearest_neighbors.create(sf, features=['deep_features', 'count_words'], label='id')

    model.save(WEB_APP_DATA_PATH + 'nearest_neighbors_categiry_for_' + name)
    return model

# Nearest Neighbors models to classify categiry by image, title and description
def category_classifier(sf):
    model = graphlab.boosted_trees_classifier.create(sf, target='category_name',
                                          features=['deep_features', 'count_words'],
                                          max_iterations = 20,
                                          max_depth =  3
                                          )

    model.save(WEB_APP_DATA_PATH + 'boosted_trees_category_classifier')
    return model


def run_and_save_model():
    models_lst = read_data()
    models_lst = [features(model) for model in models_lst]
    phones_train, phones_test, home_train, home_test, apparel_train, apparel_test = models_lst

    train_dict = {'phones_train': phones_train, 'home_train': home_train, 'apparel_train': apparel_train}

    for dataset_name, dataset in train_dict.iteritems():
        dataset = topic_model(dataset, dataset_name)
        nearest_neighbors(dataset, dataset_name)
        random_forest_model(dataset, dataset_name)
        gradient_boosted_regression_trees_model(dataset, dataset_name)
        nearest_neighbors_categiry_classifier(dataset, dataset_name)

    image_train = phones_train.append(home_train).append(apparel_train)
    shuffle(image_train, random_seed=0)
    category_classifier(image_train)

if __name__ == '__main__':
    run_and_save_model()
