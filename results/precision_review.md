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

## Extension to 2020-2026: the same check on 2020-2023 (2026-10-14, evening)

The analysis was extended to 2020-2026 with the same rules and the same method. The question for the new years is
whether each rule's words mean the same thing in 2020-2023 as in 2024-2026 (sense drift): a word that is used in
another sense more often in the early years inflates the early shares and flattens or exaggerates the change.

Checks, all on the final measure (title rule on the title or abstract rule on the abstract):
1. Most frequent matched words per rule, 2020-2023 and 2024-2026 side by side, titles
   (scratch audit) and abstracts (`results/audit_abstract_matches_by_period.txt`).
2. Ten random 2020-2023 papers matched by the abstract only, for every topic
   (`results/precision_ta_samples_2020_2023/`, seed 0), read one by one.
3. For the rules that looked weak: every 2020-2023 match read (diffusion: 44 papers, world models: 31, leader-follower: 8
   titles), and every paper whose membership changed under the corrected rule listed and read, both periods.
4. The 2024-2026 samples drawn with the same seed reproduce the archived ones exactly (same papers, same order, same rules),
   so the earlier review still applies to them.

What was wrong, and the fix (counts = papers, old -> new rule, 2020-2023 | 2024-2026):

| topic | problem (2020-2023 sample or full listing) | fix | 2020-23 | 2024-26 |
|---|---|---|---|---|
| Diffusion / flow generative models | 18 of 44 early matches are not generative models: advection-/reaction-diffusion, label diffusion, distributed (consensus) diffusion, diffusion tensor imaging, SDE drift and diffusion terms, thermal / pheromone / smoke diffusion, cognitive drift-diffusion model, diffusion distance, "diffusion of" (spread of robots, of responsibilities), intermittent-diffusion optimisation, game "score based", image "denoising models"; 2020-2022 have no generative-diffusion paper at all. A rule requiring a generative word next to "diffusion" was tried and dropped: it lost real 2024-2026 papers ("diffusion-based endoscopic image generation", "Diffusion and Transformer models") | those senses excluded | 44 -> 26 | 552 -> 541 |
| World models / video prediction | 12 of 31 early papers use the classical sense (the robot's semantic or symbolic world representation, the operator's mental model) or "real-world model(s)" | "world model" counts when a learning / prediction word is in the same sentence (learned, latent, deep, generative, predict, video, train, policy, dynamics, simulation, driving, embodied...), "real-world", "semantic", "spatial", "reliable", "abstract world model" excluded | 38 -> 26 | 125 -> 120 |
| Teleoperation | "leader-follower" is mostly multi-robot formation control (6 of 8 early titles; also most 2024-2026 hits) | kept only in teleoperation set-ups (bilateral / haptic leader-follower, leader-follower arms, devices, interfaces) | 300 -> 277 | 393 -> 377 |
| Cross-embodiment | "(for/on) any robot" is a generic portability claim (8 of 10 early abstract-only samples) | removed; added the plural sense that was missed: "diverse / multiple / novel robot embodiments", "across ... embodiments", "embodiment gap" (52 added papers read: about 45 in the cross-embodiment sense) | 21 -> 15 | 94 -> 127 |
| Language grounding | "non-verbal" matched "verbal"; "context-conditioned" matched "text-conditioned"; "natural language processing" as a field name | excluded | 180 -> 157 | 522 -> 501 |
| Deformable objects | "bag-of-words", "bag of tricks"; "deformable" for robot bodies, terrain, tactile elastomers, deformable convolution / attention | "deformable" counts only before an object word (objects, linear objects, materials, cloth, cables, tissue...); "bag of" excluded | 304 -> 210 | 361 -> 230 |
| Imitation learning / LfD | "a demonstration video is available at ..." (project-video links) | excluded | 870 -> 862 | 1241 -> 1229 |
| Learning from human video | the same project-video links ("Video demonstration: https://...") | excluded | 66 -> 56 | 133 -> 125 |
| Aerial robots / UAV | time-of-flight sensors; flight / aerial phases of legged robots | excluded | 1202 -> 1172 | 1062 -> 1041 |
| Micro / bio-inspired robots | fish-eye cameras; animal experiments / tissue in medical papers | excluded | 440 -> 429 | 406 -> 393 |
| Agriculture / field | energy / solar harvesting; image crops | excluded | 205 -> 200 | 238 -> 232 |
| Event cameras / neuromorphic | event-based (event-triggered) control, discrete-event simulators, Siamese networks (SNNs) | excluded | 110 -> 106 | 133 -> 131 |
| Uncertainty / probabilistic | "probabilistically complete" planners, probabilistic roadmaps | excluded | 1171 -> 1136 | 911 -> 894 |
| 3D Gaussian splatting | SplatPlanner (permutohedral lattice splatting, 2021) | excluded | 1 -> 0 | 223 -> 223 |
| Underwater / marine | "submarine bunker" | word boundary | 331 -> 330 | 380 -> 379 |

