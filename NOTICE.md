# Attribution

`ste` is a derivative work. Three upstream projects, all MIT licensed, are
combined here. Their license texts are reproduced in `LICENSE`.

## AminBlg/SimpleEnglish — the base

<https://github.com/AminBlg/SimpleEnglish> · MIT · Copyright (c) 2026 AminBlg

Used as the base of this skill. `skills/ste/SKILL.md`,
`references/checklist.md`, `references/use-cases.md`, and
`prompts/system-prompt.md` are adapted from that repository, and the 53-rule
catalog, the two-mode structure, the procedural/descriptive classification step,
the modal ladder, the slop substitution table, and the self-check step are its
work. `tools/ste_lint.py` keeps its structure, its procedural/descriptive
sentence limits, and its self-test.

## woosal1337/blog — trigger phrasing and slop heuristics

<https://github.com/woosal1337/blog> (`videos/ep01-the-cure-for-ai-slop/`) · MIT · Copyright (c) 2026 Ege Çelebi

The `description` frontmatter leads with the natural-language triggers from that
skill ("make writing not sound like AI"), which fired more reliably in testing
than a description written around document types. `skills/ste-lite/` is a
compact single-file variant in the shape of its distilled sheet, extended with
the modal ladder and the safety-instruction pattern that the original omits.
`tools/ste_lint.py` takes its passive-voice, "-ing" main verb, nominalization,
phrasal-verb, marketing-adjective, modal-hedge, paragraph-length, em-dash and
multi-file summary checks. The note that STE bans the semicolon but not the em
dash is also its correction.

## danyuchn/asd-ste100-skill — precision over compliance

<https://github.com/danyuchn/asd-ste100-skill> · MIT · Copyright (c) 2026 Dustin Yuchen Teng

The "Keep Precision Over Compliance" section and the "What I did not simplify"
output block come from that skill's rule that a rewrite must never silently drop
a safety condition, a scope qualifier, or a number, and must flag the trade-off
instead. Its agent-to-agent framing is the basis of the agent-to-agent section in
`references/use-cases.md`.

## ASD-STE100

ASD-STE100 is a registered trademark of ASD (the AeroSpace and Defense
Industries Association of Europe). This project is not affiliated with or
endorsed by ASD or STEMG. It paraphrases rule categories for teaching and
reproduces no specification text and no dictionary content. The standard is a
free download at <https://asd-ste100.org>.

First issued in 1986 as AECMA Document PSC-85-16598. Current edition: Issue 9,
January 2025.
