# Emoji and Symbol Ranges (from `banned.txt`)

This document explains the emoji/symbol ranges configured in `banned.txt`, with links to accessible, authoritative Unicode sources. It also outlines practical guidance for carving out exceptions (what you may want to allow) using the project’s allowlist.

- Authoritative, human-friendly source for emoji: https://unicode.org/emoji/charts/full-emoji-list.html
- Authoritative block charts (code charts): https://www.unicode.org/charts/

## How the ban works (quick refresher)
- `banned.txt` supports whole Unicode ranges like `\U0001F600-\U0001F64F` and literal characters on their own lines (e.g., `✅❌`).
- The scanner matches individual code points — complex emoji sequences are matched code point by code point.
- To allow specific characters or phrases without changing ranges, use `allowed.txt` (preferred). It can list literal sequences or `re:` regex patterns that suppress matches inside those spans.

## Ranges in `banned.txt`

| Range (hex) | Name (Unicode block) | What it covers | Examples | Link |
| - | - | - | - | - |
| U+1F600–U+1F64F | Emoticons | Faces and hand gestures (classic “emoji faces”) | 😀 😃 😂 😊 🙏 | https://www.unicode.org/charts/PDF/U1F600.pdf |
| U+1F300–U+1F5FF | Miscellaneous Symbols and Pictographs | Weather, celebration, office, nature, activity, etc. | 🌀 🎯 🎁 🔥 💡 🗿 | https://www.unicode.org/charts/PDF/U1F300.pdf |
| U+1F680–U+1F6FF | Transport and Map Symbols | Vehicles, traffic, map symbols | 🚀 🚁 🚗 🚦 🗺️ | https://www.unicode.org/charts/PDF/U1F680.pdf |
| U+1F1E0–U+1F1FF | Regional Indicator Symbols (“Flags” building blocks) | Flag sequences use pairs of these code points | 🇺🇸 🇬🇧 🇯🇵 🇪🇺 | Included in https://www.unicode.org/charts/PDF/U1F100.pdf (end of chart) |
| U+1F900–U+1FAFF | Supplemental Symbols and Pictographs + Symbols and Pictographs Extended-A | Newer emoji/symbols (objects, body parts, activities, etc.). Note: this span crosses multiple blocks in Unicode. | 🤖 🥳 🧠 🧪 🫠 | https://www.unicode.org/charts/PDF/U1F900.pdf and https://www.unicode.org/charts/PDF/U1FA70.pdf |
| U+2700–U+27BF | Dingbats | Checkmarks, crosses, stars, envelopes, scissors, sparkles | ✂ ✨ ✅ ❌ ➿ | https://www.unicode.org/charts/PDF/U2700.pdf |
| U+2600–U+26FF | Miscellaneous Symbols | Weather, warning, zodiac, phone, recycling, etc. | ☀ ☔ ☕ ☎ ✈ ⚠ ⛔ | https://www.unicode.org/charts/PDF/U2600.pdf |
| U+25A0–U+25FF | Geometric Shapes | Squares, circles, triangles, bullets | ▪ ▫ ▴ ▾ ◼ ◻ ◯ | https://www.unicode.org/charts/PDF/U25A0.pdf |
| U+1F780–U+1F7FF | Geometric Shapes Extended | Colored circles/squares and related shapes | 🟠 🟢 🟣 🟦 🟥 🟩 | https://www.unicode.org/charts/PDF/U1F780.pdf |
| U+2B00–U+2BFF | Miscellaneous Symbols and Arrows | Arrows, stars, miscellaneous symbols | ⬆ ⬇ ⬅ ➡ ⬛ ⬜ ⭐ | https://www.unicode.org/charts/PDF/U2B00.pdf |
| U+1F650–U+1F67F | Ornamental Dingbats | Decorative ornaments (font support varies) | 🕴 🖤 (varies by font) | https://www.unicode.org/charts/PDF/U1F650.pdf |

