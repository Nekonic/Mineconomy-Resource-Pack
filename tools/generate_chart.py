#!/usr/bin/env python3
"""
Mineconomy 차트 조각 텍스처 + 모델 JSON 생성
실행 위치: mineconomy-resource-pack/
의존성:    pip install Pillow

개요:
    비트 하나당 PNG 하나(총 16개)를 생성하고,
    각 비트 모델은 단일 레이어(1 layer)로 구성한다.
    drawBar()에서 각 셀마다 해당 비트의 CMD를 사용하므로
    item/generated 5-레이어 한계 문제가 없다.

    비트 배치 (MSB=bit15, LSB=bit0):
        bit15 bit14 bit13 bit12   ← row 0 (top)
        bit11 bit10  bit9  bit8   ← row 1
         bit7  bit6  bit5  bit4   ← row 2
         bit3  bit2  bit1  bit0   ← row 3 (bottom)

    bar 채움 순서: row3 왼→오른, row2 왼→오른, ... (level 1~16)
    CMD = 1 << bit  (개별 비트 값)
"""

from PIL import Image
import json, os, shutil

TEXTURE_SIZE = 16
CELL_SIZE    = 4
FILL = (255, 255, 255, 255)
BG   = (0, 0, 0, 0)

TEXTURES_DIR = "assets/minecraft/textures/item/graph"
MODELS_DIR   = "assets/minecraft/models/item/graph"
POTION_JSON  = "assets/minecraft/items/potion.json"

def bit_name(bit: int) -> str:
    return "_" + format(1 << bit, "016b")

def main():
    for d in (TEXTURES_DIR, MODELS_DIR):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)

    entries = []

    for bit in range(16):
        # 텍스처: 해당 비트 위치에 4×4 셀 하나만 흰색
        row = 3 - (bit // 4)
        col = 3 - (bit % 4)
        img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), BG)
        px  = img.load()
        x0, y0 = col * CELL_SIZE, row * CELL_SIZE
        for x in range(x0, x0 + CELL_SIZE):
            for y in range(y0, y0 + CELL_SIZE):
                px[x, y] = FILL
        img.save(os.path.join(TEXTURES_DIR, bit_name(bit) + ".png"))

        # 모델: 단일 레이어 (1-layer, 5-레이어 한계 안전)
        model = {
            "parent": "item/generated",
            "textures": {"layer0": f"item/graph/{bit_name(bit)}"}
        }
        with open(os.path.join(MODELS_DIR, bit_name(bit) + ".json"), "w") as f:
            json.dump(model, f, indent=2)

        entries.append({
            "threshold": float(1 << bit),
            "model": {"type": "minecraft:model", "model": f"item/graph/{bit_name(bit)}"}
        })

    # threshold 오름차순 정렬 (range_dispatch 요구사항)
    entries.sort(key=lambda e: e["threshold"])

    # ── items/potion.json ─────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(POTION_JSON), exist_ok=True)
    potion = {
        "model": {
            "type": "minecraft:range_dispatch",
            "property": "minecraft:custom_model_data",
            "entries": entries,
            "fallback": {"type": "minecraft:model", "model": "item/potion"}
        }
    }
    with open(POTION_JSON, "w") as f:
        json.dump(potion, f, indent=2)

    print(f"비트 텍스처/모델 {len(entries)}개 (단일 레이어) + items/potion.json 생성 완료")
    print("CMD 값: " + ", ".join(str(int(e['threshold'])) for e in entries))

if __name__ == "__main__":
    main()
