import graphlab

DATA_PATH = "data/"

def load_models():
    # boosted_trees_category_classifier
    btcc = graphlab.load_model(DATA_PATH + 'boosted_trees_category_classifier')

    #topic_model_phones
    tmp = graphlab.load_model(DATA_PATH + 'topic_model_phones')
    #topic_model_apparel
    tma = graphlab.load_model(DATA_PATH + 'topic_model_apparel')
    #topic_model_home
    tmh = graphlab.load_model(DATA_PATH + 'topic_model_home')

    #words vectorizer phones
    vp = graphlab.load_model(DATA_PATH + 'vectorizer_phones')
    #words vectorizer apparel
    va = graphlab.load_model(DATA_PATH + 'vectorizer_apparel')
    #words vectorizer home
    vh = graphlab.load_model(DATA_PATH + 'vectorizer_home')

    #boosted_trees_regression_for_phones
    btrp = graphlab.load_model(DATA_PATH + 'boosted_trees_regression_for_phones')
    #boosted_trees_regression_for_apparel
    btra = graphlab.load_model(DATA_PATH + 'boosted_trees_regression_for_apparel')
    #boosted_trees_regression_for_home
    btrh = graphlab.load_model(DATA_PATH + 'boosted_trees_regression_for_home')

    #similar_images_for_phones
    sip = graphlab.load_model(DATA_PATH + 'similar_images_for_phones')
    #similar_images_for_apparel
    sia = graphlab.load_model(DATA_PATH + 'similar_images_for_apparel')
    #similar_images_for_home
    sih = graphlab.load_model(DATA_PATH + 'similar_images_for_home')

    #neural network trained on the 1.2 million images of the ImageNet Challenge.
    deep_learning_model = graphlab.load_model(DATA_PATH + 'imagenet_model')

    #[boosted_trees_category_classifier, topic_model_phones, topic_model_apparel,
    #topic_model_home, vectorizer_phones, vectorizer_apparel, vectorizer_home,
    #boosted_trees_regression_for_phones, boosted_trees_regression_for_apparel,
    #boosted_trees_regression_for_home, similar_images_for_phones, similar_images_for_apparel,
    #similar_images_for_home, deep_learning_model]
    return [btcc, tmp, tma, tmh, vp, va, vh, btrp, btra, btrh, sip, sia, sih, deep_learning_model]
