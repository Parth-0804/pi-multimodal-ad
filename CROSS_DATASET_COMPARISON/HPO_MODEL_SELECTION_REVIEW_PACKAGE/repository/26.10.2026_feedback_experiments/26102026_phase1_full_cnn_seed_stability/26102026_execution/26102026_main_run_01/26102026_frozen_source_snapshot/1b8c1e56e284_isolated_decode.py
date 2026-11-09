"""Read-only video decoder. No file writes, cache spill, or historical imports."""
from collections import OrderedDict
from pathlib import Path

import cv2
import numpy as np
from transformers import RTDetrImageProcessor


class IsolatedDecoder:
    def __init__(self, repo: Path, weights: str, rescale_factor: float, decoder_threads: int = 1):
        self.repo = repo
        self.scale = rescale_factor
        assert decoder_threads in (1, 2, 4)
        self.decoder_threads = decoder_threads
        self.processor = RTDetrImageProcessor.from_pretrained(repo / weights, local_files_only=True)
        self.captures = OrderedDict()
        cv2.setNumThreads(1)

    def __call__(self, sample):
        key = sample["video_path"]
        if key not in self.captures:
            if len(self.captures) >= 4:
                _, old = self.captures.popitem(last=False)
                old.release()
            # OpenCV's general thread setting does not constrain FFmpeg's
            # independent decoder pool. Bound that pool at video-open time.
            cap = cv2.VideoCapture(str(self.repo / key), cv2.CAP_FFMPEG,
                                   [cv2.CAP_PROP_N_THREADS, self.decoder_threads])
            assert cap.isOpened(), ("VIDEO_OPEN_FAILURE", sample["sample_id"])
            assert int(cap.get(cv2.CAP_PROP_N_THREADS)) == self.decoder_threads
            self.captures[key] = cap
        cap = self.captures[key]
        self.captures.move_to_end(key)
        images = []
        for index in sample["frames32"]:
            current = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            if index < current or index - current > 64:
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(index))
            else:
                for _ in range(index - current):
                    cap.grab()
            ok, image = cap.read()
            assert ok, ("FRAME_DECODE_FAILURE", sample["sample_id"], index)
            images.append(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        pixels = self.processor(images=images, return_tensors="np")["pixel_values"]
        u = np.rint(pixels / self.scale).astype("uint8")
        assert np.array_equal(u.astype("float32") * np.float32(self.scale), pixels)
        return u

    def __del__(self):
        for cap in getattr(self, "captures", {}).values():
            cap.release()
