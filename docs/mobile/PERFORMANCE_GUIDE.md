# Performance Optimization Guide

## Overview

Performance is critical for mobile apps. This guide covers profiling, optimization techniques, and common anti-patterns for I Language apps on both Android and iOS.

---

## Startup Time Optimization

### Measuring Startup

```bash
# Android
iglu profile android --startup
# Reports: cold start, warm start, hot start times

# iOS
iglu profile ios --template "App Launch"
```

### Cold Start Optimization

```i
// Lazy initialize non-critical services
component AppStartup {
    // Critical path — must initialize synchronously
    onInit {
        initializeCrashReporter()
        initializeLogger()
    }

    // Deferred — run after first frame
    onFirstFrame {
        async(Dispatchers.Default) {
            preloadDatabase()
            setupPushNotifications()
            initializeAnalytics()
            preloadFonts()
            setupTheming()
        }
    }

    // Lazy — only when first needed
    val heavyService = lazy {
        HeavyAnalyticsService()
    }

    // After auth — UI process
    onAuthenticated {
        async(Dispatchers.Main) {
            heavyService.value.start()
        }
    }
}
```

### Baseline Profiles (Android)

```json
{
  "android": {
    "baselineProfile": {
      "enabled": true,
      "profileFile": "baseline-prof.txt",
      "generationTask": true
    }
  }
}
```

```i
// Baseline profile generation
component BaselineProfileGenerator {
    fun generate() {
        // These methods are AOT-compiled
        startupSequence()
        profileNavigation()
        profileListScrolling()
    }

    fun startupSequence() {
        MainActivity() // Initial screen
        renderHomeFeed()
        renderNavigation()
    }
}
```

### App Startup Library (Android)

```json
{
  "dependencies": {
    "androidx.startup": "1.1.1"
  }
}
```

```xml
<!-- AndroidManifest auto-initializers -->
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup"
    android:exported="false">
    <meta-data
        android:name="com.example.CrashReporterInitializer"
        android:value="androidx.startup" />
</provider>
```

### iOS Startup

```i
// Defer using BGTask
func application(_ application: UIApplication,
    didFinishLaunchingWithOptions options: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {

    // Critical
    setupCoreDataStack()
    configureAppearance()

    // Deferred
    DispatchQueue.global(qos: .background).async {
        preloadContent()
        syncSubscriptions()
    }

    return true
}
```

### Startup Benchmarks

| Optimization | Android Cold Start | iOS Cold Start |
|-------------|-------------------|----------------|
| Without optimization | ~2.5s | ~1.8s |
| With deferred init | ~1.2s | ~0.9s |
| With Baseline Profiles | ~0.8s | — |
| With Prewarm | — | ~0.5s |

---

## Layout Optimization

### Efficient Composables

```i
// ❌ Bad: Deep nesting causes many layout passes
view {
    VStack {
        ForEach(items) { item ->
            VStack {
                HStack {
                    Image(item.icon)
                    VStack {
                        Text(item.title)
                        Text(item.subtitle)
                    }
                }
            }
        }
    }
}

// ✅ Good: Flat hierarchy
view {
    LazyVStack {
        ForEach(items) { item ->
            ItemRow(item: item)
        }
    }
}

component ItemRow(item: Item) {
    view {
        HStack(spacing: 12) {
            AsyncImage(item.icon, size: 40)
            VStack(alignment: .leading) {
                Text(item.title).font(.body.weight(.semibold))
                Text(item.subtitle).font(.caption).foregroundColor(.secondary)
            }
        }
    }
}
```

### Avoid Unnecessary Recomposition

```i
// ❌ Bad: Recreates lambda every frame
view {
    Button("Tap") {
        handleTap() // New lambda = recomposition
    }
}

// ✅ Good: Stable lambda reference
val onTap = remember { ::handleTap }
view {
    Button("Tap", onTap: onTap)
}

// ❌ Bad: Unstable state in scope
view {
    val currentTime = state(System.currentTimeMillis())
    Text("\(currentTime.value)") // Rebuilds every frame
}

// ✅ Good: Isolate unstable state
component ClockDisplay {
    val currentTime = state(System.currentTimeMillis())
    view {
        Text("\(currentTime.value)")
    }
}
```

