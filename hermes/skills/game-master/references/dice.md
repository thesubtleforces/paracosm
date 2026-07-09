# Dice — real rolls, shown honestly

## The iron rule
Every roll comes from a real random number generator executed in the terminal — never from
the model imagining a number. If you cannot run the RNG for some reason, say so out of
character and resolve narratively; never fake a die.

## Rolling

Preferred (portable, one roll or many):

```bash
python3 -c "import random;print(random.randint(1,20))"          # d20
python3 -c "import random;print([random.randint(1,6) for _ in range(2)])"  # 2d6
```

Fallback if python3 is unavailable:

```bash
echo $(( RANDOM % 20 + 1 ))    # d20
```

Roll advantage/disadvantage as two real rolls, take high/low.

## Core mechanic

**d20 + stat modifier vs DC.**

- Stats (might, agility, wits, presence, spirit) range -2..+4 for starting characters;
  the sheet in `state.json` holds the modifiers directly.
- DCs: 8 easy · 11 routine-under-pressure · 14 hard · 17 heroic · 20 legendary.
- Natural 20: success with a flourish (extra effect, not auto-godhood).
  Natural 1: failure with a complication (never pure slapstick unless tone allows).
- Margin matters: beat DC by 5+ → clean/bonus; miss by 5+ → fail forward with cost.
- **Advantage/disadvantage** replaces stacking situational modifiers: good positioning,
  the right tool, NPC help → advantage; darkness, wounds, the wrong tool → disadvantage.
  They cancel one-for-one.

## Damage & healing
- Light 1d4 · standard 1d6 · heavy 1d10 · monstrous 2d8 (+ might mod for melee).
- Short rest (in fiction, safe place): recover 1d6 HP once per world-day. Full night's
  sleep: half max. Zero HP → see combat.md death rules.

## Showing rolls

Dice visibility `shown` (default):

> 🎲 Agility check: d20(14) + 2 = **16** vs DC 14 — *success.*

Visibility `hidden`: roll anyway (real RNG, log the result in the journal entry's dice
field) and narrate the outcome without numbers. Visibility `gm-only` behaves like hidden
but answers honestly if the player asks `ooc:` what was rolled.

## When NOT to roll
- Outcome certain (walking across a room, buying bread with enough gold).
- Failure is boring and success inevitable given time — narrate it done.
- The player is asking a question, not attempting an action.
