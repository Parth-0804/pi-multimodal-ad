# Scientific conclusions

Generated 2026-11-10T23:47:30.757333+00:00. 74 completed fits; 0 partially trained fits; 1 currently running fits (PID and creation time verified); 20 complete F2 assessment cohorts. Unfinished planned work is not a negative scientific result.

1. **Did 20-epoch full CNN training improve visual prediction?** UNTESTED: no complete paired assessment yet.

2. **Did 100-epoch full CNN training improve visual prediction?** UNTESTED: no complete paired assessment yet.

3. **Did either improvement translate into better F2 fusion?** FULL20 minus FROZEN20: UNTESTED: no complete paired assessment yet. FULL100 minus FROZEN100: UNTESTED: no complete paired assessment yet.

4. **Did F2 beat static sensor LR?** FROZEN20, seed 42, fold 0: delta -0.000878, 95% [-0.003629, +0.003521]; inconclusive; not equivalence; FROZEN20, seed 42, fold 1: delta +0.001265, 95% [-0.001417, +0.003440]; inconclusive; not equivalence; FROZEN20, seed 42, fold 2: delta -0.000006, 95% [-0.000148, +0.000267]; inconclusive; not equivalence; FROZEN20, seed 123, fold 0: delta -0.001232, 95% [-0.004143, +0.000197]; inconclusive; not equivalence; FROZEN20, seed 123, fold 1: delta -0.002539, 95% [-0.006493, +0.001002]; inconclusive; not equivalence; FROZEN20, seed 123, fold 2: delta +0.000209, 95% [-0.000289, +0.000473]; inconclusive; not equivalence; FROZEN20, seed 20261023, fold 0: delta -0.007216, 95% [-0.018215, +0.000558]; inconclusive; not equivalence; FROZEN20, seed 20261023, fold 1: delta +0.000731, 95% [-0.001071, +0.001864]; inconclusive; not equivalence; FROZEN20, seed 20261023, fold 2: delta -0.000348, 95% [-0.000810, +0.000195]; inconclusive; not equivalence; DONOR20, seed 42, fold 0: delta +0.000385, 95% [-0.000484, +0.001200]; inconclusive; not equivalence; DONOR20, seed 42, fold 1: delta +0.000841, 95% [-0.001381, +0.002976]; inconclusive; not equivalence; DONOR20, seed 42, fold 2: delta +0.000678, 95% [-0.000812, +0.002671]; inconclusive; not equivalence; DONOR20, seed 123, fold 0: delta -0.001030, 95% [-0.019140, +0.011237]; inconclusive; not equivalence; DONOR20, seed 123, fold 1: delta -0.001603, 95% [-0.007223, +0.003896]; inconclusive; not equivalence; DONOR20, seed 123, fold 2: delta +0.002053, 95% [-0.002132, +0.007745]; inconclusive; not equivalence; DONOR20, seed 20261023, fold 0: delta +0.002925, 95% [-0.004300, +0.009368]; inconclusive; not equivalence; DONOR20, seed 20261023, fold 1: delta -0.000974, 95% [-0.004611, +0.002439]; inconclusive; not equivalence; DONOR20, seed 20261023, fold 2: delta +0.000193, 95% [-0.001086, +0.001625]; inconclusive; not equivalence; FROZEN100, seed 42, fold 0: delta -0.013777, 95% [-0.028973, -0.000509]; negative conditional interval; DONOR100, seed 42, fold 0: delta -0.011396, 95% [-0.022382, -0.002021]; negative conditional interval; FROZEN20, seed 42, fold pooled3: delta -0.019694, 95% [-0.029058, -0.006425]; negative conditional interval; FROZEN20, seed 123, fold pooled3: delta -0.021935, 95% [-0.030067, -0.009592]; negative conditional interval; FROZEN20, seed 20261023, fold pooled3: delta -0.024419, 95% [-0.033270, -0.011148]; negative conditional interval; DONOR20, seed 42, fold pooled3: delta -0.021223, 95% [-0.030381, -0.008262]; negative conditional interval; DONOR20, seed 123, fold pooled3: delta -0.011122, 95% [-0.021349, +0.002059]; inconclusive; not equivalence; DONOR20, seed 20261023, fold pooled3: delta -0.018038, 95% [-0.027250, -0.004905]; negative conditional interval.