### Layout Performance Tips

| Tip | Impact | Platform |
|-----|--------|----------|
| Use `LazyVStack`/`LazyHStack` instead of `ScrollView`+`ForEach` | High | Both |
| Prefer `HStack`/`VStack` over `ZStack` | Medium | Both |
| Avoid `GeometryReader` in hot paths | High | iOS |
| Use `Modifier.size` instead of `frame` when possible | Low | Both |
| Minimize `Modifier` chain length | Medium | Both |
| Use `Canvas` for complex custom drawing | High | Both |

### List Performance

```i
// Efficient list with stable IDs
LazyVStack {
    ForEach(
        items: items,
        id: { it.id }, // Stable ID — prevents unnecessary rebuilds
        content: { item -> ItemRow(item) }
    )
}

// Item caching
LazyVStack(
    itemCacheSize: 50,
    preloadMargin: 100 // pixels
) {
    ForEach(items) { item ->
        ItemRow(item)
            .equatable() // Skip recomposition if props unchanged
    }
}
```

---

## Image Optimization

### Efficient Image Loading

```i
// ❌ Bad: Load full resolution
Image(path: "photo.jpg")

// ✅ Good: Load at display size
AsyncImage(
    source: "https://example.com/photo.jpg",
    width: 200,
    height: 200,
    contentMode: .aspectFill,
    placeholder: PlaceholderView(),
    loading: LoadingSpinner(),
    error: ErrorView()
)
```

### Image Pipeline Configuration

```i
imageCache {
    memorySize: 50 * 1024 * 1024,   // 50 MB
    diskSize: 100 * 1024 * 1024,    // 100 MB
    compressionQuality: 0.8,
    maxDimension: 2048,
    preheat: true,                    // Preload offscreen images
}

// Image prefetching
fun prefetchImages(urls: List<String>) {
    imageCache.prefetch(urls, priority: .low)
}

// Thumbnail generation
fun generateThumbnail(path: String, size: Int) -> Image {
    return Image(path).resize(size, size)
        .compress(quality: 0.7, format: .webp)
}
```

### Image Formats

| Format | Use Case | Size vs PNG |
|--------|----------|-------------|
| WebP | Photos with transparency | -35% |
| AVIF | Next-gen photos | -50% |
| JPEG | Photos without transparency | -20% |
| PNG | Screenshots, UI elements | Baseline |
| Vector (SVG/PDF) | Icons, illustrations | ~1 KB |

### Progressive Loading

```i
component ProgressiveImage {
    view {
        ZStack {
            // Low-res placeholder (blurred)
            Image(thumbnailUrl)
                .blur(radius: 20)
                .opacity(lowResLoaded ? 1 : 0)

            // High-res image
            AsyncImage(
                source: highResUrl,
                onLoad: { lowResLoaded = false }
            )
            .transition(.opacity(duration: 0.3))
        }
    }
}
```

---

## Memory Management

### Monitoring Memory

```i
// Track memory usage
fun logMemoryStats() {
    val runtime = Runtime.getRuntime()
    val usedMB = (runtime.totalMemory() - runtime.freeMemory()) / 1024 / 1024
    val maxMB = runtime.maxMemory() / 1024 / 1024
    log("Memory: \(usedMB)MB / \(maxMB)MB used")

    if (usedMB > maxMB * 0.8) {
        trimMemory()
    }
}

// Android
fun checkMemoryPressure() {
    val info = ActivityManager.MemoryInfo()
    activityManager.getMemoryInfo(info)
    if (info.lowMemory) {
        releaseCaches()
    }
}
```

### Avoiding Leaks

```i
// ❌ Bad: Anonymous inner class holds Activity reference
val callback = object : Callback {
    override fun onResult(value: String) {
        updateUI(value) // Holds outer class reference
    }
}

// ✅ Good: Weak reference
val callback = weakCallback { value ->
    updateUI(value)
}

// ❌ Bad: Long-lived subscription
val disposable = someObservable.subscribe { data ->
    updateView(data)
}
// Never disposed!

// ✅ Good: Lifecycle-scoped
onMount {
    disposable = lifecycle.scope {
        someObservable.subscribe { data ->
            updateView(data)
        }
    }
} // Auto-disposed on unmount
```

