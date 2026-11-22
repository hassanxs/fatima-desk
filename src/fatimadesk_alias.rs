//! Fatima Desk: aliases and IDs assigned in the Console.
//!
//! A device keeps its 9-digit ID and may also have an alias. The Fatima Desk
//! server stores the alias, resolves it for clients that dial it, and sends
//! the device its alias (and any ID the admin assigned) in every
//! RegisterPeerResponse.

use hbb_common::{
    bytes::Bytes,
    config::{Config, CONNECT_TIMEOUT, RENDEZVOUS_PORT},
    log,
    rendezvous_proto::*,
    socket_client, tokio,
};
use std::{sync::Mutex, time::Instant};

pub const OPTION_ALIAS: &str = "fd-alias";
const ASSIGN_RETRY_SECS: u64 = 30;

lazy_static::lazy_static! {
    static ref LAST_ASSIGN_ATTEMPT: Mutex<Option<Instant>> = Default::default();
}

fn device_uuid() -> Bytes {
    #[cfg(not(any(target_os = "android", target_os = "ios")))]
    return Bytes::from(
        hbb_common::machine_uid::get()
            .unwrap_or_default()
            .as_bytes()
            .to_vec(),
    );
    #[cfg(any(target_os = "android", target_os = "ios"))]
    return Bytes::from(hbb_common::get_uuid());
}

async fn first_rendezvous_server() -> Option<String> {
    #[cfg(not(any(target_os = "android", target_os = "ios")))]
    let servers = crate::ipc::get_rendezvous_servers(1_000).await;
    #[cfg(any(target_os = "android", target_os = "ios"))]
    let servers = Config::get_rendezvous_servers();
    servers.into_iter().next()
}

async fn request(server: &str, msg: RendezvousMessage) -> Option<RendezvousMessage> {
    let mut socket = socket_client::connect_tcp(
        crate::check_port(server, RENDEZVOUS_PORT),
        CONNECT_TIMEOUT,
    )
    .await
    .ok()?;
    socket.send(&msg).await.ok()?;
    crate::common::get_next_nonkeyexchange_msg(&mut socket, None).await
}

/// The numeric ID behind `alias`, or an empty string when `alias` is not an
/// alias on this server (the caller then dials it as it is).
#[tokio::main(flavor = "current_thread")]
pub async fn resolve_alias(alias: String) -> String {
    if !hbb_common::is_valid_fd_alias(&alias) {
        return String::new();
    }
    let Some(server) = first_rendezvous_server().await else {
        return String::new();
    };
    let mut msg = RendezvousMessage::new();
    msg.set_fd_alias_request(FdAliasRequest {
        alias: alias.clone(),
        ..Default::default()
    });
    match request(&server, msg).await.and_then(|m| m.union) {
        Some(rendezvous_message::Union::FdAliasResponse(r)) if r.alias == alias => r.id,
        _ => String::new(),
    }
}

/// Sets this device's alias (an empty `alias` removes it). Returns "" on
/// success, otherwise the text the UI shows.
#[tokio::main(flavor = "current_thread")]
pub async fn set_alias(id: String, alias: String) -> String {
    if !alias.is_empty() && !hbb_common::is_valid_fd_alias(&alias) {
        return "Invalid format".to_owned();
    }
    let uuid = device_uuid();
    if uuid.is_empty() {
        return "Unknown error".to_owned();
    }
    let Some(server) = first_rendezvous_server().await else {
        return "Failed to connect to rendezvous server".to_owned();
    };
    let mut msg = RendezvousMessage::new();
    msg.set_fd_set_alias(FdSetAlias {
        id,
        uuid,
        alias: alias.clone(),
        ..Default::default()
    });
    use fd_set_alias_response::Result::*;
    match request(&server, msg).await.and_then(|m| m.union) {
        Some(rendezvous_message::Union::FdSetAliasResponse(r)) => match r.result.enum_value() {
            Ok(OK) => String::new(),
            Ok(ALIAS_EXISTS) => "Not available".to_owned(),
            Ok(TOO_FREQUENT) => "Too frequent".to_owned(),
            Ok(INVALID_FORMAT) => "Invalid format".to_owned(),
            Ok(SERVER_ERROR) => "Server error".to_owned(),
            _ => "Unknown error".to_owned(),
        },
        None => "Failed to connect to rendezvous server".to_owned(),
        _ => "server_not_support".to_owned(),
    }
}

/// Called by the rendezvous mediator for every RegisterPeerResponse.
pub fn on_register_peer_response(host: &str, rpr: &RegisterPeerResponse) {
    if Config::get_option(OPTION_ALIAS) != rpr.fd_alias {
        Config::set_option(OPTION_ALIAS.to_owned(), rpr.fd_alias.clone());
    }
    let new_id = rpr.fd_assign_id.as_str();
    if new_id.is_empty() || !hbb_common::is_valid_custom_id(new_id) || new_id == Config::get_id()
    {
        return;
    }
    {
        let mut last = LAST_ASSIGN_ATTEMPT.lock().unwrap();
        if last.is_some_and(|t| t.elapsed().as_secs() < ASSIGN_RETRY_SECS) {
            return;
        }
        *last = Some(Instant::now());
    }
    let host = host.to_owned();
    let new_id = new_id.to_owned();
    tokio::spawn(async move {
        let old_id = Config::get_id();
        let uuid = device_uuid();
        if uuid.is_empty() {
            return;
        }
        let err = crate::ui_interface::check_id(host, old_id.clone(), new_id.clone(), uuid).await;
        if err.is_empty() {
            log::info!("ID assigned by the server: {} -> {}", old_id, new_id);
            Config::set_key_confirmed(false);
            Config::set_id(&new_id);
        } else {
            log::warn!("Applying the ID assigned by the server failed: {}", err);
        }
    });
}
