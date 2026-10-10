# Why runs get stuck: six transcripts

**Source.** Six game transcripts (`solver_analysis/*.html`) from the [2026-10-09 run](../README.md):
- g50t p0 and p1
- tn36 p0 and p1
- bp35 p0
- sc25 p0

In each of these passes the model got stuck on a level that another pass solved. Except for bp35, which is stuck on level 2 in every pass, each game was solved on some other pass:
- tn36 level 2 once took 15 actions;
- g50t level 1 once took 39;
- sc25 level 1 took 23–75.

**Method.** One agent read each game's full reasoning against the same checklist. I then checked the key quotes against the transcripts.

**Per-game reports:** [g50t](g50t.md), [tn36](tn36.md), [bp35](bp35.md), [sc25](sc25.md).

The original transcripts are 1–2.6 MB each and are not committed. They are in the Kaggle run's output.

## What keeps happening

### 1. The model finds the right idea, then rules it out with a weak test

This happened in 5 of 6 passes.

**g50t p1:**
- The model wrote: *"the intended solution: press SPACE while standing on the plate to leave a ghost on the plate"*.
- It then checked one spot straight away, saw nothing, and dropped the idea.
- The copy was hidden under the player and only reached the plate a few moves later.

**tn36 p1:**
- The model proposed copying a demonstration panel into the live controls.
- It tested one fragment instead of the whole configuration, and moved on.

**sc25 p0:**
- The model wrote: *"If the tip were 2 rows tall it might fit into the narrow channel"*.
- It then tested while the avatar was full size, got no movement, and concluded: *"Stop pressing LEFT."*

**Pattern.** A single null result, often from a test that didn't meet its own preconditions, counts as a refutation, and the idea is never revisited.

### 2. The fresh start made things worse every time it fired

It fired in 5 passes. In each one it wiped knowledge the model needed, and the model rebuilt wrong facts:
- **tn36 p1:** it erased the copy-the-demo idea 7 actions after the model stated it.
- **g50t p1:** it fired in the turn where the decisive event became visible.
- **bp35:** it fired a minute after the model said it knew the route.

This agrees with the run-level numbers.

### 3. Some of what the model sees gets lost

- **Batches hide transient events.** In g50t p1 the door opened at step 71 in the middle of a pre-planned batch. The diff image covers the whole batch, so the model never saw it open.
- **The model's own tracking code misses things.** It filtered colours and ignored rotation and scale (tn36, g50t).
- **Front trimming drops earlier levels.** It took tn36 from 94 to 42 messages and dropped what level 1 had taught.

### 4. The scheduler sets games aside that were close

- **sc25 p0** got 14 minutes of turns, then none for the remaining 3.5 hours. It was about 10 actions from a likely solve.
- **bp35 p0** idled for 3.5 of 4 hours. It ran out of time while re-deriving the game after its fresh start.

## What this rules out, or makes unlikely

- **Fresh starts that delete context:** they hurt.
- **Replaying a game and keeping the best attempt:** not possible. The toolkit's competition mode, which Kaggle enforces, allows one `make` per game, and game resets become level resets.
- **Structured notes, periodic summaries, a stronger verification hint, extra guards:** Franzen tried these and found no clear gain ([write-up](../../../../WRITEUP.md), section 6). The per-game reports suggest a "knowledge ledger"; that is close to his structured notes, so its prior is weak.

## Candidate changes

1. **Stuck review instead of fresh start.** At a token threshold on one level, keep the whole conversation and add one prompt asking the model to:
   - list the hypotheses it has rejected on this level;
   - say, for each one, whether its test met the preconditions and covered the whole board over enough actions;
   - properly re-test the most coherent weakly-tested one.

   This targets pattern 1 while the right idea is still in context, and has none of the fresh start's costs (no deletion, no scheduler reset). Effort is low: it reuses the fresh-start trigger.
2. **Surprise guard for batches.** Stop a batch when an object other than the moving one appears, disappears or changes size outside the HUD border, and report it. This targets pattern 3. The risk is that it stops batches constantly in games with moving parts. Effort is medium; it extends the existing no-op guard.

## Measuring a change

Two-pass runs of all 25 games cannot detect a few points of change.

The plan is to run only the games whose outcome varies between passes, with more passes each. Games that always score 100, or always get stuck on level 1 or 2, carry no information. Keeping about 50 concurrent game runs keeps the compute per game the same as on Kaggle.
