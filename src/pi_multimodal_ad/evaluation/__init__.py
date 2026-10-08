"""DEPRECATED compatibility forwarding only.

Canonical implementation: phm2026.evaluation.
Retained for external/historical callers; no automatic removal date.
Do not add scientific implementation here.
"""

from pi_multimodal_ad._forward import forward_package as _forward_package

_forward_package(globals(), 'phm2026.evaluation')
