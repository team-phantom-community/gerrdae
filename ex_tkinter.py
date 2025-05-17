import tkinter as tk
from threading import Timer

def on_start_button_click():
    """Startボタンがクリックされたときに実行される処理"""
    label.config(text="処理を開始しました！")
    start_button.config(state=tk.DISABLED)  # ボタンを無効化
    Timer(5, enable_start_button).start()  # 5秒後にボタンを有効化

def enable_start_button():
    """Startボタンを再び有効化する処理"""
    start_button.config(state=tk.NORMAL)
    label.config(text="ボタンが再び有効になりました！")

# メインウィンドウを作成
root = tk.Tk()
root.title("Startボタンの無効化例")
root.geometry("300x200")  # ウィンドウサイズを設定

# ラベルを作成
label = tk.Label(root, text="ここにメッセージが表示されます", font=("Arial", 14))
label.pack(pady=20)

# Startボタンを作成
start_button = tk.Button(root, text="Start", command=on_start_button_click, font=("Arial", 14))
start_button.pack(pady=20)

# メインループを開始
root.mainloop()
