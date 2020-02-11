import numpy as np
import PIL, io, os, glob, shutil, tables, urllib.request 
import pandas as pd
import matplotlib.pyplot as plt
import keras
from keras.layers import Dense, InputLayer, Conv2D, MaxPooling2D, Flatten, Dropout
from keras.applications.vgg16 import preprocess_input
from keras.applications import MobileNetV2, VGG16 
from keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array, array_to_img, image
from keras import Sequential, models, layers, optimizers, Model
import tensorflow as tf
import sqlalchemy as sql

path = os.getcwd()
os.mkdir(os.path.join(path, 'train'))
os.mkdir(os.path.join(path, 'validation'))
os.mkdir(os.path.join(path, 'test'))


Server = "freightwaves.ctaqnedkuefm.us-east-2.rds.amazonaws.com"
Database = "Warehouse"
PWD = 'sierra_watkins'
UID = '5Kj5iwMuh#6I^*DH'

engine = sql.create_engine(f"mssql+pymssql://{PWD}:{UID}@{Server}/{Database}")
con = engine.connect()

rs = con.execute('select * from warehouse.dbo.StateTrafficCameras_MetaData where trailers is not null or passengervehicles is not null or largenonfreightvehicles is not null or unclassifiable is not null or daytime is not null')
newdf = pd.DataFrame(rs.fetchall())
newdf.columns = rs.keys()

OR1338 = newdf[newdf.uuid == 'OR00000001338']
OR1338 = OR1338.reset_index(drop = True)

imglist = []
for i in range(len(OR1338['image_url'])):

    with urllib.request.urlopen(OR1338['image_url'][i ]) as url:

        img  = io.BytesIO(url.read())
        inbetween = PIL.Image.open(img)
        # dimensions for OR1338 and probably all oregon stuff 
        area = (70, 100, 250, 250) # left, top, right, bottom 
        cropped = inbetween.crop(area)
        cropped.save('OR1338_%s.png' %i , 'PNG')
        imglist.append('OR1338_%s.png')

print(len(imglist))

input_shape = (250, 250, 3)

# parameters change with different cameras
train_max = 1194
val_max = 1535
for i in range(len(imglist)):
    if i < train_max: 
        shutil.move("OR1338_%s.png" % i,  "/train/")
    elif train_max <= i < val_max : 
        shutil.move("OR1338_%s.png" % i, "/validation")
    elif i >= val_max: 
        shutil.move("OR1338_%s.png" % i, "/test")
    else:
        pass

input_shape = (250, 250, 3)

# vgg model

vgg = VGG16(input_shape = input_shape, weights = 'imagenet', include_top = False) #imagenet: image dataset via WordNet hierachy  
output = vgg.layers[-1].output # 
output = keras.layers.Flatten()(output) # flattens last layer, adds channel dimension

vgg_model = Model(vgg.input, output)
vgg_model.trainable = False #freezes weights in the model

# freeze layers in model to use vgg purely as imgae feature extractor
for layer in vgg_model.layers: 
    layer.trainable = False

pd.set_option('max_colwidth', -1)
layers = [(layer, layer.name, layer.trainable) for layer in vgg_model.layers]
vgg_df = pd.DataFrame(layers, columns = ['Layer Type', 'Layer Name', 'Layer Trainable'])
vgg_df.head

# mobilenet model

mobile = MobileNetV2(input_shape = input_shape, weights = 'imagenet', include_top = False)
output = mobile.layers[-1].output
output = keras.layers.Flatten()(output)

mobile_model = Model(mobile.input, output)
mobile_model.trainable = False

# freeze layers in model
for layer in mobile_model.layers:
    layer.trainable = False
    
pd.set_option('max_colwidth', -1)
layers = [(layer, layer.name, layer.trainable) for layer in vgg_model.layers]
mobile_df = pd.DataFrame(layers, columns = ['Layer Type', 'Layer Name', 'Layer Trainable'])
mobile_df.head

target_size = (250, 250)
train_files = glob.glob('/train/*')
train_imgs = [img_to_array(load_img(img, target_size = target_size)) for img in train_files] 
train_imgs = np.array(train_imgs)
train_imgs_scaled = train_imgs.astype('float32')
train_imgs_scaled /= 255

val_files = glob.glob('/validation/*')
val_imgs = [img_to_array(load_img(img, target_size = target_size)) for img in val_files]
val_imgs = np.array(val_imgs)
val_imgs  = val_imgs.astype('float32')
val_imgs /=255

test_files = glob.glob('/test/*')
test_imgs = [img_to_array(load_img(img, target_size = target_size)) for img in val_files]
test_imgs = np.array(val_imgs)
test_imgs  = val_imgs.astype('float32')
test_imgs /=255

def get_bottleneck_features(model, input_imgs):
    a = model.predict(input_imgs, batch_size=10, verbose=0)
    feat_array = np.vstack((a))
    return feat_array

# vgg
train_feat_vgg = get_bottleneck_features(vgg_model, train_imgs)
val_feat_vgg =  get_bottleneck_features(vgg_model, val_imgs)
# mobile
train_feat_mobile = get_bottleneck_features(mobile_model, train_imgs)
val_feat_mobile = get_bottleneck_features(mobile_model, val_imgs)

train_dir = os.path.join(os.getcwd(), 'train')
val_dir = os.path.join(os.getcwd(), 'validation')

labels = OR1338.filter(items = ['trailers', 'passengervehicles', 'largenonfreightvehicles', 'daytime'])
labels.loc[labels['trailers'] > 1.0, 'trailers'] = 1.0
labels.loc[labels['passengervehicles'] > 1.0, 'passengervehicles'] = 1.0
labels.loc[labels['largenonfreightvehicles'] > 1.0] = 1.0
labels.loc[labels['daytime'] == True] = 1.0
labels.loc[labels['daytime'] == False] = 0.0

input_shape_vgg = vgg_model.output_shape[1]

model1 = Sequential()
model1.add(InputLayer(input_shape = (input_shape_vgg,)))
model1.add(Dense(512, activation = 'relu', input_dim=input_shape_vgg))
model1.add(Dropout(0.3))
model1.add(Dense(512, activation = 'relu'))
model1.add(Dropout(0.3))
model1.add(Dense(4, activation='sigmoid')) # logistic function 
model1.compile(loss = 'binary_crossentropy', 
              optimizer = optimizers.RMSprop(lr=1e-4), # 
              metrics = ['accuracy'])
model1.summary()

model1history = model1.fit(train_feat_vgg, 
                   labels[:train_max], 
                   epochs = 30, 
                   batch_size = 100,
                   validation_data = (val_feat_vgg,
                                      labels[train_max:val_max]))

# plot training history 
acc = model1history.history['acc']
val_acc = model1history.history['val_acc']
loss = model1history.history['loss']
val_loss = model1history.history['val_loss']
epochs = range(len(acc))
plt.plot(epochs, acc, 'bo', label = 'Training acc')
plt.plot(epochs, val_acc, 'g', label = 'Validation acc')
plt.title('Model1 Training and Validation Accuracy')
plt.plot(epochs, loss, 'bo', label = 'Training loss')
plt.plot(epochs, val_loss, 'g', label = 'Validation loss')
plt.title('Model1 Training and Validation Loss')
plt.legend()
plt.savefig('VGGBottleneck_model_OR1338_training.png')
model1.save('VGGbottleneck_model_OR1338_training.h5')