Counts: papers on the final research-article set with abstracts (22,629), old rules (scripts/04_topics.py before this
check) against the final rules, title or abstract; the shares are in the result tables. The world-model "foundation" cue
was narrowed to "foundation model(s)" after the redrawn samples showed "Industry Foundation Classes" (BIM) passing it.
Read and left unchanged (precision similar in both periods): dexterous ("dexterity" in a generic sense), tactile
("touching"), calibration ("calibrated" ground truth), wearable ("assistive"), safety ("shield", kinematic
"reachability"), industrial ("manufacturing process" of a device). These are known weak spots, not drift.
Topics whose 2020-2023 samples were all in the topic's sense: VLA, LLM/VLM, other generative, RL, sim-to-real,
datasets, reasoning, NeRF (one "implicit layer"), self-supervised, GNN, humanoid, legged, space, mobile manipulation,
whole-body, multi-robot, surgical, grasping, bimanual, contact-rich, articulated/affordance, haptics, navigation,
long-horizon, HRI, perception, 3D perception, SLAM, radar, prediction, motion planning, MPC, force control, hardware.

## CoRL 2026 (added 2026-10-28): review of its abstract-only matches

Independent reviewer (a separate agent), same criterion as above, every sample in `results/precision_ta_samples_corl2026/`
read (547 papers, 66 topics; the redraw reproduced all files), plus every CoRL 2026 member of the suspicious topics.
Full report with per-topic table and counts: `results/precision_review_corl2026.md` (local only: it quotes abstract phrases).

- Overall 407/467 correct (87%; 90% with borderline) on 58 topics; vocabulary topics 78/80. On the 41 topics found clean
  after the earlier fixes (~99%), CoRL 2026 gives 87.5%.
- Clean as before: VLA, LLM/VLM, language grounding, diffusion, imitation, RL, sim-to-real, world models, human video,
  teleoperation, cross-embodiment, humanoid, legged, grasping, bimanual, deformable, contact-rich, tactile, articulated.
- Worse at CoRL 2026, each backed by a count over all CoRL 2026 members (not only the 10-paper draw):
  - MPC / optimal control: 16 of 34 members rest only on "whole-body control" (learned humanoid controllers); all 2026
    venues 41 of 228 (18%) against 13 of 270 (4.8%) in 2024; of 15 read 2026 cases 11-14 are not optimisation-based.
    Removing them cuts at most the 2024→2026 raw rise from +1.6 to +0.4 points.
  - Calibration: about 19-20 of 38 members are sensor/robot calibration; 11 use the uncertainty sense (conformal,
    calibrated confidence), 7 a generic one ("Trust-Calibrated", "action calibration").
  - Human-robot interaction: 25 of 36 correct; 7 rest on "human-robot" in a data sense (paired data, co-training,
    embodiment gap): 19% of members against ≤ 2.5% elsewhere.
  - Navigation: bare "frontier" ("frontier models") carries 11 of 71 members (1.6-3% elsewhere).
  - Motion planning: bare "planner(s)" more and more means task-level VLM/LLM planners (field-wide drift, strongest here).
  - Multi-robot: "fleet data", "multi-robot pretraining" (multi-embodiment data); LLM "multi-agent" only 1 paper.
  - Hardware: "prototype" (ML sense) 0/3, "gear" (URLs, "gear meshing") 0/3, "fabricated" 2/2.
  - Perception title rule: bare "tracking" catches humanoid motion tracking control, "detection" failure detection.
  - Wearable: mostly data-collection wearables (UMI gloves, mocap suits): a scope question, not precision.
  - Safety: "reachab" in the kinematic/goal sense; 7/10 also in the 2024-26 draw, so the earlier 4/4 was optimistic.
  - URL and substring bugs: "pose graph" inside "propose Graph", "avian" in URLs, "space robot" in "task-space robot".
