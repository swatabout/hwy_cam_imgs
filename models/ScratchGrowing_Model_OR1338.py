import numpy as np
import PIL, boto3, io, os, glob, tables, shutil, urllib.request 
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

# print(len(imglist))

train_max = 1194
val_max = 1535

# parameters change with different cameras

for i in range(len(imglist)):
    if i < train_max: 
        shutil.move("OR1338_%s.png" % i,  "/train")
    elif train_max <= i < val_max : 
        shutil.move("OR1338_%s.png" % i, "/validation")
    elif val_max <= i:
        shutil.move("OR1338_%s.png" % i, "/test")
    else: 
        pass

target_size = (250, 250)

train_files = glob.glob('/train/*')
train_imgs = [img_to_array(load_img(img, target_size = target_size)) for img in train_files] 
train_imgs = np.array(train_imgs)
train_imgs = train_imgs.astype('float32')
train_imgs /= 255

val_files = glob.glob('/validation/*')
val_imgs = [img_to_array(load_img(img, target_size= target_size)) for img in val_files]
val_imgs = np.array(val_imgs)
val_imgs  = val_imgs.astype('float32')
val_imgs /=255

test_files = glob.glob('/test/*')
test_imgs = [img_to_array(load_img(img, target_size = target_size)) for img in val_files]
test_imgs = np.array(val_imgs)
test_imgs  = val_imgs.astype('float32')
test_imgs /=255

labels = OR1338.filter(items = ['trailers', 'passengervehicles', 'largenonfreightvehicles', 'daytime'])
labels.loc[labels['trailers'] > 1.0, 'trailers'] = 1.0
labels.loc[labels['passengervehicles'] > 1.0, 'passengervehicles'] = 1.0
labels.loc[labels['largenonfreightvehicles'] > 1.0] = 1.0
labels.loc[labels['daytime'] == True] = 1.0
labels.loc[labels['daytime'] == False] = 0.0

input_shape = (250, 250, 3)

# growing model
input_shape=(250, 250, 3)
scratch = Sequential()
scratch.add(Conv2D(16, kernel_size=(3, 3), activation='relu', input_shape=input_shape))
scratch.add(MaxPooling2D(pool_size=(2,2)))

scratch.add(Conv2D(64, kernel_size=(3,3), activation='relu'))
scratch.add(MaxPooling2D(pool_size=(2,2)))

scratch.add(Conv2D(128, kernel_size=(3,3), activation='relu'))
scratch.add(MaxPooling2D(pool_size=(2,2)))

scratch.add(Flatten())
scratch.add(Dense(512, activation='relu'))
scratch.add(Dense(4, activation='sigmoid'))

scratch.compile(loss = 'binary_crossentropy',
             optimizer = optimizers.RMSprop(lr=2e-5), 
             metrics = ['acc'])
scratch.summary()

scratch2_history = scratch.fit(train_imgs, 
                             labels[:train_max],
                             epochs = 30, 
                             batch_size = 30,
                             validation_data = (val_imgs, labels[train_max:val_max]))

# plot training history 
acc = scratch2_history.history['acc']
val_acc = scratch2_history.history['val_acc']
loss = scratch2_history.history['loss']
val_loss = scratch2_history.history['val_loss']
epochs = range(len(acc))
plt.plot(epochs, acc, 'bo', label = 'Training acc')
plt.plot(epochs, val_acc, 'g', label = 'Validation acc')
plt.title('ScratchGrowing Training and Validation Accuracy')
plt.plot(epochs, loss, 'bo', label = 'Training loss')
plt.plot(epochs, val_loss, 'g', label = 'Validation loss')
plt.title('ScratchGrowing Training and Validation Loss')
plt.legend()
plt.savefig('ScratchGrowing_model_OR1338_training.png')
scratch.save('ScratchGrowing_model_OR1338_training.h5')




