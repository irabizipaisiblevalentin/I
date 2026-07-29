# iOS Platform Guide

## Overview

The I Language supports iOS development through LLVM compilation with Swift/ObjC interop. This guide covers setup, building, and publishing for Apple platforms.

## Setting Up Xcode

### Requirements

- macOS 14+ (Sonoma or later)
- Xcode 15.4+
- iOS 17+ SDK
- Apple Developer account ($99/year)

### Installation

```bash
# Install Xcode from Mac App Store or
xcode-select --install

# Install required Xcode version
xcversion install 15.4

# Accept license
sudo xcodebuild -license accept
```

### Command Line Tools

```bash
# Verify installation
xcode-select -p
# Output: /Applications/Xcode.app/Contents/Developer

# Install additional components
xcodebuild -runFirstLaunch
```

## Building for iOS

### Creating a New Project

```bash
iglu new myapp --platform ios
cd myapp
```

### Build Commands

```bash
# Debug build for simulator
iglu build ios --debug --simulator

# Release build for device
iglu build ios --release

# Run on simulator
iglu run ios

# Run on device
iglu run ios --device "My iPhone"

# Build for archive (App Store)
iglu build ios --release --archive
```

### Build Configuration (`iglu.json`)

```json
{
  "name": "MyApp",
  "bundle": "com.example.myapp",
  "version": {
    "code": 1,
    "name": "1.0.0"
  },
  "ios": {
    "minVersion": "16.0",
    "targetVersion": "17.0",
    "swiftVersion": "5.9",
    "deploymentTarget": {
      "iphone": "16.0",
      "ipad": "16.0",
      "watch": "9.0"
    },
    "capabilities": [
      "PushNotifications",
      "BackgroundModes",
      "SignInWithApple"
    ],
    "entitlements": {
      "com.apple.developer.associated-domains": ["applinks:example.com"]
    }
  }
}
```

## iOS Project Structure

```
myapp/
├── ios/
│   ├── MyApp/
│   │   ├── AppDelegate.swift
│   │   ├── SceneDelegate.swift
│   │   ├── ContentView.swift
│   │   ├── Info.plist
│   │   ├── Assets.xcassets/
│   │   └── LaunchScreen.storyboard
│   ├── MyApp.xcodeproj/
│   ├── Podfile (if using CocoaPods)
│   └── Frameworks/
├── src/
│   ├── main.i
│   └── components/
└── iglu.json
```

## Info.plist Configuration

The build system auto-generates `Info.plist` with extensible overrides:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleDisplayName</key>
    <string>MyApp</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>UILaunchStoryboardName</key>
    <string>LaunchScreen</string>
    <key>UIRequiredDeviceCapabilities</key>
    <array>
        <string>arm64</string>
    </array>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
    </array>
    <key>NSCameraUsageDescription</key>
    <string>MyApp needs camera access to take photos</string>
    <key>NSPhotoLibraryUsageDescription</key>
    <string>MyApp needs photo library access to save photos</string>
</dict>
</plist>
```

Custom values can be specified in `iglu.json` under `ios.infoPlist`.

## Swift/ObjC Bridging

### Using Swift Libraries from I

```i
// Import Swift module
@bridge(module: "UIKit")
external class UIImage {
    static func named(_ name: String) -> UIImage?
    func withRenderingMode(_ mode: Int) -> UIImage
}

// Use in I code
let image = UIImage.named("profile_pic")
let tinted = image?.withRenderingMode(1) // alwaysTemplate
```

### Using I Code from Swift

```swift
// Swift side
import MyApp

class ViewController: UIViewController {
    let engine = IEngine()

    override func viewDidLoad() {
        super.viewDidLoad()
        let result = engine.evaluate("""
            component Hello {
                view { Text("Hello from I!") }
            }
        """)
    }
}
```

### Objective-C Interop

```i
// Bridge to Objective-C framework
@bridge(header: "AVFoundation/AVFoundation.h")
external class AVCaptureSession {
    func startRunning()
    func stopRunning()
    var isRunning: Bool { get }
}
```

## iOS-Specific Features

### Human Interface Guidelines (HIG)

```i
// Adhere to HIG standard components
component ProfileScreen {
    use hig()

    view {
        NavigationStack {
            List {
                Section("Personal Info") {
                    NavigationLink("Name") { EditNameScreen() }
                    NavigationLink("Email") { EditEmailScreen() }
                }
                Section("Preferences") {
                    Toggle("Notifications", isOn: $notifications)
                    Stepper("Volume", value: $volume, in: 0...10)
                }
            }
            .navigationTitle("Profile")
        }
    }
}
```

### Gestures

```i
component GestureDemo {
    view {
        Text("Swipe me")
            .onSwipe(Direction.left) { handleSwipe() }
            .onSwipe(Direction.right) { handleUndo() }
            .onLongPress { showContextMenu() }
            .onTap(2) { handleDoubleTap() } // Double tap
            .onPinch { scale, velocity -> handleZoom(scale) }
            .onRotate { angle, velocity -> handleRotation(angle) }
    }
}
```

### Safe Areas

```i
component SafeAreaDemo {
    use safeArea()

    view {
        VStack {
            // Safe area insets
            Color.red
                .frame(height: safeArea.top)
                .ignoresSafeArea()

            MainContent()

            // Bottom safe area for home indicator
            Color.black
                .frame(height: safeArea.bottom)
                .ignoresSafeArea()
        }
        .ignoresSafeArea(.container)
    }
}
```

### Dynamic Island / Live Activities

```i
import ios.liveactivity.*

