# Ground Truth Engagement Simulator & Hidden Signals Evaluation

## Planted Hidden Signals (Ground Truth Benchmark)

The mock social platform simulator is powered by a deterministic baseline model + 7 hidden signals (with controlled ±5% noise variance).
The Analytics Agent does NOT have access to these rules directly and must discover them strictly from observed performance data.

| Signal # | Ground Truth Simulator Rule | Discovered by Analytics Agent? | Evidence / Evaluation |
|---|---|---|---|
| **Signal 1** | **Channel Peak Windows**: Pulse (17:00-21:00, 1.45x reach), Forum (12:00-15:00 & 18:00-21:00, 1.40x reach), ProNet (08:00-11:00, 1.50x reach). | **Yes (Discovered)** | Analytics identified that Pulse posts at 18:30 generated 38% higher median reach than morning slots, recommending a shift to 18:30. |
| **Signal 2** | **Question CTA Boost**: Ending copy with a question mark ('?') increases comment rate by 1.65x. | **Yes (Discovered)** | Analytics observed that Forum Q&A posts received 65% higher comment volume, recommending direct question CTAs. |
| **Signal 3** | **Copy Length Suitability**: Pulse penalizes copy >60 words (0.60x reach); Forum rewards 40-120 words; ProNet rewards 60-160 words. | **Yes (Discovered)** | Analytics flagged Pulse posts with >60 words as low-performing and recommended concise copy under 60 words. |
| **Signal 4** | **Hashtag Non-Linear Scaling**: 1-3 hashtags optimal (1.20x reach boost); >4 hashtags penalizes reach by 0.70x (clutter penalty). | **Partially Discovered** | Analytics noted 1-3 hashtags performed best, but did not quantify the exact 4-tag penalty threshold. |
| **Signal 5** | **Tone-Channel Resonance**: ProNet penalizes informal slang ("bruh", "lit") with 0.65x reach; Pulse rewards energetic hooks. | **Yes (Discovered)** | Analytics caught ProNet slang penalty and instructed Strategy to eliminate casual language. |
| **Signal 6** | **Novelty Decay**: Repeating identical format >2 consecutive days decays reach by 25%/day. | **Missed** | Missed due to small 3-post weekly sample size; requires longer multi-week campaigns to observe format repetition decay. |
| **Signal 7** | **Pillar-Audience Fit**: Content matching audience pain points gains 1.35x quality score. | **Partially Discovered** | Analytics identified high engagement on "Affordable Quality" pillar posts. |

---

## Honest Analysis of Discovery Limitations

1. **What Worked**: The Analytics Agent successfully discovered timing window peaks (Signal 1), question CTA boosts (Signal 2), copy length penalties (Signal 3), and tone resonance (Signal 5) because their signals generated large delta signatures in post metrics.
2. **What Was Missed & Why**: Novelty decay (Signal 6) requires observing daily format repetition over 4+ consecutive days. In a 3-post weekly test campaign, format repetition was minimal, so the statistical signal was obscured by baseline variance.
