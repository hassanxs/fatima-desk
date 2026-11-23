pub mod keys;

/// The Fatima Desk Console's device API (heartbeat, sysinfo, audits), used when
/// no API server is configured. Must be HTTPS: its answers can end sessions and
/// change settings. Empty leaves the device API off.
pub const FD_API_SERVER: &str = "https://fd-api.x.org.pk";
