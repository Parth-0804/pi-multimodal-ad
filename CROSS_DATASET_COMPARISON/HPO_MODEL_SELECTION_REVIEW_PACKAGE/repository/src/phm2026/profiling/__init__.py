"""Dataset-neutral structural profiling."""

from .assets import (
    InventoryPlan,
    InventoryResult,
    build_inventory_plan,
    discover_inventory_paths,
    profile_asset_inventory,
    write_inventory_run,
)

__all__ = [
    "InventoryPlan",
    "InventoryResult",
    "build_inventory_plan",
    "discover_inventory_paths",
    "profile_asset_inventory",
    "write_inventory_run",
]

from .sensors import (
    SensorProfileOptions,
    SensorProfileResult,
    SensorSource,
    build_hdf5_schema,
    load_sensor_sources,
    profile_hdf5_file,
    profile_sensor_sources,
    select_sensor_sources,
    write_sensor_run,
)

__all__ += [
    "SensorProfileOptions",
    "SensorProfileResult",
    "SensorSource",
    "build_hdf5_schema",
    "load_sensor_sources",
    "profile_hdf5_file",
    "profile_sensor_sources",
    "select_sensor_sources",
    "write_sensor_run",
]

from .images import (
    ImageProfileOptions,
    ImageProfileResult,
    ImageSource,
    build_image_schema,
    load_image_sources,
    profile_image_sources,
    select_image_sources,
    select_quality_source_ids,
    write_image_run,
)

__all__ += [
    "ImageProfileOptions",
    "ImageProfileResult",
    "ImageSource",
    "build_image_schema",
    "load_image_sources",
    "profile_image_sources",
    "select_image_sources",
    "select_quality_source_ids",
    "write_image_run",
]

from .alignment import (
    ALIGNMENT_SCHEMA_VERSION,
    AlignmentAuditResult,
    AlignmentOptions,
    CanonicalEvent,
    NearestAlignment,
    TimelineAuditResult,
    TimelineGroupAudit,
    align_event_modalities,
    audit_timelines,
    timestamps_are_comparable,
)

__all__ += [
    "ALIGNMENT_SCHEMA_VERSION",
    "AlignmentAuditResult",
    "AlignmentOptions",
    "CanonicalEvent",
    "NearestAlignment",
    "TimelineAuditResult",
    "TimelineGroupAudit",
    "align_event_modalities",
    "audit_timelines",
    "timestamps_are_comparable",
]
