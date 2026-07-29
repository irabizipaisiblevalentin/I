# Packaging and Distribution Guide

## Overview

This guide covers building, signing, and distributing I Language apps for Android and iOS, covering debug to production releases.

---

## Build Configuration

### Unified Build Config (`iglu.json`)

```json
{
  "build": {
    "appName": "MyApp",
    "version": {
      "code": 1,
      "name": "1.0.0"
    },
    "android": {
      "package": "com.example.myapp",
      "minSdk": 24,
      "targetSdk": 34,
      "compileSdk": 34
    },
    "ios": {
      "bundle": "com.example.myapp",
      "minVersion": "16.0",
      "targetVersion": "17.0"
    },
    "buildTypes": {
      "debug": {
        "signing": "debug",
        "minification": false,
        "debuggable": true,
        "ext": {}
      },
      "release": {
        "signing": "release",
        "minification": true,
        "debuggable": false,
        "ext": {}
      }
    },
    "flavors": {
      "free": {
        "appName": "MyApp Free",
        "ext": {}
      },
      "paid": {
        "appName": "MyApp Pro",
        "ext": {}
      }
    }
  }
}
```

### Build Variants

```bash
# Build specific flavor + type
iglu build android --flavor free --buildType release
iglu build ios --flavor paid --buildType debug

# List available variants
iglu build variants
```

---

## Debug Builds

### Android

```bash
# Standard debug build
iglu build android --debug

# Install directly
iglu run android --debug

# Debug APK location
# build/android/app/debug/app-debug.apk

# With device logcat
iglu run android --debug --log
```

### iOS

```bash
# Build for simulator
iglu build ios --debug --simulator

# Build for device
iglu build ios --debug --device

# Run on simulator
iglu run ios --debug --simulator "iPhone 15 Pro"

# Debug build location
# build/ios/Debug-iphonesimulator/MyApp.app
# build/ios/Debug-iphoneos/MyApp.app
```

### Debug Signing

**Android**: Auto-signed with Android debug keystore:
```bash
# Default debug keystore location
~/.android/debug.keystore
# Password: android
# Alias: androiddebugkey
```

**iOS**: Uses development provisioning profile:
```bash
# Auto-managed by Xcode
# Requires developer account team set in iglu.json
```

---

## Release Builds

### Android Release

```bash
# Build unsigned APK
iglu build android --release

# Build signed APK
iglu build android --release \
    --keystore release.keystore \
    --storepass <password> \
    --keyalias myalias \
    --keypass <password>

# Build Android App Bundle (AAB) — recommended
iglu build android --release --aab \
    --keystore release.keystore

# Build with specific signing config
iglu build android --release \
    --signingConfig release-signing.json
```

### iOS Release

```bash
# Build archive
iglu build ios --release --archive

# Export IPA
iglu export ios --exportMethod app-store

# Build and export in one step
iglu build ios --release --export \
    --exportMethod app-store \
    --teamId ABCDEF1234

# Options for export method:
#   app-store    — App Store distribution
#   ad-hoc       — Ad-hoc distribution (limited devices)
#   enterprise   — Enterprise in-house distribution
#   development  — Development distribution
```

### signingConfig.json (Android)

```json
{
  "storeFile": "release.keystore",
  "storePassword": "secret",
  "keyAlias": "myalias",
  "keyPassword": "secret",
  "storeType": "jks"
}
```

---

## APK Generation

### Standard APK

```bash
# Single universal APK
iglu build android --release --apk
# Output: build/android/app/release/app-release.apk
```

### Split APKs by ABI

```bash
# Per-architecture APKs (reduces size)
iglu build android --release --apk --splits abi

# Output:
# build/android/app/release/app-armeabi-v7a-release.apk
# build/android/app/release/app-arm64-v8a-release.apk
# build/android/app/release/app-x86_64-release.apk
```

### Split APKs by Density

