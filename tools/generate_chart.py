#!/usr/bin/env python3
"""
Mineconomy 차트 조각 텍스처 + 모델 JSON 생성
실행 위치: mineconomy-resource-pack/  (서브모듈 루트)
의존성:    pip install Pillow

개요:
    8개 단일 세그먼트 프리미티브를 생성한다.
    각 프리미티브는 16×16 텍스처에서 단 하나의 8×4 구역만 흰색으로 채운다.
    차트 렌더링 시 인벤토리 슬롯 여러 개에 개별적으로 배치하고,
    PotionMeta.setColor()로 색상을 지정한다.
    어떤 슬롯을 채울지는 플러그인 코드에서 결정 → F자 패턴 원천 불가.

인벤토리 슬롯 배치 (2열 × 4행 그리드, 위→아래):
    [bit7 CMD=1][bit6 CMD=2]  ← 상단
    [bit5 CMD=3][bit4 CMD=4]
    [bit3 CMD=5][bit2 CMD=6]
    [bit1 CMD=7][bit0 CMD=8]  ← 하단

custom_model_data: 1(bit7, 좌상단) ~ 8(bit0, 우하단)
채움 순서 예시 (아래→위, 좌→우): CMD 7→8→5→6→3→4→1→2
"""

from PIL import Image
import json, os, shutil

# ── 설정 ──────────────────────────────────────────────────────────────────────

TEXTURE_SIZE = 16
COLS, ROWS   = 2, 4
SEG_W        = TEXTURE_SIZE // COLS   # 8 px
SEG_H        = TEXTURE_SIZE // ROWS   # 4 px

FILL = (255, 255, 255, 255)   # 흰색 (불투명) — PotionMeta.setColor()로 착색됨
BG   = (0,   0,   0,   0)    # 투명

TEXTURES_DIR = "assets/minecraft/textures/item/graph"
MODELS_DIR   = "assets/minecraft/models/item/graph"
POTION_JSON  = "assets/minecraft/items/potion.json"   # 1.21.4+ item definition

# bit7=0 ~ bit0=7 순서로 세그먼트 인덱스 매핑
# segment = 7 - bit  →  col = segment % 2,  row = segment // 2
PRIMITIVES = [
    # (cmd, bit, name)
    (1, 7, "_bit7"),  # 좌상단
    (2, 6, "_bit6"),  # 우상단
    (3, 5, "_bit5"),
    (4, 4, "_bit4"),
    (5, 3, "_bit3"),
    (6, 2, "_bit2"),
    (7, 1, "_bit1"),
    (8, 0, "_bit0"),  # 우하단
]

# ── 실행 ──────────────────────────────────────────────────────────────────────

def main():
    for d in (TEXTURES_DIR, MODELS_DIR):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)

    entries = []

    for cmd, bit, name in PRIMITIVES:
        # ── PNG 생성 ──────────────────────────────────────────────────────────
        img = Image.new("RGBA", (TEXTURE_SIZE, TEXTURE_SIZE), BG)
        px  = img.load()

        segment = 7 - bit
        col = segment % COLS
        row = segment // COLS
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

    print(f"생성 완료: {len(entries)}개 프리미티브 텍스처 / 모델 / items/potion.json")
    print()
    print("슬롯 배치 (2×4 그리드):")
    print("  [bit7 CMD=1][bit6 CMD=2]  ← 상단")
    print("  [bit5 CMD=3][bit4 CMD=4]")
    print("  [bit3 CMD=5][bit2 CMD=6]")
    print("  [bit1 CMD=7][bit0 CMD=8]  ← 하단")
    print()
    print("코드 사용법:")
    print("  - 채울 슬롯: potion item, CMD=해당 비트 번호, PotionMeta.setColor(color)")
    print("  - 빈 슬롯: 다른 아이템(예: 어두운 유리판) 또는 빈 슬롯")
    print("  - 채움 순서(하단→상단): CMD 7→8→5→6→3→4→1→2")

if __name__ == "__main__":
    main()
