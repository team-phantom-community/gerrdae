import pandas as pd
import numpy as np

extract_length = 5000  # 抽出するデータの長さ
error_threshold = 4  # 許容するエラーのpersentage
error_count = 3  # 許容するエラーの回数

# CSVファイルを読み込む
file_path = './walk/20250302_193319_log.csv'  # ファイルパスを指定してください
data = pd.read_csv(file_path, header=None)
# データをnumpy配列に変換
data_array = data.values.flatten()
print(data_array)

# 初期の平均値を計算（データの最初の10個で計算）
avr = np.mean(data_array[:10])

# 許容範囲を計算
lower_bound = avr * (1 - error_threshold / 100)
upper_bound = avr * (1 + error_threshold / 100)

# データ抽出
def extract_data(data_array, avr, lower_bound, upper_bound):
    results = []
    i = 10  # 最初の10個のデータはすでに平均値の計算に使用
    while i < len(data_array) - 9 - extract_length:
        window = data_array[i:i+10]
        # 許容範囲を更新
        lower_bound = avr * (1 - error_threshold / 100)
        upper_bound = avr * (1 + error_threshold / 100)

        if np.sum((window < lower_bound) | (window > upper_bound)) >= error_count:
            results.append(data_array[i:i+extract_length])
            i += extract_length  # 次のチェックを3000個分先に進める
        else:
            i += 1
        
        # 平均値を更新
        avr = (avr * 9999 + data_array[i]) / 10000

    return results

# 抽出されたデータを取得
extracted_data_list = extract_data(data_array, avr, lower_bound, upper_bound)

# 抽出されたデータを個別のCSVファイルに保存
for idx, extracted_data in enumerate(extracted_data_list):
    output_file_path = f'extracted_data_{idx+1}.csv'
    pd.DataFrame(extracted_data).to_csv(output_file_path, index=False, header=False)
    print(f'data saved -> {output_file_path}')
