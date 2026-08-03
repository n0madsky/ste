# ste

An agent skill that makes an LLM write technical text in [ASD-STE100 Simplified Technical English](https://asd-ste100.org) — the controlled language the aerospace industry has used since 1986 so that a tired mechanic cannot misread an instruction. AI slop dies as a side effect, because STE is close to a negative image of every AI writing tell.

This is a merge of three MIT-licensed prior skills. [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) is the base and supplies the rule catalog. [woosal1337/blog](https://github.com/woosal1337/blog) supplies the trigger phrasing, the lite variant's shape, and half the linter. [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) supplies the rule that precision outranks compliance. `NOTICE.md` records what came from where.

## What is here

```
skills/ste/                 full skill: 53 numbered rules, 9 sections  (~5.5k tokens)
  SKILL.md
  references/checklist.md   full audit pass, for check mode
  references/use-cases.md   error messages, runbooks, incidents, agent-to-agent, i18n
  tools/ste_lint.py         deterministic violation counter, for CI
skills/ste-lite/            compact single-file variant                 (~2k tokens)
  SKILL.md
prompts/system-prompt.md    paste-in version for tools without skill support (+ ~70-token version)
```

The linter lives inside the skill so that the `tools/ste_lint.py` path in `SKILL.md` still resolves after you install it.

## Install

Pick one variant. They have the same triggers, so installing both means they compete.

```bash
mkdir -p ~/.claude/skills
cp -r skills/ste ~/.claude/skills/          # full
cp -r skills/ste-lite ~/.claude/skills/     # or lite
```

| | Full | Lite |
|---|---|---|
| Context per trigger | ~5.5k tokens | ~2k tokens |
| Rule numbers you can cite | 53, all 9 sections | none — rules by name only |
| Progressive-disclosure references | checklist, use-cases | none |
| Everything that changes the output | yes | yes |

Take the full one for docs work you audit, for check mode, and for anything where a reviewer will ask which rule you applied. Take lite when the skill has to share context with real work.

For editors with no skill support, paste `prompts/system-prompt.md` into your system prompt, `AGENTS.md`, or `.cursorrules`.

## What it changes against its base

1. **Trigger phrasing.** The `description` now leads with how people actually ask ("make this not sound like AI", "de-slop this draft") instead of with document types. This is the change with the largest measured effect — see below.
2. **Keep precision over compliance.** A new section, plus a `What I did not simplify` output block: the fact kept, the rule broken, the reason, one line each. This closes the failure mode of every controlled language — a shorter sentence that says less than the original. Never dropped: safety conditions, scope qualifiers, numbers, units, versions, thresholds, exceptions, named actors.
3. **Safety governs step order, not just wording.** Section 7 now says so explicitly, and the runbook guidance says a rotation procedure creates the new credential before it revokes the old one.
4. **Grammar outranks part-of-speech rulings.** Added because the noun-only ruling on "work" produced "The key stops work at once" in testing. If a ruling forces bad English, restructure (Rule 9.1).
5. **Merged linter**, shipped inside the skill. It adds passive voice, "-ing" main verbs, nominalizations, phrasal verbs, marketing adjectives, modal hedges, and paragraph length to the base's check set, plus `--fail-over N` for CI. Passive voice counts in procedural text only, since STE allows it in descriptions when the actor is unknown. Em dashes are reported, never counted — STE bans the semicolon, not the dash.
6. **Agent-to-agent section** in `use-cases.md`: name the actor, no bare pronouns, failure branch as its own sentence.
7. **Rule-number honesty.** The skill already refused to cite numbers from memory. It now also tells the user to confirm each number against the official standard before relying on it for a compliance audit.
8. **Two removals.** An unverifiable adoption statistic, and the claim that STE dates to 1983 — the first issue is AECMA PSC-85-16598, 1986.

## Measured against the base

Method: each skill body injected as its instruction, `claude-sonnet-5`, one generation per cell. Scored with the merged linter, which counts the union of both upstream rule sets. Raw outputs are in the harness that produced them.

**Triggering** — each skill installed alone in its own project, three natural requests, checking whether the model invoked the Skill tool at all:

| Request | SimpleEnglish | ste |
|---|---|---|
| "Write the troubleshooting section for my CLI's docs" | no | **triggered** |
| "Rewrite this so it doesn't sound like AI wrote it" | no | **triggered** |
| "Make this error message clear and unambiguous" | triggered | **triggered** |

1 of 3 → 3 of 3. A skill that does not fire has no effect size, so this matters more than the prose scores.

**Prose** — violations per 100 words, lower is cleaner:

| Task | SimpleEnglish | ste | ste-lite |
|---|---|---|---|
| Runbook (procedural) | 1.34 | **0.95** | 1.71 |
| README intro (descriptive) | 0.68 | **0.00** | 0.62 |
| Precision-pressure rewrite | 0.83 | **0.00** | 0.00 |

**Precision** — the third task gives 10 checkable facts (times, plan tiers, a version floor, an approval condition, a size threshold, a duration, a rate limit, an exemption) and asks for "as short and simple as possible". All three kept 10 of 10, and none emitted a spurious "What I did not simplify" block. So the new rule cost nothing here, and it did not prove its worth either: this model did not drop facts under this much pressure. The rule is insurance against a failure this test did not provoke.

Caveats: one generation per cell, one model, three tasks. The prose differences are inside the noise this design can resolve; only the trigger result is large enough to lean on. The linter counts what a regex can see, so a clean score is not compliance.

## Lint your drafts

```bash
L=skills/ste/tools/ste_lint.py
python3 $L --type procedural runbook.md            # JSON detail
python3 $L --type descriptive docs/*.md            # summary table
python3 $L --type procedural --fail-over 1.0 r.md  # exit 1 over threshold
python3 $L --self-test
```

Score is violations per 100 words, so it is length-normalized. Lint a draft, apply the skill, lint again: the delta is the signal. The absolute number is not a compliance verdict — the linter has no part-of-speech data, so it cannot check one-word-one-meaning, noun-cluster length, or whether a technical noun is the right one.

## Limits

STE is for technical facts and instructions. It deletes persuasion by design, so it does not belong on marketing copy, launch posts, or brand writing. This README breaks its own rules for that reason.

No tool can guarantee ASD-STE100 compliance, including this one. Unofficial project, not affiliated with or endorsed by ASD or STEMG. ASD-STE100 is a registered trademark of ASD. The standard is a free download at [asd-ste100.org](https://asd-ste100.org).

MIT, with the three upstream notices reproduced in `LICENSE`.
