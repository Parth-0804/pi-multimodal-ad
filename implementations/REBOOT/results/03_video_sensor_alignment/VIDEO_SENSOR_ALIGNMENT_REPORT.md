# Video and numerical-state validation

Ten demonstrations,8,980 numerical rows,40 camera views and640 selected original frames were validated. Every view has16 distinct native frame indices **and16 distinct decoded RGB contents**. Four source viewpoints are decoded with the existing CPU `libdav1d` FFmpeg binary, whose identity/hash is recorded. OpenCV's installed AV1 decoder failed, so it was not used; no environment/package or running-training modification was made.

For each source episode, the Parquet frame index is contiguous, timestamps are finite/monotone, and14-position state/command vectors have the expected shape. Video-file/chunk/episode offsets come from native episode metadata. Selected frame positions join native frame index/timestamp to original encoded video PTS; the largest nominal residual is **0.000001223 seconds**.

This tiny residual reflects floating-point/printed PTS and nominal30Hz clock arithmetic. It is **not physical camera/sensor synchronization accuracy**. The release does not provide independently timestamped per-camera exposure/robot-feedback clocks, calibrated hardware latency, or complete camera synchronization traces, so physical timing uncertainty remains unverified. Selected-frame rows retain both native episode seconds and global source-video PTS.

`observation.state` and `action` differ in every selected example (mean absolute differences about0.0018–0.0047 in undeclared native position units). This proves distinct stored arrays, not an independently calibrated force sensor. Current vendor code supports position-feedback versus commanded-target semantics; the collection-time driver revision is unknown. No force/torque signal is substituted or invented.

The frame manifest binds each PNG/RGB hash to native sample/frame/time, source video, repository revision and fixed review crop. Source videos remain byte-identical to official hashes. H264 preview clips are labeled re-encoded review derivatives with original interval mappings; they are never used as model inputs. Context crops are display enlargements and are unsuitable for calibrated submillimetre geometry measurements. Source full-camera PNGs and original media remain available.

The entire decoded window and all four cameras are available in the randomized review gallery. Successful nominal timing checks alone do not establish visible abnormality or valid outcome labels.
