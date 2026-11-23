# Fatima Desk user guide

Fatima Desk lets you see and control another computer or phone, copy files
and text between them, and chat while you work. This guide covers installing
the app, connecting to a device, letting someone connect to yours, and what
to do when something doesn't work.

> [!Caution]
> Only connect to devices you own or have permission to use, and only let
> people you trust connect to yours. Anyone with your ID and password can see
> your screen and use your mouse and keyboard.

**Contents:**
[Before you start](#before-you-start) ·
[Install](#install) ·
[The main window](#the-main-window) ·
[Connect to another device](#connect-to-another-device) ·
[Let someone connect to you](#let-someone-connect-to-you) ·
[Unattended access](#unattended-access-permanent-password) ·
[Aliases](#aliases) ·
[When your ID changes](#when-your-id-changes) ·
[During a session](#during-a-session) ·
[Transfer files](#transfer-files) ·
[Android](#android) ·
[Updating](#updating) ·
[Troubleshooting](#troubleshooting)

---

## Before you start

- **Both devices need Fatima Desk** and an internet connection. Fatima Desk
  connects only through the Fatima Desk server, so it can't talk to RustDesk
  or other remote-desktop apps.
- **Every device has a 9-digit ID**, such as `482 915 307`. It is how others
  find your device. The server admin assigns IDs; you can't pick your own.
- **A device can also have an alias**, such as `Office-PC@fd`, which is
  easier to remember. Typing the alias works exactly like typing the ID.
- **To connect you need the other device's ID (or alias) and its password**,
  or someone at that device who clicks *Accept*.

## Install

Download the file for your device from the
[latest release](https://github.com/hassanxs/fatima-desk/releases/latest).

### Windows 10 and 11

| File | Use it when |
|---|---|
| `fatimadesk-1.5.3-x64.msi` | Recommended. Installs Fatima Desk for all users with a background service, so the computer can be reached after a restart and before anyone signs in. |
| `fatimadesk-1.5.3-install.exe` | Same app with a guided installer. |
| `fatimadesk-1.5.3-windows-portable.zip` | You can't or don't want to install. Unzip and run; it works only while it is open, and Windows prompts (such as UAC) can't be controlled remotely. |

The app isn't code-signed yet, so Windows SmartScreen or your antivirus may
warn you. Choose **More info → Run anyway**.

### macOS

1. Open the DMG for your Mac: `aarch64` for Apple Silicon (M1 and newer),
   `x86_64` for Intel.
2. Drag **Fatima Desk** to **Applications**.
3. The app isn't notarized, so the first time **right-click it and choose
   Open**, then confirm.
4. To let others see and control this Mac, open **System Settings → Privacy &
   Security** and turn on Fatima Desk under **Screen Recording** and
   **Accessibility**. Quit and reopen the app afterwards.

Intel Macs need a Metal-capable graphics driver.

### Linux

Install the package for your distribution:

```sh
sudo apt install ./fatimadesk-1.5.3-x86_64.deb       # Debian, Ubuntu, Mint
sudo dnf install ./fatimadesk-1.5.3-0.x86_64.rpm     # Fedora
sudo zypper install ./fatimadesk-1.5.3-0.x86_64-suse.rpm   # openSUSE
```

The package runs a background service so the computer can be reached after
a reboot. Being controlled needs an **X11** session; choose "Xorg" or "X11"
on the login screen if your desktop offers it. The Wayland login screen isn't
supported.

### Android (5.1 or newer)

1. Download `fatimadesk-1.5.3-arm64-v8a.apk` (almost every phone made since
   2017) or `armeabi-v7a.apk` (old 32-bit phones).
2. When asked, allow **Install unknown apps** for your browser or file
   manager, then install the APK.
3. See [Android](#android) for sharing the phone's screen.

## The main window

On a computer the main window has two halves.

**Left – your device.** This is what others need to connect to you:

- **ID** – your 9-digit ID. Double-click it to copy it.
- **Alias** – shown under the ID if your device has one, as `name@fd`.
  Double-click it to copy it.
- **One-time password** – changes after each session. Click the refresh
  icon to get a new one now, or the pencil to set a permanent password.

**Right – control a remote desktop.** Type an ID or alias here to connect.
Below it are your **Recent sessions**, **Favorites** and the **Address book**
of devices you have connected to.

At the bottom, a green dot and **Ready** mean you are connected to the server
and can make and receive connections.

## Connect to another device

1. Get the other device's **ID or alias** and its **password** from the
   person at that device (or from your own notes, if it is yours).
2. Type the ID (spaces are optional) or the alias (`Office-PC` or
   `Office-PC@fd`) into **Control Remote Desktop**.
3. Click **Connect**. To only move files, click the arrow next to *Connect*
   and choose **Transfer file**.
4. Enter the password when asked. Tick **Remember password** if this is a
   device you use often.
   If the other side hasn't set a password for you, the person there sees a
   prompt and must click **Accept**.

The remote screen opens in a new tab. Close the tab, or click the **X** in
the session toolbar, to disconnect.

## Let someone connect to you

1. Tell them your **ID** (or alias) and your current **one-time password**.
   Share these only with people you trust, ideally over the phone or in
   person.
2. When they connect, a small window opens showing who is connecting.
   Click **Accept** to let them in or **Dismiss** to refuse.
3. While they are connected, the same window lets you switch individual
   permissions off: keyboard and mouse, clipboard, file transfer, audio and
   more. You can also chat with them there.
4. Click **Disconnect** in that window to end the session at any time.

The one-time password changes after each session, so the next person needs
a new one from you.

## Unattended access (permanent password)

For a computer you want to reach when nobody is there, such as your office
PC, set a permanent password on it:

1. On that computer, open **Settings → Security**. On Windows, click
   **Unlock security settings** first and confirm the prompt.
2. Under **Password**, click **Set permanent password** and enter a strong
   password that you don't use anywhere else.
3. Choose **Use permanent password** (or **Use both passwords** to keep the
   one-time password working too).

Install the app (MSI or installer on Windows, the package on Linux) so its
service keeps running after a restart. Then you can connect any time with the
ID and that password.

## Aliases

An alias is a second, easier name for your device, such as `Office-PC@fd`.
Your 9-digit ID stays the same; people can connect with either.

**Setting your alias** (you can do this once):

- **Computer:** **Settings → Security → ID → Set alias**.
- **Android:** on the **Share screen** tab, tap the **⋮** menu → **Set
  alias**.

Type the name without `@fd` and click **OK**. The rules:

- 4 to 16 characters,
- starts with a letter,
- only letters, digits, `-` and `_`.

The dialog shows each rule in green once your alias meets it. After it is
saved, the alias appears under your ID within a few seconds.

**After that, only the server admin can change or remove your alias.** The
*Set alias* button is greyed out and says "Your alias is set." If you need a
different alias, ask the admin. Changes the admin makes show up on your
device automatically.

| Message | Meaning |
|---|---|
| Not available | Another device already has this alias. Choose another. |
| Too frequent | Too many attempts in a short time. Wait a minute and try again. |
| Invalid format | The alias breaks one of the rules above. |
| Your alias is set. Only the server admin can change it. | This device already has an alias. |
| Failed to connect to rendezvous server | The app isn't connected to the server. Check your internet connection. |

## When your ID changes

The server admin can give your device a new 9-digit ID, for example to keep
IDs in order. You don't need to do anything: the app picks up the new ID by
itself the next time it checks in with the server, usually within a minute,
and shows it in the main window.

- Tell the people who connect to you about the new ID, or give them your
  alias, which **stays the same when the ID changes**.
- Saved entries in other people's address books and recent sessions still
  point to the old ID; they need to update them.

## During a session

The toolbar at the top of the remote screen has:

- **Display** – switch between the remote device's monitors, scale the
  picture to fit or show it at original size, and change image quality
  (choose *Optimize reaction time* on a slow connection).
- **Keyboard** – choose how keys are sent, and send **Ctrl+Alt+Del** and
  other special keys.
- **Actions** – **Transfer file**, **Chat**, lock or restart the remote
  computer, block the remote user's input, and copy the clipboard.
- **Full screen**, **minimize** and **close** buttons.

Copying and pasting text, and files on Windows, works between the two
devices while the clipboard permission is on.

## Transfer files

Open **Transfer file** from the connect button or from the session toolbar.
The window shows your files on the left and the remote device's files on the
right. Select files or folders and click the send arrow, or drag them from
one side to the other. Progress is shown at the bottom, and you can pause or
cancel a transfer there.

## Android

### Share your phone's screen

1. Open Fatima Desk and go to the **Share screen** tab. Your ID (and alias,
   if you have one) is shown at the top.
2. Tap **Start service** and allow screen capture when Android asks.
3. Give the person connecting your ID and password, and tap **Accept** when
   they connect.

### Let a PC control the phone

To let the other side tap and swipe, turn on **Input control** on the *Share
screen* tab. Android opens **Accessibility** settings: find **Fatima Desk
Input** and turn it on. Without it the other side can only watch.

Under the same tab you can also allow file transfer and audio capture.
Some phones stop background apps to save battery; if sharing stops when the
screen turns off, set Fatima Desk's battery usage to **Unrestricted**.

### Control a computer from the phone

Use the **Connect** tab: type the computer's ID or alias and tap the arrow.
Drag with one finger to move the mouse, tap to click, and use the keyboard
icon to type. Switch between mouse mode and touch mode from the toolbar.

## Updating

From version 1.5.3-fd2, Fatima Desk checks for a new version each time it
starts. When there is one, a card on the home screen says so:

- **Windows and macOS** (installed): click **Update**. Fatima Desk downloads
  the new version, checks that it is the genuine signed release, and installs
  it. Windows asks for permission (UAC), macOS for your password.
- **Android** (from 1.5.3-fd3): tap the banner. The app downloads the new
  version and opens Android's installer; tap **Update**. The first time,
  Android asks you to allow Fatima Desk to install apps.
- **Linux**: click **Download** to open the release page, then install the new
  package over the old one.

**Changelog** on the card shows what's new. On Windows and macOS (from
1.5.3-fd3), *Settings → General → Auto update* installs new versions in the
background when nobody is connected. On a computer, turn off *Check for software update on startup* in
the same place to stop the check.

Versions before 1.5.3-fd2 don't check for updates: download the new version
from the [releases page](https://github.com/hassanxs/fatima-desk/releases)
and install it over the old one. In every case your ID, alias, passwords and
address book are kept.

## Troubleshooting

| Problem | What to try |
|---|---|
| The status says **Not ready** or keeps connecting | Check your internet connection. Some company or school networks block remote-desktop traffic; try another network or ask the network admin. |
| **ID does not exist** | Check the ID with the other person. If their ID was recently changed by the admin, use the new one, or their alias. The other device must be on and running Fatima Desk. |
| **Wrong password** | One-time passwords change after every session; ask for the current one. |
| The alias doesn't connect | Type it exactly as shown, with or without `@fd`. If the admin changed it, ask for the new one. |
| **Black or frozen screen** on a Mac | Turn on *Screen Recording* for Fatima Desk in System Settings → Privacy & Security, then quit and reopen the app. |
| The remote Mac ignores the mouse | Turn on *Accessibility* for Fatima Desk in the same place. |
| Can't connect to a Linux computer at the login screen | Sign in once with an X11/Xorg session; the Wayland login screen isn't supported. |
| Android: the PC sees the screen but can't control it | Turn on *Input control* and enable *Fatima Desk Input* under Accessibility. |
| Windows: can't click on admin prompts (UAC) | Install the app with the MSI instead of running the portable version. |
| The session is slow or choppy | In the toolbar choose *Optimize reaction time*, or lower the image quality. |

If the problem continues, [open an issue](https://github.com/hassanxs/fatima-desk/issues)
and attach the log file:

- **Windows:** `%APPDATA%\FatimaDesk\log`
- **macOS:** `~/Library/Logs/FatimaDesk`
- **Linux:** `~/.local/share/logs/FatimaDesk`

Don't post your password in an issue.
