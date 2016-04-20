import graphlab
import re

def extract_image_features():
    #Used graphlab.neuralnet_classifier.NeuralNetClassifier.extract_features which takes an input dataset, propagates each example through the network, and returns an SArray of dense feature vectors, each of which is the concatenation of all the hidden unit values at layer[layer_id].
    #Used a pre-trained model for ImageNet, as described by Alex Krizhevsky et. al. It is located at http://s3.amazonaws.com/dato-datasets/deeplearning/imagenet_model_iter45

    items = graphlab.SFrame.read_json('../data/items.json')
    #Remove duplicate rows of the SFrame
    items = items.unique()
    items.remove_column('image')

    #Split data by category
    phones = items.filter_by(['Cell Phones'], 'category_name')
    apparel = items.filter_by(['Baby & Kids', 'Clothing & Shoes'], 'category_name')
    home = items.filter_by(['Furniture', 'Household', 'Home & Garden'], 'category_name')

    #Load images
    phone_images = graphlab.image_analysis.load_images('data/images_by_category/Cell Phones', "auto", with_path=True, recursive=True)
    baby_images = graphlab.image_analysis.load_images('data/images_by_category/Baby & Kids', "auto", with_path=True, recursive=True)
    clothing_images = graphlab.image_analysis.load_images('data/images_by_category/Clothing & Shoes', "auto", with_path=True, recursive=True)
    furniture_images = graphlab.image_analysis.load_images('data/images_by_category/Furniture', "auto", with_path=True, recursive=True)
    household_images = graphlab.image_analysis.load_images('data/images_by_category/Household', "auto", with_path=True, recursive=True)
    home_garden_images = graphlab.image_analysis.load_images('data/images_by_category/Home & Garden', "auto", with_path=True, recursive=True)

    apparel_images = baby_images.append(clothing_images)
    home_images = furniture_images.append(household_images).append(home_garden_images)

    phone_images['id'] = phone_images['path'].apply(get_id)
    apparel_images['id'] = apparel_images['path'].apply(get_id)
    home_images['id'] = home_images['path'].apply(get_id)

    phones_with_images = phones.join(phone_images, on='id', how='inner')
    apparel_with_images = apparel.join(apparel_images, on='id', how='inner')
    home_with_images = home.join(home_images, on='id', how='inner')

    #Split data into train and test select_features
    phones_train, phones_test = phones_with_images.random_split(.8, seed=0)
    apparel_train, apparel_test = apparel_with_images.random_split(.8, seed=0)
    home_train, home_test = home_with_images.random_split(.8, seed=0)

    #Used the neural network trained on the 1.2 million images of the ImageNet Challenge.
    deep_learning_model = graphlab.load_model('data/imagenet_model')

    phones_train['deep_features'] = deep_learning_model.extract_features(phones_train)
    apparel_train['deep_features'] = deep_learning_model.extract_features(apparel_train)
    home_train['deep_features'] = deep_learning_model.extract_features(home_train)
    phones_test['deep_features'] = deep_learning_model.extract_features(phones_test)
    apparel_test['deep_features'] = deep_learning_model.extract_features(apparel_test)
    home_test['deep_features'] = deep_learning_model.extract_features(home_test)

    #Store into data folder


def get_id(str):
    m = re.match( r'.+\/(\d+)\/[^\/]+$', str)
    return int(m.group(1))

if __name__ == '__main__':
    extract_image_features()
