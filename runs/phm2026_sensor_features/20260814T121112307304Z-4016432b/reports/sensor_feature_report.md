# Bounded PHM minute-feature extraction

The versioned table contains 372 LF HDF5 source records across 1 experiment/runs. 372 have verified UTC `wf_start_time` and enter chronological model sequences; 0 remain traceable but excluded.

Each source HDF5 file is materialized and processed one at a time from its nested ZIP. Only compact statistics are retained. No HDF5, waveform, or full sensor array is cached. The initial baseline deliberately uses LF context, organizer RMS, and four condition indicators; it does not use raw high-frequency vibration.

Physical units are recorded only when present in source attributes. The target is the provisional `phm2026_image_damage_v2` end-of-run image-derived target and is not organizer ground truth.
