#!/usr/bin/env python3
"""
List available components by category
"""

import argparse

COMPONENTS = {
    "navigation": ["navbar", "sidebar", "tabs", "breadcrumbs", "pagination", "dropdown"],
    "hero": ["split", "centered", "gradient", "with-form", "with-stats", "video-bg"],
    "cards": ["feature", "product", "profile", "testimonial", "stats", "blog", "pricing"],
    "forms": ["input", "select", "checkbox", "radio", "toggle", "datepicker", "file-upload"],
    "buttons": ["solid", "outline", "ghost", "link", "icon", "group"],
    "layouts": ["grid", "container", "section", "sidebar-layout", "two-column", "centered"],
    "feedback": ["alert", "toast", "modal", "tooltip", "progress", "spinner", "skeleton"],
    "tables": ["basic", "sortable", "striped", "compact", "with-selection"]
}

def main():
    parser = argparse.ArgumentParser(description="List available components")
    parser.add_argument("--category", help="Component category to list")
    args = parser.parse_args()

    if args.category:
        category = args.category.lower()
        if category in COMPONENTS:
            print(f"\n📦 Components in '{category}':")
            for comp in COMPONENTS[category]:
                print(f"   • {comp}")
        else:
            print(f"Category '{category}' not found. Available categories:")
            for cat in COMPONENTS.keys():
                print(f"   • {cat}")
    else:
        print("\n📦 All Component Categories:")
        for cat, items in COMPONENTS.items():
            print(f"\n  {cat.upper()} ({len(items)}):")
            for item in items:
                print(f"    • {item}")

    print("\n💡 Use generate_component.py --type <component> to generate code")

if __name__ == "__main__":
    main()