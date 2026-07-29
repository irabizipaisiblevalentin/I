# Android Platform Guide

## Overview

The I Language provides first-class Android support through its `iglu` build system. This guide covers everything from SDK setup to Play Store publishing.

## Setting Up Android SDK

### Prerequisites

```bash
# Install Android SDK (if not using Android Studio)
# Set environment variables
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

### SDK Components

Required SDK versions:
- **minSdk**: 24 (Android 7.0)
- **targetSdk**: 34 (Android 14)
- **compileSdk**: 34

```bash
# Install required SDK components via sdkmanager
sdkmanager "platforms;android-34"
sdkmanager "build-tools;34.0.0"
sdkmanager "ndk;25.2.9519653"
sdkmanager "cmake;3.22.1"
```

## Building for Android

### Creating a New Project

```bash
iglu new myapp --platform android
cd myapp
```

### Build Commands

```bash
# Debug build
iglu build android --debug

# Release build
iglu build android --release

# Run on connected device
iglu run android

# Generate signed APK/AAB
iglu build android --release --keystore mykey.jks
```

### Build Configuration (`iglu.json`)

```json
{
  "name": "MyApp",
  "package": "com.example.myapp",
  "version": {
    "code": 1,
    "name": "1.0.0"
  },
  "android": {
    "minSdk": 24,
    "targetSdk": 34,
    "compileSdk": 34,
    "ndkVersion": "25.2.9519653",
    "permissions": [
      "android.permission.INTERNET",
      "android.permission.CAMERA"
    ],
    "features": {
      "material3": true,
      "edgeToEdge": true
    }
  }
}
```

## Android Project Structure

```
myapp/
├── android/
│   ├── app/
│   │   ├── src/
│   │   │   ├── main/
│   │   │   │   ├── java/com/example/myapp/
│   │   │   │   │   ├── MainActivity.kt
│   │   │   │   │   └── IApp.kt
│   │   │   │   ├── res/
│   │   │   │   │   ├── drawable/
│   │   │   │   │   ├── values/
│   │   │   │   │   └── mipmap-*/
│   │   │   │   └── AndroidManifest.xml
│   │   │   └── test/
│   │   └── build.gradle.kts
│   ├── build.gradle.kts
│   └── settings.gradle.kts
├── src/
│   ├── main.i
│   └── components/
└── iglu.json
```

## AndroidManifest.xml Generation

The `iglu` build system auto-generates `AndroidManifest.xml` from your `iglu.json` configuration:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.myapp">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.CAMERA" />

    <application
        android:allowBackup="false"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.MyApp"
        android:supportsRtl="true">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize"
            android:configChanges="orientation|screenSize|screenLayout">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

You can provide a custom template via `android/templates/AndroidManifest.xml`.

## Gradle Configuration

### Top-Level `build.gradle.kts`

```kotlin
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.20" apply false
}
```

### App-Level `build.gradle.kts`

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.myapp"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.activity:activity-compose:1.8.1")
}
```

## Android-Specific Features

### Material Design (Material 3)

```i
// In your I component
component MyScreen {
    use material3()

    view {
        Scaffold {
            TopAppBar(title = "My App")
            Content {
                Button("Click Me") {
                    onClick = { showDialog() }
                }
            }
        }
    }
}
```

### Edge-to-Edge Display

```i
// Enable edge-to-edge in component
component FullScreenView {
    use edgeToEdge()
    use systemBars()

    view {
        // Content renders behind system bars
        Column(Modifier.fillMaxSize()) {
            // Use padding from system bars
            Spacer(height = systemBars.top)
            Content()
            Spacer(height = systemBars.bottom)
        }
    }
}
```

### Back Gesture Handling

```i
component DetailScreen {
    use backHandler()

    // Intercept back gesture
    onBackPressed = {
        if (hasUnsavedChanges) {
            showConfirmDialog()
            true // Prevent default
        } else {
            false // Allow default
        }
    }
}
```

### Notifications

```i
import android.notifications.*

component NotificationService {
    // Create notification channel
    val channel = NotificationChannel(
        id = "messages",
        name = "Messages",
        importance = Importance.HIGH
    )

    // Send notification
    fun sendMessageNotification(sender: String, text: String) {
        NotificationBuilder(channel)
            .setSmallIcon(R.drawable.ic_message)
            .setContentTitle(sender)
            .setContentText(text)
            .setAutoCancel(true)
            .build()
            .notify()
    }
}
```

### Deep Links

```i
// In iglu.json
{
  "android": {
    "deepLinks": [
      {
        "scheme": "myapp",
        "host": "profile",
        "path": "/user/{id}"
      }
    ]
  }
}

// Handle in I code
component Router {
    onDeepLink = { url ->
        when (url) {
            "myapp://profile/user/*" -> navigate(UserProfile(id = url.pathParam("id")))
        }
    }
}
```

## Publishing to Google Play

### Generating a Signed Release Build

