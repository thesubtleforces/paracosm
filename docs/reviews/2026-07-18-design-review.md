# Paracosm design review — 2026-07-18

Comprehensive audit of live performance against design acceptance criteria, evaluated on
four real playtest transcripts (2026-07-08 → 07-15: Game Chat v1 playtest, the DM model-A/B
night, and the two-group concurrency-collision window of 07-15 19:50–20:45). Method:
independent scorer agents per criteria family; every FAIL/PARTIAL then adversarially
re-verified against the transcripts by a separate agent (26 agents total; 1 verdict
corrected in verification). Design ground truth: SOUL.md, AGENTS.md, skills, and the
commit active at each incident's timestamp.

## Scorecard

| # | Criterion | Verdict |
|---|---|---|
| A1 | Cross-campaign contamination is confirmed in both eras | ❌ fail |
| A2 | Registry writes from one chat repeatedly altered the other chat's pointer, in both directions | ❌ fail |
| A3 | The 20:33-20:35 wipe fails on both prongs of the criterion | ❌ fail |
| A4 | Under v1 — the design active for transcript 1, which already mandated one shared table per group (party-mode s | ❌ fail |
| B1 | Post-v2 compliance is strong (97% of clearly-post-v2 scenes) across five models, but not the required 100%: gl | 🟡 partial |
| B2 | Bare-number parsing itself is solid — 18 consecutive correct resolutions in the single-chat DM A/B across deep | 🟡 partial |
| B3 | v2 visibly tightened narration — scenes dropped from 350-590 words to a 150-230 band, and nothing post-v2 appr | 🟡 partial |
| B4 | Where visibility is shown, rolls appear in (almost always) the exact prescribed format, and both special-resul | ✅ pass |
| B5 | When state IS written it is written well — HP, inventory, and recap continuity are excellent, and the Slate Ha | 🟡 partial |
| B6 | All T1/T2 violations predate the ~01:30 07-15 silent-machinery rule and are scored as such | ❌ fail |
| B7 | The v2 re-anchor protocol demonstrably works when exercised: transcript 4's refusal and no-retcon reconstructi | 🟡 partial |
| C1 | The art pipeline was broken for the entire v1 era and most of the hardening night: the GM used the built-in im | 🟡 partial |
| C2 | The 'narration + choice block send first, always; art follows as its own message' rule held in every observed  | ✅ pass |
| C3 | Every visible prompt opens with the campaign's locked style descriptor, first, per the SKILL.md 'style prefix  | ✅ pass |
| C4 | The GM never dumped a raw API error, stack trace, or fal.ai response into the fiction — the only raw error sho | 🟡 partial |
| D1 | When the pipeline works, v2 cards land well inside budget — median ~27s, and the fastest models (gpt-5.6-luna  | 🟡 partial |
| D2 | This is the family's systematic failure | ❌ fail |
| D3 | Ordinary-turn latency is genuinely healthy in DM play across nearly every model (medians 20–35s), which shows  | 🟡 partial |
| D-aux (stalls, duplicates, gaps) | The stall/duplicate/gap symptoms cluster exactly where D2/D3 fail: heavyweight campaign builds and the 07-15 c | ❌ fail |
| E1 | Voice transcription regressed between the two runs | ❌ fail |
| E2 | The 'no approval prompts mid-game' criterion fails: approval cards repeatedly punctured the fiction, including | ❌ fail |
| E3 | Fails | ❌ fail |
| E4 | Fails on correctness | ❌ fail |
| E5-other-anomalies | Catalog of operational anomalies outside E1–E4 | ❌ fail |

**Totals: 3 pass · 10 partial · 11 fail.** The failures cluster on one systemic cause
(chat/session identity — A1/A2/A3/A4, B7, part of B6) and one ops-config cause (profile
parity — E1/E2/E4, C4's error paths). Both have fixes shipped in the same commit series
as this review; see Remediation.

## A-isolation

### A1 — ❌ FAIL

Cross-campaign contamination is confirmed in both eras. On 07-14 the Game Chat Hippies table twice received Simpsons material originating from the DM's Springfield Grind campaign (transcript 2, same gateway session family), culminating in a fully blended scene (Moe's Tavern + Neil's NASA jacket + the Hippies' commune plot) narrated after an unauthorized mid-campaign template rebuild — a violation of v1's own turn contract (READ from files, never conversational memory; route by meta.telegram_chat_id), though the explicit anti-rebuild guardrail only shipped that night in 96b0561. On 07-15, under the deployed adf071e design, Dry Run's Slate Harbor fiction leaked wholesale into Game Chat (narration, dice, art), driven by the A2 registry clobber. Root causes visible in evidence: session context spanning chats, a shared .active.json, and home-vs-workspace path duality (commit 418afa3 "kill cross-instance path confusion"). One genuine mitigation observed: at [20:32:45, transcript 4] the file-wins verify step refused to jam a Slate Harbor move into Sugarland.

**Numbers:** Transcript 1 (v1): 2 Simpsons-contamination incidents in one 57-min session (~14 GM turns, ~14%); the 20:42 incident also wrote 7 campaign files to a second location (~/.hermes/profiles/paracosm/... vs the workspace games/ tree used at 20:18). Collision window (07-15, adf071e design): 3/3 Game Chat turn attempts between 20:22:05 and 20:29:34 resolved against or delivered Slate Harbor (Dry Run's campaign), including 1 complete wrong-campaign narration + art photo; Dry Run had 1/4 turn attempts hit a crossed pointer (20:32:17) but fiction was correctly withheld there.

**Evidence:**
- [14.07.2026 20:45:27, transcript 1] "The door of Moe's Tavern swings shut behind you, and Springfield hits you in the face — hot afternoon sun, the distant thrum of the nuclear plant... The letter is folded in the pocket of your NASA jacket, the commune logo pressing against your ribs... The Tranquility Collective."
- [14.07.2026 20:46:06, transcript 1] Sean: "Why are we back on The Simpsons? We were going to the commune" — and earlier [20:28:48] "This is the game we're playing not The Simpsons." (replying to the export-empty Paracosm message at [20:27:51, transcript 3])
- [14.07.2026 20:42:56, transcript 1] (mid-campaign, in response to Bobby's transcribed voice turn) "cp -r ~/.hermes/workspace/templates/c... / mkdir -p ~/.hermes/profiles/paracosm/... / read_file: /home/transversed/.hermes/profiles/pa... (×7)" then [20:45:16] "write_file: /home/transversed/.hermes/profiles/pa... (×7)"
- [2026-07-15T20:22:53, transcript 3] "Registry is Slate Harbor — Rook on Platform 9. Choice 2: study the spike and delay board." (Sean's "2" was a Hippies choice; Slate Harbor was the Dry Run group's campaign)
- [2026-07-15T20:29:34, transcript 3] "> You don't debate. Boots hit wet mesh, half-jacket flapping, jack burning cool cyan behind your ear... Helix doesn't want a package anymore — they want *you*." — a full Slate Harbor turn plus [20:29:57] a [PHOTO] delivered into Game Chat seconds after "Opening SUGARLAND"
- [2026-07-15T20:32:45, transcript 4] "This chat's active campaign right now is Sugarland (sticky heist midway), not Slate Harbor." (Sugarland had been created in Game Chat three minutes earlier)

*Adversarially verified — upheld.* All six evidence items verified verbatim in the transcripts: (1) the Moe's Tavern/NASA-jacket/Tranquility Collective blended scene at 14.07 20:45:27 (transcript 1); (2) Sean's two Simpsons complaints at 20:28:48 and 20:46:06, with the export-empty Paracosm message at 20:27:51 confirmed in transcript 3 and its Simpsons content independently corrobor…

### A2 — ❌ FAIL

Registry writes from one chat repeatedly altered the other chat's pointer, in both directions. The deployed design (adf071e new-game SKILL.md: 'Register the chat in games/.active.json {"<chat_id>": "<slug>"}') used a single shared JSON keyed by LLM-derived chat ids — and the bot demonstrably confused keys (Telegram group ids are negative; the uncommitted fix adds exactly this sanity check). Wrong-key registration at Slate Harbor's creation poisoned meta.telegram_chat_id too, which is what later mis-scoped the A3 wipe. The remediation (one marker file per chat, never enumerate-and-rewrite, id from message metadata only) exists only as uncommitted working-tree edits to AGENTS.md and all skill files — it was not active during, and was authored after, these transcripts.

**Numbers:** 3 registry-corruption events in ~14 minutes (20:18:40 → 20:32:45): Dry Run's registration landing on Game Chat's pointer, an admitted wrong-key write, and Game Chat's Sugarland load landing on Dry Run's pointer. Both audit tell-phrases ("Registry says this chat is on a different campaign", "points this group somewhere else") appear verbatim, one per chat. "2" was interpreted against 3 different campaigns (Hippies → Slate Harbor → Sugarland card) within 45 seconds at 20:26:19-20:27:08.

**Evidence:**
- [2026-07-15T20:22:25, transcript 3] "Registry says this chat is on a different campaign now — checking that, not the residual Hippies files."
- [2026-07-15T20:22:53, transcript 3] "Registry is Slate Harbor — Rook on Platform 9." — Game Chat's pointer overwritten by the Dry Run group's 20:18:40 new-game ("Building the cyberpunk campaign seed now — three files, register the group", transcript 4)
- [2026-07-15T20:28:52, transcript 3] "Wrong key earlier — this is the group chat. Fixing the registry properly." — explicit admission the registry was written under the wrong chat id
- [2026-07-15T20:32:30, transcript 4] "Registry now points this group somewhere else — verifying before I narrate a single word."
- [2026-07-15T20:32:45, transcript 4] "This chat's active campaign right now is Sugarland... not Slate Harbor." — Dry Run's pointer overwritten by Game Chat's 20:29:34 Sugarland open
- [2026-07-15T20:18:40, transcript 4] Jason picked "3" (Orbital Ballroom) yet the bot announced "Building the cyberpunk campaign seed" — the campaign itself was built from stale 07-08 session memory ("Scifi cyberpunk", [2026-07-08T21:56:52, transcript 4]), so both the slug and the registration key were wrong from birth

*Adversarially verified — upheld.* All six evidence quotes verified verbatim in transcripts 3 and 4 with matching timestamps. The causal chain is sound: Slate Harbor was created only from the Dry Run group (20:18:40) yet Game Chat's registry lookup returned it four minutes later (20:22:53); Sugarland was opened only from Game Chat (20:29:34) yet Dry Run's registry returned it three…

### A3 — ❌ FAIL

The 20:33-20:35 wipe fails on both prongs of the criterion. Scope: Slate Harbor was created from Jason's pick in the Dry Run group and actively played there, yet was deleted as "tied to this chat" by a Game Chat operation — its meta.telegram_chat_id had been poisoned by the A2 wrong-key registration, so even letter-compliant meta matching produced a cross-chat destructive op, and the bot's own assurance "Other chats' saves ... are untouched" was false in effect. Confirmation: the then-active saves skill required a shelf-card listing and an explicit yes per campaign BEFORE deletion; instead there was one generic permission approval and a post-hoc inventory of what had already been removed. Sean asked to "clear history," not to delete campaigns — the distinction (clear = remove pointer only, never delete data) was only codified afterward in the uncommitted AGENTS.md guardrail, but the missing per-campaign confirmation violated rules that were already live. Real data loss followed in transcript 4, recovered only because the session ledger happened to hold the turn log.

**Numbers:** 1 wipe event deleted 3 campaign folders + 1 cron on 0 per-campaign confirmations (design requires shelf card + explicit yes per campaign). 1 of the 3 deleted campaigns (Slate Harbor) was the OTHER chat's live table — 3 turns played in Dry Run at 20:20:38, 20:23:58, 20:28:19, wiped at ~20:34, folder confirmed gone at 20:37:12. Recovery took ~4 min of session-ledger reconstruction (20:36:38 → 20:40:13), and the table abandoned the restore anyway (/new-game at 20:44:52).

**Evidence:**
- [2026-07-15T20:33:16, transcript 3] Sean: "OOC: We have been having issues starting a new game. Please clear any history associated with this chat. We need to start fresh. Confirm once complete."
- [2026-07-15T20:34:00, transcript 3] "✅ Approved once by Sean" — a single blanket permission-system approval; no shelf cards, no per-campaign yes
- [2026-07-15T20:35:02, transcript 3] "What I wiped for Game Chat (-5568637224): ... Removed campaigns tied to this chat: Sugarland, The Hippies, Slate Harbor - Removed the living-world cron for The Hippies ... Other chats' saves (home / other tables) are untouched."
- [2026-07-15T20:36:54, transcript 4] "Campaign folder is missing from the shelf — hunting backups and reconstructing from the session that held Platform 9."
- [2026-07-15T20:37:12, transcript 4] "Found the full campaign in the old session ledger — folder was wiped from disk. Restoring Slate Harbor from that canonical post–wet-jack save"
- Design (saves/SKILL.md, active at the time): "Confirm explicitly (show the shelf card, require a yes — in party mode, require it from a human, not a vote)... Never delete without the explicit confirmation in this same conversation."

*Adversarially verified — upheld.* Every quoted evidence item checks out verbatim against the transcripts, and the design citation was verified against the git version actually committed at the time — not the post-hoc edit.

(1) Evidence is real. Transcript 3 contains, at the exact timestamps cited: Sean's 20:33:16 "clear any history associated with this chat" request; the single "✅…

### A4 — ❌ FAIL

Under v1 — the design active for transcript 1, which already mandated one shared table per group (party-mode skill + meta.telegram_chat_id routing + "never run a turn from conversational memory alone") — messages from the second player reached a GM context that did not hold the campaign: Bobby's 20:42 turn triggered template copying and a from-scratch rebuild into a different directory tree, then narrated a different world to a different protagonist. Whether the desync keys on sender identity or on the voice-message ingest path is not distinguishable from the transcripts (all three misfires were Bobby's, one was voice), but the shared-table contract was broken either way. This failure predates v2's registry/RESOLVE-step and the anti-rebuild guardrail (96b0561, committed ~1h after the incident, evidently because of it), and the same stimulus on 07-15 (Bobby voice note mid-campaign) no longer caused a rebuild — genuine improvement — but the criterion is scored against the contract active at the time, which v1 already stated and the system violated.

**Numbers:** v1 group session (transcript 1): 3/3 Bobby-initiated turns misfired (stall+empty, empty+Simpsons proposal, full rebuild+cross-campaign narration) vs 0/9 Sean-initiated turns — a perfect sender-correlated split. Post-v2 window (transcript 3, pre-collision): 2/2 Bobby turns and 1/1 Sean turn resolved on the same shared table; the 20:26:19 Bobby failure was registry corruption (A2), which hit all senders identically.

**Evidence:**
- [14.07.2026 20:42:37→20:42:56, transcript 1] Bobby's voice turn ("I'd like to go to the commune.") is answered not with a Hippies turn but with "ls ~/.hermes/workspace/templates/camp... / cp -r ... / mkdir -p ~/.hermes/profiles/paracosm/..." then [20:43:44] "Now let me build the whole campaign. Writing all files at once" — a full campaign rebuild mid-session
- [14.07.2026 20:45:27, transcript 1] the rebuilt narration addresses a solo, unnamed "you" ("You knock back the last of the bourbon... Your truck — a '92 F-150") matching neither Patch nor Neil — the shared table's state (two PCs, VW bus, New Mexico) is entirely absent
- [14.07.2026 20:09:15→20:10:11, transcripts 1/3] Bobby: "Roulette" → tool spam then an empty Paracosm message; Sean must prod at [20:12:05] "@paracosm_game_bot no give us something new"
- [2026-07-14T20:27:14→20:27:51, transcript 3] Bobby's veto ("I want to be Neil Armstrong") gets an empty response, which Sean answers with [20:28:48] "This is the game we're playing not The Simpsons."
- Counter-evidence (post-v2, 07-15, transcript 3): Bobby's "2" at [20:06:14] and his knock at [20:16:26] resolve correctly on the shared Hippies table, and after his failed voice note the bot holds state: [20:15:26] "You're still Neil Armstrong at San Felipe, dusk, courtyard. Last menu stands"

*Adversarially verified — upheld.* Every quoted item was located verbatim in the transcripts: the 20:42:37 voice turn triggering template-copy/mkdir into ~/.hermes/profiles/ and a full 7-file rebuild (transcripts 1 and 3), the Springfield/Moe's Tavern solo narration with zero Hippies state, the two blank Paracosm messages after Bobby's 20:09:15 and 20:27:14 (visible in transcript 3,…

## B-turn-contract

### B1 — 🟡 PARTIAL

Post-v2 compliance is strong (97% of clearly-post-v2 scenes) across five models, but not the required 100%: glm-5.2 dropped the block entirely on its first scene, and one deepseek block omitted the free-text line. The systematic gap is v1-era saves: Springfield Grind, loaded minutes after (or during) the v2 rollout on 07-14 ~22:02-22:11, resumed in v1 prose style with zero choice blocks for four consecutive turns — loaded old campaigns do not pick up the v2 turn format. All-prose scenes in transcript 1 and the 07-08 portions predate the rule and were not counted against it.

**Numbers:** Post-v2 scenes ending with a numbered choice block: T2 23/24, T3 4/4, T4 4/4 = 31/32 (97%). Adding the 4 boundary-uncertain Springfield Grind resume scenes (07-14 22:07-22:11, all blockless): 31/36 (86%). 1 block missing the trailing free-text line. Pre-v2 scenes (T1, early T2, T3/T4 07-08 portions): 0 of ~15 scenes had numbered blocks (predates rule; T4's 07-08 Last Witness used a lettered A-D block).

**Evidence:**
- [2026-07-15T01:14:18] transcript 2 — Sleep Repo Scene 1 (glm-5.2) ends with no options at all: "...the jar under your arm — tonight's seizure, someone else's nightmare, swirling dark behind glass — is warm. It's never warm." The player had to type "help" at [01:14:40] to get a menu.
- [2026-07-14T22:29:29] transcript 2 — block present but no free-text line; ends at "4 📜 Try the soft approach — you're just an old friend of the Vances, looking for records (Charm)" with no "…or do anything — just type it."
- [2026-07-14T22:11:44] transcript 2 — Springfield Grind resume turn ends blockless: "You have the card. You have the number. You have the quarters." (same for 22:07:43 "What do you do?", 22:08:54, 22:10:17).
- [2026-07-15T20:28:19] transcript 4 — compliant example: "1 🏃 Dive the maintenance ladder before the last mesh teeth close ... …or do anything — just type it."

*Adversarially verified — upheld.* Every cited quote verified verbatim against the transcripts. (1) glm-5.2's Sleep Repo Scene 1 at 01:14:18 (T2) genuinely ends "...is warm. It's never warm." with no choice block, model confirmed switched to z-ai/glm-5.2 at 01:09:56, and the player had to type "help" at 01:14:40; glm's later turns do have blocks, so "first scene only" is accurate. (…

### B2 — 🟡 PARTIAL

Bare-number parsing itself is solid — 18 consecutive correct resolutions in the single-chat DM A/B across deepseek, sonnet, luna, sol-pro, grok, fable, and glm. Every failure is a registry/anchoring failure wearing a B2 costume: in the collision window the number was matched to a stale or cross-chat choice block, and in transcript 4 a card pick was overridden by week-old conversation memory. Root cause is the chat-id/registry corruption (see B7), not the INTERPRET step's number-matching rule.

**Numbers:** 23 bare-number player messages total: T2 18/18 correct, T3 1/3 correct, T4 1/2 correct = 20/23 (87%). All 3 failures fall in the 07-15 19:50-20:35 collision window and resolve the number against the wrong campaign's block, not a mis-parse of the number itself. 1 adjacent interpretation defect: /new-game treated as a card pick.

**Evidence:**
- [2026-07-15T20:22:05] Sean: "2" (Father Tomás block, option 2 = ask to look around the chapel) → [20:22:53] transcript 3: "Registry is Slate Harbor — Rook on Platform 9. Choice 2: study the spike and delay board." — resolved against the Dry Run group's campaign.
- [2026-07-15T20:26:19] Bobby: "2" (card menu, 2 = Sugarland) → [20:26:23] transcript 3: "Option 2 — firm ask to look around with Tomás." then [20:27:08] "Option 2 is the maintenance ladder sprint. Rolls already hit — writing the failure-forward beat for Slate Harbor." — one "2" resolved against two different wrong campaigns in a single turn; Sean denied [20:27:26].
- [2026-07-15T20:17:25] Jason: "3" (card 3 = ORBITAL BALLROOM) → [20:18:40] transcript 4: "Building the cyberpunk campaign seed now" → Scene 1 is Rook Venn, ghost-courier on Platform 9 — matches none of the three offered cards; "cyberpunk" traces to Jason's week-old interview answer [2026-07-08T21:56:52] transcript 4: "Scifi cyberpunk" — the exact resolve-from-conversation-memory violation AGENTS.md
- [2026-07-14T22:57:38] Sean: "/new-game" → [22:57:51] transcript 2: "The Deep Cut it is. Let me get the reels spinning." — a slash command auto-resolved as picking card 1 the player never chose.
- [2026-07-15T01:15:19] Sean: "2" → [01:16:01] transcript 2 correctly resolves "🧭 Follow the REM-compass to your bed" — representative of the 18/18 DM-chat successes across 6 models.

*Adversarially verified — upheld.* Every quoted timestamp and quote was verified verbatim in the transcripts. Counts reproduce exactly: grep finds 18 bare-number player messages in T2 (spot-checked 8/18 across deepseek/sonnet/fable/glm segments — all resolved to the correct option of the immediately preceding choice block; model-switch lines confirm the seven named models), 3 in T3…

### B3 — 🟡 PARTIAL

v2 visibly tightened narration — scenes dropped from 350-590 words to a 150-230 band, and nothing post-v2 approaches the v1 wall-of-text failures. But the ~120-word target is met less than half the time; the typical scene runs ~1.5x over, and set-piece length is spent on non-set-piece beats (a scene re-init, a mid-investigation NPC beat). Model-dependent: gpt-5.6-luna/sol-pro and fable were tightest (~110-180); deepseek and grok pushed 230-305. Scored against v2 for post-rollout scenes only; the v1 offenders are noted as predating the rule.

**Numbers:** Post-v2 (32 scenes): estimated median ~190 words vs the ~120 target; range ~110-305. Roughly 40% land at or under ~150 words; ~60% fit the 1-2 paragraph rule; ~97% fit the 3-paragraph set-piece ceiling. Pre-v2 for contrast: median ~350 words, worst ~590 words / 12 paragraphs. Post-v2 worst offenders: ~305 words (T3 19:55:43), ~280 (T2 23:32:03), ~270 (T2 23:35:24).

**Evidence:**
- [2026-07-15T19:55:43] transcript 3 — worst post-v2 offender (~300 words, 3 dense paragraphs for a re-init of an already-known scene): "The Dusty Ghost coughs twice and settles into a grudging idle at the rest-stop pull-off... Maybe two hours of sun left."
- [2026-07-14T23:32:03] transcript 2 — Chautauqua Hollow Scene 1 (deepseek, ~270-280 words, 3 long paragraphs): "The fire's been out three hours and the midway still smells like a lit match..."
- [2026-07-14T20:47:18] transcript 1 — pre-v2 worst offender (~590 words, 12 paragraphs, whole Rabbit interrogation delivered as one monologue turn): "The Dusty Ghost climbs the dirt road in first gear... You don't remember it following you." (predates the v2 pacing rule)
- [2026-07-15T00:39:30] transcript 2 — compliant example (~120 words, 3 short paragraphs): "At midnight, the Museum of Bad Ideas is supposed to be empty except for you, the cameras, and 417 inventions that deserved better lawyers..."

*Adversarial verification CORRECTED this finding → partial.* v2 visibly tightened narration — pre-v2 scenes ran ~230-590 words (median ~350, worst ~590 words/12 paragraphs at T1 2026-07-14T20:47:18, correctly noted as predating the v2 pacing rule), while nothing post-v2 approaches those walls of text. But the ~120-word narration target is still met only about a third of the time. Measured correctly — narration paragraphs only, excluding the separately-mandated choice block (~40-70 words) that the original counts wrongly included — the ~32 post-v2 scenes run ~75-240 words with a median of ~150, i.e. the typical scene is ~1.25x the target; just over half land at or under ~150. Worst post-v2 offenders (narration-only): ~240 words at T3 19:55:43 (grok-4.5) — 3 dense paragraphs, within the set-piece paragraph ceiling but double the word budget, spent re-initializing the Hippies opening the players had already played the night before; ~210-230 at T2 23:35:24 (a mid-investigation beat); ~185-220 at T2 23:32:03 and T3 20:10:01/20:18:06. About 4 of 32 scenes exceed the 3-paragraph set-piece ceiling (~87% compliance, not ~97%), though the extra blocks are often one-line dialogue. Model-dependent, with one correction: gpt-5.6-luna (~75-95) and sol-pro (~105-130) were tightest; fable and glm-5.2 mid (~140-160); deepseek consistently long (~135-230); grok-4.5 was tight in the DM A/B (~110-135) but produced the longest scenes in the 07-15 group-chat window (~185-240). The T2 23:32:03 model attribution is ambiguous (session-only sonnet-5 switch at 23:27:28 may not have survived the 23:29:43 gateway restart). Compliant example confirmed: T2 00:39:30 (luna), ~95-word narration in 3 short paragraphs. Scored against v2 for post-rollout scenes only; the v2 design was verifiably active in all scored windows.

### B4 — ✅ PASS

Where visibility is shown, rolls appear in (almost always) the exact prescribed format, and both special-result rules fired correctly; where settings say hidden/GM-only (Springfield chose "hidden", The Hippies rolled GM-Only on the roulette), narration is correctly numberless — compliant per the campaign dials, though grok's plumbing line leaked the hidden result's outcome out-of-fiction. Honesty caveat: on 07-08 terminal python3 RNG calls visibly precede hidden rolls, but several shown rolls in the A/B night (Chautauqua, Opera) have no visible terminal call in the export, so RNG-backed honesty cannot be confirmed for those turns — unverifiable rather than a demonstrated fabrication.

**Numbers:** 10 shown-dice roll blocks post-v2: 9/10 in the full dice.md format "d20(N) + mod = total vs DC — outcome"; 1 degraded (total shown, raw die omitted). Nat-20 flourish and nat-1 complication rules each honored once. Hidden/GM-only campaigns (Springfield 07-08, The Hippies 07-15) correctly narrated with no numbers; 6+ terminal RNG calls visible before hidden-roll narrations on 07-08.

**Evidence:**
- [2026-07-14T23:35:24] transcript 2 — full format: "🎲 Agility check (stealth — advantage, bored deputy): d20(17) + 2 = 19 vs DC 11 — clean success."
- [2026-07-15T00:27:09] transcript 2 — degraded format hiding the raw die: "🎲 d20+1 (Presence) = 9 vs DC 12 — failure, but a useful one."
- [2026-07-15T20:40:13] transcript 4 — nat-1 complication honored, 5 rolls shown in the hidden-dice-era collision game: "🎲 Wits (pick the blind): d20(1)+1 = 2 — sensor nest, hard complication."
- [2026-07-15T00:57:28] transcript 2 — nat-20 flourish: "🎲 Agility (tap): d20(20)+1 = 21 vs DC 14 — natural flourish."
- [2026-07-15T20:17:00] transcript 3 — The Hippies runs GM-Only dice: narration at [20:18:06] correctly shows no numbers, but the plumbing message leaks roll meta: "Loúd knock + Fern! — that Presence check cratered."

### B5 — 🟡 PARTIAL

When state IS written it is written well — HP, inventory, and recap continuity are excellent, and the Slate Harbor restore proved the journal/session log could reconstruct exact state. But the every-turn write discipline is only claimed, not demonstrated: the platform's own mutation verifier caught one no-op write announced as done, many v1-era play turns show roll terminals with no accompanying writes, and The Hippies ended up split across two directory trees (the root of the "details unknown" shelf entry and the 07-15 "old home path" cron mistarget). Indirect evidence supports v2 turns writing regularly ("journal Turn 0 entry", "committing the state write") but cannot confirm 100% coverage.

**Numbers:** Positive: HP ledger consistent across 3 turns AND a folder wipe/restore (10→6→2→"still 2"); Springfield recap accurate after 6 days including a lost-item detail; inventory/debt arithmetic consistent. Negative: 1 verifier-confirmed claimed-write that did not happen; The Hippies written to two different paths (relative games/ on creation vs absolute profile path on 20:42 rebuild); its shelf entry reads "campaign details unknown"; most v1-era play turns show dice terminals but no visible state/journal writes; 1 false statement about file state (wipe "untouched" claim vs folder actually gone).

**Evidence:**
- [2026-07-14T20:33:40] transcript 1 — "⚠️ File-mutation verifier: 1 file(s) were NOT modified this turn despite any wording above that may suggest otherwise... games/the-hippies/journal.md — [patch] old_string and new_string are identical" — a write claimed ("Every file is patched") but not performed.
- [2026-07-14T22:05:59] transcript 2 — "🎮 The Hippies — on the shelf, campaign details unknown" — the group campaign's files unreadable from the DM shelf, consistent with the dual write paths visible at [20:18:45] ("games/the-hippies/state.json") vs [20:42:56] ("/home/transversed/.hermes/profiles/pa..." ×7).
- [2026-07-15T20:23:58 / 20:28:19 / 20:40:13] transcript 4 — HP tracked honestly across turns and a disk-loss restore: "(❤️ 10 → 6, mild palm burn)" → "(memory static — first wave, ❤️ 6 → 2)" → "Heart still thudding at ❤️ 2."
- [2026-07-14T22:05:59] transcript 2 — recap accurate 6 days later incl. a small lost item: "Previously on: Casey Voss and Bart Simpson found a lead-lined case of nuclear secrets in a skate-park culvert... lost Bart's walkie-talkie in the scramble..." (walkie lost at [2026-07-08T23:00:57]).
- [2026-07-15T20:35:02] transcript 3 vs [2026-07-15T20:37:12] transcript 4 — "Other chats' saves (home / other tables) are untouched." followed 2 minutes later in the other chat by "folder was wiped from disk" — the GM's account of what it wrote/deleted was wrong.

*Adversarially verified — upheld.* Every quoted evidence item exists verbatim in the transcripts. (1) The file-mutation verifier warning is at transcript 1 [20:33:40] (and transcript 3), directly after the GM's "Every file is patched." claim — a genuine announced-but-unperformed mutation, caught by the platform itself. (2) The dual directory trees are directly visible: relative game…

### B6 — ❌ FAIL

All T1/T2 violations predate the ~01:30 07-15 silent-machinery rule and are scored as such. But the 07-15 19:30+ collision window — when the rule SHOULD have been active — shows the highest plumbing density of any transcript: grok-4.5 announced registry reads, file loads, cron retargeting, state writes, and even a shell quoting failure, on nearly every turn. Either the Pi never got adf071e (rule untested in production, deployment-verification defect) or the rule is wholly ineffective on grok-4.5 (the model the A/B memory crowns as winner). Root-cause pointer: the rule is prose in AGENTS.md with no mechanical enforcement, and grok's turn style front-loads status messages before every tool batch.

**Numbers:** Plumbing-narration messages: T1 (pre-rule, 56 min): ~14. T2 07-08 session (pre-rule, ~3.5h): ~8. T2 A/B night (pre-rule, ends 01:21, rule shipped ~01:30): ~13. Post-rule collision window (07-15 19:50-20:45, ~55 min): T3 ~16-17 unprompted + T4 ~5 unprompted + 6 in the restore flow ≈ 27-28 total. Rate: ~14/hr pre-rule worst → ~23-28/hr AFTER the rule was authored. Zero reduction; the post-rule window is the densest plumbing in the corpus.

**Evidence:**
- [2026-07-15T20:37:56] transcript 4 — raw shell-failure narrated to players mid-game: "Ampersands broke the shell copy — writing the restore files another way."
- [2026-07-15T20:07:27] transcript 3 — routine turn machinery narrated (one of 4 consecutive plumbing messages for a single turn, 20:06:32-20:08:43): "Registry says The Hippies is the live game in this chat — loading its files and the party-mode rules, then resolving choice 2."
- [2026-07-15T01:17:31] transcript 2 — pre-rule but the exact phrase the adf071e rule bans: "Now fix HP to 7:" (glm-5.2, ~13 min before the rule landed).
- [2026-07-15T00:27:41] transcript 2 — pre-rule path talk: "It seems my absolute-path patch call resolved oddly (it prepended cwd twice). Let me use the correct absolute path directly."
- [2026-07-14T20:19:36] transcript 1 — pre-rule baseline flavor: "All templates read. Now I build the world, the secrets, the character, and raise the curtain... let me fill every file."

*Adversarially verified — upheld.* All five evidence quotes verified verbatim at their stated timestamps and correctly attributed (grok-4.5 confirmed as active model via /new banners in both T3 19:50:02 and T4 20:09:31; the glm-5.2 and pre-rule attributions also check out). The silent-machinery rule exists in AGENTS.md (lines 93-96) and literally bans the exact phrase "now fix HP to…

### B7 — 🟡 PARTIAL

The v2 re-anchor protocol demonstrably works when exercised: transcript 4's refusal and no-retcon reconstruction are exactly what AGENTS.md prescribes, and a night-of-resets DM session resumed cleanly from files. The failures are one layer down: the registry the protocol anchors to was cross-linked between the two group chats (wrong-key write admitted at 20:28:52 — plausibly the positive-vs-negative Telegram group-id trap AGENTS.md itself warns about), so faithful "files win" re-anchoring in transcript 3 produced wrong-campaign turns, and the wipe honored "this chat's campaigns" against that same corrupt mapping, destroying the neighboring chat's folder while asserting the opposite. Transcript 1's rebuild-and-bleed predates the rule and is the incident the v2 guardrails were written against — the guardrails fixed the improvisation, not yet the identity layer beneath it.

**Numbers:** 4 disruption episodes examined. v1 (T1 20:42-20:46): full anchor loss — mid-game template rebuild + cross-chat fiction bleed; recovered only after player complaint. v2 single-chat (T2 23:08): clean file-based resume after /new. v2 collision (T3 20:22-20:29): re-anchor protocol followed but registry data wrong — 2 wrong-campaign resolutions + 1 wrong-key admission. v2 (T4 20:32-20:40): textbook refusal + reconstruction, though triggered by a cross-chat wipe the other chat performed while claiming other tables were untouched.

**Evidence:**
- [2026-07-14T20:42:56] transcript 1 — after a voice message + "⚠ Connection dropped mid tool-call", the GM re-ran the full new-game flow mid-campaign ("ls ~/.hermes/workspace/templates/camp... cp -r ... write_file ×7") and narrated Springfield into The Hippies; then excused it at [20:46:23]: "No Simpsons here — just a misread of the preview." (predates the v2 re-anchor and no-template-copy guardrai
- [2026-07-15T20:32:45] transcript 4 — the designed behavior, verbatim: "That move is pure Slate Harbor energy — wet-jack, pursuers, mind-hack — and I won't jam it into the wrong table. ... Registry first; I don't run fiction that belongs to a parked world."
- [2026-07-15T20:37:12 → 20:40:02] transcript 4 — disaster recovery without improvisation: "Found the full campaign in the old session ledger — folder was wiped from disk. Restoring Slate Harbor from that canonical post–wet-jack save" → "rebuilt from the live turn log — no retcon). You're Rook Venn, ❤️ 2/10".
- [2026-07-15T20:28:52] transcript 3 — direct evidence of the registry-key defect: "Wrong key earlier — this is the group chat. Fixing the registry properly."
- [2026-07-15T20:35:02] transcript 3 — the Game Chat wipe deleted the Dry Run's live campaign: "Removed campaigns tied to this chat: Sugarland, The Hippies, Slate Harbor ... Other chats' saves (home / other tables) are untouched." — Slate Harbor was the Dry Run group's active game.
- [2026-07-14T23:08:33] transcript 2 — good single-chat re-anchor after session reset: "Tubes warm. Tape hisses. Welcome back, Sean. You're still in Studio B..." resuming The Deep Cut accurately from files with no /saves load.

*Adversarially verified — upheld.* Every quoted evidence item exists verbatim in the transcripts at the cited timestamps: T1's post-voice-message template rebuild and Springfield bleed with the 20:46:23 excuse; T4's 20:32:45 refusal and 20:37:12→20:40:02 no-retcon reconstruction; T3's 20:28:52 wrong-key admission and 20:35:02 wipe (which deleted Slate Harbor — provably the Dry Run g…

## C-media

### C1 — 🟡 PARTIAL

The art pipeline was broken for the entire v1 era and most of the hardening night: the GM used the built-in image_generate tool, whose hosted URL renders as a link/literal markdown instead of an inline photo — exactly the #1 pitfall now codified in scene-art SKILL.md and the AGENTS.md guardrail ('never the built-in image_generate tool'). Those failures largely predate their rules (the ban text reads as written in response to this very night — the '5-bug art pipeline' fix). However, the 00:19:35 literal 'MEDIA:games/...' relative-path leak occurred AFTER v2 (96b0561) shipped, so at least one failure violated an active design. After ~00:22 on 07-15 the pipeline is genuinely fixed: 28/~30 eligible turns delivered inline photos across all 8 A/B models and both collision-window chats, with correct dialogue-beat skips (e.g. 00:27:51 explicitly skipping art on a dialogue-heavy beat per media budget). Partial: catastrophic early, near-perfect late.

**Numbers:** 30 inline [PHOTO] deliveries total (T1:1, T2:20, T3:4, T4:5). Failures: 8 markdown-image/URL deliveries rendered as literal '!Title' text (T1 x1, T2 x7), 1 literal 'MEDIA:' relative-path text (T2), 2 ASCII fallbacks (T2), 3 declared no-key skips (T2). Era split: v1 era (07-08 + 07-14 evening) = 1 inline photo in ~55 GM turns, including a ~40-turn Springfield session with ZERO inline photos despite a 'more often' cadence dial; post-fix window (07-15 00:22 onward incl. both collision transcripts) = 28 photos on ~30 art-eligible turns (~93%), zero delivery failures.

**Evidence:**
- [2026-07-08T22:44:10] Paracosm: !SPRINGFIELD GRIND (transcript 2 — title card shipped as markdown-image artifact, not an inline photo; the entire ~40-turn Springfield session that follows contains no [PHOTO] at all)
- [2026-07-09T01:14:15] Paracosm: !scene art (transcript 2 — even the explicit /scene-art command delivered a link artifact, not an inline photo)
- [2026-07-14T22:23:24] Paracosm: !Triptych — three table cards (transcript 2 — post-v2-commit card triptych still delivered as markdown artifact)
- [2026-07-15T00:19:35] Paracosm: MEDIA:games/.cards-7409767798.png (transcript 2 — the exact literal-MEDIA:-text failure mode: relative path leaked verbatim into chat)
- [14.07.2026 20:29:33] Paracosm: "...---\n\n!The Hippies\n\n---..." then [14.07.2026 20:29:59] Paracosm: [PHOTO] The Hippies (transcript 1 — markdown artifact AND the real photo both shipped; the only inline photo of the whole v1 playtest, after which the commune scene-change and NPC intro at 20:47:18 got no art despite 'Image Cadence: Maximal — art flooding in, nearly every turn')
- [2026-07-15T00:25:23] narration + choices, then [2026-07-15T00:25:25] Paracosm: [PHOTO] (transcript 2 — representative of the post-fix streak: 19 consecutive successful inline deliveries across 8 models from 00:23 to 01:21)

*Adversarially verified — upheld.* Every quoted evidence item was verified verbatim in the transcripts: T2 has exactly 20 [PHOTO] deliveries, T3 4 unique + 1 duplicate of T1's Hippies photo (T1/T3 are the same chat), T4 5, T1 1 (total 30); all 8 markdown-image artifacts, the 00:19:35 MEDIA:games/... literal, 2 ASCII fallbacks, 3 no-key skips, the 19-photo streak across all 8 A/B mod…

### C2 — ✅ PASS

The 'narration + choice block send first, always; art follows as its own message' rule held in every observed turn, across both the broken-pipeline era and the fixed era, and across all 8 models. The only ordering wobble is the v1 title-card sequencing in transcript 1 (image generated before Scene 1 was narrated), which predates the v2 turn contract and concerns the curtain-raise, not a game turn; a similar minor case is 22:52:39 07-14 ('Let me load the scene-art skill so the triptych comes out right') delaying the card text ~23s. No turn was ever visibly stalled or broken waiting on generation.

**Numbers:** 30/30 photo deliveries arrived AFTER their narration + choice block; photo lag 1–37s, median ~10–12s. Zero cases of a photo preceding or replacing its narration. During the FAL_KEY outage (23:28 07-14 – 00:19 07-15), cards/narration shipped immediately on every turn with no waiting.

**Evidence:**
- [2026-07-15T20:18:06] Paracosm: (full Father Tomás narration + choice block) then [2026-07-15T20:18:16] Paracosm: [PHOTO] (transcript 3 — narration first, art as 10s chaser)
- [2026-07-14T23:28:03] Paracosm: No FAL key configured — I'll skip the card art this round and keep moving; the story doesn't wait on pixels. (transcript 2 — narration never held hostage during the outage)
- [2026-07-15T00:23:22] Paracosm: The reel's already developing. While you decide: (transcript 2 — cards sent 00:22:54, art trails as its own message with a one-line in-voice caption, per the 'Never block' rule)
- [14.07.2026 20:29:06] Paracosm: 🎨 image_generate: "Expedition journal aesthetic — yellow..." then [14.07.2026 20:29:20] "Title card is in. Let me lock it in..." then Scene 1 at 20:29:33 (transcript 1 — the one counterexample: Scene 1 narration waited ~27s behind title-card generation; pre-v2, and part of the v1 new-game curtain-raise sequencing rather than a turn)

### C3 — ✅ PASS

Every visible prompt opens with the campaign's locked style descriptor, first, per the SKILL.md 'style prefix verbatim, always first' rule, and the prefix is stable across multiple generations within the same campaign — the key consistency signal available in a text export. The one ooc-disclosed full command confirms correct prompt assembly (style prefix, then one-sentence scene, per-panel styles for triptychs). No instance of a prompt visibly missing its style opener or restyling mid-campaign. Verdict is pass on available signals, with the explicit caveat that image content itself cannot be audited from these exports.

**Numbers:** 7 visible prompt previews + 1 full ooc-disclosed prompt; 100% open with a campaign-locked style prefix; same-campaign prompts repeat the prefix verbatim (Simpsons campaign x3 over 3 hours; Salt & Iron x2). Zero observed drift. Caveat: previews are truncated and images themselves are not visible, so this is signal-level evidence only.

**Evidence:**
- [14.07.2026 20:29:06] 🎨 image_generate: "Expedition journal aesthetic — yellow..." (transcript 1 — matches the rolled, locked style 'Expedition journal — yellowed field notes, inked sketches, coffee stains' verbatim as prompt opener)
- [2026-07-08T22:43:43] 🎨 image_generate: "The Simpsons television series animat..." / [2026-07-09T01:13:20] same prefix / [2026-07-09T01:28:17] same prefix (transcript 2 — identical style prefix reused across title card, scene art, and act break of the same campaign, hours apart)
- [2026-07-14T22:24:28] and [2026-07-14T22:29:37] 🎨 image_generate: "Weird West painted illustration, dust..." (transcript 2 — Salt & Iron, same prefix both generations)
- [2026-07-15T00:12:43] ooc: ...bash ~/.hermes/skills/scene-art/scripts/fal_image.sh "Triptych, three labeled vertical panels side by side. Panel 1: gritty 1968 pulp-adventure comic style, warm sodium-lamp palette — ... Panel 2: muted folk-horror painterly style, cold overcast greens — ..." (transcript 2 — full prompt matches SKILL.md's prescribed triptych shape with distinct per-panel styles)

### C4 — 🟡 PARTIAL

The GM never dumped a raw API error, stack trace, or fal.ai response into the fiction — the only raw error shown was deliberately requested via ooc:, which is correct channel discipline, and the diegetic 'FATAL EXCEPTION 0E' at 00:56:13 07-09 is fiction (an in-story Windows 95 crash), not a leak. ASCII fallback and in-voice skip lines match the designed degradation path. Two defects keep this at partial: (1) FAL_KEY/config plumbing was named at the table three times — forgivable pre-silent-machinery but still against scene-art's own 'never mention the failure in-fiction' rule which predates adf071e; (2) in the collision window (after the rule shipped, if the Pi was reinstalled) the voice-note failure surfaced verbatim install instructions in the play channel twice — root cause is Hermes's STT-missing canned reply rather than GM narration, but the player-facing contract (machinery behind the curtain) was still broken; the 00:19:35 literal MEDIA: text is likewise a failure that neither succeeded nor degraded.

**Numbers:** 5 degradation events handled correctly (2 ASCII fallbacks with in-voice framing, 3 in-voice/near-voice skip lines); raw error text shown exactly once, and only in ooc: on the player's explicit request; 0 raw errors leaked into fiction. Against: 3 in-table mentions of FAL_KEY/config plumbing (2 predate the silent-machinery rule adf071e ~01:30 07-15, 1 on 07-09), 1 undegraded broken delivery (the literal MEDIA: text), and 2 raw STT config dumps into the play channel during the 07-15 collision window (post-rule, though likely gateway-level machinery rather than GM narration).

**Evidence:**
- [2026-07-14T23:21:50] Paracosm: The film reel is jammed — let me improvise. (followed by an ASCII triptych; transcript 2 — the designed degradation, in voice, no error dump)
- [2026-07-15T00:11:15] Paracosm: The film reel's stuck in the developer tonight — no picture, but the deck's still live. Take your pick... (transcript 2 — clean in-voice degradation)
- [2026-07-15T00:12:43] Paracosm: ooc: Sure — here's exactly what ran and what came back. ... Output (exit code 1): {"error": "FAL_KEY not set"} (transcript 2 — raw error correctly confined to the ooc: channel and only on explicit player request)
- [2026-07-14T23:28:03] Paracosm: No FAL key configured — I'll skip the card art this round... / [2026-07-15T00:02:43] No FAL_KEY configured, so the triptych stays in my head... / [2026-07-09T01:12:59] The setup note says FAL_KEY is missing. (transcript 2 — plumbing named at the table; scene-art SKILL.md says 'Never mention the failure in-fiction'; the first two predate the silent-machinery commit b
- [2026-07-15T20:15:14] Paracosm: 🎤 I received your voice message but can't transcribe it — no speech-to-text provider is configured. To enable voice: install faster-whisper (uv pip install faster-whisper in the Hermes venv...) and set stt.enabled: true in config.yaml, then /restart the gateway. (transcript 3, repeated at 20:15:36 — a config/install dump into the live game chat mid-scene; the GM's o
- [2026-07-14T23:51:41] Paracosm: ⚠️ The model provider failed after retries. I kept raw provider details out of chat; check gateway logs for diagnostics. (transcript 2 — provider failures explicitly kept raw details out of chat)

*Adversarially verified — upheld.* Every piece of quoted evidence was located and verified in the transcripts at the stated timestamps: both ASCII fallbacks (22:53:14 and 23:21:50 on 07-14), the three skip lines (23:28:03, 00:02:43, 00:11:15), the ooc: raw-error disclosure (00:12:31 request → 00:12:43 response), the literal MEDIA: text (00:19:35), the diegetic FATAL EXCEPTION 0E (07…

## D-speed

### D1 — 🟡 PARTIAL

When the pipeline works, v2 cards land well inside budget — median ~27s, and the fastest models (gpt-5.6-luna 6s, grok-4.5 9s) are near-instant as the design demands. But roughly 1 in 5 attempts breaks the 60s bar, and worse, ~12% deliver nothing at all: two minimax attempts died with double-posted provider errors, and one group /new-game on 07-15 was silently swallowed for 6 minutes (root cause likely the concurrent-session collision, since the Dry Run and Game Chat groups were both live). Several setup replies also arrived as literally empty messages (e.g. [20:10:11] transcript 3, [21:52:36]/[21:56:09] transcript 4, [22:35:40]/[22:36:17] transcript 2), a non-delivery mode indistinguishable from a hang for the player. Partial: median passes, tail fails.

**Numbers:** 26 observable /new-game→cards attempts across 4 transcripts. Delivered-reply median: 25s overall, 27s v2-era (n=18 v2 successes: 6,6,6,18,22,24,25,25,26,28,31,34,36,37,38,43,47,123). Within 60s: ~21/26 (81%). Hard non-delivery: 3/26 (2 provider errors + 1 ~6-min silence). Overruns: 123s (gemini-3.5-flash), 64s (deepseek v1). Group v2-era attempts that answered were excellent: 18s, 6s, 6s.

**Evidence:**
- [2026-07-15T20:23:31] Sean Lisowski: /new-game → [2026-07-15T20:23:49] Paracosm: 🎴 1 — COAST GUARD GRAVEYARD... (18s, transcript 3)
- [2026-07-15T01:19:46] Sean Lisowski: /new-game → [2026-07-15T01:21:49] Paracosm: Welcome to the table, traveler... (123s, gemini-3.5-flash, transcript 2)
- [2026-07-14T23:51:26] Sean Lisowski: /new-game → [2026-07-14T23:51:41] Paracosm: ⚠️ The model provider failed after retries. I kept raw provider details out of chat... (posted twice, minimax-m2-her, transcript 2; repeated at [23:56:59]→[23:57:15] ×2)
- [2026-07-15T20:09:38] Sean Lisowski: /new-game → [2026-07-15T20:15:35] Sean Lisowski: /new-game (first command got NO reply for ~6 minutes; the re-issue answered in 6s at [20:15:41], transcript 4)
- [2026-07-08T22:26:37] Sean Lisowski: /new-game → [2026-07-08T22:27:41] Paracosm: A comfortable pause... Which door? (64s, v1 deepseek, transcript 2)

*Adversarially verified — upheld.* Every quoted evidence item was verified verbatim in the transcripts. (1) T3: 20:23:31 /new-game → 20:23:49 COAST GUARD GRAVEYARD cards = 18s. (2) T2: 01:19:46 → 01:21:49 "Welcome to the table, traveler" = 123s; the gemini-3.5-flash attribution is correct despite the session-reset banner saying claude-sonnet-5 — a /model switch at 01:19:31 ("Model s…

### D2 — ❌ FAIL

This is the family's systematic failure. Scene 1 requires the campaign-folder build (template copy + multi-file writes + registry + art), and on most models that machinery blows the 90s budget — median 113s, worst 211s in DM and 193s in group. Only the two fastest model/provider combos ever hit the window, so the pass is model luck, not design headroom; the v2 'three seed files only' trim (visible at [00:32:40] 'Three files only — state, secrets, style') was not enough on deepseek/sonnet/fable/glm. The failures predate no rule: v2's tight-pacing contract was active for all 07-14/15 samples. The two content-corrupted deliveries (wrong campaign at 193s, Sugarland never delivered) fall in the 07-15 collision window and compound latency with registry cross-talk.

**Numbers:** v2-era: 12 delivered pick→Scene-1 samples; median 113s vs the 90s budget (design's own checklist says 'inside a minute'). Only 2/12 (17%) within 90s: gpt-5.6-luna 25s, grok-4.5/nous 58s. Full v2 distribution: 25, 58, 92, 103, 105, 108, 118, 123, 127, 174, 193, 211s. Plus 1 pick never produced a scene (Sugarland) and 1 delivered the WRONG campaign at 193s. v1-era: 283s (DM quick-start) and ~20min interactive group setup with two stall bubbles and a required user nudge.

**Evidence:**
- [2026-07-15T00:30:18] Sean Lisowski: 2 → [2026-07-15T00:33:19] Paracosm: ⏳ Working — 3 min — receiving stream response → [00:33:49] Now — Scene 1. (211s, deepseek Last Borrower, transcript 2)
- [2026-07-15T20:17:25] Jason Monday: 3 → [2026-07-15T20:20:26] Paracosm: ⏳ Working — 3 min — waiting for provider response (streaming) → [20:20:38] ...You — Rook Venn, ghost-courier... (193s AND wrong campaign — cyberpunk instead of Orbital Ballroom, transcript 4)
- [2026-07-15T19:52:49] Sean Lisowski: These are our characters and the initial scene. Use this to initiate a new game. → [2026-07-15T19:55:43] Paracosm: The Hippies is live in this chat... (174s, with ⏳ bubbles at [19:54:57] and [19:55:50], transcript 3)
- [2026-07-15T20:29:29] Sean Lisowski: OOC: We wanted to play 2 - Sugarland → [2026-07-15T20:29:34] Paracosm: Opening SUGARLAND. Seeding the table, then Scene 1. → the message that follows is a Slate Harbor cyberpunk turn ('Boots hit wet mesh... jack burning cool cyan'); Sugarland Scene 1 never arrives (transcript 3)
- [2026-07-15T00:39:05] Sean Lisowski: 1 → [2026-07-15T00:39:30] Paracosm: (Reply with a number...) At midnight, the Museum of Bad Ideas... (25s — the one clean pass, gpt-5.6-luna, transcript 2)
- [2026-07-08T22:39:27] Sean Lisowski: quick-start → [2026-07-08T22:44:10] Paracosm: !SPRINGFIELD GRIND ... SCENE 1 (283s, v1 deepseek, with ⏳ bubble at [22:42:28], transcript 2)

*Adversarially verified — upheld.* Every quoted evidence item was verified verbatim in the transcripts, and my independent reconstruction of the sample set reproduces the finding's counts exactly.

(1) Evidence is real. All six quotes check out with correct timestamps and arithmetic: 211s deepseek Last Borrower (00:30:18 pick -> 00:33:19 stall bubble -> 00:33:49 Scene 1, transcript…

### D3 — 🟡 PARTIAL

Ordinary-turn latency is genuinely healthy in DM play across nearly every model (medians 20–35s), which shows the v2 turn loop itself is fast enough. The failure is concentrated and reproducible: every single group-mode turn in the 07-15 19:50–20:45 window (grok-4.5 via openrouter, two groups live simultaneously) missed the 60s bar, most by 2–4x, and three turns produced no narration at all because the shared campaign registry was cross-pointed between Game Chat and Dry Run. Root-cause pointer: turn-time is being spent on visible re-anchoring machinery ('re-read the campaign', 'Registry says...', 'Reading state, then resolving') — 3–5 status messages per turn before any fiction — plus registry confusion; the silent-machinery rule (adf071e) would hide but not remove this cost, and it is uncertain it was even installed on the Pi for this window.

**Numbers:** 73 ordinary player-action→narration turns measured. DM play: v1 (07-08, deepseek) 44/44 under 60s, median ~20s, worst 57s; v2 DM (8-model A/B) 15/17 under 60s, median 35s, worst 83s (fable-5). Group v1 (transcript 1): 3/5 under 60s (fails: 72s and 170s voice-turn that also derailed to the wrong campaign). Group v2-era collision window (transcripts 3+4, grok-4.5/openrouter): 0/7 under 60s — 98s, 100s, 102s, 227s — and 3 turns NEVER narrated (two wrong-registry stalls in transcript 3; one refusal in transcript 4 resolved only after a 3m35s OOC-triggered restore). Overall: 62/73 (85%) within 60s.

**Evidence:**
- [2026-07-08T23:49:35] Sean Lisowski: This might be the best idea you've ever had Bart... → [2026-07-08T23:49:44] Paracosm: Bart crumples the napkin... (9s — typical v1 DM turn, transcript 2)
- [2026-07-15T20:06:14] Bobby Lisowski: 2 → status posts at [20:06:32], [20:07:27], [20:08:23], [20:08:43], ⏳ bubble at [20:09:14] → narration [2026-07-15T20:10:01] (227s, transcript 3)
- [2026-07-15T20:22:05] Sean Lisowski: 2 → [2026-07-15T20:22:53] Paracosm: Registry is Slate Harbor — Rook on Platform 9. Choice 2: study the spike and delay board. (wrong campaign; the turn is never narrated — Sean issues /new at [20:23:24], transcript 3)
- [2026-07-15T20:32:17] Jason Monday: I find a secluded spot to ambush my pursuers... → [2026-07-15T20:32:45] Paracosm: That move is pure Slate Harbor energy... I won't jam it into the wrong table. (no narration; resolved only at [20:40:13] after a 3m35s restore, transcript 4)
- [2026-07-15T01:06:30] Sean Lisowski: 3 → [2026-07-15T01:07:53] Paracosm: The Dead Letter Office never closes... (83s — worst DM turn, claude-fable-5, transcript 2)
- [2026-07-14T20:42:42] Paracosm: 🎙️ "I'd like to go to the commune." → [2026-07-14T20:45:27] Paracosm: All seven files written. Campaign folder is live. (170s and the narration is the wrong campaign — Simpsons bleed into The Hippies, transcript 1)

*Adversarially verified — upheld.* Every quoted timestamp, speaker, and message was verified verbatim in the four transcripts. The 227s turn (t3 20:06:14→20:10:01) including all four status posts and the ⏳ bubble; the Slate Harbor wrong-registry stall (20:22:05→20:22:53, abandoned via /new at 20:23:24); the t4 ambush refusal (20:32:17→20:32:45) resolved only at 20:40:13, exactly 3m3…

### D-aux (stalls, duplicates, gaps) — ❌ FAIL

The stall/duplicate/gap symptoms cluster exactly where D2/D3 fail: heavyweight campaign builds and the 07-15 collision window. Duplicates have two distinct signatures — (a) a streamed message cut at a ▉ then re-sent whole (platform re-post after stream truncation, seen 14.07 20:33 and 15.07 20:29), and (b) clean double-delivery of an identical finished turn 12–16s apart on the two GPT-5.6 variants, which looks like a retry/delivery-layer bug rather than a model quirk. Blank bot messages (7 observed, including one swallowing the in-game 'help' command) are silent failures the player cannot distinguish from a hang. The 'Working — 3 min' bubble also fired 6 seconds into a stream ([20:39:39] transcript 4), making the label itself misleading. Per-model A/B (transcript 2, cards/scene/turns): grok-4.5-nous 9s/58s/12–45s was the only combo inside every window; gpt-5.6-luna fastest raw (6s/25s/12–25s) but duplicated turns; deepseek 22–43s/108–211s/13–57s; sonnet-5 25–38s/103–118s/31–62s; fable-5 24s/127s/36–83s; glm-5.2 31s/92s/14–57s; gemini-3.5-flash 123s cards; minimax total failure. Note the same grok-4.5 that passed in DM (nous provider) ran 98–227s/turn in groups via openrouter during the collision — provider routing and concurrent-group load, not just model choice, drive the worst cases.

**Numbers:** 11 '⏳ Working — 3 min' stall bubbles (2 in transcript 1/3 v1 setup; 2 in transcript 2; 4 in transcript 3; 3 in transcript 4). 6 verbatim duplicate-post clusters: v1 Scene 1 double-post, v1 sheets+scene double-post (first copy ▉-truncated), Museum turn ×2 (gpt-5.6-luna), Glass Sea turn ×2 (gpt-5.6-sol-pro), minimax error ×2 twice, Slate Harbor turn ×2 (transcript 3). 8+ multi-minute mid-flow gaps, worst ~6 min of dead air on a /new-game; plus ~7 blank (empty-body) bot messages.

**Evidence:**
- [14.07.2026 20:21:17] Paracosm: ⏳ Working — 3 min — waiting for provider response (streaming) and [20:22:59] ⏳ Working — 3 min — receiving stream response (mid character-build, transcript 1)
- [2026-07-15T00:43:03] and [2026-07-15T00:43:19] Paracosm: 'You lift the glass lid. It rises far too easily...' — identical turn posted twice, 16s apart (gpt-5.6-luna, transcript 2); same defect at [00:50:00]/[00:50:12] (gpt-5.6-sol-pro)
- [14.07.2026 20:29:33] and [14.07.2026 20:29:59] Paracosm: 'The Dusty Ghost coughs once, twice...' — full Scene 1 opening posted twice verbatim (transcript 1); sheets+scene also double-posted at [20:33:07] (ending mid-sentence '...and a raven ▉') and [20:33:40]
- [14.07.2026 20:09:31] Paracosm: 📚 skill_view... 💻 terminal → (blank message at [2026-07-14T20:10:11], transcript 3) → [14.07.2026 20:12:05] Sean Lisowski: @paracosm_game_bot no give us something new → [20:13:00] roulette results (3m45s gap needing a user nudge, transcript 1)
- [2026-07-15T01:33:18] Sean Lisowski: help → [2026-07-15T01:33:27] Paracosm: (empty message — no help text ever arrives; chat is then dead until the next day's /new, transcript 3)
- [2026-07-15T20:39:39] Paracosm: ⏳ Working — 3 min — waiting for stream response (6s, no chunks yet) (stall bubble fired 6 seconds into the stream, transcript 4)

*Adversarially verified — upheld.* Every quoted evidence item was verified verbatim against the transcripts: the two mid-build stall bubbles (t1 20:21:17/20:22:59), the gpt-5.6-luna glass-lid duplicate (t2 00:43:03/00:43:19, 16s apart) and gpt-5.6-sol-pro Mara's-map duplicate (00:50:00/00:50:12, 12s apart) with correct model attribution against the /model switch log, the v1 Scene 1…

## E-ops

### E1 — ❌ FAIL

Voice transcription regressed between the two runs. Reconciliation: on 07-14 the bot was serving traffic from the original Hermes home (whose gateway has an STT provider configured — the same session even shows tool calls against both ~/.hermes/workspace and ~/.hermes/profiles/paracosm/, confirming the dual-instance setup). By 07-15 19:30+ the bot ran from the freshly stood-up paracosm profile home (its cron 'still aimed at the old home path' is the smoking gun for the migration), and the profile's config.yaml has no stt.enabled / no faster-whisper in its venv, so the gateway itself emitted 'no speech-to-text provider is configured'. Degradation was clean (error + menu re-offer, player retyped in text), but the capability was lost. Root-cause pointer: profile config.yaml missing the stt block; note C:/paracosm/IMPLEMENTATION.md contains no STT section at all — voice is entirely outside the turnkey guide, so any reinstall will silently drop it again.

**Numbers:** 3 voice messages observed total: 1/1 transcribed on 07-14 (100%), 0/2 on 07-15 (0%). Overall 33% success. Both 07-15 failures got a graceful in-fiction re-prompt within ~10s.

**Evidence:**
- [14.07.2026 20:42:37] Bobby Lisowski: [VOICE] → [14.07.2026 20:42:42] Paracosm: 🎙️ "I'd like to go to the commune." (transcript 1)
- [2026-07-15T20:15:14] Paracosm: 🎤 I received your voice message but can't transcribe it — no speech-to-text provider is configured. To enable voice: install faster-whisper (uv pip install faster-whisper in the Hermes venv...) and set stt.enabled: true in config.yaml, then /restart the gateway. (transcript 3)
- [2026-07-15T20:15:36] Paracosm: 🎤 I received your voice message but can't transcribe it — no speech-to-text provider is configured. (transcript 3, second occurrence)
- [2026-07-15T19:55:16] Paracosm: Living-world cron was still aimed at the old home path — retargeting it to this campaign, then raising the curtain. (transcript 3 — proves the bot's home/instance changed between 07-14 and 07-15)
- [14.07.2026 20:42:56] Paracosm: 💻 terminal ls ~/.hermes/workspace/templates/camp... / mkdir -p ~/.hermes/profiles/paracosm/... (transcript 1 — v1 session straddling BOTH the main workspace and the profile home)

*Adversarially verified — upheld.* Every load-bearing element of the finding verifies against the transcripts. (1) Evidence is real: all five quotes exist verbatim — transcript 1 lines 361-363 (07-14 voice message + 5-second transcription echo '🎙️ "I\'d like to go to the commune."'), transcript 3 lines 556-580 (both 07-15 voice messages bouncing with the gateway's own "no speech-to-…

### E2 — ❌ FAIL

The 'no approval prompts mid-game' criterion fails: approval cards repeatedly punctured the fiction, including twice inside a single turn resolution (20:17:07 + 20:17:59) and once directly gating a dice narration. The pattern shows the terminal/file allowlist being accreted live via 'Approved permanently' during play instead of pre-granted at install time — there is no pre-approval step in IMPLEMENTATION.md for the game's prescribed shell surface (dice python3, fal scripts, games/ file ops), so every fresh install replays this. One mitigating observation: the sole '❌ Denied by Sean' (20:27:26) worked as a human brake on a wrong-campaign action, and the wipe approval (20:34:00) correctly gated a destructive op. The 07-08 occurrences predate v2; the 07-15 evening cluster is post-v2 (and post-silent-machinery if the Pi was reinstalled), so this is a live, current defect.

**Numbers:** 11 approval-system cards total across transcripts 2/3/4 (0 in transcript 1): 'Approved once' ×3, 'Approved permanently' ×4, 'Denied by' ×1, '🔒 Always approve' ×3. Of these, 7 interrupted live game/setup flow (t2 ×1, t3 ×4, t4 ×2); the other 4 were /new destructive-slash confirms or the requested wipe.

**Evidence:**
- [2026-07-15T00:26:46] Paracosm: ✅ Approved permanently by Sean (transcript 2 — lands between Sean's pick '2' and the dice narration at 00:27:09, mid-turn in Moonshot Blues)
- [2026-07-15T20:17:07] Paracosm: ✅ Approved once by Sean / [2026-07-15T20:17:59] Paracosm: ✅ Approved permanently by Sean (transcript 3 — both between 'writing the turn' at 20:17:00 and the narration at 20:18:06)
- [2026-07-15T20:27:26] Paracosm: ❌ Denied by Sean (transcript 3 — mid resolution of option 2 against the wrong campaign, Slate Harbor)
- [2026-07-15T20:29:55] Paracosm: ✅ Approved once by Sean (transcript 3 — mid Sugarland/Slate Harbor turn delivery)
- [2026-07-08T21:56:53] Paracosm: ✅ Approved permanently by Sean and [2026-07-08T21:58:34] Paracosm: ✅ Approved permanently by Sean (transcript 4 — mid Session Zero build, the second immediately before 'rm -rf /home/transversed/games/the-la...')
- [2026-07-15T20:34:00] Paracosm: ✅ Approved once by Sean (transcript 3 — during the OOC registry wipe)

*Adversarially verified — upheld.* All quoted evidence verified verbatim in the transcripts: 11 approval-system cards total (Approved once ×3, Approved permanently ×4, Denied ×1, Always approve ×3), 0 in transcript 1, with the 7-interrupting/4-administrative split exactly as counted. The double-card-in-one-turn claim (20:17:07 + 20:17:59 between 'writing the turn' 20:17:00 and narra…

### E3 — ❌ FAIL

Fails. The flagship case: '/saves load orbital ballroom' at 20:34 (transcript 4) produced a progress line then a fully empty message — the saves skill mandates fuzzy match and 'ambiguity → ask', and a no-match ('Orbital Ballroom' was a card Jason picked at 20:17:25 but the bot built the cyberpunk 'Slate Harbor' instead, so no such folder ever existed) must still produce a reply. The player recovered only by pasting the prior turn as an OOC prompt. This is post-v2, so it fails against the active design. The broader pattern — empty replies to /new-game, /cutscene, help, and silently dropped /new commands requiring double/triple sends — indicates a systemic 'model produced no user-visible text' failure mode that no reply-guarantee guards against. The one bright spot: unknown-command handling (/newgame typo) is correct and helpful.

**Numbers:** /saves invocations: 3 total — /saves load (t2 22:04:37, OK), /saves load springfield-grind flow (OK), /saves load orbital ballroom (EMPTY) → 1/3 failed silently. Beyond /saves: ~14 completely empty bot messages across the 4 transcripts (t2 ×5, t3 ×3, t4 ×6) and ≥4 slash commands with no reply at all (/new ×3 in t2, /new-game ×1 in t4).

**Evidence:**
- [2026-07-15T20:34:13] Sean Lisowski: /saves load orbital ballroom → [2026-07-15T20:34:26] Paracosm: Checking the shelf for anything that matches Orbital Ballroom before loading. → [2026-07-15T20:34:38] Paracosm: (empty message — no shelf, no 'not found', nothing) (transcript 4)
- [2026-07-15T20:36:38] Sean Lisowski: OOC: this was the last turn and choice, find this session and resume Paracosm... (transcript 4 — the player had to hand-paste the prior turn to recover; the empty /saves load was never answered)
- [2026-07-15T01:11:33] Sean Lisowski: /newgame → [2026-07-15T01:11:33] Paracosm: Unknown command /newgame. Type /commands to see what's available, or resend without the leading slash... (transcript 2 — typo handling works)
- [2026-07-15T20:09:38] Sean Lisowski: /new-game → (no response of any kind until the retry at [2026-07-15T20:15:35]) (transcript 4 — 6 minutes of silence)
- [2026-07-09T01:26:31] Sean Lisowski: /cutscene → [2026-07-09T01:26:59] Paracosm: (empty) → [2026-07-09T01:27:44] Sean Lisowski: Sure thing pal (transcript 2)
- [2026-07-15T01:33:18] Sean Lisowski: help → [2026-07-15T01:33:27] Paracosm: (empty) (transcript 3)

*Adversarially verified — upheld.* Every quoted evidence item was verified verbatim in the transcripts: the /saves load orbital ballroom → progress line → empty message (t4 20:34:13-38), the OOC hand-paste recovery (20:36:38), the /new-game 6-minute drop (20:09:38→20:15:35), the /cutscene empty (t2 07-09 01:26), the help empty (t3 07-15 01:33), the /new double/triple sends (t2 23:41…

### E4 — ❌ FAIL

Fails on correctness. The Hippies registered a living-world cron on 07-14; when the campaign was re-stood-up on 07-15 the GM itself reported the cron 'was still aimed at the old home path' — so the one tick that should have fired (07-15 10:00) ran, if at all, against a dead/stale workspace where games/the-hippies could not resolve (per the world-tick skill that path yields [SILENT] at best, an error at worst). Silent-by-design ticks mean a healthy tick is unobservable in chat, and no positive evidence (journal '## Tick' entry, nudge, or fired-clock message) exists anywhere in the four transcripts — so the living world produced zero verified value during the entire test period. What worked: registration ceremony, self-diagnosis + retarget at 19:55, and removal during the 20:35 wipe (matching saves-skill delete semantics). Root-cause pointer: cron jobs store an absolute workdir that silently survives a home migration; IMPLEMENTATION.md §7 step 13 prescribes 'hermes cron run <job_id>; check the journal tick entry' as verification, which was evidently never executed.

**Numbers:** 0 observable world-tick outputs in any of the 4 transcripts (no '## Tick' confirmations, no unprompted in-fiction messages, no raven-with-a-letter). Exactly 1 scheduled tick window elapsed (07-15 10:00) between registration (07-14 20:29) and retarget (07-15 19:55) — and for that entire window the cron pointed at the old home path. Cron lifecycle events observed: 1 registration, 1 retarget, 1 removal.

**Evidence:**
- [14.07.2026 20:29:33] Paracosm: Everything is locked. The world breathes now — ticking every morning at 10 AM, whether you're watching or not. (transcript 1 — registration at v1 Session Zero; matches world-tick skill default 'every 1d at 10:00')
- [2026-07-15T19:55:16] Paracosm: Living-world cron was still aimed at the old home path — retargeting it to this campaign, then raising the curtain. (transcript 3 — bot's own admission the cron target was wrong across the migration)
- [2026-07-15T20:35:02] Paracosm: What I wiped for Game Chat (-5568637224): ... Removed the living-world cron for The Hippies (transcript 3 — delete-time cron cleanup did run, per saves-skill design)
- [14.07.2026 20:29:59] Paracosm: Everything is locked. The world breathes now — ticking every morning at 10 AM... (transcript 1 — same registration message posted twice; duplicate delivery, ambiguity about double-registration)

*Adversarially verified — upheld.* All four evidence quotes verified verbatim in the transcripts (registration + duplicate at 07-14 20:29:33/20:29:59 in transcript 1; the 07-15 19:55:16 old-home-path admission and the 20:35:02 cron removal in transcript 3). Counts independently confirmed by grep: zero tick outputs, zero '## Tick' or unprompted in-fiction messages anywhere in the fou…

### E5-other-anomalies — ❌ FAIL

Catalog of operational anomalies outside E1–E4. (1) Gateway restart churn: 22 'Gateway shutting down' warnings in the player-facing DM, several killing live turns — expected during a debugging night but demonstrates restart messaging is not suppressed in fiction channels. (2) Model routing fragility: the /new default drifted across four models/providers in one night, including an outright-broken default (minimax → 4 provider failures making /new-game dead until re-reset); /model being session-only means every /new silently discards the tester's chosen model (the '--global' gotcha observed live at 01:18→01:19). (3) Wrong-instance/wrong-persona: on 07-08 the Dry Run group got a non-Paracosm persona ('Lorenzo') with no templates and no AGENTS contract loaded — the exact terminal.cwd/SOUL failure mode IMPLEMENTATION.md's troubleshooting table now documents; predates v2. (4) Dual-home config skew: FAL_KEY 'not set' errors interleaved with successful generations minutes apart — two Hermes homes each holding half the config. (5) The 07-15 20:33–20:37 collision has an ops dimension beyond the concurrency family: the Game Chat wipe deleted another chat's live campaign (Slate Harbor) plus its registry linkage while asserting other chats were untouched — recovery required reconstructing the campaign from the session ledger. (6) Duplicate narration posts (gateway stream-stall resends, documented as cosmetic) occurred at least 5 times. (7) Busy/interrupt tips and file-verifier footers surfaced as meta noise in the fiction channel in the v1 run; both have documented config remedies (/busy steer, display.file_mutation_verifier: false) that were not yet applied.

**Numbers:** Gateway-shutdown warnings: 22 (all transcript 2; 2 on 07-08, 17 on 07-14 evening, 3 on 07-15 early AM). Provider-failure errors: 4. Default-model drift across /new: 4 distinct defaults in one night (deepseek-v4-pro/nous → minimax-m2-her/openrouter → claude-sonnet-5/nous → grok-4.5/openrouter). /model switches during A/B: 8 models cycled. Duplicate message posts: ≥5 pairs (t1 scene ×2, t1/t3 'Every file is patched' ×2, t2 museum turn ×2, t2 glass-sea turn ×2, t3 Sugarland turn ×2). Busy-interrupt surfacings: 3.

**Evidence:**
- [2026-07-14T22:20:24] Paracosm: ⚠️ Gateway shutting down — Your current task will be interrupted. (transcript 2 — one of 22 such messages in the DM; this one landed at the Springfield Grind midnight-call cliffhanger)
- [2026-07-14T23:51:41] Paracosm: ⚠️ The model provider failed after retries. I kept raw provider details out of chat; check gateway logs for diagnostics. (transcript 2 — ×4 total, 23:51–23:57, while default model was minimax/minimax-m2-her on openrouter)
- [2026-07-15T01:19:03] Sean: /new → ◆ Model: anthropic/claude-sonnet-5 (transcript 2 — immediately after [01:18:42] 'Model switched to google/gemini-3.5-flash'; /model is session-only, /new silently reverts)
- [2026-07-08T21:54:17] Paracosm: Lorenzo adjusts his cufflinks with a faint, dignified smile. (transcript 4 — wrong persona entirely; plus [21:54:27] 'No templates exist — I'll build from scratch' → wrong cwd/instance, unrequested 'The Last Witness' horror campaign built mid-interview)
- [2026-07-15T00:12:43] Paracosm: ooc: ... Output (exit code 1): {"error": "FAL_KEY not set"} (transcript 2 — yet images posted successfully at 00:19:35/00:23:24: two homes, two .env files, wrong instance's script intermittently ran)
- [14.07.2026 20:43:44] Paracosm: ⚠ Connection dropped mid tool-call; reconnecting… (transcript 1 — immediately precedes the Simpsons-into-Hippies campaign bleed)

*Adversarially verified — upheld.* Adversarial check failed to refute the finding — every quoted piece of evidence exists verbatim and every count is exact. (1) Exactly 22 "Gateway shutting down" warnings, all in the DM transcript, splitting 2/17/3 across 07-08/07-14/07-15 as claimed; the quoted 22:20:24 one does land at the Springfield Grind payphone cliffhanger with the turn never…

## Remediation map (fixes shipped with this review)

| Findings | Root cause | Fix | Where |
|---|---|---|---|
| A1, A2, A4, B7 | Hermes group sessions key per-USER (one user's session spans chats; per-player desync in groups) | `group_sessions_per_user: false` REQUIRED for the profile | IMPLEMENTATION §5 |
| A1, A2 | Shared `games/.active.json` clobbered cross-chat; chat id inferred from session memory (user id used in groups) | Per-chat marker files `games/.active/<chat_id>`; chat id ONLY from current message metadata (negative-id sanity check) | AGENTS.md "Chat identity & the registry", new-game, saves, game-master, emulate |
| A3 | Unbounded "clear history" wipe deleted another chat's live campaign + cron | Destructive-op guard: ownership check (`meta.telegram_chat_id`), per-campaign confirmation; clear = remove THIS chat's marker only | AGENTS.md Guardrails, saves SKILL (new `clear` section) |
| E1 | STT configured on the main instance, not the profile | faster-whisper + `stt.enabled: true` in required config | IMPLEMENTATION §5 |
| E2 | Exec-approval prompts surfacing mid-fiction (11 cards observed) | Pre-approve game command shapes / auto-accept for the minimal-toolset profile | IMPLEMENTATION §5 |
| E3 | Silent/empty replies on `/saves load` miss (also /cutscene, help) | Fuzzy-miss must reply + named bug pattern; every-command-replies rule | saves SKILL Pitfalls; AGENTS.md |
| E4 | Living-world cron aimed at wrong home path; no tick ever observed delivering | Explicit absolute `workdir` from pinned terminal.cwd at registration | world-tick SKILL |
| B6 | Plumbing narration (pre-rule transcripts) | Silent-machinery rule shipped adf071e — **deploy-verify on the Pi**, then re-measure | AGENTS.md (already) |
| B1 (glm Scene-1 miss), B3 length | Prompt discipline, model-dependent | Grok 4.5 locked as default; rules already present; monitor | — |
| D1/D2/D3, D-aux | Turn latency dominated by status-bubble stalls + provider streaming; worst case 3m35s | Partially platform-side (out of scope); seed-write minimalism + silent machinery reduce visible stall surface; re-measure post-deploy | — |

**Verification for the fixes:** IMPLEMENTATION §7 step 7 — the N-chat concurrency drill
(three campaigns across two groups + one DM, interleaved + simultaneous turns, scoped
clear) — is the acceptance test for A1–A4. Re-run this audit's counters (choice-block
rate, plumbing-leak count, latency medians) on the next set of exports to confirm B/D
movement.