component OrderTracker {
    use liveActivity()

    // Start live activity
    fun startTracking(orderId: String) {
        LiveActivity.request(
            attributes: OrderAttributes(orderId: orderId),
            content: OrderStatus("Preparing")
        )
    }

    // Update
    fun updateStatus(status: String) {
        LiveActivity.update(OrderStatus(status))
    }
}
```

### Widgets

```i
import ios.widget.*

@widget(kind: "com.example.myapp.weather")
component WeatherWidget {
    use widgetConfiguration()

    view {
        VStack {
            Text("\(currentTemp)°")
                .font(.system(size: 40, weight: .bold))
            Text(condition)
                .font(.caption)
        }
        .padding()
    }

    // Timeline provider
    fun getTimeline() async -> Timeline {
        Timeline(
            entries: [
                Entry(date: now, value: fetchWeather()),
                Entry(date: now + 3600, value: fetchWeather())
            ],
            policy: .after(nextRefresh)
        )
    }
}
```

## Publishing to Apple App Store

### Certificate Management

```bash
# Using fastlane (recommended)
fastlane produce --app_identifier com.example.myapp --app_name MyApp

# Create distribution certificate
fastlane match appstore --app_identifier com.example.myapp

# Or manually via Xcode
# - Apple Developer Portal -> Certificates -> Production
# - Download and install in Keychain
```

### Archive & Upload

```bash
# Build archive
iglu build ios --release --archive

# Export for App Store
xcodebuild -exportArchive \
    -archivePath build/MyApp.xcarchive \
    -exportPath build/MyApp.ipa \
    -exportOptionsPlist exportOptions.plist

# Upload with altool
xcrun altool --upload-app \
    -f build/MyApp.ipa \
    -u username@apple.com \
    -p @keychain:AC_PASSWORD
```

### exportOptions.plist

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
</dict>
</plist>
```

### App Store Connect Checklist

- [ ] App name and subtitle (30 chars)
- [ ] Description (4000 chars max)
- [ ] Keywords (100 chars max)
- [ ] Screenshots (6.5" and 5.5" required)
- [ ] App preview video (optional, 30s)
- [ ] Privacy policy URL
- [ ] Age rating
- [ ] Build uploaded via Xcode or altool
- [ ] TestFlight internal/external testing
- [ ] Pricing and availability
- [ ] In-app purchases (if applicable)

### TestFlight Distribution

```bash
# Upload to TestFlight
fastlane beta

# Or via altool (same as upload above)
# Manage via App Store Connect -> TestFlight
```

## iPad Support (Split View, Multitasking)

### Configuration

```json
{
  "ios": {
    "ipad": {
      "supportsAllOrientations": true,
      "requiresFullScreen": false,
      "supportsSplitView": true,
      "supportsSlideOver": true,
      "supportsStageManager": true
    }
  }
}
```

### Adaptive Layout

```i
component AdaptiveLayout {
    use sizeClass()

    view {
        // Respond to horizontal size class
        if sizeClass.horizontal == .regular {
            // iPad split view layout
            HSplit {
                Sidebar()
                DetailContent()
            }
        } else {
            // iPhone compact layout
            NavigationStack {
                List {
                    ForEach(items) { item in
                        NavigationLink(item.title) { DetailView(item) }
                    }
                }
            }
        }
    }
}
```

### Multi-Window Support (iPadOS)

```i
component DocumentApp {
    use scene()

    // Open document in new window
    fun openDocumentInNewWindow(docId: String) {
        UIApplication.shared.requestSceneSessionActivation(
            nil,
            userActivity: NSUserActivity("com.example.openDocument")
                .withUserInfo(["docId": docId])
        )
    }
}
```

## watchOS Support

### Watch App Configuration

```json
{
  "ios": {
    "watch": {
      "enabled": true,
      "companionApp": "com.example.myapp",
      "watchVersion": "9.0",
      "independentlyRun": true
    }
  }
}
```

### Watch Connectivity

