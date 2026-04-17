"""The Sophos XG integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import SophosXGDataUpdateCoordinator, SophosXGBandwidthCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sophos XG from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Main coordinator — slow poll (60 s): device info, stats, licenses, services, CPU
    main_coordinator = SophosXGDataUpdateCoordinator(hass, entry)
    await main_coordinator.async_config_entry_first_refresh()

    # Bandwidth coordinator — fast poll (10 s): interface throughput
    bandwidth_coordinator = SophosXGBandwidthCoordinator(hass, entry)
    await bandwidth_coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "main": main_coordinator,
        "bandwidth": bandwidth_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok