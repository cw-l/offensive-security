#!/usr/bin/env python3
"""
get_comments.py
---------------
Extracts HTML and JavaScript comments from a webpage's source code.
Designed to be used with curl via stdin piping.

Usage:
    curl -s https://example.com | python3 get_comments.py
    curl -s https://example.com | python3 get_comments.py --html-only
    curl -s https://example.com | python3 get_comments.py --js-only
    curl -s https://example.com | python3 get_comments.py --no-color

Author: @cw-l github.com/cw-l
Generated with assistance from Claude (Anthropic)
License: GNU Affero General Public License v3.0 (AGPLv3)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import re
import argparse


# ── ANSI color codes ──────────────────────────────────────────────────────────
class Color:
    HEADER   = "\033[95m"
    CYAN     = "\033[96m"
    GREEN    = "\033[92m"
    YELLOW   = "\033[93m"
    RED      = "\033[91m"
    BOLD     = "\033[1m"
    DIM      = "\033[2m"
    RESET    = "\033[0m"


def colorize(text, *codes):
    return "".join(codes) + text + Color.RESET


# ── Extraction logic ──────────────────────────────────────────────────────────
def get_html_comments(html: str) -> list[str]:
    """Get <!-- ... --> style HTML comments."""
    return re.findall(r'<!--.*?-->', html, re.DOTALL)


def get_js_single_comments(html: str) -> list[str]:
    """
    Get // single-line JS comments.
    Excludes:
      - URLs (http:// https://)
      - Protocol-relative URLs (//)
      - // inside quoted strings (best effort)
    """
    # Match // that is preceded by whitespace or start-of-line, not followed by http/https or just /
    pattern = r'(?:^|(?<=\s))//(?!/|https?:).*?$'
    return re.findall(pattern, html, re.MULTILINE)


def get_js_multi_comments(html: str) -> list[str]:
    """Extract /* ... */ style JS multi-line comments."""
    return re.findall(r'/\*.*?\*/', html, re.DOTALL)


# ── Display helpers ───────────────────────────────────────────────────────────
def print_section(title: str, comments: list[str], use_color: bool):
    if use_color:
        print(colorize(f"\n{'═' * 50}", Color.DIM))
        print(colorize(f"  {title} ({len(comments)} found)", Color.BOLD, Color.CYAN))
        print(colorize(f"{'═' * 50}", Color.DIM))
    else:
        print(f"\n{'=' * 50}")
        print(f"  {title} ({len(comments)} found)")
        print(f"{'=' * 50}")

    if not comments:
        msg = "  No comments found."
        print(colorize(msg, Color.DIM) if use_color else msg)
        return

    for i, comment in enumerate(comments, 1):
        stripped = comment.strip()
        if use_color:
            print(colorize(f"[{i}] ", Color.YELLOW) + colorize(stripped, Color.GREEN))
        else:
            print(f"[{i}] {stripped}")


def print_summary(html_count, js_single_count, js_multi_count, use_color):
    total = html_count + js_single_count + js_multi_count
    summary = (
        f"\n  Summary: {total} total comment(s) found  "
        f"[HTML: {html_count} | JS Single: {js_single_count} | JS Multi: {js_multi_count}]"
    )
    if use_color:
        print(colorize("\n" + "═" * 50, Color.DIM))
        print(colorize(summary, Color.BOLD, Color.HEADER))
        print(colorize("═" * 50, Color.DIM))
    else:
        print("\n" + "=" * 50)
        print(summary)
        print("=" * 50)


# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        description="Get HTML and JS comments from a webpage piped via curl.",
        epilog="Example: curl -s https://example.com | python3 get_comments.py"
    )
    parser.add_argument("--html-only",  action="store_true", help="Show only HTML comments")
    parser.add_argument("--js-only",    action="store_true", help="Show only JS comments")
    parser.add_argument("--no-color",   action="store_true", help="Disable colored output")
    return parser.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    use_color = not args.no_color and sys.stdout.isatty() or not args.no_color

    if sys.stdin.isatty():
        print("No input detected. Pipe HTML content via curl:")
        print("  curl -s https://example.com | python3 get_comments.py")
        sys.exit(1)

    html = sys.stdin.read()

    if not html.strip():
        print("Input is empty. Make sure curl returned content.")
        sys.exit(1)

    html_comments    = get_html_comments(html) if not args.js_only else []
    js_single        = get_js_single_comments(html) if not args.html_only else []
    js_multi         = get_js_multi_comments(html) if not args.html_only else []

    if use_color:
        print(colorize("\n  🔍 Get Webpage Comments", Color.BOLD, Color.HEADER))

    if not args.js_only:
        print_section("HTML Comments  <!-- -->", html_comments, use_color)

    if not args.html_only:
        print_section("JS Single-line Comments  //", js_single, use_color)
        print_section("JS Multi-line Comments  /* */", js_multi, use_color)

    print_summary(len(html_comments), len(js_single), len(js_multi), use_color)


if __name__ == "__main__":
    main()
