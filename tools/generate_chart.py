#!/usr/bin/env python3
"""
Mineconomy 차트 조각 텍스처 + 모델 JSON 생성
실행 위치: mineconomy-resource-pack/
의존성:    pip install Pillow

개요:
    바 차트 셀용 솔리드(16x16 전체 흰색) 텍스처 1개만 생성.
    drawBar()에서 채워진 슬롯에만 이 아이템을 배치하고,
    빈 슬롯에는 아무것도 두지 않는다.
    포션 색상(PotionMeta.color)이 흰색에 곱해져 바 색상이 표시된다.
"""

from PIL import Image
import json, os, shutil

TEXTURE_SIZE = 16
FILL = (255, 255, 255, 255)

TEXTURES_DIR = "assets/minecraft/textures/item/graph"
MODELS_DIR   = "assets/minecraft/models/item/graph"
POTION_JSON  = "assets/minecraft/items/potion.json"

BAR_NAME = "_bar"

def main():
    for d in (TEXTURES_DIR, MODELS_DIR):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)

    # 솔리드 텍스처: 16x16 전체 흰색
    img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), FILL)
    img.save(os.path.join(TEXTURES_DIR, BAR_NAME + ".png"))

    # 단일 레이어 모델
    model = {
        "parent": "item/generated",
        "textures": {"layer0": f"item/graph/{BAR_NAME}"}
    }
    with open(os.path.join(MODELS_DIR, BAR_NAME + ".json"), "w") as f:
        json.dump(model, f, indent=2)

    # items/potion.json: threshold 1.0 → _bar 모델
    os.makedirs(os.path.dirname(POTION_JSON), exist_ok=True)
    potion = {
        "model": {
            "type": "minecraft:range_dispatch",
            "property": "minecraft:custom_model_data",
            "entries": [
                {
                    "threshold": 1.0,
                    "model": {"type": "minecraft:model", "model": f"item/graph/{BAR_NAME}"}
                }
            ],
            "fallback": {"type": "minecraft:model", "model": "item/potion"}
        }
    }
    with open(POTION_JSON, "w") as f:
        json.dump(potion, f, indent=2)

    print(f"솔리드 텍스처 1개 + 모델 1개 / items/potion.json 생성 완료")
    print(f"  텍스처: {TEXTURES_DIR}/{BAR_NAME}.png (16x16 전체 흰색)")
    print(f"  모델: {MODELS_DIR}/{BAR_NAME}.json (단일 레이어)")
    print(f"  CMD 임계값: 1.0")

if __name__ == "__main__":
    main()