5. **Did F2 beat the strongest available unimodal reference?** Retained HGB: FROZEN20, seed 42, fold 0: delta -0.050760, 95% [-0.165195, +0.059899]; inconclusive; not equivalence; FROZEN20, seed 42, fold 1: delta -0.021658, 95% [-0.099882, +0.043737]; inconclusive; not equivalence; FROZEN20, seed 42, fold 2: delta -0.058828, 95% [-0.152813, -0.022552]; negative conditional interval; FROZEN20, seed 123, fold 0: delta -0.051114, 95% [-0.166558, +0.059889]; inconclusive; not equivalence; FROZEN20, seed 123, fold 1: delta -0.025462, 95% [-0.100903, +0.038389]; inconclusive; not equivalence; FROZEN20, seed 123, fold 2: delta -0.058613, 95% [-0.152695, -0.022425]; negative conditional interval; FROZEN20, seed 20261023, fold 0: delta -0.057098, 95% [-0.175083, +0.055779]; inconclusive; not equivalence; FROZEN20, seed 20261023, fold 1: delta -0.022191, 95% [-0.100664, +0.043370]; inconclusive; not equivalence; FROZEN20, seed 20261023, fold 2: delta -0.059170, 95% [-0.152881, -0.022925]; negative conditional interval; DONOR20, seed 42, fold 0: delta -0.049497, 95% [-0.164293, +0.061279]; inconclusive; not equivalence; DONOR20, seed 42, fold 1: delta -0.022082, 95% [-0.100499, +0.043762]; inconclusive; not equivalence; DONOR20, seed 42, fold 2: delta -0.058144, 95% [-0.152020, -0.022299]; negative conditional interval; DONOR20, seed 123, fold 0: delta -0.050912, 95% [-0.165874, +0.062219]; inconclusive; not equivalence; DONOR20, seed 123, fold 1: delta -0.024526, 95% [-0.099046, +0.038070]; inconclusive; not equivalence; DONOR20, seed 123, fold 2: delta -0.056769, 95% [-0.150711, -0.021723]; negative conditional interval; DONOR20, seed 20261023, fold 0: delta -0.046957, 95% [-0.160226, +0.064479]; inconclusive; not equivalence; DONOR20, seed 20261023, fold 1: delta -0.023897, 95% [-0.098887, +0.039367]; inconclusive; not equivalence; DONOR20, seed 20261023, fold 2: delta -0.058629, 95% [-0.152791, -0.022389]; negative conditional interval; FROZEN100, seed 42, fold 0: delta -0.063659, 95% [-0.183347, +0.052269]; inconclusive; not equivalence; DONOR100, seed 42, fold 0: delta -0.061278, 95% [-0.178274, +0.051565]; inconclusive; not equivalence; FROZEN20, seed 42, fold pooled3: delta -0.070740, 95% [-0.121794, -0.031755]; negative conditional interval; FROZEN20, seed 123, fold pooled3: delta -0.072981, 95% [-0.123935, -0.034548]; negative conditional interval; FROZEN20, seed 20261023, fold pooled3: delta -0.075465, 95% [-0.126833, -0.036829]; negative conditional interval; DONOR20, seed 42, fold pooled3: delta -0.072270, 95% [-0.123241, -0.033546]; negative conditional interval; DONOR20, seed 123, fold pooled3: delta -0.062168, 95% [-0.111669, -0.024264]; negative conditional interval; DONOR20, seed 20261023, fold pooled3: delta -0.069084, 95% [-0.118862, -0.031108]; negative conditional interval. Corresponding vision: FROZEN20, seed 42, fold 0: delta +0.219695, 95% [+0.145620, +0.296831]; positive conditional interval; FROZEN20, seed 42, fold 1: delta +0.203397, 95% [+0.107836, +0.271503]; positive conditional interval; FROZEN20, seed 42, fold 2: delta +0.125987, 95% [+0.056658, +0.192604]; positive conditional interval; FROZEN20, seed 123, fold 0: delta +0.232480, 95% [+0.176084, +0.301919]; positive conditional interval; FROZEN20, seed 123, fold 1: delta +0.197542, 95% [+0.104919, +0.269732]; positive conditional interval; FROZEN20, seed 123, fold 2: delta +0.138600, 95% [+0.061887, +0.207763]; positive conditional interval; FROZEN20, seed 20261023, fold 0: delta +0.217421, 95% [+0.158081, +0.291738]; positive conditional interval; FROZEN20, seed 20261023, fold 1: delta +0.214318, 95% [+0.114006, +0.293069]; positive conditional interval; FROZEN20, seed 20261023, fold 2: delta +0.148215, 95% [+0.074711, +0.212559]; positive conditional interval; DONOR20, seed 42, fold 0: delta +0.245221, 95% [+0.182308, +0.316453]; positive conditional interval; DONOR20, seed 42, fold 1: delta +0.213880, 95% [+0.119212, +0.281839]; positive conditional interval; DONOR20, seed 42, fold 2: delta +0.146576, 95% [+0.056969, +0.232000]; positive conditional interval; DONOR20, seed 123, fold 0: delta +0.236768, 95% [+0.169214, +0.306679]; positive conditional interval; DONOR20, seed 123, fold 1: delta +0.207934, 95% [+0.124252, +0.275795]; positive conditional interval; DONOR20, seed 123, fold 2: delta +0.146064, 95% [+0.053922, +0.239338]; positive conditional interval; DONOR20, seed 20261023, fold 0: delta +0.244558, 95% [+0.184333, +0.317501]; positive conditional interval; DONOR20, seed 20261023, fold 1: delta +0.210467, 95% [+0.099153, +0.291625]; positive conditional interval; DONOR20, seed 20261023, fold 2: delta +0.122748, 95% [+0.025343, +0.218938]; positive conditional interval; FROZEN100, seed 42, fold 0: delta +0.143225, 95% [+0.061848, +0.228811]; positive conditional interval; DONOR100, seed 42, fold 0: delta +0.125153, 95% [+0.070151, +0.191018]; positive conditional interval; FROZEN20, seed 42, fold pooled3: delta +0.121415, 95% [+0.075668, +0.172282]; positive conditional interval; FROZEN20, seed 123, fold pooled3: delta +0.131809, 95% [+0.092092, +0.177610]; positive conditional interval; FROZEN20, seed 20261023, fold pooled3: delta +0.136943, 95% [+0.097339, +0.182084]; positive conditional interval; DONOR20, seed 42, fold pooled3: delta +0.136383, 95% [+0.090742, +0.188104]; positive conditional interval; DONOR20, seed 123, fold pooled3: delta +0.148841, 95% [+0.104705, +0.200037]; positive conditional interval; DONOR20, seed 20261023, fold pooled3: delta +0.138751, 95% [+0.088319, +0.192506]; positive conditional interval. Historical V1: FROZEN20, seed 42, fold 0: delta +0.231387, 95% [+0.165564, +0.310058]; positive conditional interval; FROZEN20, seed 42, fold 1: delta +0.213649, 95% [+0.130681, +0.276048]; positive conditional interval; FROZEN20, seed 42, fold 2: delta +0.122504, 95% [+0.053687, +0.196310]; positive conditional interval; FROZEN20, seed 123, fold 0: delta +0.238871, 95% [+0.186013, +0.310495]; positive conditional interval; FROZEN20, seed 123, fold 1: delta +0.192375, 95% [+0.100685, +0.269624]; positive conditional interval; FROZEN20, seed 123, fold 2: delta +0.137904, 95% [+0.061647, +0.206766]; positive conditional interval; FROZEN20, seed 20261023, fold 0: delta +0.227941, 95% [+0.172264, +0.297710]; positive conditional interval; FROZEN20, seed 20261023, fold 1: delta +0.213700, 95% [+0.121224, +0.286275]; positive conditional interval; FROZEN20, seed 20261023, fold 2: delta +0.148215, 95% [+0.074711, +0.212559]; positive conditional interval; DONOR20, seed 42, fold 0: delta +0.232650, 95% [+0.166975, +0.310144]; positive conditional interval; DONOR20, seed 42, fold 1: delta +0.213225, 95% [+0.130329, +0.276716]; positive conditional interval; DONOR20, seed 42, fold 2: delta +0.123188, 95% [+0.053469, +0.196670]; positive conditional interval; DONOR20, seed 123, fold 0: delta +0.239073, 95% [+0.190707, +0.308718]; positive conditional interval; DONOR20, seed 123, fold 1: delta +0.193311, 95% [+0.100786, +0.271496]; positive conditional interval; DONOR20, seed 123, fold 2: delta +0.139749, 95% [+0.061178, +0.211054]; positive conditional interval; DONOR20, seed 20261023, fold 0: delta +0.238082, 95% [+0.191895, +0.304358]; positive conditional interval; DONOR20, seed 20261023, fold 1: delta +0.211994, 95% [+0.116372, +0.286216]; positive conditional interval; DONOR20, seed 20261023, fold 2: delta +0.148756, 95% [+0.074285, +0.213618]; positive conditional interval; FROZEN100, seed 42, fold 0: delta +0.218488, 95% [+0.144555, +0.299830]; positive conditional interval; DONOR100, seed 42, fold 0: delta +0.220869, 95% [+0.149578, +0.301429]; positive conditional interval; FROZEN20, seed 42, fold pooled3: delta +0.134124, 95% [+0.096220, +0.178479]; positive conditional interval; FROZEN20, seed 123, fold pooled3: delta +0.130669, 95% [+0.092597, +0.178340]; positive conditional interval; FROZEN20, seed 20261023, fold pooled3: delta +0.140168, 95% [+0.102114, +0.183264]; positive conditional interval; DONOR20, seed 42, fold pooled3: delta +0.132594, 95% [+0.094703, +0.177628]; positive conditional interval; DONOR20, seed 123, fold pooled3: delta +0.141482, 95% [+0.103301, +0.188147]; positive conditional interval; DONOR20, seed 20261023, fold pooled3: delta +0.146549, 95% [+0.108946, +0.189487]; positive conditional interval. LR-only superiority does not establish this claim.

