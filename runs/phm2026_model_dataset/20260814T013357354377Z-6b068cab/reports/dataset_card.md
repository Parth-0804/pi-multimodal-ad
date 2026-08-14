# Provisional PHM model dataset card

Targets are automated dark/horizontally-textured damage-candidate masks pending human review, not organizer ground truth or calibrated spall area. All 20 run inspections have 28 tooth identities, but EXP-A/B use multiple close-ups for teeth 1–4 whereas EXP-F uses one canonical image per tooth. This acquisition-protocol shift is a major external-validity limitation.

HDF5 members are one-minute source records according to the official challenge description. Duration here is member count × 60 seconds, not a fully verified timestamp span. Full compact sensor features require a separate streaming job and remain unavailable.
