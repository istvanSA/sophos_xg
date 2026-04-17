"""DataUpdateCoordinator for Sophos XG."""
from __future__ import annotations

import logging
import time
from datetime import timedelta

from pysnmp.hlapi.v3arch.asyncio import (
    get_cmd,
    next_cmd,
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    BANDWIDTH_SCAN_INTERVAL,
    CONF_COMMUNITY,
    # Device Info
    OID_DEVICE_NAME,
    OID_DEVICE_TYPE,
    OID_DEVICE_FW_VERSION,
    # Device Stats
    OID_UPTIME,
    OID_LIVE_USERS,
    OID_DISK_CAPACITY,
    OID_DISK_PERCENT,
    OID_MEMORY_CAPACITY,
    OID_MEMORY_PERCENT,
    OID_SWAP_CAPACITY,
    OID_SWAP_PERCENT,
    # CPU
    OID_CPU_LOAD_BASE,
    # Services
    SERVICE_OIDS,
    # Interfaces
    OID_IF_IN_OCTETS,
    OID_IF_OUT_OCTETS,
    OID_IF_DESCR,
    # Licenses
    LICENSE_DEFINITIONS,
)

_LOGGER = logging.getLogger(__name__)


# ── Shared SNMP mixin ─────────────────────────────────────────────


class SophosXGSnmpMixin:
    """Shared SNMP helper methods for both coordinators."""

    host: str
    port: int
    community: str
    snmp_engine: SnmpEngine

    async def _async_get(self, oid: str):
        """Perform an SNMP GET. Returns the value or None on error."""
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            self.snmp_engine,
            CommunityData(self.community, mpModel=1),
            await UdpTransportTarget.create((self.host, self.port), timeout=5, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )

        if errorIndication:
            _LOGGER.warning("SNMP GET error on %s: %s", oid, errorIndication)
            return None
        if errorStatus:
            _LOGGER.warning("SNMP GET error on %s: %s", oid, errorStatus.prettyPrint())
            return None

        for varBind in varBinds:
            return varBind[1]
        return None

    async def _async_get_str(self, oid: str) -> str | None:
        """GET an OID and return its value as a string."""
        val = await self._async_get(oid)
        return str(val) if val is not None else None

    async def _async_get_int(self, oid: str) -> int | None:
        """GET an OID and return its value as an int."""
        val = await self._async_get(oid)
        if val is None:
            return None
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    async def _async_walk(self, base_oid: str) -> dict:
        """Perform an SNMP WALK using repeated next_cmd calls."""
        results = {}
        current_oid = base_oid

        while True:
            errorIndication, errorStatus, errorIndex, varBinds = await next_cmd(
                self.snmp_engine,
                CommunityData(self.community, mpModel=1),
                await UdpTransportTarget.create((self.host, self.port), timeout=5, retries=1),
                ContextData(),
                ObjectType(ObjectIdentity(current_oid)),
                lexicographicMode=False,
            )

            if errorIndication:
                _LOGGER.warning("SNMP Walk error on %s: %s", base_oid, errorIndication)
                break
            if errorStatus:
                _LOGGER.warning("SNMP Walk error on %s: %s", base_oid, errorStatus.prettyPrint())
                break
            if not varBinds:
                break

            oid_obj, val = varBinds[0]
            oid_str = str(oid_obj)

            if not oid_str.startswith(base_oid):
                break

            index = oid_str[len(base_oid):].lstrip(".")
            try:
                results[index] = int(val)
            except (ValueError, TypeError):
                results[index] = str(val)

            current_oid = oid_str

        return results


# ── Main coordinator (60 s) ───────────────────────────────────────


