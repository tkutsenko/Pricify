# Price recommender
Galvanize Data Science Program. Capstone Project.

![Pricify](images/pricify.png)

## Overview
Price recommendation by product picture. Project aims to save your time and money predicting fair market price for product by analyzing title, description and finding similar items by picture. As OfferUp says, "with a single snap, you can take a photo of an item and instantly circulate it to people nearby". It's not exactly true as one still has to set price which could be hard without research. This project fills the gap and allows for true one-click listing.

Analysis was conducted on an Amazon Web Services EC2 instance using NLP and Neural Network.


## Data source
All data were scraped from OfferUp (offerupnow.com). OfferUp is mobile marketplace that provides safe and convenient place to easily buy and sell used goods.

**script/scrap_offerup.rb** issues HTTP requests to https://offerupnow.com/ and scraps recent offers page by page until the date limit was reached. Each offer is stored into file in JSON format.

**script/normalize_scraped.rb** splits and combines offers into 3 JSON files, namely:

* items.json 605 Mb 380,107 items
* owners.json 141.2 Mb item owners
* images.json 214.1 Mb links to item images

**script/download_images.rb** downloads images and sorts them between subfolders by size:
* detail
* full
* list

## Data Preparation

items.json contains 300,304 unique items with 34 fields per item. Items belong to 37 different categories.

To simplify the model, we picked most interesting categories and joined them into 3 supercategories:

```
Baby & Kids              37114
Clothing & Shoes         27743  


Furniture                22857
Household                21974
Home & Garden            9529

Cell Phones              14307
```

Models were trained and fine-tuned for each supercategory separately.

### Text processing:
features = ['id', 'description', 'title', 'category_name', 'price']

Topic model with TF-IDF vectorization of product title and description is used here. Topics are used as features in training BoostedTreesRegression and BoostedTreesClassifier models.

### Image processing:
For image processing we used pre-trained model of Alexnet (https://static.turi.com/products/graphlab-create/resources/models/python2.7/imagenet_model_iter45), which was fitted on our data using GraphLab Create extract_features API. Its architecture allows it to work only with fixed-size 256 x 256 x 3 images. Model returns an SArray of feature vectors which are then used as input to train BoostedTreesRegression and BoostedTreesClassifier models.

#### References:
Krizhevsky, Alex, Ilya Sutskever, and Geoffrey E. Hinton. “Imagenet classification with deep convolutional neural networks.” Advances in neural information processing systems. 2012.

### Nearest Neighbors

On the last step BoostedTreesRegression model predicts the exact price and Nearest Neighbors model finds top 5 nearest offers to display for user.

### Model - How it works from data side

![How it works from user side](images/data_side.png)

### Model - How it works from user side

![How it works from user side](images/user_side.png)

### Results

Results look promising for some cases:

#### Phones
![Phone category](images/phone.png)

#### Single furniture items
![Home category](images/home.png)

#### But not so much for items that look alike, but differ in price greatly:
![Apparel and kids category](images/kids.png)

#### And it can even get confused about the product type:
![Issues](images/issues_img.png)

## Future Work
* Add weights to text features and use more advanced featurization techniques with text (e.g. Doc2Vec) to maximize information extraction from the data.
* Predict price interval instead of exact price.
* Architect neural net specifically fitted for kind of images used and supporting different aspect ratios.

## Packages used
* NumPy
* pandas
* scikit-learn
* matplotlib
* GraphLab Create
* Flask
