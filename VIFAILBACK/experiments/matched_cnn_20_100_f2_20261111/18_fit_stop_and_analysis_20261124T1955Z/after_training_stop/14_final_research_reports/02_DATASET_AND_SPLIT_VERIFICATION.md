# Dataset and split verification

Frozen cohort: 4,382 episodes; 3,753 failures; 629 successes; 99 canonical tasks. Native failure=1. Existing quality exclusions remain intact. Cohort SHA `69ef64b012f683c5c8be7882c7e047675f88ed6a448f53c3aa21f432e9858560`; split SHA `ad003bba25de31072612b6a3346690087ecb9f8c94f9558d2663fe99da150231`.

First predefined outer fold 0 has 1,107 assessment episodes / 33 tasks. First inner role has T 1,430 / V 534 / C 523 / meta 788 episodes and 26 / 9 / 9 / 22 tasks. These five roles partition the cohort and are task-disjoint. No held-out score selected the fold.

The 20-epoch study uses three outer folds and three inner OOF roles per outer. The 100-epoch study uses seed 42, outer 0, base role outer0_inner0 only. Its complete 100-epoch fit is not a three-fold experiment.

Verified source/frame identities and episode/task memberships: `../02_dataset_and_splits/`. Original splits: `VIFAILBACK/04_evaluation_splits/train_validation_test/20261029T004900Z/fit_partitions.json`. The 28 measured sensor channels are 14 positions, 12 nonplaceholder velocities and two gripper-effort fields; these are not calibrated force/torque.
