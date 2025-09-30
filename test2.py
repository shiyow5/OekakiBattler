import cv2
import numpy as np

input_path = './data/characters/S__14188554.jpg'
output_path = './shiba-inu-remove.png'

# 画像の読み込み
image = cv2.imread(input_path)

# 画像をグレースケールに変換
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# しきい値処理で背景をマスク
_, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)  # 背景が白の場合

# 元画像とマスクを組み合わせて背景削除
result = cv2.bitwise_and(image, image, mask=mask)

# 背景を透明にするためにアルファチャンネルを追加
b, g, r = cv2.split(result)
alpha = mask
rgba = cv2.merge([b, g, r, alpha])

# 保存
cv2.imwrite(output_path, rgba)