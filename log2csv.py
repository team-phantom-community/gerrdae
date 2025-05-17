# -*- coding: utf-8 -*-
import csv
import serial
import os
import time

time.sleep(5)
start = time.time()

i = 0  #カウント用
ser = serial.Serial("COM3",115200)  # Arduinoが接続されているCOMポートを指定
#ser = serial.Serial("COM5",9600)  # Arduinoが接続されているCOMポートを指定

os.remove('COM8log.csv')

ser.readline()
time.sleep(0.1)
ser.readline()
time.sleep(0.1)
ser.readline()
time.sleep(0.1)

try:
    while time.time() - start < 20: # 24時間分計測＆保存
    
        filename = "COM8log.csv"
        
        #csvファイルに書き込み
        with open(filename,'a',newline='') as f:  #csvファイルの生成
            writer = csv.writer(f)
                
            #情報の取得
            data1 = float(ser.readline().rstrip().decode(encoding='utf-8'))
            #data1 = ser.readline().rstrip().decode(encoding='utf-8').split(',')
            print(data1)
            # data2 = float(ser.readline().rstrip().decode(encoding='utf-8'))
            
            #データの書き込み
            writer.writerow([float(data1)])  #1行目以降：データ
            #d1 = float(data1)
            #writer.writerow([float(data1[0]),float(data1[1]),float(data1[2])])
    ser.close()  #ポートを閉じる
    print("End")
    
    
except KeyboardInterrupt:
    ser.close()  #ポートを閉じる
    print("End")