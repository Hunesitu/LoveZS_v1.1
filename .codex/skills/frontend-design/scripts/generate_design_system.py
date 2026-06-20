#!/usr/bin/env python3
"""
Frontend Design System Generator
Generates complete design systems with colors, typography, spacing, and effects.
"""

import argparse
import json
from pathlib import Path

DESIGN_SYSTEMS = {
    "romantic": {
        "name": "Romantic Elegant",
        "description": "Soft rose tones, warm neutrals, gold accents for luxury feel",
        "colors": {
            "primary": {
                "50": "#fdf2f7",
                "100": "#fce7ef",
                "200": "#f8d1de",
                "300": "#f2abd",
                "400": "#e87fa0",
                "500": "#d95984",
                "600": "#c03d6a",
                "700": "#a12f56",
                "800": "#862847",
                "900": "#6e223b"
            },
            "secondary": {
                "50": "#fefcf8",
                "100": "#fdf8ef",
                "200": "#f9f0d9",
                "300": "#f3e5be",
                "400": "#e8d498",
                "500": "#d4bc70",
                "600": "#b99f52",
                "700": "#9a8242",
                "800": "#7d6837",
                "900": "#66552e"
            },
            "neutral": {
                "50": "#faf8f6",
                "100": "#f5f2ef",
                "200": "#e7e2dd",
                "300": "#d6cdc4",
                "400": "#a89a90",
                "500": "#8a7c72",
                "600": "#5c524a",
                "700": "#423b36",
                "800": "#2d2825",
                "900": "#1a1817"
            },
            "success": {"500": "#558755", "600": "#436d43"},
            "warning": {"500": "#d4a052", "600": "#b98636"},
            "error": {"500": "#c03d6a", "600": "#a12f56"}
        },
        "typography": {
            "heading": {
                "font": "Noto Serif SC",
                "fallback": "Georgia, serif",
                "weights": [400, 500, 600, 700],
                "letter_spacing": "0.02em"
            },
            "body": {
                "font": "Noto Sans SC",
                "fallback": "system-ui, sans-serif",
                "weights": [300, 400, 500, 600]
            },
            "scale": {
                "xs": "0.75rem",
                "sm": "0.875rem",
                "base": "1rem",
                "lg": "1.125rem",
                "xl": "1.25rem",
                "2xl": "1.5rem",
                "3xl": "1.875rem",
                "4xl": "2.25rem",
                "5xl": "3rem"
            }
        },
        "effects": {
            "shadows": {
                "sm": "0 1px 2px rgba(92, 82, 74, 0.05)",
                "md": "0 4px 12px rgba(92, 82, 74, 0.08)",
                "lg": "0 8px 24px rgba(92, 82, 74, 0.1)",
                "xl": "0 16px 48px rgba(92, 82, 74, 0.12)",
                "elevated": "0 2px 6px rgba(92, 82, 74, 0.1), 0 16px 32px rgba(92, 82, 74, 0.08)"
            },
            "border_radius": {
                "sm": "0.375rem",
                "md": "0.625rem",
                "lg": "0.875rem",
                "xl": "1.125rem",
                "full": "9999px"
            },
            "transitions": {
                "fast": "150ms ease",
                "base": "250ms ease",
                "slow": "350ms ease"
            }
        },
        "spacing": {
            "section": "5rem",
            "card": "1.5rem",
            "gutter": "1.25rem"
        }
    },
    "minimal": {
        "name": "Minimal Clean",
        "description": "Ultra clean, spacious design with neutral palette",
        "colors": {
            "primary": {
                "500": "#0f172a",
                "600": "#1e293b"
            },
            "accent": {
                "500": "#3b82f6",
                "600": "#2563eb"
            },
            "neutral": {
                "100": "#f8fafc",
                "200": "#f1f5f9",
                "300": "#e2e8f0",
                "400": "#94a3b8",
                "500": "#64748b",
                "600": "#475569",
                "700": "#334155",
                "800": "#1e293b",
                "900": "#0f172a"
            }
        },
        "typography": {
            "heading": {"font": "Inter"},
            "body": {"font": "Inter"}
        }
    }
}

def main():
    parser = argparse.ArgumentParser(description="Generate frontend design system")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--style", default="romantic", help="Design style")
    parser.add_argument("--industry", help="Industry type")
    parser.add_argument("--type", help="Product type")
    parser.add_argument("--output", default="./design-system.json", help="Output path")

    args = parser.parse_args()

    style = args.style.lower()
    if "elegant" in style or "romantic" in style or "luxury" in style:
        system = DESIGN_SYSTEMS["romantic"]
    else:
        system = DESIGN_SYSTEMS["minimal"]

    output = {
        "project": args.project,
        "style": args.style,
        "industry": args.industry,
        "type": args.type,
        **system
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Design system generated: {output_path}")
    print(f"\nSummary:")
    print(f"   Style: {system['name']}")
    print(f"   Description: {system['description']}")
    print(f"   Primary color: {system['colors']['primary']['500']}")
    print(f"   Heading font: {system['typography']['heading']['font']}")
    print(f"   Body font: {system['typography']['body']['font']}")

if __name__ == "__main__":
    main()