"""Constants for the Sophos XG integration."""

DOMAIN = "sophos_xg"
DEFAULT_PORT = 161
DEFAULT_SCAN_INTERVAL = 60    # seconds — device info, stats, licenses, services, CPU
BANDWIDTH_SCAN_INTERVAL = 5  # seconds — interface throughput

CONF_COMMUNITY = "community"

# ── OIDs: Sophos SFOS-FIREWALL-MIB (enterprises.2604.5.1) ──

# Device Info  (sfosXGMIBObjects.1)
OID_DEVICE_NAME = "1.3.6.1.4.1.2604.5.1.1.1.0"
OID_DEVICE_TYPE = "1.3.6.1.4.1.2604.5.1.1.2.0"
OID_DEVICE_FW_VERSION = "1.3.6.1.4.1.2604.5.1.1.3.0"

# Device Stats (sfosXGMIBObjects.2)
OID_UPTIME = "1.3.6.1.4.1.2604.5.1.2.2.0"
OID_LIVE_USERS = "1.3.6.1.4.1.2604.5.1.2.6.0"
OID_DISK_CAPACITY = "1.3.6.1.4.1.2604.5.1.2.4.1.0"
OID_DISK_PERCENT = "1.3.6.1.4.1.2604.5.1.2.4.2.0"
OID_MEMORY_CAPACITY = "1.3.6.1.4.1.2604.5.1.2.5.1.0"
OID_MEMORY_PERCENT = "1.3.6.1.4.1.2604.5.1.2.5.2.0"
OID_SWAP_CAPACITY = "1.3.6.1.4.1.2604.5.1.2.5.3.0"
OID_SWAP_PERCENT = "1.3.6.1.4.1.2604.5.1.2.5.4.0"

# CPU (standard HOST-RESOURCES-MIB)
OID_CPU_LOAD_BASE = "1.3.6.1.2.1.25.3.3.1.2"

# License Details (sfosXGMIBObjects.5)
OID_BASE_LICENSE_STATUS = "1.3.6.1.4.1.2604.5.1.5.1.1.0"
OID_BASE_LICENSE_EXPIRY = "1.3.6.1.4.1.2604.5.1.5.1.2.0"
OID_NET_PROT_LICENSE_STATUS = "1.3.6.1.4.1.2604.5.1.5.2.1.0"
OID_NET_PROT_LICENSE_EXPIRY = "1.3.6.1.4.1.2604.5.1.5.2.2.0"
OID_WEB_PROT_LICENSE_STATUS = "1.3.6.1.4.1.2604.5.1.5.3.1.0"
OID_WEB_PROT_LICENSE_EXPIRY = "1.3.6.1.4.1.2604.5.1.5.3.2.0"
OID_MAIL_PROT_LICENSE_STATUS = "1.3.6.1.4.1.2604.5.1.5.4.1.0"
OID_MAIL_PROT_LICENSE_EXPIRY = "1.3.6.1.4.1.2604.5.1.5.4.2.0"
OID_WEB_SERVER_LICENSE_STATUS = "1.3.6.1.4.1.2604.5.1.5.5.1.0"
OID_WEB_SERVER_LICENSE_EXPIRY = "1.3.6.1.4.1.2604.5.1.5.5.2.0"
OID_SANDSTORM_LICENSE_STATUS = "1.3.6.1.4.1.2604.5.1.5.6.1.0"
OID_SANDSTORM_LICENSE_EXPIRY = "1.3.6.1.4.1.2604.5.1.5.6.2.0"
OID_ENHANCED_SUPPORT_STATUS = "1.3.6.1.4.1.2604.5.1.5.7.1.0"
OID_ENHANCED_SUPPORT_EXPIRY = "1.3.6.1.4.1.2604.5.1.5.7.2.0"
OID_ENHANCED_PLUS_STATUS = "1.3.6.1.4.1.2604.5.1.5.8.1.0"
OID_ENHANCED_PLUS_EXPIRY = "1.3.6.1.4.1.2604.5.1.5.8.2.0"
OID_CENTRAL_ORCH_STATUS = "1.3.6.1.4.1.2604.5.1.5.9.1.0"
OID_CENTRAL_ORCH_EXPIRY = "1.3.6.1.4.1.2604.5.1.5.9.2.0"