6. **Did REASSEMBLE-trained CNN weights transfer successfully?** Mechanical learned-state compatibility is verified separately from predictive benefit. Donor20: seed 42, fold 0: delta -0.024263, 95% [-0.083623, +0.026911]; inconclusive; not equivalence; seed 42, fold 1: delta -0.010907, 95% [-0.039810, +0.018839]; inconclusive; not equivalence; seed 42, fold 2: delta -0.019905, 95% [-0.056637, +0.022343]; inconclusive; not equivalence; seed 123, fold 0: delta -0.004086, 95% [-0.024444, +0.036454]; inconclusive; not equivalence; seed 123, fold 1: delta -0.009456, 95% [-0.036981, +0.020411]; inconclusive; not equivalence; seed 123, fold 2: delta -0.005619, 95% [-0.047814, +0.037791]; inconclusive; not equivalence; seed 20261023, fold 0: delta -0.016995, 95% [-0.048555, +0.016889]; inconclusive; not equivalence; seed 20261023, fold 1: delta +0.002145, 95% [-0.036688, +0.053587]; inconclusive; not equivalence; seed 20261023, fold 2: delta +0.026008, 95% [-0.032273, +0.088120]; inconclusive; not equivalence; seed 42, fold pooled3: delta -0.016497, 95% [-0.032908, +0.001339]; inconclusive; not equivalence; seed 123, fold pooled3: delta -0.006219, 95% [-0.025260, +0.012160]; inconclusive; not equivalence; seed 20261023, fold pooled3: delta +0.004573, 95% [-0.021106, +0.035886]; inconclusive; not equivalence. Donor100: seed 42, fold 0: delta +0.020453, 95% [-0.015122, +0.051843]; inconclusive; not equivalence.

