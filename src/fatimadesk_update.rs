//! Fatima Desk updates come from the GitHub releases of hassanxs/fatima-desk.
//!
//! Each release is tagged `v<VERSION>-fd<N>`. The check asks GitHub for the
//! latest release; when it is newer than [`RELEASE`], its page URL becomes the
//! software update URL, and the existing updater downloads the signed
//! `fatimadesk-update.json` from that release and installs the matching file.

use hbb_common::{bail, log, ResultType};

pub const REPO_OWNER: &str = "hassanxs";
pub const REPO_NAME: &str = "fatima-desk";
/// The release this build is part of. Bump it for every release.
pub const RELEASE: &str = "1.5.3-fd3";
pub const UPDATE_METADATA_FILE: &str = "fatimadesk-update.json";
const LATEST_RELEASE_API: &str = "https://api.github.com/repos/hassanxs/fatima-desk/releases/latest";
const MAX_RESPONSE_BYTES: usize = 1024 * 1024;

/// `1.5.3-fd2` or `v1.5.3-fd2` -> (1, 5, 3, 2). A plain `1.5.3` is build 0.
pub fn parse_release(release: &str) -> Option<(u16, u16, u16, u16)> {
    let release = release.strip_prefix('v').unwrap_or(release);
    let (version, build) = match release.split_once("-fd") {
        Some((version, build)) => (version, Some(build)),
        None => (release, None),
    };
    let number = |s: &str| -> Option<u16> {
        if s.is_empty() || !s.bytes().all(|b| b.is_ascii_digit()) {
            return None;
        }
        s.parse().ok()
    };
    let mut parts = version.split('.');
    let major = number(parts.next()?)?;
    let minor = number(parts.next()?)?;
    let patch = number(parts.next()?)?;
    if parts.next().is_some() {
        return None;
    }
    let build = match build {
        Some(build) => number(build)?,
        None => 0,
    };
    Some((major, minor, patch, build))
}

pub fn release_page_url(tag: &str) -> String {
    format!("https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/tag/{tag}")
}

pub fn release_download_prefix(tag: &str) -> String {
    format!("https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{tag}/")
}

/// The page of the latest release when it is newer than this build.
fn newer_release_url() -> ResultType<Option<String>> {
    let client = crate::hbbs_http::create_http_client_with_url_strict(LATEST_RELEASE_API)?;
    let response = client
        .get(LATEST_RELEASE_API)
        .header("Accept", "application/vnd.github+json")
        .header("User-Agent", "FatimaDesk-Updater")
        .timeout(std::time::Duration::from_secs(30))
        .send()?;
    if !response.status().is_success() {
        bail!("Update check failed with HTTP status {}", response.status());
    }
    let bytes = response.bytes()?;
    if bytes.len() > MAX_RESPONSE_BYTES {
        bail!("Update check response is too large");
    }
    let latest: serde_json::Value = serde_json::from_slice(&bytes)?;
    let Some(tag) = latest["tag_name"].as_str() else {
        bail!("Update check response has no tag_name");
    };
    let Some(latest_release) = parse_release(tag) else {
        bail!("Latest release tag is not a Fatima Desk release: {tag}");
    };
    let Some(current) = parse_release(RELEASE) else {
        bail!("This build's release is invalid: {RELEASE}");
    };
    if latest_release > current {
        Ok(Some(release_page_url(tag)))
    } else {
        Ok(None)
    }
}

/// Checks GitHub and sets (or clears) the software update URL. Blocking: call
/// it from a plain thread, not from async code.
pub fn check() -> ResultType<()> {
    let result = newer_release_url();
    let url = match &result {
        Ok(Some(url)) => url.clone(),
        _ => String::new(),
    };
    *crate::common::SOFTWARE_UPDATE_URL.lock().unwrap() = url.clone();
    if !url.is_empty() {
        log::info!("Fatima Desk update available: {url}");
        #[cfg(feature = "flutter")]
        {
            let data = serde_json::json!({"name": "check_software_update_finish", "url": url});
            let _ = crate::flutter::push_global_event(crate::flutter::APP_TYPE_MAIN, data.to_string());
        }
    }
    result.map(|_| ())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn release_matches_this_version() {
        let (major, minor, patch, build) = parse_release(RELEASE).unwrap();
        assert_eq!(format!("{major}.{minor}.{patch}"), crate::VERSION);
        assert!(build > 0);
    }

    #[test]
    fn compares_releases() {
        assert_eq!(parse_release("v1.5.3-fd2"), Some((1, 5, 3, 2)));
        assert!(parse_release("v1.5.3-fd10") > parse_release("1.5.3-fd9"));
        assert!(parse_release("v1.6.0-fd1") > parse_release("1.5.3-fd9"));
        assert!(parse_release("v1.5.3-fd1") > parse_release("1.5.3"));
        for bad in ["", "nightly", "v1.5", "v1.5.3.1", "v1.5.3-rc1", "v1.5.3-fd", "v1.5.3-fd+1", "v99999.1.1"] {
            assert_eq!(parse_release(bad), None, "{bad}");
        }
    }

    /// Needs the network and this build's release published on GitHub:
    /// `cargo test --lib -- --ignored live_release`.
    #[cfg(not(any(target_os = "android", target_os = "ios")))]
    #[test]
    #[ignore]
    fn live_release_manifest_verifies() {
        let tag = format!("v{RELEASE}");
        let page = release_page_url(&tag);
        for (platform, arch, format) in [
            ("windows", "x86_64", "msi"),
            ("windows", "x86_64", "exe"),
            ("macos", "aarch64", "dmg"),
            ("macos", "x86_64", "dmg"),
        ] {
            let query = crate::update_metadata::UpdateArtifactQuery { platform, arch, format };
            let artifact = crate::updater::verified_update_artifact_for_release_page_url(&page, query)
                .unwrap_or_else(|e| panic!("{platform} {arch} {format}: {e}"));
            assert!(artifact.url.starts_with(&release_download_prefix(&tag)));
        }
        assert_eq!(newer_release_url().unwrap(), None);
    }
}