```bash
# Per-screen density APKs
iglu build android --release --apk --splits density
```

### Multi-APK Configuration

```json
{
  "android": {
    "splits": {
      "abi": {
        "enable": true,
        "universalApk": true,
        "include": ["armeabi-v7a", "arm64-v8a", "x86_64"]
      },
      "density": {
        "enable": false,
        "include": ["mdpi", "hdpi", "xhdpi", "xxhdpi"]
      }
    }
  }
}
```

---

## AAB Generation (Android App Bundle)

### Building AAB

```bash
# Build AAB for Google Play
iglu build android --release --aab
# Output: build/android/app/release/app-release.aab
```

### AAB Benefits

- Smaller downloads (Google Play serves optimized APK per device)
- On-Demand Delivery (install features on demand)
- In-app updates API support
- Play Feature Delivery for modularization

### Dynamic Delivery / Feature Modules

```json
{
  "android": {
    "dynamicFeatures": [
      {
        "name": "camera",
        "installTime": "ondemand",
        "modules": ["camera_feature"]
      },
      {
        "name": "ar",
        "installTime": "conditional",
        "conditions": {
          "device": [
            {"feature": "android.hardware.camera.ar"}
          ]
        }
      }
    ]
  }
}
```

### AAB Testing

```bash
# Test AAB locally
bundletool build-apks \
    --bundle=build/app-release.aab \
    --output=build/app.apks \
    --ks=release.keystore \
    --ks-pass=pass:secret

# Install on connected device
bundletool install-apks --apks=build/app.apks
```

---

## IPA Generation (iOS)

### Archive and Export

```bash
# Step 1: Create archive
xcodebuild archive \
    -workspace ios/MyApp.xcworkspace \
    -scheme MyApp \
    -archivePath build/MyApp.xcarchive

# Step 2: Export IPA
xcodebuild -exportArchive \
    -archivePath build/MyApp.xcarchive \
    -exportPath build/MyApp.ipa \
    -exportOptionsPlist exportOptions.plist
```

### Export Options Plist

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store</string>
    <key>teamID</key>
    <string>YOUR_TEAM_ID</string>
    <key>uploadBitcode</key>
    <false/>
    <key>compileBitcode</key>
    <true/>
    <key>uploadSymbols</key>
    <true/>
    <key>destination</key>
    <string>export</string>
    <key>signingStyle</key>
    <string>automatic</string>
    <key>provisioningProfiles</key>
    <dict>
        <key>com.example.myapp</key>
        <string>MyApp App Store Profile</string>
    </dict>
</dict>
</plist>
```

### Using Fastlane

```ruby
# Fastfile
lane :release do
  match(type: "appstore")
  gym(
    scheme: "MyApp",
    export_method: "app-store",
    output_directory: "build"
  )
  pilot(
    skip_waiting_for_build_processing: true
  )
end
```

```bash
# Run
fastlane release
```

---

## Code Signing

### Android Code Signing

```bash
# Generate keystore
keytool -genkey -v -keystore release.keystore \
    -alias myalias \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000

# Verify keystore
keytool -list -v -keystore release.keystore -alias myalias

# Sign existing APK manually
apksigner sign --ks release.keystore app-release-unsigned.apk

# Verify signature
apksigner verify app-release.apk
```

### Play App Signing

```json
// iglu.json
{
  "android": {
    "signing": {
      "playAppSigning": true,
      "uploadKeystore": "upload.keystore",
      "uploadKeyAlias": "uploadkey"
    }
  }
}
```

1. Upload the public certificate to Google Play Console
2. Google manages the app signing key
3. Your upload key is used only for upload verification

### iOS Code Signing

```bash
# Using fastlane match (recommended)
fastlane match appstore \
    --app_identifier com.example.myapp

# Manual signing
# 1. Create certificates in Apple Developer Portal
# 2. Create provisioning profile
# 3. Download and install both