7. **Were differences consistent across seeds and task groups?** Completed assessment seeds [42, 123, 20261023], outer folds ['0', '1', '2']. 110 completed arm/seed/task cells have lower F2 macro AP than sensor LR. Across those separately fitted evaluations, 306 sensor-correct episode occurrences became F2 errors; these are not unique independent examples. Report08 retains all task directions. One seed cannot establish seed stability; missing matched coverage remains untested.

8. **What was the actual GPU cost?** Observed GPU-controller process time is 0.231250 hours (session definition in report11). Recorded new training across CPU/GPU arms is 0.095152 hours, separated per arm in Table D. Validation and incomplete-epoch elapsed time remain separate; absent GPU telemetry is UNKNOWN.

9. **Which claims are supported, inconclusive or untested?** Verified identities, executed fit counts and independent saved-score arithmetic support reproducibility within completed scope. Positive/negative conditional intervals are identified numerically above; intervals crossing zero are inconclusive, not equivalence. Unfinished fits, missing pairs/seeds and new-task generalization remain untested. Successful tests alone do not establish scientific validity.

10. **What remains necessary for independent confirmation?** Predeclared evaluation on new task/collection groups with verified session/operator identities, multiple refits/seeds, frozen donor/selection choices and adequate grouped uncertainty. Previously examined tasks do not provide pristine confirmation.

