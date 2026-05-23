#!/usr/bin/env python3
"""
Mineconomy 차트 조각 텍스처 + 모델 JSON 일괄 생성
실행 위치: mineconomy-resource-pack/  (서브모듈 루트)
의존성:    pip install Pillow

비트 레이아웃 (2열 × 4행, 위→아래 / 좌→우):
    [bit7][bit6]  ← top
    [bit5][bit4]
    [bit3][bit2]
    [bit1][bit0]  ← bottom

custom_model_data:
    mask (1–255) 을 그대로 CMD 값으로 사용
    예) 0b00000001 = 1  → 우하단 하나만
        0b11111111 = 255 → 전체 채움
"""

from PIL import Image
import json, os, shutil

# ── 설정 ──────────────────────────────────────────────────────────────────────

TEXTURE_SIZE = 16
COLS, ROWS   = 2, 4
SEG_W        = TEXTURE_SIZE // COLS   # 8 px
SEG_H        = TEXTURE_SIZE // ROWS   # 4 px

FILL = (255, 255, 255, 255)   # 흰색 (불투명)
BG   = (0,   0,   0,   0)    # 투명

TEXTURES_DIR = "assets/minecraft/textures/item/graph"
MODELS_DIR   = "assets/minecraft/models/item/graph"
POTION_JSON  = "assets/minecraft/models/item/potion.json"

# ── 실행 ──────────────────────────────────────────────────────────────────────

def main():
    # 기존 파일 전부 교체
    for d in (TEXTURES_DIR, MODELS_DIR):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)

    overrides = []

    for mask in range(1, 256):
        name = f"_{mask:08b}"   # e.g. _00000001

        # ── PNG 생성 ──────────────────────────────────────────────────────────
        img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), BG)
        px  = img.load()

        for bit in range(8):
            if mask & (1 << (7 - bit)):   # bit7 = 맨 위 왼쪽 … bit0 = 맨 아래 오른쪽
                col = bit % COLS
                row = bit // COLS
                x0  = col * SEG_W
                y0  = row * SEG_H
                for x in range(x0, x0 + SEG_W):
                    for y in range(y0, y0 + SEG_H):
                        px[x, y] = FILL

        img.save(os.path.join(TEXTURES_DIR, name + ".png"))

        # ── model JSON 생성 ───────────────────────────────────────────────────
        model = {
            "parent": "item/generated",
            "textures": {"layer0": f"item/graph/{name}"}
        }
        with open(os.path.join(MODELS_DIR, name + ".json"), "w") as f:
            json.dump(model, f, indent=2)

        overrides.append({
            "predicate": {"custom_model_data": mask},
            "model": f"item/graph/{name}"
        })

    # ── potion.json 재생성 ────────────────────────────────────────────────────
    potion = {
        "parent": "item/handheld",
        "textures": {"layer0": "item/potion"},
        "overrides": overrides
    }
    with open(POTION_JSON, "w") as f:
        json.dump(potion, f, indent=2)

    print(f"생성 완료: {len(overrides)}개 텍스처 / 모델 / potion.json")
    print()
    print("비트 레이아웃:")
    print("  [bit7][bit6]  ← 상단")
    print("  [bit5][bit4]")
    print("  [bit3][bit2]")
    print("  [bit1][bit0]  ← 하단")
    print()
    print("CMD 범위: 1 (0b00000001) ~ 255 (0b11111111)")
    print("바 차트 예시 (아래→위 순서로 채움):")
    for level in range(9):
        mask_val = (1 << level) - 1  # 하위 level 비트 모두 set
        # 비트를 아래에서 위로 채우려면 bit0=하단우, bit7=상단좌 기준 반전 필요
        # 실제 채움 순서는 플러그인 렌더러에서 결정
        print(f"  level {level}/8 → mask 0b{mask_val:08b} = {mask_val}")

if __name__ == "__main__":
    main()