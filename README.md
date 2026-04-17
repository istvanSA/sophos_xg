# Sophos XG Firewall Integration for Home Assistant

<p align="center">
  <img src="https://raw.githubusercontent.com/istvanSA/sophos_xg/main/icon.png" width="150" height="150">
</p>

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A custom Home Assistant integration to monitor Sophos XG (SFOS) Firewalls using SNMP. This integration provides real-time hardware health, network throughput, license status, and service monitoring.

## Features

- **Hardware Monitoring:** CPU load (per core), Memory usage/capacity, Disk usage/capacity, Swap usage/capacity, and Uptime.
- **Network Throughput:** Real-time **Download/Upload speeds in Mbps** for all network interfaces (calculated automatically from SNMP counters).
- **License Status:** Monitor all 9 Sophos license modules (Base, Network, Web, Mail, Sandstorm, etc.) with their status and expiry dates.
- **Service Monitoring:** Tracks the status of 21 internal Sophos services (DNS, IPS, Web, Database, etc.).
- **Live Users:** Monitor the count of live connected users.
- **Automatic Setup:** Easy UI configuration.

## Prerequisites

- **SNMP Enabled:** You must enable SNMP on your Sophos XG Firewall.
  - Go to **System > Administration > SNMP**.
  - Enable the **SNMP Agent**.
  - Create an **SNMPv2 Community** (e.g., `public`).
  - Go to **System > Administration > Device Access** and ensure **SNMP** is checked for the Zone where Home Assistant is located (usually `LAN`).

## Installation

### Method 1: HACS (Recommended)
1. Open **HACS** in Home Assistant.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Paste `https://github.com/istvanSA/sophos_xg` into the Repository field.
4. Select **Integration** as the Category and click **Add**.
5. Find "Sophos XG Firewall" in the HACS store and click **Download**.
6. Restart Home Assistant.

### Method 2: Manual
1. Download the latest release.
2. Copy the `custom_components/sophos_xg` folder to your Home Assistant `config/custom_components` directory.
3. Restart Home Assistant.

## Configuration

1. In Home Assistant, go to **Settings > Devices & Services**.
2. Click **Add Integration** and search for **Sophos XG Firewall**.
3. Enter your firewall's **Host/IP**, **SNMP Port** (default 161), and **Community String**.

## License

This project is licensed under the [MIT License](LICENSE).

## Credits
Built with ❤️ for the Sophos community.