|Comparison|Seed|Fold|Paired macro AP difference|95% interval|Interpretation|
|---|---|---|---|---|---|
|DONOR20 minus FROZEN20 / visual|42|0|-0.024263|[-0.083623, 0.026911]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / F2|42|0|0.001263|[-0.002532, 0.003649]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / visual|42|1|-0.010907|[-0.039810, 0.018839]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / F2|42|1|-0.000424|[-0.002108, 0.001337]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / visual|42|2|-0.019905|[-0.056637, 0.022343]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / F2|42|2|0.000684|[-0.000798, 0.002661]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / visual|123|0|-0.004086|[-0.024444, 0.036454]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / F2|123|0|0.000202|[-0.018798, 0.014141]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / visual|123|1|-0.009456|[-0.036981, 0.020411]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / F2|123|1|0.000936|[-0.002158, 0.004474]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / visual|123|2|-0.005619|[-0.047814, 0.037791]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / F2|123|2|0.001845|[-0.002096, 0.007374]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / visual|20261023|0|-0.016995|[-0.048555, 0.016889]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / F2|20261023|0|0.010141|[-0.002810, 0.024748]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / visual|20261023|1|0.002145|[-0.036688, 0.053587]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / F2|20261023|1|-0.001706|[-0.006168, 0.002966]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / visual|20261023|2|0.026008|[-0.032273, 0.088120]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / F2|20261023|2|0.000541|[-0.001011, 0.002183]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / visual|42|pooled3|-0.016497|[-0.032908, 0.001339]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / F2|42|pooled3|-0.001530|[-0.002673, -0.000237]|negative conditional interval|
|DONOR20 minus FROZEN20 / visual|123|pooled3|-0.006219|[-0.025260, 0.012160]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / F2|123|pooled3|0.010813|[0.006082, 0.015846]|positive conditional interval|
|DONOR20 minus FROZEN20 / visual|20261023|pooled3|0.004573|[-0.021106, 0.035886]|inconclusive; not equivalence|
|DONOR20 minus FROZEN20 / F2|20261023|pooled3|0.006381|[0.003638, 0.009305]|positive conditional interval|
|DONOR100 minus FROZEN100 / visual|42|0|0.020453|[-0.015122, 0.051843]|inconclusive; not equivalence|
|DONOR100 minus FROZEN100 / F2|42|0|0.002381|[-0.006076, 0.011112]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_average|42|0|0.012294|[-0.004497, 0.034493]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_HGB|42|0|-0.050760|[-0.165195, 0.059899]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_V1|42|0|0.231387|[0.165564, 0.310058]|positive conditional interval|
|FROZEN20 / F2_minus_sensor_LR|42|0|-0.000878|[-0.003629, 0.003521]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_visual|42|0|0.219695|[0.145620, 0.296831]|positive conditional interval|
|FROZEN20 / F2_minus_average|42|1|0.013883|[-0.022964, 0.050290]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_HGB|42|1|-0.021658|[-0.099882, 0.043737]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_V1|42|1|0.213649|[0.130681, 0.276048]|positive conditional interval|
|FROZEN20 / F2_minus_sensor_LR|42|1|0.001265|[-0.001417, 0.003440]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_visual|42|1|0.203397|[0.107836, 0.271503]|positive conditional interval|
|FROZEN20 / F2_minus_average|42|2|0.000003|[-0.000743, 0.000960]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_HGB|42|2|-0.058828|[-0.152813, -0.022552]|negative conditional interval|
|FROZEN20 / F2_minus_historical_V1|42|2|0.122504|[0.053687, 0.196310]|positive conditional interval|
|FROZEN20 / F2_minus_sensor_LR|42|2|-0.000006|[-0.000148, 0.000267]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_visual|42|2|0.125987|[0.056658, 0.192604]|positive conditional interval|
|FROZEN20 / F2_minus_average|123|0|0.016001|[0.004052, 0.031172]|positive conditional interval|
|FROZEN20 / F2_minus_historical_HGB|123|0|-0.051114|[-0.166558, 0.059889]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_V1|123|0|0.238871|[0.186013, 0.310495]|positive conditional interval|
|FROZEN20 / F2_minus_sensor_LR|123|0|-0.001232|[-0.004143, 0.000197]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_visual|123|0|0.232480|[0.176084, 0.301919]|positive conditional interval|
|FROZEN20 / F2_minus_average|123|1|-0.001205|[-0.034165, 0.034500]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_HGB|123|1|-0.025462|[-0.100903, 0.038389]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_V1|123|1|0.192375|[0.100685, 0.269624]|positive conditional interval|
|FROZEN20 / F2_minus_sensor_LR|123|1|-0.002539|[-0.006493, 0.001002]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_visual|123|1|0.197542|[0.104919, 0.269732]|positive conditional interval|
|FROZEN20 / F2_minus_average|123|2|0.007017|[-0.005558, 0.015531]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_HGB|123|2|-0.058613|[-0.152695, -0.022425]|negative conditional interval|
|FROZEN20 / F2_minus_historical_V1|123|2|0.137904|[0.061647, 0.206766]|positive conditional interval|
|FROZEN20 / F2_minus_sensor_LR|123|2|0.000209|[-0.000289, 0.000473]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_visual|123|2|0.138600|[0.061887, 0.207763]|positive conditional interval|
|FROZEN20 / F2_minus_average|20261023|0|0.011296|[0.004313, 0.019713]|positive conditional interval|
|FROZEN20 / F2_minus_historical_HGB|20261023|0|-0.057098|[-0.175083, 0.055779]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_V1|20261023|0|0.227941|[0.172264, 0.297710]|positive conditional interval|
|FROZEN20 / F2_minus_sensor_LR|20261023|0|-0.007216|[-0.018215, 0.000558]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_visual|20261023|0|0.217421|[0.158081, 0.291738]|positive conditional interval|
|FROZEN20 / F2_minus_average|20261023|1|0.003247|[-0.017920, 0.034368]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_HGB|20261023|1|-0.022191|[-0.100664, 0.043370]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_V1|20261023|1|0.213700|[0.121224, 0.286275]|positive conditional interval|
|FROZEN20 / F2_minus_sensor_LR|20261023|1|0.000731|[-0.001071, 0.001864]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_visual|20261023|1|0.214318|[0.114006, 0.293069]|positive conditional interval|
|FROZEN20 / F2_minus_average|20261023|2|0.014774|[-0.004792, 0.025426]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_HGB|20261023|2|-0.059170|[-0.152881, -0.022925]|negative conditional interval|
|FROZEN20 / F2_minus_historical_V1|20261023|2|0.148215|[0.074711, 0.212559]|positive conditional interval|
|FROZEN20 / F2_minus_sensor_LR|20261023|2|-0.000348|[-0.000810, 0.000195]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_visual|20261023|2|0.148215|[0.074711, 0.212559]|positive conditional interval|
|DONOR20 / F2_minus_average|42|0|0.026686|[0.004070, 0.041295]|positive conditional interval|
|DONOR20 / F2_minus_historical_HGB|42|0|-0.049497|[-0.164293, 0.061279]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_V1|42|0|0.232650|[0.166975, 0.310144]|positive conditional interval|
|DONOR20 / F2_minus_sensor_LR|42|0|0.000385|[-0.000484, 0.001200]|inconclusive; not equivalence|
|DONOR20 / F2_minus_visual|42|0|0.245221|[0.182308, 0.316453]|positive conditional interval|
|DONOR20 / F2_minus_average|42|1|0.030629|[-0.025165, 0.077222]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_HGB|42|1|-0.022082|[-0.100499, 0.043762]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_V1|42|1|0.213225|[0.130329, 0.276716]|positive conditional interval|
|DONOR20 / F2_minus_sensor_LR|42|1|0.000841|[-0.001381, 0.002976]|inconclusive; not equivalence|
|DONOR20 / F2_minus_visual|42|1|0.213880|[0.119212, 0.281839]|positive conditional interval|
|DONOR20 / F2_minus_average|42|2|0.017736|[-0.010166, 0.047577]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_HGB|42|2|-0.058144|[-0.152020, -0.022299]|negative conditional interval|
|DONOR20 / F2_minus_historical_V1|42|2|0.123188|[0.053469, 0.196670]|positive conditional interval|
|DONOR20 / F2_minus_sensor_LR|42|2|0.000678|[-0.000812, 0.002671]|inconclusive; not equivalence|
|DONOR20 / F2_minus_visual|42|2|0.146576|[0.056969, 0.232000]|positive conditional interval|
|DONOR20 / F2_minus_average|123|0|0.025422|[-0.014478, 0.049663]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_HGB|123|0|-0.050912|[-0.165874, 0.062219]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_V1|123|0|0.239073|[0.190707, 0.308718]|positive conditional interval|
|DONOR20 / F2_minus_sensor_LR|123|0|-0.001030|[-0.019140, 0.011237]|inconclusive; not equivalence|
|DONOR20 / F2_minus_visual|123|0|0.236768|[0.169214, 0.306679]|positive conditional interval|
|DONOR20 / F2_minus_average|123|1|0.007555|[-0.031842, 0.041879]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_HGB|123|1|-0.024526|[-0.099046, 0.038070]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_V1|123|1|0.193311|[0.100786, 0.271496]|positive conditional interval|
|DONOR20 / F2_minus_sensor_LR|123|1|-0.001603|[-0.007223, 0.003896]|inconclusive; not equivalence|
|DONOR20 / F2_minus_visual|123|1|0.207934|[0.124252, 0.275795]|positive conditional interval|
|DONOR20 / F2_minus_average|123|2|0.031429|[-0.014641, 0.077016]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_HGB|123|2|-0.056769|[-0.150711, -0.021723]|negative conditional interval|
|DONOR20 / F2_minus_historical_V1|123|2|0.139749|[0.061178, 0.211054]|positive conditional interval|
|DONOR20 / F2_minus_sensor_LR|123|2|0.002053|[-0.002132, 0.007745]|inconclusive; not equivalence|
|DONOR20 / F2_minus_visual|123|2|0.146064|[0.053922, 0.239338]|positive conditional interval|
|DONOR20 / F2_minus_average|20261023|0|0.043235|[0.013243, 0.066192]|positive conditional interval|
|DONOR20 / F2_minus_historical_HGB|20261023|0|-0.046957|[-0.160226, 0.064479]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_V1|20261023|0|0.238082|[0.191895, 0.304358]|positive conditional interval|
|DONOR20 / F2_minus_sensor_LR|20261023|0|0.002925|[-0.004300, 0.009368]|inconclusive; not equivalence|
|DONOR20 / F2_minus_visual|20261023|0|0.244558|[0.184333, 0.317501]|positive conditional interval|
|DONOR20 / F2_minus_average|20261023|1|0.009123|[-0.038081, 0.051682]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_HGB|20261023|1|-0.023897|[-0.098887, 0.039367]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_V1|20261023|1|0.211994|[0.116372, 0.286216]|positive conditional interval|
|DONOR20 / F2_minus_sensor_LR|20261023|1|-0.000974|[-0.004611, 0.002439]|inconclusive; not equivalence|
|DONOR20 / F2_minus_visual|20261023|1|0.210467|[0.099153, 0.291625]|positive conditional interval|
|DONOR20 / F2_minus_average|20261023|2|0.003819|[-0.014798, 0.027258]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_HGB|20261023|2|-0.058629|[-0.152791, -0.022389]|negative conditional interval|
|DONOR20 / F2_minus_historical_V1|20261023|2|0.148756|[0.074285, 0.213618]|positive conditional interval|
|DONOR20 / F2_minus_sensor_LR|20261023|2|0.000193|[-0.001086, 0.001625]|inconclusive; not equivalence|
|DONOR20 / F2_minus_visual|20261023|2|0.122748|[0.025343, 0.218938]|positive conditional interval|
|FROZEN100 / F2_minus_average|42|0|0.046450|[0.001057, 0.094535]|positive conditional interval|
|FROZEN100 / F2_minus_historical_HGB|42|0|-0.063659|[-0.183347, 0.052269]|inconclusive; not equivalence|
|FROZEN100 / F2_minus_historical_V1|42|0|0.218488|[0.144555, 0.299830]|positive conditional interval|
|FROZEN100 / F2_minus_sensor_LR|42|0|-0.013777|[-0.028973, -0.000509]|negative conditional interval|
|FROZEN100 / F2_minus_visual|42|0|0.143225|[0.061848, 0.228811]|positive conditional interval|
|DONOR100 / F2_minus_average|42|0|0.008988|[-0.018001, 0.042690]|inconclusive; not equivalence|
|DONOR100 / F2_minus_historical_HGB|42|0|-0.061278|[-0.178274, 0.051565]|inconclusive; not equivalence|
|DONOR100 / F2_minus_historical_V1|42|0|0.220869|[0.149578, 0.301429]|positive conditional interval|
|DONOR100 / F2_minus_sensor_LR|42|0|-0.011396|[-0.022382, -0.002021]|negative conditional interval|
|DONOR100 / F2_minus_visual|42|0|0.125153|[0.070151, 0.191018]|positive conditional interval|
|FROZEN20 / F2_minus_average|42|pooled3|0.004034|[-0.012893, 0.024191]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_HGB|42|pooled3|-0.070740|[-0.121794, -0.031755]|negative conditional interval|
|FROZEN20 / F2_minus_historical_V1|42|pooled3|0.134124|[0.096220, 0.178479]|positive conditional interval|
|FROZEN20 / F2_minus_sensor_LR|42|pooled3|-0.019694|[-0.029058, -0.006425]|negative conditional interval|
|FROZEN20 / F2_minus_visual|42|pooled3|0.121415|[0.075668, 0.172282]|positive conditional interval|
|FROZEN20 / F2_minus_average|123|pooled3|0.004642|[-0.008999, 0.019609]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_HGB|123|pooled3|-0.072981|[-0.123935, -0.034548]|negative conditional interval|
|FROZEN20 / F2_minus_historical_V1|123|pooled3|0.130669|[0.092597, 0.178340]|positive conditional interval|
|FROZEN20 / F2_minus_sensor_LR|123|pooled3|-0.021935|[-0.030067, -0.009592]|negative conditional interval|
|FROZEN20 / F2_minus_visual|123|pooled3|0.131809|[0.092092, 0.177610]|positive conditional interval|
|FROZEN20 / F2_minus_average|20261023|pooled3|0.004553|[-0.011875, 0.019330]|inconclusive; not equivalence|
|FROZEN20 / F2_minus_historical_HGB|20261023|pooled3|-0.075465|[-0.126833, -0.036829]|negative conditional interval|
|FROZEN20 / F2_minus_historical_V1|20261023|pooled3|0.140168|[0.102114, 0.183264]|positive conditional interval|
|FROZEN20 / F2_minus_sensor_LR|20261023|pooled3|-0.024419|[-0.033270, -0.011148]|negative conditional interval|
|FROZEN20 / F2_minus_visual|20261023|pooled3|0.136943|[0.097339, 0.182084]|positive conditional interval|
|DONOR20 / F2_minus_average|42|pooled3|0.016915|[-0.002625, 0.038027]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_HGB|42|pooled3|-0.072270|[-0.123241, -0.033546]|negative conditional interval|
|DONOR20 / F2_minus_historical_V1|42|pooled3|0.132594|[0.094703, 0.177628]|positive conditional interval|
|DONOR20 / F2_minus_sensor_LR|42|pooled3|-0.021223|[-0.030381, -0.008262]|negative conditional interval|
|DONOR20 / F2_minus_visual|42|pooled3|0.136383|[0.090742, 0.188104]|positive conditional interval|
|DONOR20 / F2_minus_average|123|pooled3|0.032050|[0.010674, 0.053099]|positive conditional interval|
|DONOR20 / F2_minus_historical_HGB|123|pooled3|-0.062168|[-0.111669, -0.024264]|negative conditional interval|
|DONOR20 / F2_minus_historical_V1|123|pooled3|0.141482|[0.103301, 0.188147]|positive conditional interval|
|DONOR20 / F2_minus_sensor_LR|123|pooled3|-0.011122|[-0.021349, 0.002059]|inconclusive; not equivalence|
|DONOR20 / F2_minus_visual|123|pooled3|0.148841|[0.104705, 0.200037]|positive conditional interval|
|DONOR20 / F2_minus_average|20261023|pooled3|0.014901|[-0.004723, 0.036095]|inconclusive; not equivalence|
|DONOR20 / F2_minus_historical_HGB|20261023|pooled3|-0.069084|[-0.118862, -0.031108]|negative conditional interval|
|DONOR20 / F2_minus_historical_V1|20261023|pooled3|0.146549|[0.108946, 0.189487]|positive conditional interval|
|DONOR20 / F2_minus_sensor_LR|20261023|pooled3|-0.018038|[-0.027250, -0.004905]|negative conditional interval|
|DONOR20 / F2_minus_visual|20261023|pooled3|0.138751|[0.088319, 0.192506]|positive conditional interval|