```i
import ios.watchconnectivity.*

component WatchConnectivity {
    use watchSession()

    // Send data to iPhone
    fun sendHeartRate(bpm: Int) {
        watchSession.sendMessage(
            ["type": "heartrate", "value": bpm],
            replyHandler = { response in
                print("Received: \(response)")
            }
        )
    }

    // Receive data from iPhone
    onMessage { message in
        when (message["type"]) {
            "workout" -> startWorkout(message["id"])
            "music" -> playPlaylist(message["playlist"])
        }
    }
}
```

### Watch-Specific UI

```i
component WatchWorkout {
    use watchUI()

    view {
        TabView {
            // Metrics tab
            VStack {
                Text("\(heartRate)")
                    .font(.system(.largeTitle, design: .rounded))
                    .foregroundStyle(.red)
                Text("BPM").font(.caption2)
            }
            .tabItem { Text("HR") }

            // Controls tab
            VStack {
                Button("Pause") { pauseWorkout() }
                    .tint(.yellow)
                Button("End") { endWorkout() }
                    .tint(.red)
            }
            .tabItem { Text("Control") }
        }
    }
}
```

### Complications

```i
import ios.complication.*

@complication(family: [.circular, .rectangular, .graphicRectangular])
component WeatherComplication {
    view {
        Text("\(temp)°")
            .font(.headline)
    }

    // Timeline entries
    fun getTimeline() -> [ComplicationEntry] {
        [
            ComplicationEntry(date: now, text: "\(currentTemp)°"),
            ComplicationEntry(date: now + 3600, text: "\(hourlyTemp)°")
        ]
    }
}
```

## Performance Tuning for iOS

### Startup Optimization

- Minimize dynamic framework loading
- Use `static` linking where possible
- Defer non-critical initialization

```i
component AppDelegate {
    application(didFinishLaunching:) {
        // Critical path
        initializeCrashReporter()
        initializeCoreData()

        // Defer with BG task
        DispatchQueue.global().async {
            preloadFonts()
            setupAnalytics()
        }

        return true
    }
}
```

### Memory Management

- Use value types (structs) where possible
- Avoid reference cycles with `weak` references
- Use AutoRelease pool for tight loops

```i
// Use struct instead of class for data models
struct UserData {
    let id: String
    let name: String
    let avatar: Image?
}

// Auto release pool for batch processing
func processBatch(items: [Item]) {
    autoreleasepool {
        for item in items {
            transform(item)
        }
    }
}
```

### Rendering Performance

- Profile with Instruments > GPU
- Minimize view hierarchy depth
- Use `CALayer.shouldRasterize` for static content
- Prefer SwiftUI `LazyVStack` / `LazyHStack` over `ForEach` with `ScrollView`

```i
// Use lazy loading for large lists
ScrollView {
    LazyVStack {
        ForEach(items) { item in
            ItemRow(item: item)
        }
    }
}
```

### Network Optimization

```i
// URLSession with shared cache
let session = URLSession(configuration: {
    let config = URLSessionConfiguration.default
    config.urlCache = URLCache(
        memoryCapacity: 20 * 1024 * 1024,
        diskCapacity: 100 * 1024 * 1024
    )
    config.httpMaximumConnectionsPerHost = 4
    return config
}())

// Request coalescing
func fetchUser(id: String) async -> User {
    if let cached = userCache[id] { return cached }
    let user = try await api.get("/users/\(id)")
    userCache[id] = user
    return user
}
```

### Battery Optimization

- Use `BGTaskScheduler` for background work
- Batch Core Data saves
- Reduce location accuracy when not needed

```i
// Background task registration
BGTaskScheduler.shared.register(for: "com.example.sync", using: nil) { task in
    handleBackgroundSync(task: task)
}

// Schedule task
let request = BGAppRefreshTaskRequest(identifier: "com.example.sync")
request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)
try BGTaskScheduler.shared.submit(request)
```

### Profiling Tools

```bash
# Instruments CLI
xcrun xctrace record --template "Time Profiler" \
    --device "My iPhone" \
    --output profile.trace \
    MyApp

# Profile with iglu
iglu profile ios --template "Metal System Trace"
iglu profile ios --template "Leaks"
```

### Common Anti-Patterns

- ❌ Blocking main thread with sync network calls
- ❌ Creating excessive autoreleased objects in loops
- ❌ Ignoring `@MainActor` for UI updates
- ❌ Overusing `GeometryReader` (causes layout passes)
- ❌ Retaining large view hierarchies in memory

---

## Platform-Specific Notes

- **Simulator**: Use iPhone 15 Pro simulator for development. Run `iglu run ios --simulator "iPhone 15 Pro"`.
- **Debug Builds**: Debug builds are signed with development certificates only. They cannot be distributed.
- **Bitcode**: Deprecated in Xcode 14. Disable for faster builds.
- **Swift Concurrency**: I's async/await maps directly to Swift's structured concurrency.
- **Xcode Cloud**: CI/CD integration via Xcode Cloud workflows defined in `.xcodecloud.yml`.