class SophosXGDataUpdateCoordinator(SophosXGSnmpMixin, DataUpdateCoordinator):
    """Coordinator for slow-changing data: device info, stats, licenses, services, CPU."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.community = entry.data[CONF_COMMUNITY]
        self.snmp_engine = SnmpEngine()

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_main",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict:
        """Fetch slow-changing data from SNMP."""
        try:
            data: dict = {}

            # ── Device Info ───────────────────────────────────────
            data["device_name"] = await self._async_get_str(OID_DEVICE_NAME)
            data["device_type"] = await self._async_get_str(OID_DEVICE_TYPE)
            data["fw_version"] = await self._async_get_str(OID_DEVICE_FW_VERSION)

            # ── System stats ──────────────────────────────────────
            data["uptime"] = await self._async_get_int(OID_UPTIME)
            data["live_users"] = await self._async_get_int(OID_LIVE_USERS)

            # Disk
            data["disk_capacity"] = await self._async_get_int(OID_DISK_CAPACITY)
            data["disk_percent"] = await self._async_get_int(OID_DISK_PERCENT)

            # Memory
            data["memory_capacity"] = await self._async_get_int(OID_MEMORY_CAPACITY)
            data["memory_percent"] = await self._async_get_int(OID_MEMORY_PERCENT)

            # Swap
            data["swap_capacity"] = await self._async_get_int(OID_SWAP_CAPACITY)
            data["swap_percent"] = await self._async_get_int(OID_SWAP_PERCENT)

            # ── Licenses ──────────────────────────────────────────
            for key, oid_status, oid_expiry, _ in LICENSE_DEFINITIONS:
                data[f"{key}_status"] = await self._async_get_int(oid_status)
                data[f"{key}_expiry"] = await self._async_get_str(oid_expiry)

            # ── CPU Walk ──────────────────────────────────────────
            cpu_data = await self._async_walk(OID_CPU_LOAD_BASE)
            data["cpu"] = {k: int(v) for k, v in cpu_data.items() if v is not None}

            # ── Service Status ────────────────────────────────────
            data["services"] = {}
            for oid, svc_name in SERVICE_OIDS.items():
                val = await self._async_get_int(oid)
                data["services"][svc_name] = val

            return data

        except Exception as err:
            raise UpdateFailed(f"Error communicating with SNMP: {err}") from err


# ── Bandwidth coordinator (10 s) ──────────────────────────────────


class SophosXGBandwidthCoordinator(SophosXGSnmpMixin, DataUpdateCoordinator):
    """Coordinator for fast-changing interface bandwidth data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.community = entry.data[CONF_COMMUNITY]
        self.snmp_engine = SnmpEngine()

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_bandwidth",
            update_interval=timedelta(seconds=BANDWIDTH_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict:
        """Fetch interface bandwidth data from SNMP."""
        current_time = time.time()

        try:
            old_data = self.data if self.data else {}

            if_descr = await self._async_walk(OID_IF_DESCR)
            if_in = await self._async_walk(OID_IF_IN_OCTETS)
            if_out = await self._async_walk(OID_IF_OUT_OCTETS)

            interfaces: dict = {}
            for idx, descr_val in if_descr.items():
                if not descr_val:
                    continue
                descr = str(descr_val)
                current_in = int(if_in.get(idx, 0))
                current_out = int(if_out.get(idx, 0))

                in_mbps = 0.0
                out_mbps = 0.0

                old_iface = old_data.get("interfaces", {}).get(idx)
                old_time = old_data.get("timestamp")

                if old_iface and old_time and current_time > old_time:
                    time_diff = current_time - old_time

                    old_in = old_iface.get("in_octets", current_in)
                    if current_in >= old_in:
                        in_mbps = round(((current_in - old_in) * 8) / time_diff / 1_000_000, 3)

                    old_out = old_iface.get("out_octets", current_out)
                    if current_out >= old_out:
                        out_mbps = round(((current_out - old_out) * 8) / time_diff / 1_000_000, 3)

                interfaces[idx] = {
                    "name": descr,
                    "in_octets": current_in,
                    "out_octets": current_out,
                    "in_mbps": in_mbps,
                    "out_mbps": out_mbps,
                }

            return {
                "timestamp": current_time,
                "interfaces": interfaces,
            }

        except Exception as err:
            raise UpdateFailed(f"Error communicating with SNMP (bandwidth): {err}") from err