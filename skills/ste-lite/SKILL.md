---
name: ste-lite
version: 1.0.0
description: |
  Write or rewrite technical prose in ASD-STE100 Simplified Technical English so
  it is unambiguous and free of AI slop. Use when asked to make writing not sound
  like AI, de-slop a draft, make docs clear or plain, write for non-native
  readers, or enforce a controlled writing style. Applies to documentation,
  READMEs, runbooks, procedures, error messages, release notes, incident reports,
  API guides, PR descriptions, changelogs, and agent instruction files. Also
  triggers on "STE", "ASD-STE100", "Simplified Technical English", "simplify
  this", "make this readable". Never applies to code, identifiers, or command
  syntax, and never to marketing copy. Two modes: pragmatic and strict.
license: MIT
metadata:
  standard: ASD-STE100 Issue 9 (2025-01-15)
  variant: lite (no rule numbers, no references, ~1/4 the context of ste)
---

# ste-lite

Write prose in ASD-STE100 Simplified Technical English. This applies to documentation, READMEs, runbooks, error messages, release notes, incident reports, PR text, and agent instruction files. It does not apply to code, identifiers, or command syntax. It is not for marketing copy or anything that needs a voice — STE strips voice on purpose.

Install `ste` instead of this file when you need numbered rule citations, per-use-case adaptations, or a compliance audit. This variant carries the rules that change the output and drops the catalog.

## Classify first

Every length rule depends on this.

- **Procedural** (instructions): imperative, max 20 words per sentence, one instruction per sentence.
- **Descriptive** (explanations): simple tenses, max 25 words per sentence, one topic per paragraph, max six sentences. No imperative.

Do not mix the two in one passage. A note inside a procedure is descriptive.

## Rules

WORDS
- One item, one name. Do not call it "config" here and "settings" there. Pick one of check/verify/confirm/validate before you draft and use only that one.
- Use the short common word: use (not utilize/leverage), start (not begin/commence/initiate), help (not facilitate), make sure that (not ensure), before (not prior to), after (not subsequent to), get (not obtain/acquire), show (not demonstrate), also (not additionally/furthermore/moreover), many (not myriad/plethora), because (not due to the fact that), if (not in the event that), to (not in order to).
- Give each word one meaning. "fall" means to move down, not to decrease. "follow" means to come after, not to obey.
- Delete words that carry no fact: simply, just, easily, seamlessly, effortlessly, robust, powerful, comprehensive, performant, "it is worth noting that", "is designed to".
- Keep domain nouns and verbs ("webhook", "commit", "deploy"). Do not use a technical noun as a verb.
- Multi-word nouns of three words or fewer. Break longer chains with a preposition: "the timeout value for the connection pool".
- American spelling. No Latin abbreviations: "for example" not "e.g.", "that is" not "i.e.", name the items instead of "etc.".

VERBS
- Active voice. "The parser reads the file", not "the file is read by the parser". In descriptive text, passive is legal only when the actor is genuinely unknown.
- Simple tenses only: infinitive, imperative, simple present, simple past, simple future, past participle as an adjective. No present perfect ("has completed" → "completed"). No "is to be installed".
- No "-ing" form as a verb. ", making it easy to..." becomes a new sentence.
- Use a verb for an action: "compress the file", not "perform compression of the file".
- **Approved modals: can, will, must. Banned: should, would, may, might, could.** A requirement becomes "must". A recommendation is stated as fact or deleted. Possibility becomes "can". This matters double in agent instructions: models read "should" as optional.

SENTENCES
- One instruction per sentence, unless two actions happen at the same time.
- Put a required condition before its command, divided by a comma: "If the build fails, read the log."
- No contractions. Keep articles (a, an, the, this, these). Keep "that" after "make sure".
- Do not omit words to shorten a sentence. STE is short sentences with complete grammar, not telegraph style. "Ensure file exists before running" → "Make sure that the file exists before you run the command."
- Use a vertical list for a sequence or for three or more conditions. One action per item, imperative form.

PUNCTUATION
- No semicolons. Write two sentences. Everything else is legal, including the em dash — if the user wants no em dashes, that is house style, not STE.
- Code in backticks, numbers with units, identifiers, and quoted text each count as one word toward the sentence limit.

WARNINGS AND SAFETY
- Give the risk level first: WARNING for injury, CAUTION for damage or data loss.
- Then the command or condition. Then the risk. Never bury the instruction after the explanation.
- "Note that data loss may occur if the destructive flag is enabled against production" → "CAUTION: Do not use the `--force` flag against production. The flag deletes rows that do not match the source."
- This also governs step ORDER. When the safe order of a procedure differs from the order you were given, write the safe order and open with the warning that explains it.

UNTOUCHABLE
- Code blocks, inline code, identifiers, CLI flags, file paths, quoted error messages, log lines, product names, and config keys stay exact.

Write only the requested text. No preamble, no summary, no closing remarks.

## Modes

- **pragmatic** (default) — docs, READMEs, PR text, error messages: apply every structural rule and keep your domain vocabulary.
- **strict** — the user names STE, ASD-STE100, or compliance: add full vocabulary discipline, and say that full compliance needs the official dictionary (free at asd-ste100.org).

## Keep precision over compliance

Never drop a safety condition, a precondition, a scope qualifier, a number, a unit, a version, a threshold, an exception, or a named actor to satisfy a rule. When a rule and one of these collide, split the sentence or restructure it first. If neither works, keep the fact and break the rule.

Then report it. End your output with this block, and only when you kept something:

```markdown
**What I did not simplify**
- Kept "only after the pg_dump job reports exit code 0" (28 words, over the 20-word limit): splitting it separated the condition from its command.
```

Name the fact, the rule you broke, and the reason, in one sentence per item. Use the same block to report a step order you changed for safety. Omit the block for a clean rewrite, and never pad it. If the input already complies, say so and change nothing.

## Self-lint (run before returning text)

1. Any sentence over the limit for its type (20 procedural, 25 descriptive)? Split it.
2. Any semicolon? Replace with a period. Any contraction? Expand it.
3. Any `has been`, `have been`, or other present perfect? Use simple past.
4. Any should/would/may/might/could? Apply the modal ladder.
5. Any "-ing" verb, especially after a comma? New sentence.
6. Any passive voice with a known actor? Make it active.
7. Any "if" or "when" mid-sentence? Move the condition to the front.
8. Same thing named two ways? Pick one name and replace every other hit.
9. Every fact from the source still present? Anything kept against a rule listed in the block above?

The mechanical rules are lintable and are what removes slop. Full STE also needs judgment — the right technical noun, whether a sentence makes good sense. A checker cannot certify that. This skill fixes the FORM of slop. It cannot make a hollow paragraph true.

Unofficial aid, not affiliated with ASD or STEMG. ASD-STE100 is a registered trademark of ASD. Free standard: https://asd-ste100.org

Credits: [woosal1337/blog](https://github.com/woosal1337/blog), [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish), [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill), all MIT.