```bash
# Generate keystore (one-time)
keytool -genkey -v -keystore my-release-key.jks \
    -keyalg RSA -keysize 2048 -validity 10000 \
    -alias my-alias

# Build signed AAB (recommended for Play Store)
iglu build android --release --aab \
    --keystore my-release-key.jks \
    --storepass <password> \
    --keyalias my-alias \
    --keypass <password>
```

### Google Play Console Checklist

- [ ] App name, description, screenshots (at least 8)
- [ ] Feature graphic (1024x500)
- [ ] Privacy policy URL
- [ ] Content rating questionnaire
- [ ] App signing by Google Play (recommended)
- [ ] Internal / closed / open testing track
- [ ] Production release

### App Signing

For Play App Signing:
```bash
# Upload your public key certificate
# Google manages the signing key
iglu build android --release --aab \
    --upload-keystore my-upload-key.jks
```

## Android TV Support

### TV-Optimized Layout

```i
component TvHomeScreen {
    use leanback()

    view {
        BrowseFragment {
            Header("Movies")
            Row {
                MovieCard("Inception") { navigateTo(movieDetail(1)) }
                MovieCard("Interstellar") { navigateTo(movieDetail(2)) }
            }
            Header("TV Shows")
            Row {
                ShowCard("Breaking Bad") { navigateTo(showDetail(1)) }
            }
        }
    }
}
```

### TV Configuration

```json
// iglu.json extensions
{
  "android": {
    "tv": {
      "leanback": true,
      "banner": "@drawable/tv_banner",
      "providesContent": true
    }
  }
}
```

### Required TV Permissions

```xml
<uses-feature android:name="android.hardware.touchscreen" android:required="false" />
<uses-feature android:name="android.software.leanback" android:required="true" />
```

## Wear OS Support

### Wear-Specific Components

```i
import android.wear.*

component WearMainScreen {
    use wear()

    view {
        WearBox {
            Position.LEFT -> Text("Steps: 8432")
            Position.RIGHT -> Text("HR: 72")
        }
    }
}
```

### Wear Configuration

```json
{
  "android": {
    "wear": {
      "enabled": true,
      "standalone": true,
      "companion": "com.example.myapp"
    }
  }
}
```

### Data Sync

```i
component WearDataSync {
    use wearChannel()

    // Sync health data
    fun syncSteps(count: Int) {
        wearChannel.send("/steps", count)
    }

    // Receive messages from watch
    onMessage("/heartrate") { bpm ->
        updateHeartRate(bpm)
    }
}
```

## Performance Tuning for Android

### Startup Optimization

- Use **App Startup** library for initializers
- Defer heavy work with `launch(Dispatchers.Default)`
- Enable Baseline Profiles for AOT compilation

```i
// Baseline profile config
component MyApp {
    use baselineProfile()

    startup {
        // Critical path only
        initializeCrashReporting()
        initializeAnalytics()

        // Defer non-critical
        async {
            initializeImageCache()
            preloadFonts()
        }
    }
}
```

### Memory Management

- Use `@Stable` annotations on immutable data classes
- Avoid leaking Activities — use `weakReference()` for long-lived references
- Monitor with `memoryInfo()` API:

```i
fun checkMemoryUsage() {
    val info = memoryInfo()
    if (info.heapAllocated > info.heapLimit * 0.8) {
        trimCache()
    }
}
```

### Rendering Performance

- Keep Composables lean — split large trees
- Use `remember` and `derivedStateOf` judiciously
- Profile with `iglu profile android`

### Network Optimization

```i
// Use response caching
httpClient {
    cacheSize(10 * 1024 * 1024) // 10 MB
    timeout(30_000)
}

// Batch requests
val batch = api.batch {
    get("/user/profile")
    get("/user/notifications")
}
```

### Battery Optimization

- Use `WorkManager` for deferrable tasks
- Batch network calls
- Location updates with `priority = PRIORITY_BALANCED`

```i
workManager.enqueue(
    WorkRequest<SyncWorker>()
        .setConstraints(Constraints(
            networkType = NetworkType.CONNECTED,
            batteryNotLow = true
        ))
        .build()
)
```

### ProGuard/R8 Rules

```
# Generated iglu ProGuard rules
-keep class com.example.myapp.** { *; }
-keepattributes *Annotation*
-keepclassmembers class * {
    @kotlin.Metadata <methods>;
}
-dontwarn com.example.myapp.**
```

### GPU Acceleration

- Use `Modifier.graphicsLayer` for hardware accelerated compositing
- Prefer `Canvas` over `drawRect` for custom drawing
- Enable GPU profiling via `iglu profile android --gpu`

---

## Platform-Specific Notes

- **Emulator**: Use x86_64 images for faster emulation. Recommended: API 34 with Google APIs.
- **Multi-APK**: Generate per-ABI splits to reduce APK size via `iglu build android --splits abi`
- **R8 Full Mode**: Enable for maximum optimization: `android.enableR8.fullMode=true` in `gradle.properties`
- **Kotlin**: The Android runtime uses Kotlin interop. I code compiles to Kotlin bytecode.
