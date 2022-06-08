import math
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import imagenet_utils
from tensorflow.keras.utils import to_categorical
import os

model_path = os.path.join(os.path.dirname(__file__), 'model/checkpoint')
print('model_path', model_path)
model = tf.keras.models.load_model(model_path)
classes = ['1.5', '2.5', '3.5', '4.5', '5.5', 'hb', 'sb', 'x']

def analyze(src):
  img = image.load_img(src, target_size=(224, 224))
  # plt.imshow(img)

  img = image.img_to_array(img)
  img = np.expand_dims(img, axis=0)
  # img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
  # print(img)
  predictions = model.predict(img)[0]
  
  return dict(zip(classes, [math.floor(float(p) * 100 + 0.5) for p in predictions]))