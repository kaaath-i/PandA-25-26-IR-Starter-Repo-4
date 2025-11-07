#!/usr/bin/env python3
"""Part 2 starter CLI (students complete manual substring search + highlighting)."""
from typing import List, Dict, Tuple
from constants import BANNER, HELP
from sonnets import SONNETS

def find_spans(text: str, pattern: str):
    """Return [(start, end), ...] for all (possibly overlapping) matches.
    Inputs should already be lowercased by the caller."""

    spans = []

    for i in range(len(text)-len(pattern)+1):
        if text[i:i+len(pattern)] == pattern:
            spans.append((i, i + len(pattern)))

    return spans


def ansi_highlight(text: str, spans):
    if not spans:
        return text
    spans = sorted(spans)
    merged = []
    for s, e in spans:
        if not merged or s > merged[-1][1]:
            merged.append([s, e])
        else:
            merged[-1][1] = max(merged[-1][1], e)
    out, i = [], 0
    for s, e in merged:
        if s > i:
            out.append(text[i:s])
        out.append("\x1b[1m\x1b[43m")
        out.append(text[s:e])
        out.append("\x1b[0m")
        i = e
    out.append(text[i:])
    return "".join(out)


def search_sonnet(sonnet, query: str):
    title_raw = str(sonnet["title"])
    lines_raw = sonnet["lines"]  # list[str]

    q = query.lower()
    title_spans = find_spans(title_raw.lower(), q)

    line_matches = []
    for idx, line_raw in enumerate(lines_raw, start=1):  # 1-based line numbers
        spans = find_spans(line_raw.lower(), q)
        if spans:
            line_matches.append({"line_no": idx, "text": line_raw, "spans": spans})

    total = len(title_spans) + sum(len(lm["spans"]) for lm in line_matches)
    return {
        "title": title_raw,
        "title_spans": title_spans,
        "line_matches": line_matches,
        "matches": total,
    }


def print_results(query: str, results, highlight: bool):
    total_docs = len(results)
    matched = [r for r in results if r["matches"] > 0]
    print(f'{len(matched)} out of {total_docs} sonnets contain "{query}".')

    for idx, r in enumerate(matched, start=1):
        title_line = ansi_highlight(r["title"], r["title_spans"]) if highlight else r["title"]
        print(f"\n[{idx}/{total_docs}] {title_line}")
        for lm in r["line_matches"]:
            line_out = ansi_highlight(lm["text"], lm["spans"]) if highlight else lm["text"]
            print("  " + line_out)

def combine_results(result1, result2):
    # ToDo 1) Copy your solution from exercise 3

    total_title_spans = result1["title_spans"] + result2["title_spans"]
    result1["title_spans"] = total_title_spans

    total_line_matches = []
    seen_line_nos = set()
    for line_entry1 in result1["line_matches"]:
        found_match = False
        for line_entry2 in result2["line_matches"]:
            if line_entry1["line_no"] == line_entry2["line_no"]:
                spans1 = line_entry1["spans"]
                spans2 = line_entry2["spans"]

                merged_spans = list({tuple(s) for s in spans1} | {tuple(s) for s in spans2})
                merged_spans.sort(key=lambda s: s[0])

                merged_entry = {
                    "line_no": line_entry1["line_no"],
                    "text": line_entry1["text"],
                    "spans": merged_spans,
                }

                total_line_matches.append(merged_entry)
                seen_line_nos.add(line_entry1["line_no"])
                found_match = True
                break
        if not found_match:
            total_line_matches.append(line_entry1)
            seen_line_nos.add(line_entry1["line_no"])
    for line_entry2 in result2["line_matches"]:
        if line_entry2["line_no"] not in seen_line_nos:
            total_line_matches.append(line_entry2)
            seen_line_nos.add(line_entry2["line_no"])
    total_line_matches.sort(key=lambda entry: entry["line_no"])
    result1["line_matches"] = total_line_matches

    total_matches = result1["matches"] + result2["matches"]
    result1["matches"] = total_matches

    combined = {
        "title": result1["title"],
        "title_spans": total_title_spans,
        "line_matches": total_line_matches,
        "matches": total_matches,
    }

    return combined

def main() -> None:
    # ToDo 2 - Part 1 - Introduce a new variable to store the current search mode

    search_mode = "AND"

    highlight = True
    print(BANNER)
    print()  # blank line after banner
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not raw:
            continue

        if raw.startswith(":"):
            if raw == ":quit":
                print("Bye.")
                break
            if raw == ":help":
                print(HELP)
                continue
            if raw.startswith(":highlight"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].lower() in ("on", "off"):
                    highlight = (parts[1].lower() == "on")
                    print("Highlighting", "ON" if highlight else "OFF")
                else:
                    print("Usage: :highlight on|off")
                continue

            # ToDo 2 - Part 1 - Copy the logic from the highlight feature and adapt it for the search-mode

            if raw.startswith(":search-mode"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].upper() in ("AND", "OR"):
                    search_mode = parts[1].upper()
                    print("Search mode set to", search_mode)
                else:
                    print("Usage: :search-mode AND|OR")
                continue


            print("Unknown command. Type :help for commands.")
            continue

        # query
        combined_results = []

        #  ToDo 1) Copy your solution from exercise 3
        words = raw.split()

        for word in words:
            # Searching for the word in all sonnets
            results = [search_sonnet(s, word) for s in SONNETS]

            if not combined_results:
                # No results yet. We store the first list of results in combined_results
                combined_results = results
            else:
                # We have an additional result, we have to merge the two results: loop all sonnets
                for i in range(len(combined_results)):
                    # Checking each sonnet individually
                    combined_result = combined_results[i]
                    result = results[i]

                    # ToDo 2 - Part 2: Here you have to find a way to extend for logical OR searches

                    if search_mode == "AND":
                        if combined_result["matches"] > 0 and result["matches"] > 0:
                            combined_results[i] = combine_results(combined_result, result)
                        else:
                            combined_result["matches"] = 0
                    elif search_mode == "OR":
                        if combined_result["matches"] > 0 or result["matches"] > 0:
                            combined_results[i] = combine_results(combined_result, result)
                        else:
                            combined_result["matches"] = 0


        print_results(raw, combined_results, highlight)

if __name__ == "__main__":
    main()