# importセクション
import tensorflow as tf
import pandas as pd

import numpy as np
import io
import os

print(tf.__version__)

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(100,)),
    tf.keras.layers.Dense(100, activation='sigmoid'),
    tf.keras.layers.Dense(10, activation='relu'),#１層目の大きさを入力データ数に合わせて変える
    tf.keras.layers.Dense(2, activation=tf.nn.softmax) #最終層も同じ
])

# print(len(data[0]))
model.load_weights('./savedweight.weights.h5')
model.summary()

section = ["non-walk", "walk"]

data_array = []
file_path = "fft_data_20250308_162904_3.csv"
print(file_path)
df = pd.read_csv(file_path, header=None, usecols=[0])
data_array.append(df[0].tolist())  # 1列目のデータをdata_arrayに追加
data_array = np.array(data_array)
#正規化
data_generalized = data_array / np.amax(data_array)
print(data_generalized)

data_generalized_tensor = tf.convert_to_tensor(data_generalized, dtype=tf.float32)

p = model.predict(data_generalized_tensor)
print(p[0])

print(section[round(p[0][1])])