Notes:
- “Flags” are not a single block; they are sequences built from U+1F1E6–U+1F1FF Regional Indicators. The link above covers the parent block where they live.
- The U+1F900–U+1FAFF span crosses more than one block in Unicode. It is grouped here because it aligns with modern emoji additions; the charts linked cover the relevant blocks in that span.

## Literal characters explicitly banned

These appear as literal entries in `banned.txt` and will be matched even if you remove a broader range. Names are per Unicode; links are to the corresponding block charts.

| Character | Code point(s) | Unicode name | Notes | Link |
| - | - | - | - | - |
| ✅ | U+2705 | WHITE HEAVY CHECK MARK | From Dingbats | https://www.unicode.org/charts/PDF/U2700.pdf |
| ❌ | U+274C | CROSS MARK | From Dingbats | https://www.unicode.org/charts/PDF/U2700.pdf |
| ⚠️ | U+26A0 U+FE0F | WARNING SIGN + VARIATION SELECTOR-16 | VS-16 forces emoji style | https://www.unicode.org/charts/PDF/U2600.pdf |
| ✓ | U+2713 | CHECK MARK | Text-style check | https://www.unicode.org/charts/PDF/U2700.pdf |
| ❗️ | U+2757 U+FE0F | HEAVY EXCLAMATION MARK SYMBOL + VS-16 | Often shown as emoji | https://www.unicode.org/charts/PDF/U2700.pdf |
| ⭐️ | U+2B50 U+FE0F | WHITE MEDIUM STAR + VS-16 | Emoji-styled star | https://www.unicode.org/charts/PDF/U2B00.pdf |

Tip: Many symbols have both a “text” presentation and an “emoji” presentation. The optional U+FE0F (VS-16) requests emoji presentation. The scanner bans per code point; the VS-16 itself will also match as a banned code point when included in ranges/literals.

## Deciding what to allow

If you need some symbols for documentation or UI hints, consider these common, low-risk exceptions. Prefer adding allowances in `allowed.txt` rather than removing ranges, because ranges are broad and subtracting a single code point isn’t supported in `banned.txt`.

- Check marks: U+2713 (✓) and U+2705 (✅) for status tables.
- Cross mark: U+274C (❌) for failure indicators.
- Warning sign: U+26A0 (⚠), optionally with VS-16 for emoji style (⚠️).
- Stars: U+2B50 (⭐), optionally with VS-16 (⭐️), for ratings/emphasis.
- Plain geometric bullets: selected items from U+25A0–U+25FF if you want non-emoji bullets. Note some fonts render them as glyphs, not emoji, which may be acceptable.

How to allow them (recommended):
1) Add exact literals to `allowed.txt` (one per line), e.g.

```
# allowed.txt
✅
❌
⚠️
✓
⭐️
```

2) Or allow phrases to reduce accidental use, e.g. allow star only in a heading:

```
re:^\s*⭐️\s+Important\b
```

3) Run the scanner with your allowlist:
- `uv run python main.py scan ./vault --banned banned.txt --allowed allowed.txt`

What not to do (unless you accept broad allowance):
- Removing or shrinking a large range (e.g., Dingbats U+2700–U+27BF) just to permit one character. That re-introduces many other symbols unintentionally. Use `allowed.txt` instead.

## Quick reference by intent

- Faces/people/gestures: U+1F600–U+1F64F, U+1F900–U+1FAFF
- Objects/activities/nature: U+1F300–U+1F5FF, U+1F680–U+1F6FF, U+1F900–U+1FAFF
- Flags: U+1F1E0–U+1F1FF (as sequences)
- Symbols (check, cross, warning, stars): U+2600–U+26FF, U+2700–U+27BF, U+2B00–U+2BFF
- Shapes (bullets, squares, circles): U+25A0–U+25FF, U+1F780–U+1F7FF

## Useful links (authoritative)
- Full emoji list (searchable, with names): https://unicode.org/emoji/charts/full-emoji-list.html
- Emoji sequences and presentations: https://unicode.org/reports/tr51/
- Unicode code charts index: https://www.unicode.org/charts/

