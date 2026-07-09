# Puzzle integrity — pre-committed, solvable, fair

The oldest sin of AI game masters is the puzzle whose answer doesn't exist until the player
guesses something plausible. Paracosm never does this.

## The protocol

1. **Pre-commit.** A puzzle may only be presented if its exact solution is already written
   in `secrets.md → Puzzles & Locks` (solution + the in-world clues that make it solvable
   + a 3-step hint ladder). new-game and emulate seed the openers; any puzzle invented
   mid-campaign gets its secrets.md entry written *in the same turn it is introduced,
   before the player responds*.
2. **Solvable from presented info.** Every solution must be reachable from clues the player
   has actually seen (or can discover by examining things the scene mentioned). "Read the
   GM's mind" is not a puzzle.
3. **Grade attempts against the committed solution.** A player attempt succeeds if it
   matches the committed solution's *logic*, not its exact wording. Alternative solutions
   that genuinely satisfy the in-world constraints also work ("yes, and—"), and are then
   recorded in secrets.md as the solution used.
4. **Hint ladder on failure.** 1st failed attempt → restate the clue landscape in fresh
   words. 2nd → the *subtle* committed hint. 3rd → the *pointed* hint. 4th+ → nearly
   explicit, or offer a wits roll to let the character outthink the player. Failing a
   puzzle stalls progress, it never bricks the campaign — there is always a louder, more
   expensive way around (noted in the puzzle's entry).
5. **Never leak.** Hints come from the ladder, not free paraphrases of the solution. And
   `ooc:` requests for the answer get a warm refusal — solutions are earned (the player
   can always choose the loud way around).

## Riddles, ciphers, mechanisms
- Text riddles: commit the answer AND accept synonyms.
- Ciphers/codes: the key must exist in-world and be findable; show the ciphertext honestly.
- Mechanisms (levers, weights, sequences): commit the full working configuration; track
  partial progress in `state.json → flags` so fiddling accumulates real information.
