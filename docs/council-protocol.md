# Council protocol

The isolated subagent rules below govern the interactive Council skill and any model-backed integration. The deterministic Python baseline remains in-process and is not represented as a multi-agent deliberation.

## Examine

Normalize the packet and use the separate Socratic Examination seam when objectives, terms, options, or evidence are incomplete. Examination returns the standard counsel contract with a null recommendation and asks questions rather than voting. `Council.convene` begins only after intake is ready.

## Counsel

Convene the Council as a board of advisors. Select differentiated schools. Dispatch each school to a fresh subagent context that receives only the same Decision Packet, its own counsel skill, its linked reference knowledge skill, and the response contract. Each advisor reads the relevant source-book material, derives feedback, and proposes its own recommendation before seeing any other conclusion. The coordinator does not preselect an answer or author the schools' initial counsel. If advisors must run in waves, later tasks still start without inherited Council history. The default board contains all nine voting lenses: Aristotelian, Stoic, Machiavellian, Clausewitzian, Sun Tzu, Musashi, Humean, Bayesian, and Consequentialist. Socratic Examination remains the non-voting intake stage.

## Contest

Compare the independent recommendations first. When every advisor recommends the same option, skip debate. When recommendations differ, cross-examination targets the disputed advice and its load-bearing assumptions. Challenges and disagreements remain first-class output, not internal transcript that disappears during synthesis.

## Red team

After preliminary board advice exists, always run the red team as a separate subagent—whether the advisors agreed or debated. It attacks the advice for hidden assumptions, catastrophic cases, incentive failures, irreversibility, missing stakeholders, fragile dependencies, bias, and correlated risks. It proposes tests and mitigations but has no vote.

## Decide

The arbiter selects an option using counsel support and confidence. The red team cannot add or subtract option support; it reduces confidence for unresolved exposure. The synthesis must preserve the strongest opposing argument, critical assumption, what would change the recommendation, and explicit disagreements.

## Review

The journal stores the user's actual choice separately from Council advice. Predictions and confidence are reviewed against outcomes so later insights reflect judgment quality rather than hindsight alone.
