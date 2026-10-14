# Co-occurrence of manipulation, imitation learning, VLA/VLM, diffusion/flow, Gaussian splatting

Title + abstract measure; papers with abstracts; raw shares (2026 = ICRA, RSS, T-RO, IJRR, Science Robotics only).

| combination                   |   n_2024 |   pct_2024 |   n_2025 |   pct_2025 |   n_2026 |   pct_2026 |
|:------------------------------|---------:|-----------:|---------:|-----------:|---------:|-----------:|
| manipulation                  |      879 |      20.88 |     1000 |      21.93 |      643 |      28.62 |
| M+IL                          |      180 |       4.28 |      270 |       5.92 |      206 |       9.17 |
| M+IL+Gen(diffusion/flow)      |       20 |       0.48 |       50 |       1.1  |       56 |       2.49 |
| M+IL+VLA/VLM                  |       18 |       0.43 |       38 |       0.83 |       42 |       1.87 |
| M+IL+VLA/VLM+Gen              |        3 |       0.07 |        5 |       0.11 |        9 |       0.4  |
| M+GS                          |        4 |       0.1  |       30 |       0.66 |       15 |       0.67 |
| M+IL+GS                       |        1 |       0.02 |        5 |       0.11 |        2 |       0.09 |
| all five: M+IL+VLA/VLM+Gen+GS |        0 |       0    |        0 |       0    |        0 |       0    |
| flow matching (any)           |        4 |       0.1  |       15 |       0.33 |       43 |       1.91 |
| M+IL+flow matching            |        1 |       0.02 |        2 |       0.04 |       10 |       0.45 |

Pairwise lift in 2025 (all seven venues):

| pair      |   observed_pct |   expected_if_independent_pct |   lift |
|:----------|---------------:|------------------------------:|-------:|
| IL & Gen  |           1.8  |                          0.64 |   2.83 |
| IL & VLx  |           1.47 |                          1.05 |   1.4  |
| VLx & Gen |           0.77 |                          0.52 |   1.47 |
| M & GS    |           0.66 |                          0.64 |   1.03 |
| IL & GS   |           0.22 |                          0.33 |   0.66 |
| VLx & GS  |           0.18 |                          0.27 |   0.65 |
| Gen & GS  |           0.15 |                          0.16 |   0.94 |

Papers with manipulation + imitation learning + Gaussian splatting:

- IROS 2025 | LensDFF: Language-enhanced Sparse Feature Distillation for Efficient Few-Shot Dexterous Manipulation
- RSS 2025 | Novel Demonstration Generation with Gaussian Splatting Enables Robust One-Shot Manipulation
- RSS 2026 | TAIL-Safe: Task-Agnostic Safety Monitoring for Imitation Learning Policies
- CoRL 2024 | Splat-MOVER: Multi-Stage, Open-Vocabulary Robotic Manipulation via Editable Gaussian Splatting
- CoRL 2025 | Mobi-$\pi$: Mobilizing Your Robot Learning Policy
- CoRL 2025 | One Demo is Worth a Thousand Trajectories: Action-View Augmentation for Visuomotor Policies
- CoRL 2025 | Motion Blender Gaussian Splatting for Dynamic Reconstruction
- ICRA 2026 | SINGER: An Onboard Generalist Vision-Language Navigation Policy for Drones
