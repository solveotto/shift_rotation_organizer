"""
Double Shift Scanner

Scans a strekliste PDF for "<<" markers that indicate double shifts
(a shift that is a continuation of the shift above it).

Outputs a JSON file with pairs of shift numbers that form double shifts.
"""

import os
import re
import json
import sys

# Allow running as standalone script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pdfplumber
from config import conf


# Shift numbers appear in the leftmost column (consistent with strekliste_generator.py)
SHIFT_NR_VISUAL_X_MAX = 50
SHIFT_NR_PATTERN = re.compile(r'^(\d{4,5})(?:-.*)?$')


def scan_double_shifts(pdf_path: str) -> list[dict]:
    """
    Scan a strekliste PDF for "<<" markers and identify double shift pairs.

    The "<<" marker sits on its own row between two shift rows, indicating
    that the shift below it is a continuation of the shift above it.

    Args:
        pdf_path: Path to the strekliste PDF file.

    Returns:
        List of dicts with 'first_shift' (upper) and 'second_shift' (lower/marked) keys.
    """
    double_shifts = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(x_tolerance=3, y_tolerance=2)

            # Separate shift numbers and "<<" markers
            shift_numbers = []
            double_markers = []

            for word in words:
                text = word['text'].strip()
                x = word['x0']
                y_mid = (word['top'] + word['bottom']) / 2

                if text == '<<':
                    double_markers.append({'y': y_mid, 'x': x})
                elif x < SHIFT_NR_VISUAL_X_MAX and SHIFT_NR_PATTERN.match(text):
                    shift_numbers.append({
                        'nr': text,
                        'nr_base': SHIFT_NR_PATTERN.match(text).group(1),
                        'y': y_mid,
                    })

            # Sort shift numbers by y position (top to bottom)
            shift_numbers.sort(key=lambda s: s['y'])

            # For each "<<" marker, find the closest shift above and below it
            for marker in double_markers:
                above_shift = None
                below_shift = None

                for s in shift_numbers:
                    if s['y'] < marker['y']:
                        # Closest shift above the marker
                        if above_shift is None or s['y'] > above_shift['y']:
                            above_shift = s
                    elif s['y'] > marker['y']:
                        # Closest shift below the marker
                        if below_shift is None or s['y'] < below_shift['y']:
                            below_shift = s

                if above_shift is None or below_shift is None:
                    continue

                pair = (above_shift['nr'], below_shift['nr'])
                double_shifts.append(pair)

    # Deduplicate (same pair can appear on multiple pages)
    seen = set()
    unique = []
    for pair in double_shifts:
        if pair not in seen:
            seen.add(pair)
            unique.append({'first_shift': pair[0], 'second_shift': pair[1]})

    return unique


def main():
    version = 'r26'
    pdf_path = os.path.join(
        conf.turnusfiler_dir, version, 'streklister', f'{version}_streker.pdf'
    )
    output_path = os.path.join(
        conf.turnusfiler_dir, version, f'double_shifts_{version}.json'
    )

    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        sys.exit(1)

    print(f"Scanning {pdf_path} for double shift markers...")
    pairs = scan_double_shifts(pdf_path)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(pairs, f, indent=2, ensure_ascii=False)

    print(f"Found {len(pairs)} double shift pairs.")
    print(f"Output written to {output_path}")

    for pair in pairs:
        print(f"  {pair['first_shift']} + {pair['second_shift']}")


if __name__ == '__main__':
    main()
