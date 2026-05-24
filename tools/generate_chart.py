#!/usr/bin/env python3
"""
Mineconomy 차트 조각 텍스처 + 모델 JSON 생성
실행 위치: mineconomy-resource-pack/
의존성:    pip install Pillow

개요:
    비트 하나당 PNG 하나(총 16개)를 생성하고,
    레벨 모델 JSON에서 layer 조합으로 렌더링한다.

    비트 배치 (MSB=bit15, LSB=bit0):
        bit15 bit14 bit13 bit12   ← row 0 (top)
        bit11 bit10  bit9  bit8   ← row 1
         bit7  bit6  bit5  bit4   ← row 2
         bit3  bit2  bit1  bit0   ← row 3 (bottom)

    bar 채움 순서: row3 왼→오른, row2 왼→오른, ... (level 1~16)
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

# level i 에서 채워지는 셀의 비트 위치 (row3 왼→오른, row2 왼→오른, ...)
FILL_ORDER = [
    (3 - row) * 4 + (3 - col)
    for row in range(3, -1, -1)
    for col in range(4)
]

def bit_name(bit: int) -> str:
    return "_" + format(1 << bit, "016b")

def level_pattern(level: int) -> int:
    pattern = 0
    for i in range(level):
        pattern |= (1 << FILL_ORDER[i])
    return pattern

def pattern_name(pattern: int) -> str:
    return "_" + format(pattern, "016b")

def main():
    for d in (TEXTURES_DIR, MODELS_DIR):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)

    # ── 기본 텍스처 16개: 비트 하나씩 ────────────────────────────────────────
    for bit in range(16):
        row = 3 - (bit // 4)
        col = 3 - (bit % 4)
        img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), BG)
        px  = img.load()
        x0, y0 = col * CELL_SIZE, row * CELL_SIZE
        for x in range(x0, x0 + CELL_SIZE):
            for y in range(y0, y0 + CELL_SIZE):
                px[x, y] = FILL
        img.save(os.path.join(TEXTURES_DIR, bit_name(bit) + ".png"))

    # ── 레벨 모델 JSON 16개: 각 비트 텍스처를 layer로 조합 ───────────────────
    entries = []

    for level in range(1, 17):
        pattern = level_pattern(level)
        name    = pattern_name(pattern)
        cmd     = float(pattern)

        textures = {}
        layer = 0
        for bit in range(16):
            if pattern & (1 << bit):
                textures[f"layer{layer}"] = f"item/graph/{bit_name(bit)}"
                layer += 1

        model = {"parent": "item/generated", "textures": textures}
        with open(os.path.join(MODELS_DIR, name + ".json"), "w") as f:
            json.dump(model, f, indent=2)

        entries.append({
            "threshold": cmd,
            "model": {"type": "minecraft:model", "model": f"item/graph/{name}"}
        })

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

    print(f"기본 텍스처 16개 + 레벨 모델 {len(entries)}개 / items/potion.json 생성 완료")

if __name__ == "__main__":
    main()
