# Topic codebook for semantic labelling, v2 (2026-10-28, full run)

v2 settles the boundary cases the 500-paper pilot exposed (results/semantic_pilot_2026-10-28/); changes from v1 are marked [v2].

Read the paper's title and abstract and decide which topics it is about. Two labels per paper:

- **involves**: the paper's own work (its method, system, task, platform, data or evaluation) involves the topic.
  A topic named only as background, motivation, contrast ("unlike X"), related work or future work does NOT count.
  A paper usually involves several topics.
- **main**: the 1 to 3 topics that best describe the paper's main contribution. Every main topic is also an involves topic.

Judge the meaning, not the words: a paper counts even if it never uses the topic's usual words, and does not count when a
word is used in another sense. When unsure, decide by the definition; do not count a topic just because a word appears.
[v2] A routine component named in passing (e.g. "an EKF fuses the sensors") counts only where a topic says so. If no
topic fits the contribution, "main" may be empty. Decide from the title and abstract only; do not guess from a model's name.

## A. Learning methods and models

1. **VLA / robot foundation models**: vision-language-action models and generalist / foundation robot policies trained on
   large multi-task, often multi-robot data (RT-2, OpenVLA, π0, Octo, large behaviour models); training, fine-tuning,
   evaluating, steering or analysing them. [v2] A VLM fine-tuned to output actions counts even for one task. Not: a VLM or
   LLM used only for perception or planning (that is 2); an ordinary policy trained for one task.
2. **LLM / VLM**: large language models, vision-language models or multimodal LLMs used in the work (planning, reasoning,
   perception, reward or code generation, interaction), including the VLM backbone of a VLA. [v2] Open-vocabulary
   vision-language models (CLIP-type encoders, text-prompted detectors or segmenters) count.
3. **Language grounding / open-vocabulary**: robots that take natural-language instructions or goals, ground language in
   perception or action, follow instructions, or recognise open-vocabulary (arbitrary named) objects. [v2] A VLA paper
   counts only when language instructions or goals are part of its tasks or evaluation as described in the abstract.
4. **Diffusion / flow generative models**: denoising diffusion, score-based models, flow matching, rectified flow,
   consistency models, used for policies, planning, generation or perception. Not: physical, heat, chemical or
   information diffusion; diffusion tensor imaging.
5. **Other generative models**: VAEs, GANs, normalising flows, autoregressive generative models and other generative
   modelling that is not diffusion or flow matching. Not: "generative design" of hardware without a generative ML model.
   [v2] When a paper uses a generative model of unstated kind, give neither 4 nor 5.
6. **Imitation learning / learning from demonstration**: learning policies or skills from demonstrations (behaviour
   cloning, LfD, kinesthetic teaching, inverse RL from demonstrations). Not: "video demonstrations" of the results.
   [v2] Imitating reference motions or motion-capture clips counts (also 7 if trained with RL). Teacher-student policy
   distillation alone does not. A VLA paper counts only when it trains or fine-tunes on demonstrations.
7. **Reinforcement learning**: learning from rewards by trial and error (deep RL, policy gradient, Q-learning,
   actor-critic, RL fine-tuning, RL from human feedback, reward learning or design for RL).
8. **Sim-to-real**: transferring policies or models trained in simulation to real robots; domain randomisation;
   real-to-sim(-to-real); closing the reality gap. [v2] Counts when training (or tuning) in simulation or on synthetic data
   AND real-world deployment or evaluation are both evident; synthetic-to-real perception counts.
9. **World models / video prediction**: learned models of how the world evolves (latent or pixel-space dynamics, video
   prediction or generation) used for planning, policy learning, data generation or evaluation. Not: "world model" as a
   map or semantic representation of the environment; analytic dynamics models. [v2] Learned dynamics of objects,
   contacts, terrain or the robot-environment interaction count; a learned model of only the robot's own body or actuators
   (system identification, actuator networks) does not.
10. **Learning from human video / human-to-robot transfer**: using videos of people (egocentric, internet, in-the-wild) or
    transferring skills from human hands or bodies to robots. Not: the robot's own camera views; teleoperated robot data.
11. **Teleoperation (incl. data-collection interfaces)**: people controlling robots remotely for any purpose, and
    devices or interfaces for collecting robot demonstrations (VR teleoperation, UMI-style handheld grippers, leader-follower
    arms, puppeteering). [v2] Wearable data-collection devices (gloves, VR or body trackers, motion-capture suits) belong
    here, not in 31. Counts when the paper teleoperates robots, builds or uses such an interface, or collects its own data
    by teleoperation; training only on an existing teleoperated dataset does not.
12. **Datasets / benchmarks**: the paper contributes a new dataset, benchmark or large benchmarking study. Not: only
    evaluating on existing datasets. [v2] Data collected for the paper's own experiments counts only when the abstract
    presents it as a contribution (released, described as a dataset or benchmark).
13. **Reasoning / chain-of-thought**: the method performs explicit reasoning as a capability (spatial, physical,
    commonsense, causal or task reasoning; chain-of-thought; reasoning models or VLM reasoning; neuro-symbolic reasoning).
    [v2] "Reasoning" as a loose word for inference or computation does not count.