### Memory Tips

| Practice | Description |
|----------|-------------|
| Use `SoftReference` for caches | Allows GC to reclaim when needed |
| Recycle bitmaps | Call `bitmap.recycle()` when no longer needed |
| Use `SparseArray` over `HashMap<Int, V>` | Lower memory overhead (Android) |
| Avoid `enum` | Use `@IntDef` or sealed classes |
| Minimize `String` concatenation | Use `StringBuilder` |
| Release resources in `onPause`/`onStop` | Camera, sensors, location |
| Use `@Stable` annotations | Mark immutable containers |

### Detecting Leaks

```bash
# Android
iglu profile android --leaks
# Integrates with LeakCanary

# iOS
iglu profile ios --template "Leaks"
# Xcode Instruments Leaks template
```

---

## Battery Optimization

### Network Batching

```i
// ❌ Bad: Many small requests
async { api.logEvent("screen_view") }
async { api.logEvent("button_tap") }
async { api.logEvent("scroll") }

// ✅ Good: Batch events
fun logEvents(events: List<Event>) {
    api.batchLog(events) // Single request
}

// Queue and flush
val eventQueue = mutableListOf<Event>()
fun accumulateEvent(event: Event) {
    eventQueue.add(event)
    if (eventQueue.size >= 10) {
        flushEvents()
    }
}

fun flushEvents() {
    if (eventQueue.isNotEmpty()) {
        api.batchLog(eventQueue.toList())
        eventQueue.clear()
    }
}

// Auto-flush on background
onDeactivate { flushEvents() }
```

### Location Efficiency

```i
// ❌ Bad: High accuracy always
location.requestUpdates(accuracy: .high, interval: 1000)

// ✅ Good: Adaptive accuracy
fun startEfficientLocation() {
    if (isCharging) {
        location.requestUpdates(accuracy: .high, interval: 5000)
    } else {
        location.requestUpdates(accuracy: .balanced, interval: 30000)
    }
}

// Geofencing instead of constant updates
location.startMonitoring(
    region: CircleRegion(center: home, radius: 500)
) { event ->
    when (event) {
        .enter -> startHighAccuracyTracking()
        .exit -> stopTracking()
    }
}
```

### Background Work

```i
// Android: Use WorkManager
val syncWork = WorkRequest<SyncWorker>(
    constraints: Constraints(
        networkType: NetworkType.CONNECTED,
        batteryNotLow: true,
        idleRequired: false
    ),
    backoffPolicy: .exponential
)
workManager.enqueue(syncWork)

// iOS: Use BGTaskScheduler
let request = BGProcessingTaskRequest(identifier: "com.example.sync")
request.requiresNetworkConnectivity = true
request.requiresExternalPower = false
try BGTaskScheduler.shared.submit(request)
```

### Battery Impact Guide

| Operation | Battery Cost (per hour) |
|-----------|------------------------|
| Constant GPS (high accuracy) | ~15% |
| GPS (balanced, 5 min) | ~2% |
| Network polling (1 min) | ~8% |
| Network polling (15 min) | ~1% |
| Wake lock held continuously | ~12% |
| Sensor batching enabled | ~0.5% |
| Video recording | ~25% |
| Heavy GPU rendering | ~20% |

---

## Network Optimization

### Caching Strategy

```i
// HTTP caching
httpClient {
    cache(10 * 1024 * 1024) // 10 MB cache
    cachePolicy: .cacheFirst, // Show cache while refreshing
    staleWhileRevalidate: true
}

// In-memory cache
val userCache = Cache<String, User>(
    maxSize: 100,
    expiry: Duration.minutes(5)
)

fun getUser(id: String) async -> User {
    val cached = userCache.get(id)
    if (cached != null) return cached

    val user = await api.getUser(id)
    userCache.put(id, user)
    return user
}
```

### Request Optimization

