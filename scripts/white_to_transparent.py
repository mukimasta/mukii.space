#!/usr/bin/env python3
"""Remove near-white paper background from a scan; write PNG with alpha."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument(
        "--threshold",
        type=float,
        default=238.0,
        help="RGB min channel; above this (and similar channels) -> transparent",
    )
    p.add_argument(
        "--spread",
        type=float,
        default=18.0,
        help="Max R/G/B spread to treat as neutral (paper), not ink",
    )
    args = p.parse_args()

    img = Image.open(args.input).convert("RGB")
    arr = np.asarray(img, dtype=np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    # Near-white flat regions (paper); colored ink has channel imbalance or lower value
    neutral = (
        (r >= args.threshold)
        & (g >= args.threshold)
        & (b >= args.threshold)
        & (np.abs(r - g) <= args.spread)
        & (np.abs(r - b) <= args.spread)
        & (np.abs(g - b) <= args.spread)
    )

    out = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
    out[:, :, :3] = arr.astype(np.uint8)
    out[:, :, 3] = np.where(neutral, 0, 255)

    Image.fromarray(out, "RGBA").save(args.output, optimize=True)
    print(f"Wrote {args.output} ({out.shape[1]}x{out.shape[0]})")


if __name__ == "__main__":
    main()