14. **Cross-embodiment**: methods, policies or data that span different robot embodiments (transfer across robots or
    morphologies, embodiment-agnostic policies, multi-embodiment training). [v2] Merely testing one method on two
    platforms does not count; the claim must be about crossing embodiments.
15. **3D Gaussian splatting**: uses Gaussian splatting representations.
16. **NeRF / neural implicit fields**: neural radiance fields and other neural implicit representations (neural SDFs,
    feature fields).
17. **Mamba / state-space sequence models**: Mamba, S4 and similar deep state-space sequence models (not classical
    state-space models of control).
18. **Self-supervised / pretraining / representation learning**: the work itself pretrains models or learns
    representations (self-supervised, contrastive, unsupervised representation learning), or studies pretraining. Not:
    merely using an off-the-shelf pretrained model. [v2] Self-supervised learning of any kind (labels generated
    automatically from the robot's own data) counts; supervised pretrain-then-fine-tune counts when pretraining is part of
    the method; a task-specific encoder trained end-to-end does not.
19. **Graph neural networks**: GNNs, graph attention or message-passing networks in the method.

## B. Platforms and domains

20. **Humanoid robots**: humanoid robots (real or simulated) and physics-based humanoid characters.
21. **Legged robots / locomotion**: legged robots (quadrupeds, bipeds, humanoids walking, hexapods) and legged locomotion.
    Not: locomotion of non-legged robots (wheels, snakes) unless legged.
22. **Aerial robots / UAV**: drones, multirotors, fixed-wing UAVs, aerial manipulators, flying robots.
23. **Autonomous driving**: self-driving cars and other road vehicles: their perception, prediction, planning, control,
    datasets and traffic scenes. Not: bird's-eye-view maps used by indoor robots. [v2] Perception or prediction work whose
    data or evaluation is road driving (KITTI, nuScenes, Waymo, Cityscapes) counts.
24. **Underwater / marine**: underwater vehicles (AUV, ROV), surface vessels and other marine robots or applications.
25. **Space robotics**: robots for space: on-orbit servicing, space manipulators, planetary rovers, microgravity.
26. **Mobile manipulation**: robots that combine base motion (wheels or legs) with manipulation.
27. **Whole-body control / loco-manipulation**: controlling the whole body of legged, humanoid or mobile robots jointly;
    whole-body motion; loco-manipulation.
28. **Soft robots**: soft-bodied robots, soft actuators, grippers or sensors, continuum robots.
29. **Micro / bio-inspired robots**: micro- and nano-robots, magnetically actuated small robots, robots whose design is
    inspired by animals or plants, bio-hybrid robots. [v2] Bio-inspired sensors that are not robots, and manipulation of
    cells by a conventional robot, do not count.
30. **Multi-robot / multi-agent / swarms**: several robots or embodied agents acting together (coordination, multi-robot
    planning, multi-agent RL with robots or vehicles, swarms, fleets operating jointly). Not: data pooled from several robot
    embodiments; several LLM software agents running one robot; other traffic participants around a single ego vehicle;
    [v2] roadside infrastructure cooperating with one vehicle.
31. **Wearable / exoskeleton / prosthesis / rehab**: devices worn by people that assist, augment, rehabilitate or replace
    body function (exoskeletons, exosuits, prostheses, orthoses, supernumerary limbs), rehabilitation robots, and
    assistive robots for people with disabilities or older adults (feeding, dressing, wheelchairs, assistive navigation
    for blind people). [v2] Wearable data-collection devices (gloves, VR or body trackers, motion-capture suits) do NOT
    count here (they are 11). Not: "assistive" forces in training, assistant robots in ordinary collaboration, AI assistants.
32. **Surgical / medical**: surgical robots, medical and clinical robotics, robots guided by medical imaging. [v2]
    Medical microrobots navigating in the body count here (not 44).
33. **Agriculture / field**: agricultural robots (crops, harvesting, weeding, orchards, livestock), forestry, field robots
    in natural outdoor or unstructured environments [v2] (forests, farms, caves, mines, planetary analogues), when field
    deployment is the paper's setting.
34. **Industrial / logistics / construction**: industrial manipulation and manufacturing, factories, warehouses and
    logistics, construction robots, welding, bin picking.

## C. Tasks and capabilities

35. **Manipulation (any)**: robots manipulating objects in any way.
36. **Grasping**: grasp synthesis, detection, planning or execution. [v2] A picking task counts when grasping is executed
    and evaluated; "pick-and-place" named only as an example does not.
37. **Dexterous / in-hand**: multi-fingered or anthropomorphic robot hands, dexterous or in-hand manipulation. Not:
    general "dexterity" of a parallel-jaw gripper.
38. **Bimanual**: two-arm or dual-arm manipulation and coordination.
39. **Deformable objects**: manipulating, perceiving or modelling deformable objects (cloth, rope, cables, bags, dough,
    tissue).
40. **Contact-rich / assembly**: contact-rich manipulation, assembly, insertion (peg-in-hole), tasks dominated by contact.
    [v2] Simple pushing without an emphasis on contact does not count.
41. **Articulated objects / affordance**: articulated objects (doors, drawers, cabinets) and affordance learning or
    detection.
42. **Tactile sensing**: touch and tactile sensors, visuotactile sensing, using touch for perception or control. [v2]
    Force/torque sensing alone does not count.
43. **Haptics**: haptic interfaces and force feedback for people (haptic devices, haptic feedback to operators or users),
    [v2] including force-feedback teleoperation and haptic devices without a robot.
44. **Navigation**: robots moving through environments to goals; exploration; vision-language navigation; social and
    obstacle-aware navigation. Not: medical "navigation" to anatomical targets (that is 32).
45. **Long-horizon / task planning / TAMP**: multi-step and long-horizon tasks, task planning, task and motion planning,
    symbolic or PDDL planning, behaviour trees, LLM or VLM task planners. [v2] Task allocation and scheduling for robots
    count; search over low-level actions counts only when a multi-step task structure is the point.
46. **Human-robot interaction**: interaction, collaboration or communication with people; user studies; shared autonomy;
    social robots; people's trust in robots. Not: paired human/robot data; trust between machines; optimisation "trust
    regions". [v2] User studies of devices that are not robots do not count; trials of exoskeletons or prostheses are 31
    and count here only when the interaction itself (interface, intent, shared control) is studied.
47. **Perception: detection / segmentation / tracking / pose**: detecting, segmenting, tracking or estimating the pose of
    objects, people or scenes from sensors; object recognition; scene understanding. Not: detection of task failures or
    system faults, or collisions as events; a robot tracking a reference motion (control); the robot's own pose or odometry
    (that is 49). [v2] Visual detection of defects or anomalies in images counts; human pose estimation counts.
48. **3D perception / LiDAR / point clouds**: 3D sensing and representations: LiDAR, point clouds, depth estimation,
    occupancy, voxels, 3D reconstruction, 3D scene understanding. [v2] A depth image used only as an input channel does not
    count unless the method builds or processes 3D structure.
49. **SLAM / localization / state estimation**: SLAM, localisation, odometry, state estimation, place recognition,
    mapping for localisation.
50. **Radar / 4D radar**: radar sensing (mmWave, 4D radar). [v2] RF or RFID localisation does not count.
51. **Event cameras / neuromorphic**: event cameras, dynamic vision sensors, spiking or neuromorphic processing.
52. **Prediction / forecasting**: forecasting future trajectories, motions or intentions of people, vehicles or other
    agents, or other future quantities. Not: a world model predicting the next frames (that is 9). [v2] Recognising a
    current state or intent without predicting the future does not count; future occupancy prediction counts (and 9 if
    it is a learned world model).

## D. Classic methods

53. **Motion / path planning**: planning robot motions, paths or trajectories (sampling-, search- or optimisation-based,
    and learned trajectory planners such as diffusion planners); collision avoidance. Not: task-level planners that output
    subgoals, skills or language (that is 45); video planners. [v2] Optimisation-based trajectory planning counts as both
    53 and 54.
54. **MPC / optimal control / trajectory optimisation**: model predictive control, optimal control, trajectory
    optimisation (MPPI, iLQR, DDP), optimisation-based (QP, inverse-dynamics) whole-body control. Not: learned (RL or
    imitation) whole-body controllers.
55. **Safety / verification**: technical safety: safe RL and control, safety filters, control barrier functions,
    reachability analysis for safety, formal verification, temporal-logic specifications, risk-aware or chance-constrained
    control, safety guarantees. Not: kinematic reachability; "risk" of wrong labels; general reliability. [v2] Stability
    certificates (Lyapunov, contraction) alone do not count; fault tolerance counts only when framed as safety.
56. **Uncertainty / probabilistic**: representing, estimating or acting under uncertainty: Bayesian and probabilistic
    models, Gaussian processes, uncertainty quantification, belief-space planning, stochastic models. [v2] A routine Kalman
    or particle filter counts only when the paper's contribution concerns its uncertainty handling; Bayesian optimisation
    used only as a black-box optimiser and robust control against model error do not count.
57. **Force / impedance control**: force control, impedance, admittance or compliance control, regulation of contact
    forces. [v2] Force estimation without control does not count; a learned policy counts only when force or compliance is
    explicitly controlled.
58. **Hardware: mechanisms / actuators / design**: the paper designs, builds or analyses physical hardware: mechanisms,
    actuators, transmissions, grippers or hands, fabrication, physical prototypes. Not: ML "prototypes"; a learning paper
    that only mentions actuator dynamics. [v2] Kinematic or stiffness analysis of a mechanism counts; general rigid-body
    dynamics algorithms do not.
59. **Calibration / registration**: calibration of sensors, cameras, robots or kinematics (incl. hand-eye); point-cloud
    or image registration. Not: calibration of confidence, uncertainty or probabilities. [v2] Fitting a body model to a
    user is not calibration.
