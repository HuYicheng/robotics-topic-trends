# Co-occurrence of manipulation, imitation learning, VLA/VLM, diffusion/flow, Gaussian splatting

Title + abstract measure; papers with abstracts; raw shares (2026 = ICRA, RSS, T-RO, IJRR, Science Robotics only; years from scripts/config.py).

| combination                   |   n_2020 |   pct_2020 |   n_2021 |   pct_2021 |   n_2022 |   pct_2022 |   n_2023 |   pct_2023 |   n_2024 |   pct_2024 |   n_2025 |   pct_2025 |   n_2026 |   pct_2026 |
|:------------------------------|---------:|-----------:|---------:|-----------:|---------:|-----------:|---------:|-----------:|---------:|-----------:|---------:|-----------:|---------:|-----------:|
| manipulation                  |      481 |      17.71 |      570 |      19.17 |      536 |      19.51 |      684 |      21.2  |      878 |      21.07 |      997 |      21.97 |      965 |      34.04 |
| M+IL                          |       56 |       2.06 |       64 |       2.15 |       78 |       2.84 |      104 |       3.22 |      180 |       4.32 |      269 |       5.93 |      335 |      11.82 |
| M+IL+Gen(diffusion/flow)      |        0 |       0    |        0 |       0    |        0 |       0    |        4 |       0.12 |       20 |       0.48 |       50 |       1.1  |       77 |       2.72 |
| M+IL+VLA/VLM                  |        0 |       0    |        1 |       0.03 |        0 |       0    |        6 |       0.19 |       18 |       0.43 |       38 |       0.84 |       83 |       2.93 |
| M+IL+VLA/VLM+Gen              |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |        3 |       0.07 |        5 |       0.11 |       12 |       0.42 |
| M+GS                          |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |        4 |       0.1  |       30 |       0.66 |       21 |       0.74 |
| M+IL+GS                       |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |        1 |       0.02 |        5 |       0.11 |        5 |       0.18 |
| all five: M+IL+VLA/VLM+Gen+GS |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |
| flow matching (any)           |        0 |       0    |        2 |       0.07 |        2 |       0.07 |        0 |       0    |        4 |       0.1  |       15 |       0.33 |       82 |       2.89 |
| M+IL+flow matching            |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |        1 |       0.02 |        2 |       0.04 |       19 |       0.67 |

Pairwise lift in 2025 (all seven venues):

| pair      |   observed_pct |   expected_if_independent_pct |   lift |
|:----------|---------------:|------------------------------:|-------:|
| IL & Gen  |           1.81 |                          0.62 |   2.92 |
| IL & VLx  |           1.48 |                          1.04 |   1.41 |
| VLx & Gen |           0.77 |                          0.52 |   1.5  |
| M & GS    |           0.66 |                          0.64 |   1.03 |
| IL & GS   |           0.2  |                          0.33 |   0.6  |
| VLx & GS  |           0.18 |                          0.27 |   0.65 |
| Gen & GS  |           0.15 |                          0.16 |   0.95 |

Papers with manipulation + imitation learning + Gaussian splatting:

- IROS 2025 | LensDFF: Language-enhanced Sparse Feature Distillation for Efficient Few-Shot Dexterous Manipulation
- RSS 2025 | Novel Demonstration Generation with Gaussian Splatting Enables Robust One-Shot Manipulation
- RSS 2026 | TAIL-Safe: Task-Agnostic Safety Monitoring for Imitation Learning Policies
- CoRL 2024 | Splat-MOVER: Multi-Stage, Open-Vocabulary Robotic Manipulation via Editable Gaussian Splatting
- CoRL 2025 | Mobi-$\pi$: Mobilizing Your Robot Learning Policy
- CoRL 2025 | One Demo is Worth a Thousand Trajectories: Action-View Augmentation for Visuomotor Policies
- CoRL 2025 | Motion Blender Gaussian Splatting for Dynamic Reconstruction
- ICRA 2026 | SINGER: An Onboard Generalist Vision-Language Navigation Policy for Drones
- CoRL 2026 | Worlds in One Demo: A Synthetic Data Engine for Learning Open-World Mobile Manipulation
- CoRL 2026 | LEGS: Fine-Tuning Teleop-Free VLAs for Humanoid Loco-manipulation in an Embodied Gaussian Splatting World
- CoRL 2026 | WARPED: Wrist-Aligned Rendering for Robot Policy Learning from Egocentric Human Demonstrations
