import os
from PIL import Image
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

class ImageDescriptionRequest(BaseModel):
    hp: int
    attack: int
    speed: int
    discription: str


image_path = "pikachu_modoki.png"

image = Image.open(image_path)

prompt = """
あなたは有名なゲームクリエイターです。
今あなたは新たなRPGゲームを製作しようとしています。
同じ職場のイラストレーターが書いた絵を見て、ゲームキャラクターのステータスを考えてください。
ステータスは体力(hp)、攻撃力(attack)、素早さ(speed)、説明(discription)の3つです。
hp: 0~100
attack: 0~100
speed: 0~100
discription: キャラの特徴を日本語で簡潔に述べてください。
"""

client = genai.Client()
response = client.models.generate_content(
    model=os.getenv("MODEL_NAME"),
    contents=[prompt, image],
    config={
        "response_mime_type": "application/json",
        "response_schema": list[ImageDescriptionRequest],
    },
)



print(response.text)