```i
// ❌ Bad: Sequential requests
val user = await api.getUser(id)
val posts = await api.getPosts(id)
val followers = await api.getFollowers(id)

// ✅ Good: Parallel requests
val (user, posts, followers) = await all(
    api.getUser(id),
    api.getPosts(id),
    api.getFollowers(id)
)

// GraphQL-like batching
val batchResponse = await api.batch([
    Query("getUser", args: { id: id }),
    Query("getPosts", args: { userId: id, limit: 10 }),
    Query("getFollowers", args: { userId: id })
])
```

### Compression

```i
// Enable compression
httpClient {
    compression: .gzip, // or .deflate, .br (Brotli)
}

// Image compression
fun uploadPhoto(bitmap: Bitmap) {
    val compressed = bitmap.compress(
        format: .webp,
        quality: 80
    )
    api.uploadPhoto(compressed)
}
```

### Connection Pooling

```i
httpClient {
    maxConnections: 4,
    keepAlive: true,
    connectionTimeout: 10_000,
    readTimeout: 30_000,
    retryOnConnectionFailure: true
}
```

---

## GPU Acceleration

### Hardware Acceleration

```i
// Enable GPU layer
view {
    Canvas {
        // This renders on the GPU
    }
    .graphicsLayer(
        alpha: 0.9f,
        translationX: 0f,
        translationY: 0f,
        scaleX: 1f,
        scaleY: 1f,
        rotationX: 0f,
        rotationY: 0f,
        rotationZ: 0f,
        cameraDistance: 8f
    )
}
```

### Render Thread Optimization

```i
// ❌ Bad: Heavy work on main thread
view {
    Canvas {
        val path = buildComplexPath() // Blocks main thread
        drawPath(path)
    }
}

// ✅ Good: Pre-compute
val complexPath = remember {
    computeComplexPath() // Done once
}

view {
    Canvas {
        drawPath(complexPath.value)
    }
}
```

### Overdraw Reduction

```i
// ❌ Bad: Multiple overlapping backgrounds
view {
    ZStack {
        Color.blue                // Painted but hidden
            .frame(maxSize: .infinity)
        Color.white.opacity(0.8)  // Painted on top
            .frame(maxSize: .infinity)
        VStack {
            Text("Content")
                .padding()
                .background(Color.gray) // Third paint
        }
    }
}

// ✅ Good: Single background
view {
    VStack {
        Text("Content").padding()
    }
    .background(
        LinearGradient(colors: [Color.blue, Color.white])
    )
}
```

---

## Frame Rate Optimization

### Profiling Frame Drops

```bash
# Android
iglu profile android --frameRate
# Shows: missed frames, jank, frame time histogram

# iOS
iglu profile ios --template "Animation Hitches"
# Shows: hitch time ratio, reason
```

### Jank-Free Animations

```i
// ❌ Bad: Triggers layout on every frame
view {
    AnimatedVisibility(visible) {
        Text("Hello")
            .offset(x: animatedOffset.value) // Causes layout
    }
}

// ✅ Good: Use transform
view {
    AnimatedVisibility(
        visible: visible,
        enter: slideInHorizontally()  // Uses transforms
    ) {
        Text("Hello")
    }
}

// Off-screen animation
view {
    Text("Animated")
        .graphicsLayer {
            translationX = animatedOffset.value // GPU transform
        }
}
```

### Heavy Computation

```i
// Move computation off main thread
fun processItems(items: List<Item>) async -> List<ProcessedItem> {
    return await compute(Dispatchers.Default) {
        items.map { item ->
            heavyOperation(item)
        }
    }
}
```

### Frame Budget

| Device | Budget per Frame | Jank Threshold |
|--------|-----------------|----------------|
| 60 Hz | 16.67 ms | >16.67ms |
| 90 Hz | 11.11 ms | >11.11ms |
| 120 Hz | 8.33 ms | >8.33ms |
| 144 Hz | 6.94 ms | >6.94ms |

---

## Profiling Tools

### Built-in Profiling

```bash
# General profile
iglu profile android
iglu profile ios

# Specific areas
iglu profile android --area "startup"
iglu profile android --area "memory"
iglu profile android --area "network"
iglu profile android --area "rendering"

# Export profile
iglu profile android --output profile.json

# Timeline view
iglu profile android --timeline
```

### Android Tools

