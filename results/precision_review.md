# Precision review of the topic rules (manual reading, 2026-10-14)

Method: random titles matched by each rule (2024-2026) were read and judged "is this paper about the topic".
Samples: round 1 seed 0 (`precision_samples_round1_seed0/`), then rules were fixed and re-checked on fresh samples
(seeds 1-3) so the fixes were not judged on the titles they were tuned on. Judgements are mine; sample sizes are small,
so read these as "high / medium", not as measured rates. Recall was not measured.

| topic | final check | correct / read | note |
|---|---|---|---|
| VLA / robot foundation models | seed 0 | 15/15 | |
| LLM / VLM | seed 0 | 15/15 | |
| Language grounding / open-vocabulary | seed 0 | 12/12 | |
| Diffusion / flow generative models | seed 0 | 15/15 | includes diffusion for perception/planning, not only policies |
| Other generative models | seed 0 | 11/12 | "generative design" of grippers |
| Imitation learning / LfD | seed 0 | 15/15 | |
| Reinforcement learning | seed 0 | 15/15 | |
| Sim-to-real | seed 0 | 12/12 | |
| World models / video prediction | seed 1 | 8/8 | after adding video generation/prediction |
| Learning from human video / human-to-robot transfer | seed 2 | 10/10 | seed 0: ~7/15 (bare "egocentric" = robot's own view); fixed |
| Teleoperation (incl. data-collection interfaces) | seed 1 | 8/8 | covers classic teleoperation too, not only data collection |
| Datasets / benchmarks | seed 0 | 12/12 | |
| Reasoning / chain-of-thought | seed 1 | 8/8 | seed 0: 4/15 false hits on "Rethinking"; fixed |
| Cross-embodiment | seed 1 | 8/8 | seed 0: "many robots" hit "any robot"; fixed |
| 3D Gaussian splatting | seed 3 | 6/6 | split from NeRF after the n-gram check |
| NeRF / neural implicit fields | seed 0 | ~12/12 | |
| Mamba | seed 3 | 6/6 | |
| Self-supervised / pretraining / representation | seed 0 | 12/12 | |
| Graph neural networks | seed 0 | 12/12 | |
| Humanoid robots | seed 0 | 12/12 | |
| Legged locomotion | seed 0 | 12/12 | |
| Aerial robots / UAV | seed 0 | 12/12 | |
| Autonomous driving | seed 1 | 8/8 | seed 0: ~9/12 (bare "traffic", "car"); fixed |
| Underwater / marine | seed 0 | 8/8 | |
| Space robotics | seed 2 | 10/10 | seed 0: 6/8 (transorbital, satellite maps); seed 1: planetary gears; fixed |
| Mobile manipulation | seed 0 | 7/7 | |
| Whole-body control / loco-manipulation | seed 3 | 6/6 | |
| Soft robots | seed 0 | ~7/8 | origami joints counted |
| Micro / bio-inspired robots | seed 1 | 8/8 | seed 0: "Bird's-Eye View"; fixed |
| Multi-robot / multi-agent / swarms | seed 1 | 8/8 | multi-agent includes MARL for driving |
| Wearable / exoskeleton / prosthesis / rehab | seed 0 | 8/8 | |
| Surgical / medical | seed 0 | 8/8 | |
| Agriculture / field | seed 1 | 8/8 | "plant" restricted (control-theory "plant") |
| Industrial / logistics / construction | seed 2 | 10/10 | seed 0: 3/8 ("reconstruction"); seed 1: "map construction"; fixed |
| Grasping | seed 0 | 8/8 | |
| Dexterous / in-hand | seed 0 | 8/8 | |
| Bimanual | seed 0 | 8/8 | |
| Deformable objects | seed 1 | ~7/8 | seed 0: ~4/8 (cable-driven devices); fixed; "deformable" robot bodies remain |
| Contact-rich / assembly | seed 1 | 8/8 | |
| Articulated objects / affordance | seed 0 | 8/8 | |
| Tactile sensing | seed 1 | 8/8 | tactile paving excluded |
| Haptics | seed 0 | 7/7 | |
| Navigation | seed 0 | 7/7 | |
| Long-horizon / task planning / TAMP | seed 1 | 8/8 | seed 0: 5/7 (bare "hierarchical"); fixed |
| Human-robot interaction | seed 0 | 7/7 | |
| Perception: detection / segmentation / tracking / pose | seed 1 | 8/8 | trajectory-tracking control excluded |
| 3D perception / LiDAR / point clouds | seed 0 | 7/7 | |
| SLAM / localization / state estimation | seed 0 | 7/7 | |
| Radar / 4D radar | seed 3 | 6/6 | |
| Event cameras / neuromorphic | seed 0 | 7/7 | |
| Prediction / forecasting | seed 0 | 7/7 | |
| Motion / path planning | seed 0 | 7/7 | |
| MPC / optimal control / trajectory optimization | seed 1 | 8/8 | seed 0: 5/7 ("convex hull", "language model predictive"); fixed |
| Safety / verification | seed 0 | ~6/7 | "safe" as an adjective in hardware titles |
| Uncertainty / probabilistic | seed 0 | 7/7 | |
| Force / impedance control | seed 1 | 8/8 | impedance tomography excluded |
| Hardware: mechanisms / actuators / design | seed 2 | ~8/10 | weakest rule: over/under-actuated control papers partly removed; "prototype" removed after seed 2 |
| Calibration / registration | seed 1 | ~7/8 | "calibration-free" excluded after seed 1 |
| Manipulation (any) | not read | – | substring "manipulat"; broad indicator |

## Abstract-based matching (added 2026-10-14, after the user asked for abstracts)

Abstracts: 11,017 of 11,135 papers (2024-2026); every venue-year >= 97.9 % except Science Robotics (81 / 68 / 58 %),
whose gaps are editorials, viewpoints and research highlights (read 18 of them), i.e. the abstract measures cover research
articles only there. ICRA 2026: 1,064 from OpenAlex + 683 from Semantic Scholar, median length 175 vs 172 words.

Audit of what each rule matches inside abstracts (most frequent matched words) found substring and sense errors, fixed in
the rules for titles and abstracts alike before any result was read:
"limitation(s)" matched imitation (631 hits) -> \bimitation; "attention/neural/trust mechanism" matched hardware (107);
"fabrication/fabricated" matched deformable (36, also in titles); image "denoising" matched diffusion (also in titles);
youtube links matched human video; "random forest" matched agriculture; "hku-mars" matched space; "for this reason" and
"CoT" (= cost of transport) matched reasoning.

Precision of matches that come from the abstract only ("focus" measure: >= 2 abstract hits, no title hit), fresh seed 1,
after the fixes:

| topic | correct / read | note |
|---|---|---|
| Imitation learning / LfD | 9/10 | "experimental demonstration" in the showcase sense |
| Bimanual | 10/10 | |
| Contact-rich / assembly | 8/10 | "user assembly study", organoid "assembly" |
| SLAM / localization / state estimation | 6/10 | generic "mapping X to Y", "affordance localization": use the title measure |
| LLM / VLM | 10/10 | |
| Reasoning / chain-of-thought | – | after the fixes the word is used in a broad sense (contact reasoning, reasoning under uncertainty): measures the word, not specifically LLM-style reasoning |
| Diffusion / flow generative models | 9/10 | physical gas diffusion |
| Safety / verification | ~5-6/10 | motivational "safely", "safety-critical": abstract measures unreliable, use the title measure |
| VLA / robot foundation models | 5/5 | |
| World models / video prediction | 4/5 | "semantic world model" in a depth-estimation paper |
| Humanoid robots | 5/5 | |
| 3D Gaussian splatting | 5/5 | |
| Whole-body control / loco-manipulation | 4/5 | exoskeleton "whole-body" gravity compensation |
| Learning from human video | 5/5 | |

## Final measure: title + abstract (any occurrence) — review of abstract-only matches (2026-10-14, seeds 7-10)

Criterion: the abstract uses the word in the topic's sense (the paper engages with the topic, possibly in passing).
Rules rewritten for abstracts where title words are generic (scripts/04_topics.py, ABSTRACT_OVERRIDES): datasets
(contribution phrasing only), safety (technical safety terms), SLAM (no bare "mapping"/"localization"), perception (no bare
"detection"/"recognition"), uncertainty, hardware (no bare "mechanism"), industrial, reasoning (capability phrasing),
teleoperation (no bare "data collection"). Further substring/sense fixes found in this round, applied to titles too:
"satisfactory"->factory, "diffusion probabilistic", blood "vessels", "Collectively", search "forest", fruits as example
objects, bio-inspired "sensors", "re-construction", "in handling", "setpoint tracking", ropes/textiles as materials,
"user assembly study", "regenerative".

| topic | correct / read (after fixes) |
|---|---|
| VLA, LLM/VLM, imitation, RL, sim-to-real | 6/6 each |
| diffusion, world models | 5/6 each (information "diffusion"; SLAM "static world model") |
| humanoid, aerial, whole-body, soft, wearable, surgical, mobile manipulation, bimanual, tactile, haptics, navigation, long-horizon, 3D perception, SLAM (new rule), prediction, grasping, HRI | 5/5 each |
| legged | 4/5 (non-legged "locomotion": topic renamed "Legged robots / locomotion") |
| motion planning, MPC, safety (new rule), uncertainty (new rule), force, hardware (new rule), calibration, 3DGS, NeRF, language grounding, human video, radar, event, GNN, Mamba, cross-embodiment | 4/4 each (cross-embodiment 3-4/4) |
| fixed after reading (re-audited, not re-read): teleoperation 3/6, datasets 3-4/6, reasoning ~3/6, underwater 2/5, multi-robot 2-3/5, agriculture 3/5, micro/bio 3/5, industrial, dexterous 4/5, deformable 3/5, contact-rich 4/5, perception ~3/5, other generative 2-3/4 | audit of matched words clean after the fix |