# Verify signing
codesign -d -vvvv MyApp.app
```

### Signing Comparison

| Aspect | Android | iOS |
|--------|---------|-----|
| Key type | RSA 2048+ | RSA 2048+ (Apple) |
| Signing format | APK Signature Scheme v2/v3 | CMS / Mach-O |
| Key management | Keystore (JKS/PKCS12) | Keychain + Developer Portal |
| Upload key | Optional (Play Signing) | N/A |
| Profile | N/A | Provisioning Profile |
| Expiry | 25+ years | 1 year (distribution) |
| Revocation | Manual | Apple can revoke |

---

## ProGuard / R8 Optimization

### Configuration

```
# project/proguard-rules.pro
# Keep I runtime classes
-keep class com.iruntime.** { *; }
-keep class * implements com.iruntime.IComponent { *; }

# Keep data classes
-keepclassmembers class * {
    @kotlin.Metadata <methods>;
}

# Keep serialization
-keepattributes *Annotation*, InnerClasses
-keepclassmembers class * {
    @kotlinx.serialization.Serializable <fields>;
}

# Keep JNI
-keepclasseswithmembernames class * {
    native <methods>;
}

# Keep model classes
-keep class com.example.myapp.models.** { *; }
```

### R8 Full Mode

```properties
# gradle.properties
android.enableR8.fullMode=true
```

```json
{
  "android": {
    "r8": {
      "fullMode": true,
      "optimizations": [
        "class/unboxing",
        "method/merging",
        "enum/optimization"
      ],
      "configFile": "proguard-rules.pro"
    }
  }
}
```

### Size Impact

| Optimization | APK Size Reduction |
|-------------|-------------------|
| None (debug) | ~25 MB |
| ProGuard | ~18 MB |
| R8 | ~15 MB |
| R8 + Bundle | ~10 MB (download) |
| R8 + Bundle + splits | ~7 MB (per device) |

---

## App Thinning (iOS)

### On-Demand Resources

```json
{
  "ios": {
    "onDemandResources": {
      "level1-assets": {
        "tags": ["level1"],
        "category": .initialInstall
      },
      "level2-assets": {
        "tags": ["level2"],
        "category": .onDemand
      }
    }
  }
}
```

### Bitcode

```json
{
  "ios": {
    "bitcode": true
  }
}
```

### Slicing

iOS App Store automatically creates device-specific variants:
- Device family (iPhone/iPad)
- GPU family
- Display resolution

### Asset Catalog Optimization

```bash
# Check asset catalog
iglu optimize assets --platform ios

# Ensure all image sets have 1x, 2x, 3x variants
# Use vector PDFs where possible (scalable)
```

---

## Store Requirements

### Google Play

| Requirement | Detail |
|-------------|--------|
| App Bundle | Required for new apps since 2021 |
| 64-bit support | Required (arm64-v8a) |
| Target API | Must target API 31+ (Aug 2024) |
| Privacy Policy | Required if handling personal data |
| Content Rating | Required for all apps |
| Testing | 20 testers for 14 days (closed track) |
| Account | $25 one-time fee |

### Apple App Store

| Requirement | Detail |
|-------------|--------|
| 64-bit support | Required |
| iOS version | Must support current iOS + 2 previous |
| iPad support | Required for iPhone apps |
| Dark mode | Strongly recommended |
| Privacy labels | Required |
| Guideline review | Human review process |
| Account | $99/year |

### Pre-Launch Checklist

```bash
# Run automated checks
iglu verify android --prelaunch
iglu verify ios --prelaunch

# This checks:
# - Version consistency
# - Missing permissions
# - Missing resources
# - Signing validity
# - ProGuard coverage
# - Dependency licenses
```

---

## Enterprise Distribution

### Android (Internal Sharing)

```bash
# Build signed APK
iglu build android --release --apk