| Tool | Command | Purpose |
|------|---------|---------|
| Android Studio Profiler | Built-in | CPU, memory, network, energy |
| Perfetto | `perfetto -o trace.perfetto` | System-wide tracing |
| simpleperf | `simpleperf record` | CPU sampling |
| dumpsys | `adb shell dumpsys` | System service stats |
| LeakCanary | Integrated | Memory leak detection |
| Firebase Performance | SDK | Production monitoring |

### iOS Tools

| Tool | Command | Purpose |
|------|---------|---------|
| Instruments | `xcrun xctrace` | Full profiling suite |
| Time Profiler | `--template "Time Profiler"` | CPU sampling |
| Allocations | `--template "Allocations"` | Memory tracking |
| Leaks | `--template "Leaks"` | Memory leak detection |
| Core Animation | `--template "Core Animation"` | Rendering performance |
| Network | `--template "Network"` | Network activity |
| os_log | `log stream` | System log monitoring |

---

## Common Anti-Patterns

### ❌ Blocking the Main Thread

```i
// BAD
fun loadData() {
    val data = readLargeFile() // Blocks main thread!
    updateUI(data)
}

// GOOD
fun loadData() {
    async {
        val data = await readLargeFileOnBackground()
        updateUI(data)
    }
}
```

### ❌ Excessive Object Allocation

```i
// BAD — creates new objects per frame
fun renderFrame() {
    val paint = Paint() // Created every frame
    canvas.drawCircle(x, y, 10, paint)
}

// GOOD — reuse
val paint = remember { Paint() }
fun renderFrame() {
    canvas.drawCircle(x, y, 10, paint)
}
```

### ❌ Ignoring `@Stable`

Without `@Stable`, the framework treats every class as unstable and recomposes more than necessary.

### ❌ Overusing `State` for Computed Values

```i
// BAD
val double = state(0)
val source = state(5)
double.value = source.value * 2 // Manual sync

// GOOD
val double = source.derive { it * 2 } // Auto-sync
```

### ❌ Large State Objects

Keep state granular. A single massive state object causes everything to recompose when any field changes.

### ❌ Not Handling Configuration Changes

```i
// BAD — resets state on rotation
component MyScreen {
    val data = state(loadData()) // Reloads on rotation
}

// GOOD — survives rotation
component MyScreen {
    val data = rememberSaveable { state(loadData()) }
}
```

### ❌ Deep View Hierarchy

Each nesting level adds layout measurement passes. Aim for flat, balanced hierarchies.

### ❌ Missing ProGuard Rules

Without proper ProGuard/R8 rules, release builds may break or have bloated APKs.

### ❌ No Image Downsampling

Loading full-resolution images into small `ImageView`/`Image` views wastes memory.

### ❌ Retaining Large Bitmaps

```i
// BAD — never released
private var largeBitmap: Bitmap? = null
fun onImageLoaded(bitmap: Bitmap) {
    largeBitmap = bitmap // Leaks until component destroyed
}

// GOOD — release when not visible
onUnmount {
    largeBitmap?.recycle()
    largeBitmap = null
}
```

---

## Platform-Specific Optimizations

### Android

- **Use `@Composable` annotations** to help the compiler
- **Enable Baseline Profiles** for AOT compilation
- **Use `Progressive JPEG/WebP`** for network images
- **Monitor with `Android Vitals`** in Play Console
- **Use `android:largeHeap`** cautiously — remember heap grows with requests

### iOS

- **Enable `Optimization Level`** = `-Osize` for release
- **Use `SwiftUI` async images** over `UIImageView` for automatic caching
- **Prefer `struct` over `class`** for data models
- **Use `Instruments`** for Metal performance debugging
- **Mark classes as `final`** to enable static dispatch
- **Use `lazy` variables** for expensive properties

---

## Optimization Checklist

| Area | Check | Tool |
|------|-------|------|
| Startup | < 1.5s cold start | Profile, Startup |
| Layout | No missed frames >16ms | Frame Profiler |
| Memory | No leaks, < 100MB typical | Memory Profiler |
| Images | All images downsampled | Image Pipeline |
| Network | Response caching active | Network Profiler |
| Battery | No wake locks held >1s | Energy Profiler |
| GPU | < 2x overdraw | GPU Debugger |
| APK | < 20MB release size | APK Analyzer |