- Reviewer-effect control: the same reviewer re-read the reviewed 2024-26 draws of 8 flagged topics: 8 of 80 false there
  against 27 of 80 at CoRL 2026 (topics chosen after seeing the CoRL samples; the population counts are the evidence).
- Status: no rule changed yet (2026-10-28). Suggested fixes are listed in the report, section 4; untested.

## Rule fixes after the CoRL 2026 review (2026-10-28; user: "先修规则再发布")

What changed (scripts/04_topics.py; the version before is in archive/2020-2026_corl2026_before_rulefix/scripts/):
- URLs in abstracts are replaced by "(link)" before matching (12_title_abstract.py): lab names in GitHub links
  (HKUST-Aerial-Robotics, leggedrobotics, robot-learning.uk, labs/gear, mars-lab, davian) no longer count.
- MPC: "whole-body control" counts on titles only with a cue in the same title (QP, inverse dynamics, operational/task space,
  torque-based, hierarchical, Riccati, model-based ...); in abstracts (new override) when the abstract has an optimisation /
  model-based cue anywhere and no policy-learning word, or no learning word at all. "model predictive" also hyphenated.
- HRI: "human-robot" not before data / embodiment / retargeting / co-training words; "shared controllers" except "single" /
  "non-shared"; not "trust region" / "trust-calibrated".
- Calibration: not the confidence / uncertainty sense (conformal, calibrated confidence / probabilities / risk / belief,
  miscalibrated predictions ...) nor generic compounds (trust-, preference-, action calibration); "uncalibrated /
  miscalibrated / well-calibrated" cameras, sensors and robots still count, as they did before.
- Navigation: "frontier(s)" only in the exploration sense (frontier-based ..., or an exploration / map / grid cue in the same
  sentence), not "frontier models".
- Motion planning: "planner(s)" not after task / symbolic / high-level / LLM / VLM / language / PDDL / reasoning / semantic,
  unless a path / trajectory / waypoint word is in the same sentence.
- Safety: "reachab..." only as reachability analysis (reachable sets / tubes, Hamilton-Jacobi, backward / forward
  reachability, reach-avoid, reachability games), not kinematic or goal reachability.
- Perception (title rule): not failure / anomaly / fault / slip / collision / contact / error detection; humanoid motion
  tracking and whole-body tracking (control) do not count, tracking of people's or objects' motion does; "panoptic" added.
- Hardware (abstract rule): "prototype" not in the ML sense (prototype-based, class / visual / support prototypes); plural
  "prototypes" with a physical cue in the same sentence; "gear" not as a task object (gear insertion / assembly / meshing).
- Multi-robot: not "multi-robot pretraining / rollouts / data", "fleet data", "fleet-mean". Wearable: not the verb
  "rehabilitates", not AI "assistive agents". Small fixes: "\bpose graph", "\bavian", "task-space robot" ≠ space robot,
  MARS-LVIG, event-based pedestrian behaviour, whole-body interaction control, image "crops"; VSLAM / ORB-SLAM3 and
  SoftNeRF-type compounds now match.

How it was checked:
- Round 1 removed 662 topic memberships (all years). Two independent reviewers read every one of them with its matched
  phrases (results/rulefix_review_A_2026-10-28.txt: safety, perception, MPC; ..._B_...: the rest): 37 (A) + 73 (B) were
  wrong removals, mostly before 2026 (uncalibrated cameras, plural prototypes, exploration frontiers, classical QP whole-body
  control, human/object motion tracking). Their tested patches (section 3 of each review) were applied as round 2.
