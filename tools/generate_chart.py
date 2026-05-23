#!/usr/bin/env python3
"""
Mineconomy 차트 조각 텍스처 + 모델 JSON 생성
실행 위치: mineconomy-resource-pack/
의존성:    pip install Pillow

개요:
    2개의 텍스처 프리미티브를 생성한다.
      CMD=1 (_full): 16×16 전체 흰색 — 완전히 채워진 행
      CMD=2 (_half): 하단 절반(y=8~15) 흰색 — 부분 채움 행 (bar 최상단)

level 1~8 렌더링 (행 3=최하단, 행 0=최상단):
    level=1  최하단 행 CMD=2 (하단 8px)
    level=2  최하단 행 CMD=1 (16px 전체)
    level=3  최하단 행 CMD=1 + 바로 위 행 CMD=2
    level=4  하단 2행 CMD=1
    level=5  하단 2행 CMD=1 + 바로 위 행 CMD=2
    level=6  하단 3행 CMD=1
    level=7  하단 3행 CMD=1 + 바로 위 행 CMD=2
    level=8  4행 전체 CMD=1
"""

from PIL import Image
import json, os, shutil

# ── 설정 ──────────────────────────────────────────────────────────────────────

TEXTURE_SIZE = 16
FILL = (255, 255, 255, 255)
BG   = (0,   0,   0,   0)

TEXTURES_DIR = "assets/minecraft/textures/item/graph"
MODELS_DIR   = "assets/minecraft/models/item/graph"
POTION_JSON  = "assets/minecraft/items/potion.json"

# (cmd, name, y_start) — y_start..15 범위를 FILL로 채운다
PRIMITIVES = [
    (1, "_full", 0),   # 16px 전체
    (2, "_half", 8),   # 하단 8px
]

# ── 실행 ──────────────────────────────────────────────────────────────────────

def main():
    for d in (TEXTURES_DIR, MODELS_DIR):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)

    entries = []

    for cmd, name, y_start in PRIMITIVES:
        # ── PNG 생성 ──────────────────────────────────────────────────────────
        img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), BG)
        px  = img.load()
        for x in range(TEXTURE_SIZE):
            for y in range(y_start, TEXTURE_SIZE):
                px[x, y] = FILL
        img.save(os.path.join(TEXTURES_DIR, name + ".png"))

        # ── model JSON 생성 ───────────────────────────────────────────────────
        model = {
            "parent": "item/generated",
            "textures": {"layer0": f"item/graph/{name}"},
            "tints": [{"type": "minecraft:potion", "default": 16777215}]
        }
        with open(os.path.join(MODELS_DIR, name + ".json"), "w") as f:
            json.dump(model, f, indent=2)

        entries.append({
            "threshold": cmd,
            "model": {"type": "minecraft:model", "model": f"item/graph/{name}"}
        })

    # ── items/potion.json 재생성 (1.21.4+ range_dispatch 포맷) ────────────────
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

    print(f"생성 완료: {len(entries)}개 프리미티브 / items/potion.json")

if __name__ == "__main__":
    main()
