# Verb table — the classic lexicon

Three equal ways to act, every turn: **reply with a number** from the scene's choice
block, **type a classic verb** below, or **say anything in plain words**. Classic verbs
are an aesthetic courtesy to players raised on parsers, never a required syntax.
Case-insensitive, prefixes accepted (N/S/E/W/NE/U/D...).

| Verb | Effect |
|---|---|
| LOOK / L | Re-describe the current scene, fresh eyes, no time cost |
| EXAMINE X / X X | Close detail on a thing; where clues live |
| GO <dir> / N,S,E,W,UP,DOWN | Travel; unknown exits get a gentle "you can't go that way — exits are..." |
| INVENTORY / I | Read the sheet's inventory from state.json, in-voice |
| TAKE X / DROP X | Move items world↔pack; update state same turn |
| USE X [ON Y] | Apply an item; the classic puzzle verb |
| OPEN / CLOSE / PUSH / PULL / TURN | Mechanism verbs |
| TALK TO X / ASK X ABOUT Y | Conversation; NPC knowledge comes from npcs.md "Knows" |
| GIVE X TO Y / SHOW X TO Y | Social-item interactions; dispositions may shift |
| ATTACK X / FIGHT X | Enter combat (combat.md) |
| HIDE / SNEAK | Agility vs passive wits; darkness helps you (and other things) |
| SEARCH | Sweep for the non-obvious; may roll wits |
| READ X | Books, signs, inscriptions — render the text |
| LIGHT X / EXTINGUISH X | Manage light sources; the grue is patient |
| WAIT / Z | Let the world take a beat; clock advances |
| SLEEP / REST / CAMP | Rest mechanics (dice.md healing); world-tick-relevant |
| MAP | Render/refresh the ASCII map from world.md, @ marks the party |
| RECAP / STORY | "Previously on..." from recap.md + journal tail |
| SHEET / STATS | Character sheet, formatted, from state.json |
| QUESTS / JOURNAL | Active quests with current objectives |
| HELP | One-screen how-to: numbers pick menu options, verbs + plain words both work, `ooc:` talks to the GM, key slash commands |
| XYZZY | Something. Never the same thing twice. |

Unknown input is never "I don't understand" — interpret intent generously; if truly
ambiguous, offer the two most likely readings in-voice.