- Final rules vs the old ones (results/rulefix_final_check_2026-10-28.txt): 606 memberships removed, every one read by a
  reviewer: 559 right, 37 borderline, 10 still wrong (navigation 4 whose exploration cue is only in the title, MPC 2 RL+QP
  hybrids, calibration / motion planning / HRI / multi-robot 1 each). 35 added: 27 "model-predictive" MPC papers, 3 reach-avoid
  safety papers, 3 SLAM and 2 NeRF compounds; all read, all in the topic's sense.
- Scope kept as before (noted, user can change): data-collection wearables (UMI gloves, mocap suits) still count as wearable;
  visual anomaly detection titles no longer count as perception (as in the abstract rule, which never had it).
- Fresh-sample re-check after the fix (independent reviewer; `results/rulefix_recheck_2026-10-28.txt`), the 10 changed
  topics, seed-0 abstract-only draws with the final rules:
  - CoRL 2026: 69 C / 14 B / 10 F of 93 (before the fix: 60/9/31 of 100). All CoRL 2026 members of the 10 topics:
    232/33/20 of 285 (81% strict, 93% with borderline). In-sample: the fix was written from CoRL 2026's false hits.
  - 2024-26, other venues (the fairer test): 85 C / 9 B / 6 F of 100.
  - Still weak (not fixed; sizes in the re-check, section 3): calibration's uncertainty sense in other wordings ("calibrates
    ... residuals", "critic calibration", conformal "to calibrate"; growing at other 2026 venues too, about 0.2-0.4 pp of
    papers in 2024-26); "planner(s)" for task-level planners and learned modules; ML "prototype" (2 CoRL 2026 papers);
    "assistive" and "trust" broad in every period. Possible next fix for calibration: drop a match whose sentence has an
    uncertainty cue and no sensor cue (untested).

## Round 3: sentence-level vetoes (2026-10-28; user: "推完了接着修", after the push of rounds 1-2)

- New mechanism (scripts/04_topics.py: VETO, kept(), sentence_at()): for five topics a match of a target word does not count
  when its sentence has a cue of another sense and no cue of the topic's own sense. A title is one sentence; a Wearable title
  match may take its own-sense cue from the abstract. Sentences are not split after "e.g." / "i.e.".
  - Calibration: "calibrat..." with confidence / uncertainty / conformal / critic / risk cues and no sensor cue.
  - Motion planning: bare "planner(s)" with LLM / VLM / task / symbolic / high-level / agent / subgoal / skill cues and no
    motion cue (path, trajectory, collision, navigation, route, cost function ...).
  - HRI: "trust" only with a human cue in the sentence (user, operator, participants, public, usability ...).
  - Wearable: "assistive" only with a wearable / rehabilitation / disability / daily-living cue (or, for a title, in the abstract).
  - Hardware: "prototype" with ML / software cues and no physical cue.
- Check: two independent reviewers read every removal (258 in the first version; `results/rulefix_round3_review_{C,D}_2026-10-28.txt`,
  lists in `results/rulefix_diff_round3_2026-10-28/`) and tested cue additions corpus-wide; their patches were applied.
  Final round 3 vs round 2: 202 memberships removed, 0 added: 151 right, 45 borderline, 6 still wrong (motion planning 5:
  navigation / driving planners caught by "high-level", "agents", "skill"; wearable 1). Calibration 34 removed (30 right,
  4 borderline), HRI 31 (24 / 7), hardware 21 (all right).
- Fragile result: motion planning's whole-period trend becomes "declining" (q 0.040). Counting the 5 wrong removals back gives
  q 0.046; counting also the 10 borderline ones (learned "planners": video, diffusion, world-model search, heuristic,
  centralized) gives q 0.056 ("unclear"). The verdict depends on whether learned planners count as motion planning.
- Known keep-side leaks (not fixed): 8 wrong-sense papers keep their membership through an own-sense cue that has another
  meaning ("robots", "depth", "mechanism", "collaborative").