# Upload to Google Play Console → Internal App Sharing
# Or host privately via MDM
```

### iOS Enterprise

```json
{
  "ios": {
    "enterprise": {
      "manifestUrl": "https://example.com/manifest.plist",
      "provisioningProfile": "enterprise.mobileprovision"
    }
  }
}
```

```bash
# Build enterprise IPA
iglu build ios --release --exportMethod enterprise

# Host manifest.plist for OTA distribution
```

### manifest.plist (iOS OTA)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>items</key>
    <array>
        <dict>
            <key>assets</key>
            <array>
                <dict>
                    <key>kind</key>
                    <string>software-package</string>
                    <key>url</key>
                    <string>https://example.com/MyApp.ipa</string>
                </dict>
                <dict>
                    <key>kind</key>
                    <string>display-image</string>
                    <key>url</key>
                    <string>https://example.com/icon.png</string>
                </dict>
            </array>
            <key>metadata</key>
            <dict>
                <key>bundle-identifier</key>
                <string>com.example.myapp</string>
                <key>bundle-version</key>
                <string>1.0.0</string>
                <key>kind</key>
                <string>software</string>
                <key>title</key>
                <string>MyApp</string>
            </dict>
        </dict>
    </array>
</dict>
</plist>
```

---

## Automation / CI/CD

### GitHub Actions

```yaml
name: Build and Release
on:
  push:
    tags:
      - 'v*'

jobs:
  build-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      - run: iglu build android --release --aab
      - uses: actions/upload-artifact@v4
        with:
          name: app-release.aab
          path: build/android/app/release/*.aab

  build-ios:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      - run: iglu build ios --release --archive
      - run: iglu export ios --exportMethod app-store
      - uses: actions/upload-artifact@v4
        with:
          name: MyApp.ipa
          path: build/ios/*.ipa
```

### Build Version Management

```json
{
  "build": {
    "version": {
      "autoIncrement": true,
      "basedOn": "git",  // or "date", "manual"
      "format": "${major}.${minor}.${patch}+${build}"
    }
  }
}
```

---

## Troubleshooting

### Common Build Issues

| Problem | Solution |
|---------|----------|
| APK too large | Enable R8, use AAB, split by ABI |
| iOS code signing error | Run `fastlane match` or renew profiles |
| Missing native libs | Check NDK path and ABI filters |
| ProGuard stripping I code | Add keep rules for runtime classes |
| AAB install fails | Use bundletool for local testing |
| iOS archive fails | Check Swift version compatibility |
| Version conflict | Sync versions in `iglu.json` |
| Missing resources | Run `iglu verify` before build |

---

## Output Structure

```
build/
├── android/
│   ├── app/
│   │   ├── debug/
│   │   │   └── app-debug.apk
│   │   └── release/
│   │       ├── app-release.aab
│   │       ├── app-release.apk
│   │       └── app-arm64-v8a-release.apk
│   └── outputs/
│       ├── mapping/
│       │   └── release/mapping.txt
│       └── symbols/
│           └── native-debug-symbols.zip
├── ios/
│   ├── Debug-iphonesimulator/
│   │   └── MyApp.app
│   ├── Debug-iphoneos/
│   │   └── MyApp.app
│   ├── Release-iphoneos/
│   │   └── MyApp.app
│   ├── MyApp.xcarchive/
│   └── MyApp.ipa
└── build.log
```

---

## Best Practices

1. **Always use AAB** for Google Play distribution
2. **Keep keystores secure** — never commit to version control
3. **Automate code signing** with fastlane match
4. **Test release builds** on physical devices before submitting
5. **Monitor build size** — set up size budgets in CI
6. **Version consistently** — align Android versionCode with iOS CFBundleVersion
7. **Use build flavors** for different environments (dev/staging/prod)
8. **Generate ProGuard mapping** files and upload to crash reporting
9. **Enable R8 full mode** for maximum optimization
10. **Document signing credentials** in a secure vault, not README
