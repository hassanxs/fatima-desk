// Fatima Desk in-app update on Android: download the release's APK for this
// phone's ABI and hand it to Android's installer (ApkInstaller.kt). Android
// itself refuses an APK that isn't signed with the installed app's key.
import 'dart:io';

import 'package:device_info_plus/device_info_plus.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hbb/common.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:url_launcher/url_launcher.dart';

final _tagRe = RegExp(r'^v(\d+\.\d+\.\d+)-fd\d+$');

Future<void> fdAndroidUpdate(String releasePageUrl) async {
  final tag = releasePageUrl.split('/').last;
  final m = _tagRe.firstMatch(tag);
  final abis = (await DeviceInfoPlugin().androidInfo).supportedAbis;
  final abi = abis.contains('arm64-v8a')
      ? 'arm64-v8a'
      : abis.contains('armeabi-v7a')
          ? 'armeabi-v7a'
          : null;
  if (m == null || abi == null) {
    await launchUrl(Uri.parse(releasePageUrl),
        mode: LaunchMode.externalApplication);
    return;
  }
  if (await gFFI.invokeMethodWithResult<bool>('fd_can_install_apk') != true) {
    _askToAllowInstalls();
    return;
  }
  final url = 'https://github.com/hassanxs/fatima-desk/releases/download/'
      '$tag/fatimadesk-${m.group(1)}-$abi.apk';

  double progress = 0;
  bool canceled = false;
  StateSetter? update;
  gFFI.dialogManager.show((setState, close, context) {
    update = setState;
    return CustomAlertDialog(
      title: Text('${translate('Downloading')} Fatima Desk $tag'),
      content: LinearProgressIndicator(value: progress > 0 ? progress : null),
      actions: [
        dialogButton('Cancel', onPressed: () {
          canceled = true;
          close();
        }, isOutline: true),
      ],
    );
  }, tag: 'fd-apk-update');

  final client = http.Client();
  try {
    final dir = Directory('${(await getTemporaryDirectory()).path}/updates');
    await dir.create(recursive: true);
    final file = File('${dir.path}/fatimadesk-update.apk');
    final resp = await client.send(http.Request('GET', Uri.parse(url)));
    if (resp.statusCode != 200) {
      throw 'HTTP ${resp.statusCode}';
    }
    final total = resp.contentLength ?? 0;
    var received = 0;
    final sink = file.openWrite();
    try {
      await for (final chunk in resp.stream) {
        if (canceled) break;
        sink.add(chunk);
        received += chunk.length;
        if (total > 0) update?.call(() => progress = received / total);
      }
    } finally {
      await sink.close();
    }
    if (canceled) return;
    if (total > 0 && received != total) {
      throw 'download incomplete';
    }
    gFFI.dialogManager.dismissByTag('fd-apk-update');
    await gFFI.invokeMethodWithResult<bool>('fd_install_apk', {'path': file.path});
  } catch (e) {
    gFFI.dialogManager.dismissByTag('fd-apk-update');
    if (!canceled) _showError(releasePageUrl, e.toString());
  } finally {
    client.close();
  }
}

void _askToAllowInstalls() {
  gFFI.dialogManager.show((setState, close, context) {
    return CustomAlertDialog(
      title: Text(translate('Update')),
      content: const Text(
          'To install the update, allow Fatima Desk to install apps, then tap the update button again.'),
      actions: [
        dialogButton('Cancel', onPressed: close, isOutline: true),
        dialogButton('Settings', onPressed: () {
          close();
          gFFI.invokeMethod('fd_allow_install_apk');
        }),
      ],
    );
  });
}

void _showError(String releasePageUrl, String error) {
  gFFI.dialogManager.show((setState, close, context) {
    return CustomAlertDialog(
      title: Text(translate('Error')),
      content: Text('The update could not be installed: $error'),
      actions: [
        dialogButton('Close', onPressed: close, isOutline: true),
        dialogButton('Download', onPressed: () {
          close();
          launchUrl(Uri.parse(releasePageUrl),
              mode: LaunchMode.externalApplication);
        }),
      ],
    );
  });
}
