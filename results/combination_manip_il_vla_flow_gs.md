# Co-occurrence of manipulation, imitation learning, VLA/VLM, diffusion/flow, Gaussian splatting

Title + abstract measure; papers with abstracts; raw shares (2026 = ICRA, RSS, T-RO, IJRR, Science Robotics only; years from scripts/config.py).

| combination                   |   n_2020 |   pct_2020 |   n_2021 |   pct_2021 |   n_2022 |   pct_2022 |   n_2023 |   pct_2023 |   n_2024 |   pct_2024 |   n_2025 |   pct_2025 |   n_2026 |   pct_2026 |
|:------------------------------|---------:|-----------:|---------:|-----------:|---------:|-----------:|---------:|-----------:|---------:|-----------:|---------:|-----------:|---------:|-----------:|
| manipulation                  |      529 |      19.48 |      571 |      19.21 |      557 |      20.27 |      711 |      22.03 |      970 |      23.27 |     1057 |      23.3  |     1027 |      36.23 |
| M+IL                          |       69 |       2.54 |       75 |       2.52 |       77 |       2.8  |      112 |       3.47 |      210 |       5.04 |      297 |       6.55 |      438 |      15.45 |
| M+IL+Gen(diffusion/flow)      |        0 |       0    |        0 |       0    |        0 |       0    |        7 |       0.22 |       22 |       0.53 |       63 |       1.39 |      116 |       4.09 |
| M+IL+VLA/VLM                  |        0 |       0    |        3 |       0.1  |        0 |       0    |        7 |       0.22 |       29 |       0.7  |       55 |       1.21 |      162 |       5.71 |
| M+IL+VLA/VLM+Gen              |        0 |       0    |        0 |       0    |        0 |       0    |        2 |       0.06 |        1 |       0.02 |       10 |       0.22 |       33 |       1.16 |
| M+GS                          |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |        5 |       0.12 |       23 |       0.51 |       17 |       0.6  |
| M+IL+GS                       |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |        4 |       0.09 |        6 |       0.21 |
| all five: M+IL+VLA/VLM+Gen+GS |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |        1 |       0.04 |
| flow matching (any)           |        0 |       0    |        2 |       0.07 |        2 |       0.07 |        0 |       0    |        4 |       0.1  |       15 |       0.33 |       82 |       2.89 |
| M+IL+flow matching            |        0 |       0    |        0 |       0    |        0 |       0    |        0 |       0    |        1 |       0.02 |        5 |       0.11 |       31 |       1.09 |

Pairwise lift in 2025 (all seven venues):

| pair      |   observed_pct |   expected_if_independent_pct |   lift |
|:----------|---------------:|------------------------------:|-------:|
| IL & Gen  |           2.07 |                          0.54 |   3.86 |
| IL & VLx  |           1.52 |                          1.1  |   1.39 |
| VLx & Gen |           0.66 |                          0.53 |   1.24 |
| M & GS    |           0.51 |                          0.65 |   0.78 |
| IL & GS   |           0.11 |                          0.29 |   0.38 |
| VLx & GS  |           0.31 |                          0.29 |   1.06 |
| Gen & GS  |           0.11 |                          0.14 |   0.77 |

Papers with manipulation + imitation learning + Gaussian splatting:

- RSS 2025 | Novel Demonstration Generation with Gaussian Splatting Enables Robust One-Shot Manipulation
- RSS 2026 | TAIL-Safe: Task-Agnostic Safety Monitoring for Imitation Learning Policies
- CoRL 2025 | Real2Render2Real: Scaling Robot Data Without Dynamics Simulation or Robot Hardware
- CoRL 2025 | Tool-as-Interface: Learning Robot Policies from Observing Human Tool Use
- CoRL 2025 | One Demo is Worth a Thousand Trajectories: Action-View Augmentation for Visuomotor Policies
- ICRA 2026 | Observer–Actor: Active Vision Imitation Learning with Sparse-View Gaussian Splatting
- ICRA 2026 | GSWorld: Closed-Loop Photorealistic Simulation Suite for Robot Manipulation
- CoRL 2026 | LEGS: Fine-Tuning Teleop-Free VLAs for Humanoid Loco-manipulation in an Embodied Gaussian Splatting World
- CoRL 2026 | π, But Make It Fly: Physics-Guided Transfer of VLA Models to Aerial Manipulation
- CoRL 2026 | WARPED: Wrist-Aligned Rendering for Robot Policy Learning from Egocentric Human Demonstrations
