#!/usr/bin/env python3
"""Deterministic ASD-STE100 violation counter — merged heuristic set.

Combines two prior linters, both MIT:
  - AminBlg/SimpleEnglish  ste_lint.py : structure, procedural/descriptive split,
    banned modals, perfect tense, "-ing" clauses, Latin abbreviations,
    trailing conditions, synonym rotation, self-test.
  - woosal1337/blog        ste-lint.py : passive voice, "-ing" main verbs,
    nominalizations, phrasal verbs, marketing adjectives, modal hedges,
    paragraph length, em-dash reporting, multi-file summary mode.

Additions here:
  - Passive voice counts in procedural text only. STE requires active voice in
    procedures (Rule 3.6) but allows passive in descriptive text when the actor
    is unknown, which a regex cannot judge. In descriptive mode it is reported
    under `advisory` and left out of the total.
  - `--fail-over N` exits 1 when violations per 100 words exceeds N, for CI.
  - Em dashes are reported, never counted: STE bans the semicolon, not the dash.

Known ceiling: this is a regex pass, not a grammar parser. It has no
part-of-speech data, so it cannot check one-word-one-meaning, noun-cluster
length, or whether a technical noun is the right one. "has been updated" counts
twice on purpose (Rule 3.4 perfect tense and Rule 3.6 passive voice are two
violations). Numbers are comparable between texts run through the same version.
They are not a compliance verdict. No tool can guarantee STE compliance.

Usage:
  python3 ste_lint.py --type procedural file.md
  python3 ste_lint.py --type descriptive docs/*.md          # summary table
  python3 ste_lint.py --type procedural --fail-over 1.0 r.md  # CI gate
  cat text.md | python3 ste_lint.py --type descriptive -
  python3 ste_lint.py --self-test
"""
import glob
import json
import os
import re
import sys

BE = r"(?:am|is|are|was|were|be|been|being)"
PP_IRREG = (r"(?:done|made|sent|read|built|kept|held|set|put|run|written|shown|given|taken|"
            r"found|got|gotten|seen|known|thrown|drawn|lost|left|dealt)")

BANNED_MODALS = re.compile(r"\b(should|would|may|might|could)\b", re.I)
PERFECT = re.compile(r"\b(has|have|had)\s+been\b|\b(has|have)\s+\w+ed\b", re.I)
CONTRACTION = re.compile(
    r"\b\w+(n't|'ll|'re|'ve|'d)\b"
    # only the unambiguous "'s" contractions; the rest are possessives
    r"|\b(it|he|she|that|there|here|what|who|let|one|where|how)'s\b", re.I)
ING_CLAUSE = re.compile(
    r",\s*(mak|allow|enabl|ensur|highlight|creat|provid|offer|help|reduc|improv|lead|caus|"
    r"result|giv|keep|remov)ing\b", re.I)
ING_MAIN_VERB = re.compile(rf"\b{BE}\s+\w+ing\b", re.I)
PASSIVE = re.compile(rf"\b{BE}\s+(?:\w+ed|{PP_IRREG})\b", re.I)
NOMINALIZATION = re.compile(
    r"\b(?:perform(?:s|ed)?|conduct(?:s|ed)?|carry out|carries out|make use of|makes use of)\b"
    r"|\b\w{4,}(?:tion|ment|ance|ence)\s+of\b", re.I)
LATIN = re.compile(r"\b(e\.g\.|i\.e\.|etc\.?)(?=[\s,)]|$)", re.I)
SLOP = re.compile(
    r"\b(simply|just now|seamless\w*|effortless\w*|robust|leverag\w*|utiliz\w*|"
    r"comprehensive\w*|powerful|blazing\w*|lightning-fast|streamlin\w*|facilitat\w*|"
    r"performant|plethora|myriad|delve\w*|dives?\s+into|crucial\w*|pivotal|"
    r"cutting-edge|world-class|next-generation|revolutionary|turnkey|best-in-class|"
    r"state-of-the-art|game-changing|battle-tested|enterprise-grade|supercharg\w*|"
    r"unleash\w*|empower\w*|commenc\w*|initiat\w*|aforementioned|henceforth|whilst|"
    r"amongst|in order to|prior to|subsequent to|due to the fact that|in the event that)\b", re.I)
