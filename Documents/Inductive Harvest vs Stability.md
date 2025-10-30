TITLE: H3 — Inductive Harvest Efficiency and Controlled Oscillation
PROBLEM: Harvesting requires changing magnetic flux (high dΦ/dt); stability requires smooth fields (low dΦ/dt). Need both.

OBJECTIVE: Demonstrate a controlled, predictable high-frequency pulse (ω_pulse) embedded into a high-speed baseline rotation that yields significant harvested power while remaining correctable.

CONCEPTUAL APPROACHES:
- Temporal Stabilization baseline: run system at ω_base >> plasma instability frequency; superimpose low-amplitude ω_pulse for harvesting.
- Phased bias coils: external phased coils introduce and localize ω_pulse with minimal global disturbance.
- Self-compensating coils: active coil array that adjusts coupling and phase to maximize induced current without feeding back destabilizing forces.

IMMEDIATE EXPERIMENTS (bench):
1) Coil-coupled MHD loop: demonstrate induced power extraction from controlled oscillations in a conductive rotating fluid.
2) Control loop exercise: close a fast analog control loop that accepts induced-power setpoint and maintains field stability.
3) Coupling optimization: map coil geometry, distance and phase for maximal harvest vs perturbation.

SUCCESS CRITERIA (6 months):
- Harvested electrical power fraction >10% of simulated available field energy in small-scale loop.
- System maintains stability (measured flow/field variance threshold) while ω_pulse is active.
- Demonstrate stable, repeatable power extraction without runaway feedback.

RESOURCE NEEDS:
- Coil lab, power electronics, MHD fluid rig, high-speed control hardware (FPGAs), diagnostics for flux and induced current.
