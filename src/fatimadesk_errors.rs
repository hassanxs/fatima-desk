//! A connection error that would show the Fatima Desk server's address shows
//! "Fatima Desk server" instead. Errors about any other address (connecting
//! straight to a computer by its IP) are left as they are.

use hbb_common::config::{self, Config};

pub const SERVER_UNREACHABLE: &str = "Failed to connect to Fatima Desk server. Please try later";

/// The message to show instead of `err`, when `err` names one of our servers.
pub fn user_facing(err: &str) -> Option<&'static str> {
    let rest = err.strip_prefix("Failed to connect to ")?;
    let addr = rest.split_whitespace().next().unwrap_or_default();
    let host = host_of(addr);
    if !host.is_empty() && our_server_hosts().iter().any(|h| h.eq_ignore_ascii_case(host)) {
        Some(SERVER_UNREACHABLE)
    } else {
        None
    }
}

/// "1.2.3.4:21216" -> "1.2.3.4", "[::1]:21216" -> "::1", "host" -> "host".
fn host_of(addr: &str) -> &str {
    let addr = addr.trim_end_matches([':', ',', '.']);
    if let Some(v6) = addr.strip_prefix('[') {
        return v6.split(']').next().unwrap_or_default();
    }
    match addr.rsplit_once(':') {
        Some((host, port)) if !host.contains(':') && port.bytes().all(|b| b.is_ascii_digit()) => host,
        _ => addr,
    }
}

fn our_server_hosts() -> Vec<String> {
    let mut list: Vec<String> = config::RENDEZVOUS_SERVERS.iter().map(|s| (*s).to_owned()).collect();
    list.extend(Config::get_rendezvous_servers());
    for key in ["custom-rendezvous-server", "relay-server"] {
        list.push(Config::get_option(key));
    }
    list.iter()
        .map(|s| host_of(s.trim()).to_owned())
        .filter(|h| !h.is_empty())
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hides_our_server_address_only() {
        let ours = host_of(config::RENDEZVOUS_SERVERS[0]);
        assert_eq!(
            user_facing(&format!("Failed to connect to {ours}:21216")),
            Some(SERVER_UNREACHABLE)
        );
        assert_eq!(
            user_facing(&format!("Failed to connect to {ours}:21217 (timed out)")),
            Some(SERVER_UNREACHABLE)
        );
        // Connecting to a computer directly by its IP keeps that address.
        assert_eq!(user_facing("Failed to connect to 10.0.0.232:21118"), None);
        assert_eq!(user_facing("Failed to connect to relay server"), None);
        assert_eq!(user_facing("Connection refused"), None);
    }

    #[test]
    fn host_of_handles_ports_and_ipv6() {
        assert_eq!(host_of("1.2.3.4:21216"), "1.2.3.4");
        assert_eq!(host_of("[2001:db8::1]:21216"), "2001:db8::1");
        assert_eq!(host_of("id.example.com"), "id.example.com");
    }
}
