package com.carriez.flutter_hbb

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.core.content.FileProvider
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import java.io.File

/** Own class so it can't clash with a plugin's FileProvider in the merged manifest. */
class FdUpdateFileProvider : FileProvider()

/**
 * Fatima Desk in-app update: hands a downloaded APK to Android's installer.
 * Android itself refuses an APK that isn't signed with the installed app's key.
 */
object ApkInstaller {
    fun handle(activity: Activity, call: MethodCall, result: MethodChannel.Result): Boolean {
        when (call.method) {
            "fd_can_install_apk" -> result.success(canInstall(activity))
            "fd_allow_install_apk" -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    activity.startActivity(
                        Intent(
                            Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                            Uri.parse("package:${activity.packageName}")
                        )
                    )
                }
                result.success(true)
            }
            "fd_install_apk" -> {
                try {
                    val path = call.argument<String>("path") ?: throw IllegalArgumentException("no path")
                    val updates = File(activity.cacheDir, "updates").canonicalFile
                    val file = File(path).canonicalFile
                    if (file.parentFile != updates || !file.name.endsWith(".apk") || !file.isFile) {
                        throw IllegalArgumentException("not a downloaded update")
                    }
                    val uri = FileProvider.getUriForFile(activity, "${activity.packageName}.fdupdate", file)
                    val intent = Intent(Intent.ACTION_VIEW).apply {
                        setDataAndType(uri, "application/vnd.android.package-archive")
                        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
                    }
                    activity.startActivity(intent)
                    result.success(true)
                } catch (e: Exception) {
                    result.error("install_failed", e.message, null)
                }
            }
            else -> return false
        }
        return true
    }

    private fun canInstall(activity: Activity): Boolean =
        Build.VERSION.SDK_INT < Build.VERSION_CODES.O ||
            activity.packageManager.canRequestPackageInstalls()
}
