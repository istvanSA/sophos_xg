"""Sensor platform for Sophos XG."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfInformation,
    UnitOfDataRate,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    LICENSE_STATUS_MAP,
    LICENSE_DEFINITIONS,
    SERVICE_OIDS,
    SERVICE_STATUS_MAP,
)
from .coordinator import SophosXGDataUpdateCoordinator, SophosXGBandwidthCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    main_coord: SophosXGDataUpdateCoordinator = coordinators["main"]
    bw_coord: SophosXGBandwidthCoordinator = coordinators["bandwidth"]

    entities: list[SensorEntity] = []

    # ── Device Info ───────────────────────────────────────────────
    entities.append(SophosXGTextSensor(main_coord, entry, "device_name", "Device Name", "mdi:router-network"))
    entities.append(SophosXGTextSensor(main_coord, entry, "device_type", "Device Type", "mdi:devices"))
    entities.append(SophosXGTextSensor(main_coord, entry, "fw_version", "Firmware Version", "mdi:update"))

    # ── System Stats ──────────────────────────────────────────────
    entities.append(SophosXGUptimeSensor(main_coord, entry))
    entities.append(SophosXGGaugeSensor(main_coord, entry, "live_users", "Live Users", "mdi:account-multiple", None))

    # Disk
    entities.append(SophosXGGaugeSensor(main_coord, entry, "disk_capacity", "Disk Capacity", "mdi:harddisk", "MB"))
    entities.append(SophosXGGaugeSensor(main_coord, entry, "disk_percent", "Disk Usage", "mdi:harddisk", PERCENTAGE))

    # Memory
    entities.append(SophosXGGaugeSensor(main_coord, entry, "memory_capacity", "Memory Capacity", "mdi:memory", "MB"))
    entities.append(SophosXGGaugeSensor(main_coord, entry, "memory_percent", "Memory Usage", "mdi:memory", PERCENTAGE))

    # Swap
    entities.append(SophosXGGaugeSensor(main_coord, entry, "swap_capacity", "Swap Capacity", "mdi:swap-horizontal", "MB"))
    entities.append(SophosXGGaugeSensor(main_coord, entry, "swap_percent", "Swap Usage", "mdi:swap-horizontal", PERCENTAGE))

    # ── Licenses ──────────────────────────────────────────────────
    for key, _, _, display_name in LICENSE_DEFINITIONS:
        entities.append(SophosXGLicenseSensor(main_coord, entry, key, display_name))

    # ── CPU Core Sensors ──────────────────────────────────────────
    if "cpu" in main_coord.data:
        for idx, core_id in enumerate(sorted(main_coord.data["cpu"].keys())):
            entities.append(SophosXGCPUSensor(main_coord, entry, core_id, idx))

    # ── Service Status ────────────────────────────────────────────
    if "services" in main_coord.data:
        for svc_name in main_coord.data["services"]:
            entities.append(SophosXGServiceSensor(main_coord, entry, svc_name))

    # ── Interface Sensors (bandwidth coordinator — 10 s) ──────────
    if "interfaces" in bw_coord.data:
        for idx, iface in bw_coord.data["interfaces"].items():
            name = iface["name"]
            # Raw octets (disabled by default to reduce clutter)
            entities.append(SophosXGInterfaceSensor(bw_coord, entry, idx, "in", name))
            entities.append(SophosXGInterfaceSensor(bw_coord, entry, idx, "out", name))
            # Throughput (Mbps)
            entities.append(SophosXGThroughputSensor(bw_coord, entry, idx, "in", name))
            entities.append(SophosXGThroughputSensor(bw_coord, entry, idx, "out", name))

    async_add_entities(entities)


# ── Base entities ─────────────────────────────────────────────────


class SophosXGBaseEntity(CoordinatorEntity, SensorEntity):
    """Base class for Sophos XG entities backed by the main coordinator."""

    def __init__(
        self,
        coordinator: SophosXGDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_device_info = _device_info(coordinator, entry)


class SophosXGBandwidthBaseEntity(CoordinatorEntity, SensorEntity):
    """Base class for Sophos XG entities backed by the bandwidth coordinator."""

    def __init__(
        self,
        coordinator: SophosXGBandwidthCoordinator,
        entry: ConfigEntry,
        main_coordinator: SophosXGDataUpdateCoordinator | None = None,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.entry = entry
        # Device info comes from the main coordinator if available, else fallback
        ref = main_coordinator or coordinator
        self._attr_device_info = _device_info(ref, entry)


def _device_info(coordinator, entry: ConfigEntry) -> dict:
    """Build the HA device info dict from coordinator data."""
    data = coordinator.data or {}
    dev_name = data.get("device_name") or entry.title
    dev_type = data.get("device_type") or "XG Firewall"
    fw_ver = data.get("fw_version")
    info = {
        "identifiers": {(DOMAIN, entry.entry_id)},
        "name": dev_name,
        "manufacturer": "Sophos",
        "model": dev_type,
    }
    if fw_ver:
        info["sw_version"] = fw_ver
    return info


# ── Simple text sensor ────────────────────────────────────────────


class SophosXGTextSensor(SophosXGBaseEntity):
    """Generic text/diagnostic sensor."""

    def __init__(self, coordinator, entry, data_key: str, label: str, icon: str):
        super().__init__(coordinator, entry)
        self._data_key = data_key
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_name = f"{entry.title} {label}"
        self._attr_icon = icon

    @property
    def native_value(self):
        return self.coordinator.data.get(self._data_key)


# ── Generic gauge sensor ──────────────────────────────────────────


class SophosXGGaugeSensor(SophosXGBaseEntity):
    """Generic numeric gauge sensor."""

    def __init__(self, coordinator, entry, data_key: str, label: str, icon: str, unit: str | None):
        super().__init__(coordinator, entry)
        self._data_key = data_key
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_name = f"{entry.title} {label}"
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        return self.coordinator.data.get(self._data_key)


# ── Uptime sensor ────────────────────────────────────────────────


class SophosXGUptimeSensor(SophosXGBaseEntity):
    """Uptime sensor."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_uptime"
        self._attr_name = f"{entry.title} Uptime"
        self._attr_icon = "mdi:clock-outline"
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_native_unit_of_measurement = UnitOfTime.SECONDS
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self):
        ticks = self.coordinator.data.get("uptime")
        if ticks is None:
            return None
        return ticks // 100  # TimeTicks are hundredths of a second


