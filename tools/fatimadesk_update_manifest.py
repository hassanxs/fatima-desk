"""Signed update manifest for a Fatima Desk release.

The app's updater (src/updater, src/update_metadata.rs) only installs a file
listed in the release's `fatimadesk-update.json` with a matching size and
SHA-256, and only if `fatimadesk-update.json.sig` is a valid Ed25519
signature by a key in TRUSTED_UPDATE_KEYS. Needs `pip install cryptography`.

    # once: make the signing key (keep it secret, outside the repository)
    python tools/fatimadesk_update_manifest.py genkey ../secrets/fatimadesk-update-signing.pem

    # every release: write the manifest and its signature next to the files
    python tools/fatimadesk_update_manifest.py sign --key ../secrets/fatimadesk-update-signing.pem \
        --tag v1.5.3-fd2 --dir ../releases/1.5.3-fd2

Upload both outputs to the release together with the installers.
"""
import argparse
import base64
import datetime
import hashlib
import json
import os
import re
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

REPO = 'hassanxs/fatima-desk'
KEY_ID = '2026-fd-ed25519-1'
CONTEXT = b'RustDesk update metadata v1\n'   # must match update_metadata.rs
MANIFEST = 'fatimadesk-update.json'

# (file name pattern, platform, arch, format). Only formats the updater installs.
ARTIFACTS = [
    (r'fatimadesk-{v}-x64\.msi', 'windows', 'x86_64', 'msi'),
    (r'fatimadesk-{v}-install\.exe', 'windows', 'x86_64', 'exe'),
    (r'fatimadesk-{v}-aarch64\.dmg', 'macos', 'aarch64', 'dmg'),
    (r'fatimadesk-{v}-x86_64\.dmg', 'macos', 'x86_64', 'dmg'),
]


def genkey(path):
    if os.path.exists(path):
        sys.exit(f'{path} exists; not overwriting a signing key')
    key = Ed25519PrivateKey.generate()
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption())
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(pem)
    print_public(key)


def load_key(path):
    with open(path, 'rb') as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def print_public(key):
    raw = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    print(f'key_id: {KEY_ID}')
    print('public_key: [' + ', '.join(str(b) for b in raw) + ']')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def sign(key_path, tag, folder):
    m = re.fullmatch(r'v(\d+\.\d+\.\d+)-fd(\d+)', tag)
    if not m:
        sys.exit(f'tag must look like v1.5.3-fd2, not {tag}')
    version = m.group(1)
    files = os.listdir(folder)
    artifacts = []
    for pattern, platform, arch, fmt in ARTIFACTS:
        rx = re.compile(pattern.format(v=re.escape(version)))
        names = [n for n in files if rx.fullmatch(n)]
        if len(names) != 1:
            sys.exit(f'expected one file matching {rx.pattern} in {folder}, found {names}')
        name = names[0]
        path = os.path.join(folder, name)
        artifacts.append({
            'platform': platform, 'arch': arch, 'format': fmt,
            'url': f'https://github.com/{REPO}/releases/download/{tag}/{name}',
            'file_name': name, 'size': os.path.getsize(path), 'sha256': sha256(path),
        })
    metadata = {
        'schema_version': 1, 'app': 'rustdesk', 'package_id': 'rustdesk',
        'version': tag[1:], 'release_id': tag,
        'published_at': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'signature_key_id': KEY_ID, 'artifacts': artifacts,
    }
    body = json.dumps(metadata, indent=2).encode() + b'\n'
    signature = load_key(key_path).sign(CONTEXT + body)
    sig = {'schema_version': 1, 'algorithm': 'ed25519', 'key_id': KEY_ID,
           'signature': base64.b64encode(signature).decode()}
    with open(os.path.join(folder, MANIFEST), 'wb') as f:
        f.write(body)
    with open(os.path.join(folder, MANIFEST + '.sig'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(sig, indent=2) + '\n')
    for a in artifacts:
        print(f"{a['platform']:8} {a['arch']:8} {a['format']:4} {a['file_name']}")
    print(f'wrote {MANIFEST} and {MANIFEST}.sig')


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('genkey'); g.add_argument('path')
    k = sub.add_parser('pubkey'); k.add_argument('path')
    s = sub.add_parser('sign')
    s.add_argument('--key', required=True); s.add_argument('--tag', required=True)
    s.add_argument('--dir', required=True)
    a = p.parse_args()
    if a.cmd == 'genkey':
        genkey(a.path)
    elif a.cmd == 'pubkey':
        print_public(load_key(a.path))
    else:
        sign(a.key, a.tag, a.dir)


if __name__ == '__main__':
    main()