# Service Status (sfosXGMIBObjects.3)
# Map of OID suffix -> human-readable service name
SERVICE_OIDS = {
    "1.3.6.1.4.1.2604.5.1.3.1.0": "POP3",
    "1.3.6.1.4.1.2604.5.1.3.2.0": "IMAP4",
    "1.3.6.1.4.1.2604.5.1.3.3.0": "SMTP",
    "1.3.6.1.4.1.2604.5.1.3.4.0": "FTP",
    "1.3.6.1.4.1.2604.5.1.3.5.0": "HTTP",
    "1.3.6.1.4.1.2604.5.1.3.6.0": "Antivirus",
    "1.3.6.1.4.1.2604.5.1.3.7.0": "Anti-Spam",
    "1.3.6.1.4.1.2604.5.1.3.8.0": "DNS",
    "1.3.6.1.4.1.2604.5.1.3.9.0": "HA",
    "1.3.6.1.4.1.2604.5.1.3.10.0": "IPS",
    "1.3.6.1.4.1.2604.5.1.3.11.0": "Apache",
    "1.3.6.1.4.1.2604.5.1.3.12.0": "NTP",
    "1.3.6.1.4.1.2604.5.1.3.13.0": "Tomcat",
    "1.3.6.1.4.1.2604.5.1.3.14.0": "SSL VPN",
    "1.3.6.1.4.1.2604.5.1.3.15.0": "IPSec VPN",
    "1.3.6.1.4.1.2604.5.1.3.16.0": "Database",
    "1.3.6.1.4.1.2604.5.1.3.17.0": "Network",
    "1.3.6.1.4.1.2604.5.1.3.18.0": "Garner",
    "1.3.6.1.4.1.2604.5.1.3.19.0": "Dynamic Routing",
    "1.3.6.1.4.1.2604.5.1.3.20.0": "SSHd",
    "1.3.6.1.4.1.2604.5.1.3.21.0": "DGD",
}

SERVICE_STATUS_MAP = {
    0: "Untouched",
    1: "Stopped",
    2: "Initializing",
    3: "Running",
    4: "Exiting",
    5: "Dead",
    6: "Frozen",
    7: "Unregistered",
}

# Interfaces (standard IF-MIB)
OID_IF_IN_OCTETS = "1.3.6.1.2.1.2.2.1.10"
OID_IF_OUT_OCTETS = "1.3.6.1.2.1.2.2.1.16"
OID_IF_DESCR = "1.3.6.1.2.1.2.2.1.2"

LICENSE_STATUS_MAP = {
    0: "None",
    1: "Evaluating",
    2: "Not Subscribed",
    3: "Subscribed",
    4: "Expired",
    5: "Deactivated",
}

# Named license definitions for sensor creation
# (key in data dict, OID status, OID expiry, display name)
LICENSE_DEFINITIONS = [
    ("lic_base_fw", OID_BASE_LICENSE_STATUS, OID_BASE_LICENSE_EXPIRY, "Base Firewall"),
    ("lic_net_prot", OID_NET_PROT_LICENSE_STATUS, OID_NET_PROT_LICENSE_EXPIRY, "Network Protection"),
    ("lic_web_prot", OID_WEB_PROT_LICENSE_STATUS, OID_WEB_PROT_LICENSE_EXPIRY, "Web Protection"),
    ("lic_mail_prot", OID_MAIL_PROT_LICENSE_STATUS, OID_MAIL_PROT_LICENSE_EXPIRY, "Mail Protection"),
    ("lic_web_server", OID_WEB_SERVER_LICENSE_STATUS, OID_WEB_SERVER_LICENSE_EXPIRY, "Web Server Protection"),
    ("lic_sandstorm", OID_SANDSTORM_LICENSE_STATUS, OID_SANDSTORM_LICENSE_EXPIRY, "Sandstorm"),
    ("lic_enh_support", OID_ENHANCED_SUPPORT_STATUS, OID_ENHANCED_SUPPORT_EXPIRY, "Enhanced Support"),
    ("lic_enh_plus", OID_ENHANCED_PLUS_STATUS, OID_ENHANCED_PLUS_EXPIRY, "Enhanced Plus Support"),
    ("lic_central_orch", OID_CENTRAL_ORCH_STATUS, OID_CENTRAL_ORCH_EXPIRY, "Central Orchestration"),
]