# ── License sensors ──────────────────────────────────────────────


class SophosXGLicenseSensor(SophosXGBaseEntity):
    """License status sensor with expiry in attributes."""

    def __init__(self, coordinator, entry, key: str, display_name: str):
        super().__init__(coordinator, entry)
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = f"{entry.title} {display_name} License"
        self._attr_icon = "mdi:certificate"

    @property
    def native_value(self):
        status_code = self.coordinator.data.get(f"{self._key}_status")
        return LICENSE_STATUS_MAP.get(status_code, "Unknown")

    @property
    def extra_state_attributes(self):
        return {"expiry_date": self.coordinator.data.get(f"{self._key}_expiry")}


# ── CPU sensor ───────────────────────────────────────────────────


class SophosXGCPUSensor(SophosXGBaseEntity):
    """CPU Core usage sensor."""

    def __init__(self, coordinator, entry, core_id: str, core_index: int):
        super().__init__(coordinator, entry)
        self.core_id = core_id
        self._attr_unique_id = f"{entry.entry_id}_cpu_{core_id}"
        self._attr_name = f"{entry.title} CPU Core {core_index}"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:cpu-64-bit"

    @property
    def native_value(self):
        return self.coordinator.data.get("cpu", {}).get(self.core_id)


# ── Service status sensor ────────────────────────────────────────


class SophosXGServiceSensor(SophosXGBaseEntity):
    """Service running status sensor."""

    def __init__(self, coordinator, entry, svc_name: str):
        super().__init__(coordinator, entry)
        self._svc_name = svc_name
        safe_id = svc_name.lower().replace(" ", "_").replace("-", "_")
        self._attr_unique_id = f"{entry.entry_id}_svc_{safe_id}"
        self._attr_name = f"{entry.title} {svc_name} Service"
        self._attr_icon = "mdi:cog"

    @property
    def native_value(self):
        code = self.coordinator.data.get("services", {}).get(self._svc_name)
        return SERVICE_STATUS_MAP.get(code, "Unknown")


# ── Interface octets sensor ──────────────────────────────────────


class SophosXGInterfaceSensor(SophosXGBandwidthBaseEntity):
    """Network interface total octets sensor (bandwidth coordinator)."""

    def __init__(self, coordinator, entry, iface_idx: str, direction: str, iface_name: str):
        super().__init__(coordinator, entry)
        self.iface_idx = iface_idx
        self.direction = direction
        self._attr_unique_id = f"{entry.entry_id}_iface_{iface_idx}_{direction}"
        self._attr_name = f"{entry.title} {iface_name} {direction.capitalize()} Octets"
        self._attr_native_unit_of_measurement = UnitOfInformation.BYTES
        self._attr_device_class = SensorDeviceClass.DATA_SIZE
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = "mdi:upload-network" if direction == "out" else "mdi:download-network"
        self._attr_entity_registry_enabled_default = False  # disabled by default

    @property
    def native_value(self):
        iface = self.coordinator.data.get("interfaces", {}).get(self.iface_idx, {})
        return iface.get(f"{self.direction}_octets")


# ── Throughput sensor (Mbps) ─────────────────────────────────────


class SophosXGThroughputSensor(SophosXGBandwidthBaseEntity):
    """Network interface throughput sensor in Mbit/s (bandwidth coordinator)."""

    def __init__(self, coordinator, entry, iface_idx: str, direction: str, iface_name: str):
        super().__init__(coordinator, entry)
        self.iface_idx = iface_idx
        self.direction = direction
        self._attr_unique_id = f"{entry.entry_id}_iface_{iface_idx}_{direction}_mbps"
        dir_label = "Download" if direction == "in" else "Upload"
        self._attr_name = f"{entry.title} {iface_name} {dir_label}"
        self._attr_native_unit_of_measurement = UnitOfDataRate.MEGABITS_PER_SECOND
        self._attr_device_class = SensorDeviceClass.DATA_RATE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:download-network" if direction == "in" else "mdi:upload-network"

    @property
    def native_value(self):
        iface = self.coordinator.data.get("interfaces", {}).get(self.iface_idx, {})
        return iface.get(f"{self.direction}_mbps")