PHRASAL = re.compile(
    r"\b(spin(?:s|ning)? up|spin(?:s|ning)? down|stand(?:s|ing)? up|reach(?:es|ing)? out|"
    r"kick(?:s|ing)? off|roll(?:s|ing)? out|tear(?:s|ing)? down|ramp(?:s|ing)? up|"
    r"circle(?:s|ing)? back|drill(?:s|ing)? down)\b", re.I)
MODAL_HEDGE = re.compile(
    r"\b(it is important to note|it should be noted|it is worth noting|please note that|"
    r"as mentioned|as noted above|needless to say)\b", re.I)
TRAILING_COND = re.compile(r"\w[^.!?\n]{3,}\s\b(if|when)\b\s", re.I)
ROTATION_SETS = [
    ("check-verify", re.compile(r"\b(check|verify|confirm|validate|ensure)\w*\b", re.I)),
    ("config-settings", re.compile(r"\b(config|configuration|settings)\b", re.I)),
    ("run-execute", re.compile(r"\b(run|execute|invoke|launch)\w*\b", re.I)),
    ("show-display", re.compile(r"\b(show|display|render|present)\w*\b", re.I)),
]
LIMITS = {"procedural": 20, "descriptive": 25}


def strip_code(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`\n]+`", " CODESPAN ", text)  # one word per Rule 8.6
    text = re.sub(r"^#+\s.*$", " ", text, flags=re.M)  # headings exempt (titles, 8.6)
    text = re.sub(r"https?://\S+", " URL ", text)
    return text


def sentences(text):
    text = re.sub(r"^\s*([-*]|\d+\.)\s+", "", text, flags=re.M)  # list markers
    parts = re.split(r"(?<=[.!?:])\s+", text)
    return [p.strip() for p in parts if len(p.strip().split()) >= 2]


def lint(text, text_type):
    if text_type not in LIMITS:
        raise SystemExit(f"--type must be procedural or descriptive, got {text_type!r}")
    body = strip_code(text)
    sents = sentences(body)
    limit = LIMITS[text_type]
    lengths = [len(s.split()) for s in sents]
    paras = [p for p in re.split(r"\n\s*\n", strip_code(text)) if p.strip()]

    counts = {}
    counts["sentence_over_limit"] = sum(1 for n in lengths if n > limit)
    counts["long_paragraph"] = sum(1 for p in paras if len(sentences(p)) > 6)
    counts["contraction"] = len(CONTRACTION.findall(body))
    counts["banned_modal"] = len(BANNED_MODALS.findall(body))
    counts["perfect_tense"] = len(PERFECT.findall(body))
    counts["ing_clause"] = len(ING_CLAUSE.findall(body))
    counts["ing_main_verb"] = len(ING_MAIN_VERB.findall(body))
    counts["nominalization"] = len(NOMINALIZATION.findall(body))
    counts["phrasal_verb"] = len(PHRASAL.findall(body))
    counts["semicolon"] = body.count(";")
    counts["latin_abbrev"] = len(LATIN.findall(body))
    counts["slop_word"] = len(SLOP.findall(body))
    counts["modal_hedge"] = len(MODAL_HEDGE.findall(body))
    counts["trailing_condition"] = sum(
        1 for s in sents if TRAILING_COND.search(s) and not re.match(r"^(if|when)\b", s, re.I))
    rotation = 0
    for _, rx in ROTATION_SETS:
        stems = {m.group(1).lower().rstrip("s") for m in rx.finditer(body)}
        if len(stems) > 1:
            rotation += len(stems) - 1
    counts["synonym_rotation"] = rotation

    passive = len(PASSIVE.findall(body))
    advisory = {"em_dash": text.count("—") + text.count("–")}
    if text_type == "procedural":
        counts["passive_voice"] = passive          # Rule 3.6: required in procedures
    else:
        advisory["passive_voice"] = passive        # legal when the actor is unknown

    words = max(1, len(body.split()))
    total = sum(counts.values())
    return {
        "type": text_type,
        "words": words,
        "sentences": len(sents),
        "mean_sentence_words": round(sum(lengths) / max(1, len(lengths)), 1),
        "longest_sentence_words": max(lengths, default=0),
        "violations": counts,
        "advisory": advisory,
        "violations_total": total,
        "violations_per_100w": round(100.0 * total / words, 2),
    }


SLOP_FIXTURE = """Leveraging our robust retry mechanism, failed uploads are automatically
reattempted, ensuring data integrity is maintained throughout the entire process which has
been designed from the ground up to gracefully handle even the most challenging network
interruptions. You should verify your credentials; it's also worth checking the settings,
e.g. the timeout config. We will perform a validation of the account prior to the upload.
It is important to note that the upload can still fail.
The team is reaching out to support if the problem persists."""

CLEAN_FIXTURE = """The system retries a failed upload automatically. This process keeps the data correct.

If failures continue, make sure that your credentials are correct. If the problem continues, contact support."""


def self_test():
    slop = lint(SLOP_FIXTURE, "procedural")
    clean = lint(CLEAN_FIXTURE, "procedural")
    v = slop["violations"]
    for key, floor in [
        ("sentence_over_limit", 1), ("banned_modal", 1), ("contraction", 1),
        ("perfect_tense", 1), ("ing_clause", 1), ("semicolon", 1), ("latin_abbrev", 1),
        ("slop_word", 2), ("trailing_condition", 1), ("synonym_rotation", 1),
        ("passive_voice", 1), ("nominalization", 1), ("phrasal_verb", 1),
        ("ing_main_verb", 1), ("modal_hedge", 1),
    ]:
        assert v[key] >= floor, f"{key}={v[key]} < {floor}\n{json.dumps(slop, indent=2)}"
    assert clean["violations_total"] == 0, json.dumps(clean, indent=2)
    desc = lint(SLOP_FIXTURE, "descriptive")
    assert "passive_voice" in desc["advisory"], desc
    assert "passive_voice" not in desc["violations"], desc
    print(f"self-test OK: {slop['violations_total']} violations in the slop fixture, "
          f"0 in the clean fixture, passive advisory only in descriptive mode")


def main():
    args = [a for a in sys.argv[1:]]
    if "--self-test" in args:
        self_test()
        return
    text_type = "descriptive"
    if "--type" in args:
        i = args.index("--type")
        text_type = args[i + 1]
        del args[i:i + 2]
    fail_over = None
    if "--fail-over" in args:
        i = args.index("--fail-over")
        fail_over = float(args[i + 1])
        del args[i:i + 2]
    if not args:
        raise SystemExit(__doc__.split("Usage:")[1].strip())

    files = []
    for a in args:
        files += sorted(glob.glob(a)) if any(c in a for c in "*?[") else [a]

    worst = 0.0
    if files == ["-"]:
        r = lint(sys.stdin.read(), text_type)
        print(json.dumps(r, indent=2))
        worst = r["violations_per_100w"]
    elif len(files) == 1:
        with open(files[0]) as fh:
            r = lint(fh.read(), text_type)
        print(json.dumps(r, indent=2))
        worst = r["violations_per_100w"]
    else:
        for f in files:
            with open(f) as fh:
                r = lint(fh.read(), text_type)
            worst = max(worst, r["violations_per_100w"])
            print(f"{os.path.basename(f):34} words={r['words']:5d} "
                  f"total={r['violations_total']:3d} per100w={r['violations_per_100w']:6.2f} "
                  f"longest={r['longest_sentence_words']:3d} "
                  f"em_dash={r['advisory']['em_dash']:2d}")

    if fail_over is not None and worst > fail_over:
        print(f"FAIL: {worst} violations/100w exceeds --fail-over {fail_over}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
