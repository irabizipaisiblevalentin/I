# Device API Reference

## Overview

The I Language provides a comprehensive set of device APIs for accessing native hardware and platform services. All APIs follow an async permission-gated pattern.

## Camera API

### Photo Capture

```i
import device.camera.*

component CameraView {
    use camera()

    view {
        VStack {
            CameraPreview(session: camera.session)
                .aspectRatio(4/3, contentMode: .fit)

            Button("Capture") {
                async {
                    val photo = await camera.capturePhoto()
                    imageCache.store(photo)
                }
            }
        }
    }
}
```

### Video Recording

```i
component VideoRecorder {
    use camera(mode: .video)

    var isRecording = state(false)

    fun startRecording() {
        async {
            await camera.startVideoRecording(
                quality: .hd1920x1080,
                fps: 30,
                micEnabled: true
            )
            isRecording.value = true
        }
    }

    fun stopRecording() {
        async {
            val video = await camera.stopVideoRecording()
            saveToGallery(video)
            isRecording.value = false
        }
    }
}
```

### Camera Preview Customization

```i
component CustomCameraPreview {
    use camera()

    view {
        ZStack {
            CameraPreview(
                session: camera.session,
                gravity: .resizeAspectFill
            )
            .overlay {
                ViewfinderGrid()
                FocusIndicator(position: $focusPoint)
            }

            VStack {
                Spacer()
                HStack {
                    Button("Flash: \(camera.flashMode)") {
                        camera.toggleFlash()
                    }
                    Spacer()
                    Button("Flip") { camera.switchCamera() }
                }
                .padding()
            }
        }
    }

    onTap { location in
        camera.setFocusPoint(location)
    }
}
```

### API Reference

| Method | Description |
|--------|-------------|
| `camera.capturePhoto()` | Captures a single photo, returns `Photo` |
| `camera.startVideoRecording(options)` | Starts video recording |
| `camera.stopVideoRecording()` | Stops recording, returns `VideoFile` |
| `camera.switchCamera()` | Toggles between front/back cameras |
| `camera.setZoom(level)` | Sets zoom level (1.0 = normal) |
| `camera.setFlash(mode)` | Sets flash mode: `.auto`, `.on`, `.off` |
| `camera.setFocusPoint(point)` | Sets focus/exposure point |
| `camera.supportsCamera(cameraType)` | Checks if specific camera is available |

## Microphone

### Audio Recording

```i
import device.microphone.*

component AudioRecorder {
    use microphone()

    var recordingTime = state(0)
    var timer: Timer? = null

    fun startRecording() {
        async {
            val granted = await permissions.request("microphone")
            if (granted) {
                microphone.startRecording(
                    format: .aac,
                    sampleRate: 44100,
                    bitRate: 128000
                )
                startTimer()
            }
        }
    }

    fun stopRecording() {
        val audio = microphone.stopRecording()
        stopTimer()
    }
}
```

### Audio Streaming

```i
component AudioStreamer {
    use microphone()

    fun startStreaming() {
        microphone.streamAudio { buffer, timestamp ->
            wsClient.send(
                AudioPacket(
                    data: buffer.toBase64(),
                    timestamp: timestamp
                )
            )
        }
    }
}
```

### API Reference

| Method | Description |
|--------|-------------|
| `microphone.startRecording(options)` | Start recording audio to file |
| `microphone.stopRecording()` | Stop recording, returns `AudioFile` |
| `microphone.streamAudio(callback)` | Stream raw audio data in real-time |
| `microphone.isRecording` | Current recording state |
| `microphone.hasPermission` | Whether mic permission is granted |
| `microphone.audioLevel` | Current input level (0.0 - 1.0) |

## GPS / Location

### Location Updates

```i
import device.location.*

component LocationTracker {
    use location()

    val currentPosition = state<Position>(null)

    fun startTracking() {
        async {
            val granted = await permissions.request("location")
            if (granted) {
                location.requestUpdates(
                    accuracy: .high,        // .high, .balanced, .low
                    distanceFilter: 10.0,    // meters
                    interval: 5000           // ms
                ) { pos ->
                    currentPosition.value = pos
                }
            }
        }
    }

    fun stopTracking() {
        location.stopUpdates()
    }

    view {
        if (currentPosition.value != null) {
            Text("Lat: \(currentPosition.value.latitude)")
            Text("Lng: \(currentPosition.value.longitude)")
            Text("Accuracy: \(currentPosition.value.accuracy)m")
        }
    }
}
```

### Single Location Request

```i
fun getCurrentLocation() async -> Position? {
    return await location.requestSingle(
        accuracy: .balanced,
        timeout: 10000
    )
}
```

### Geocoding

```i
component GeocoderDemo {
    use location()

    // Forward geocoding (address -> coordinates)
    fun geocodeAddress(address: String) {
        async {
            val results = await location.geocode(address)
            if (results.isNotEmpty()) {
                val place = results.first()
                map.centerAt(place.latitude, place.longitude)
            }
        }
    }

    // Reverse geocoding (coordinates -> address)
    fun reverseGeocode(lat: Double, lng: Double) {
        async {
            val address = await location.reverseGeocode(lat, lng)
            showAddress(address.street, address.city)
        }
    }

    // Region monitoring
    fun monitorRegion() {
        location.startMonitoring(
            region: CircleRegion(
                center: Position(40.7128, -74.0060),
                radius: 100.0 // meters
            )
        ) { event ->
            when (event) {
                .enter -> showNotification("Welcome to NYC!")
                .exit -> showNotification("Left NYC")
            }
        }
    }
}
```

### API Reference

| Method | Description |
|--------|-------------|
| `location.requestUpdates(options)` | Start continuous location updates |
| `location.stopUpdates()` | Stop location updates |
| `location.requestSingle(options)` | Get current position once |
| `location.geocode(address)` | Convert address to coordinates |
| `location.reverseGeocode(lat, lng)` | Convert coordinates to address |
| `location.startMonitoring(region)` | Geofence region monitoring |
| `location.stopMonitoring(region)` | Stop monitoring a region |
| `location.headingUpdates(callback)` | Start compass heading updates |
| `location.isGPSEnabled` | Whether GPS is enabled on device |

## Biometrics

### Fingerprint Authentication

```i
import device.biometrics.*

component LoginScreen {
    use biometrics()

    fun authenticateWithBiometrics() {
        async {
            val result = await biometrics.authenticate(
                reason: "Log in to access your account",
                fallback: .passcode, // .passcode, .none, .custom
                options: [
                    .requireConfirmation: true,
                    .localizedCancelTitle: "Cancel",
                    .localizedFallbackTitle: "Use Passcode"
                ]
            )

            when (result) {
                .success -> navigateTo(HomeScreen())
                .failed(error) -> showError(error.message)
                .userCancel -> handleCancel()
                .notAvailable -> showPinEntry()
            }
        }
    }
}
```

### Face Authentication

```i
component SecureAction {
    use biometrics()

    fun authorizePayment(amount: Double) {
        async {
            val biometricType = await biometrics.availableTypes()
            // biometricType could be .faceID, .touchID, .fingerprint

            val result = await biometrics.authenticate(
                reason: "Confirm payment of $\(amount)",
                options: [.requireConfirmation: false]
            )

            if (result == .success) {
                processPayment(amount)
            }
        }
    }
}
```

### Biometric Key Storage

```i
component SecureStorage {
    use biometrics()
    use keychain()

    fun storeWithBiometric(key: String, value: String) {
        keychain.store(
            key: key,
            value: value,
            accessControl: .biometryCurrentSet,
            authentication: .userPresence
        )
    }

    fun retrieveWithBiometric(key: String) async -> String? {
        return await keychain.retrieve(
            key: key,
            authentication: .userPresence
        )
    }
}
```

### API Reference

| Method | Description |
|--------|-------------|
| `biometrics.authenticate(options)` | Authenticate user via biometrics |
| `biometrics.availableTypes()` | Returns supported biometric types |
| `biometrics.canAuthenticate()` | Whether biometric auth is available |
| `biometrics.isEnrolled()` | Whether user has enrolled biometrics |
| `biometrics.setAllowDeviceCredential(allow)` | Allow passcode fallback |

## Push Notifications

### Local Notifications

```i
import device.notifications.*

component LocalNotificationDemo {
    use notifications()

    fun scheduleLocal() {
        notifications.requestPermission { granted ->
            if (granted) {
                notifications.schedule(
                    Notification(
                        id: "reminder-1",
                        title: "Coffee Time!",
                        body: "Time for your afternoon break",
                        sound: .default,
                        badge: 1,
                        category: "reminder"
                    ),
                    trigger: TimeIntervalTrigger(
                        interval: 3600, // 1 hour
                        repeats: true
                    )
                )
            }
        }
    }

    fun scheduleCalendarNotification() {
        notifications.schedule(
            Notification(
                id: "meeting-1",
                title: "Team Standup",
                body: "Daily standup in 5 minutes",
                category: "meeting"
            ),
            trigger: CalendarTrigger(
                dateComponents: DateComponents(
                    hour: 9, minute: 30, weekday: 2 // Monday 9:30
                ),
                repeats: true
            )
        )
    }
}
```

### Remote Push Notifications

```i
component PushHandler {
    use notifications()

    // Register for remote notifications
    fun register() {
        notifications.registerForRemote { token, error ->
            if (token != null) {
                sendTokenToServer(token)
            }
        }
    }

    // Handle incoming push
    onNotificationReceived { notification ->
        when (notification.category) {
            "message" -> {
                val sender = notification.payload["sender"]
                val text = notification.payload["text"]
                showMessageNotification(sender, text)
            }
            "order" -> {
                val status = notification.payload["status"]
                updateOrderStatus(status)
            }
        }
    }

    // Handle notification tap
    onNotificationOpened { notification ->
        navigateTo(notification.payload["screen"])
    }

    // Notification actions
    onNotificationAction { action, notification ->
        when (action.id) {
            "reply" -> openReplyView(notification)
            "mark_read" -> markAsRead(notification.payload["id"])
            "dismiss" -> dismiss(notification)
        }
    }
}
```

### Notification Categories & Actions

```i
fun setupNotificationCategories() {
    notifications.setCategories([
        NotificationCategory(
            id: "message",
            actions: [
                NotificationAction(
                    id: "reply",
                    title: "Reply",
                    options: [.foreground, .authenticationRequired]
                ),
                NotificationAction(
                    id: "dismiss",
                    title: "Dismiss",
                    options: [.destructive]
                )
            ]
        )
    ])
}
```

### API Reference

| Method | Description |
|--------|-------------|
| `notifications.schedule(notification, trigger)` | Schedule a local notification |
| `notifications.cancel(id)` | Cancel a pending notification |
| `notifications.cancelAll()` | Cancel all pending notifications |
| `notifications.getDelivered()` | Get currently displayed notifications |
| `notifications.removeDelivered(id)` | Remove a delivered notification |
| `notifications.registerForRemote(callback)` | Register for remote push |
| `notifications.setCategories(categories)` | Define notification action categories |
| `notifications.requestPermission(callback)` | Request notification permission |

## Sensors

### Accelerometer

```i
import device.sensors.*

component ShakeDetector {
    use accelerometer()

    fun start() {
        accelerometer.startUpdates(interval: 100) { data ->
            val magnitude = sqrt(
                data.x * data.x +
                data.y * data.y +
                data.z * data.z
            )
            if (magnitude > 3.0) {
                onShake()
            }
        }
    }

    fun stop() {
        accelerometer.stopUpdates()
    }
}
```

### Gyroscope

```i
component GyroController {
    use gyroscope()

    fun startTracking() {
        gyroscope.startUpdates(interval: 50) { data ->
            // data.rotationRateX, .rotationRateY, .rotationRateZ
            update3DModel(
                pitch: data.x,
                yaw: data.y * -1,
                roll: data.z
            )
        }
    }
}
```

### Magnetometer

```i
component CompassView {
    use magnetometer()

    val heading = state(0.0)

    fun start() {
        magnetometer.startUpdates(interval: 200) { data ->
            // Calculate heading from magnetic field
            heading.value = calculateHeading(data.x, data.y)
        }
    }

    view {
        Text("Heading: \(heading.value)°")
            .rotationEffect(Angle.degrees(heading.value))
    }
}
```

### Combined Sensor Usage

```i
component StepCounter {
    use accelerometer()
    use pedometer()

    val stepCount = state(0)

    fun startCounting() {
        // Use pedometer for step counts (more accurate)
        pedometer.startUpdates { count, distance, pace ->
            stepCount.value = count
        }

        // Use accelerometer for fall detection
        accelerometer.startUpdates(interval: 50) { data ->
            val magnitude = sqrt(data.x^2 + data.y^2 + data.z^2)
            if (magnitude > 5.0) {
                detectFall()
            }
        }
    }
}
```

### API Reference

| Sensor | Method | Description |
|--------|--------|-------------|
| Accelerometer | `startUpdates(interval, callback)` | Motion data (m/s²) |
| | `stopUpdates()` | Stop accelerometer |
| Gyroscope | `startUpdates(interval, callback)` | Rotation rate (rad/s) |
| | `stopUpdates()` | Stop gyroscope |
| Magnetometer | `startUpdates(interval, callback)` | Magnetic field (μT) |
| | `stopUpdates()` | Stop magnetometer |
| Pedometer | `startUpdates(callback)` | Step count, distance, pace |
| | `stopUpdates()` | Stop pedometer |
| Barometer | `startUpdates(interval, callback)` | Pressure, altitude |
| | `stopUpdates()` | Stop barometer |
| Ambient Light | `read()` | Current lux value |
| Proximity | `startUpdates(callback)` | Near/far detection |

## Battery

```i
import device.battery.*

component BatteryMonitor {
    use battery()

    val level = state(0)
    val isCharging = state(false)

    fun startMonitoring() {
        battery.startMonitoring()
        battery.onBatteryStateChanged { info ->
            level.value = info.level // 0-100
            isCharging.value = info.isCharging
            if (info.level < 20 && !info.isCharging) {
                showLowBatteryWarning()
            }
        }
    }
}
```

### API Reference

| Method | Description |
|--------|-------------|
| `battery.startMonitoring()` | Begin battery monitoring |
| `battery.stopMonitoring()` | Stop battery monitoring |
| `battery.level` | Current battery level (0-100) |
| `battery.isCharging` | Whether device is charging |
| `battery.state` | `.unknown`, `.unplugged`, `.charging`, `.full` |
| `battery.lowPowerMode` | Whether Low Power Mode is enabled |

## Storage

```i
import device.storage.*

component StorageManager {
    use storage()

    val used = state("")
    val free = state("")

    fun checkStorage() {
        val info = storage.getStorageInfo()
        used.value = formatBytes(info.usedBytes)
        free.value = formatBytes(info.freeBytes)
    }

    fun getAppCacheSize() async -> Long {
        return await storage.getCacheSize()
    }

    fun clearCache() async {
        await storage.clearCache()
    }

    fun getFile(path: String) -> File {
        return storage.getFile(path)
    }

    fun saveToDocuments(filename: String, data: ByteArray) {
        val file = storage.documentsDirectory
            .appendPath(filename)
        file.writeBytes(data)
    }
}
```

### API Reference

| Method | Description |
|--------|-------------|
| `storage.getStorageInfo()` | Total, used, free space |
| `storage.getCacheSize()` | App cache size in bytes |
| `storage.clearCache()` | Clear app cache |
| `storage.documentsDirectory` | App documents directory path |
| `storage.cacheDirectory` | App cache directory path |
| `storage.tempDirectory` | Temporary directory path |
| `storage.getExternalStorage()` | External SD card (Android) |

## Connectivity

```i
import device.connectivity.*

component NetworkMonitor {
    use connectivity()

    val status = state<NetworkStatus>(null)

    fun startMonitoring() {
        connectivity.startMonitoring { info ->
            status.value = info.status // .wifi, .cellular, .none
            if (info.status == .wifi) {
                syncPendingData()
            }
        }
    }

    fun checkConnection() async -> Boolean {
        return await connectivity.isConnected()
    }
}
```

### API Reference

| Method | Description |
|--------|-------------|
| `connectivity.startMonitoring(callback)` | Monitor network changes |
| `connectivity.stopMonitoring()` | Stop monitoring |
| `connectivity.isConnected()` | Check if online |
| `connectivity.currentStatus` | Current network status |
| `connectivity.isCellular` | Currently on cellular |
| `connectivity.isWifi` | Currently on WiFi |
| `connectivity.isVpnConnected` | Whether VPN is active |
| `connectivity.connectionType` | `.wifi`, `.cellular`, `.ethernet`, `.none` |

## NFC

```i
import device.nfc.*

component NFCDemo {
    use nfc()

    fun startScanning() {
        async {
            val granted = await permissions.request("nfc")
            if (granted && nfc.isAvailable) {
                nfc.startSession(
                    message: "Hold near NFC tag",
                    callback: { tag ->
                        when (tag.type) {
                            .ndef -> {
                                val records = tag.readNdefRecords()
                                for (record in records) {
                                    processNdef(record)
                                }
                            }
                            .isoDep -> {
                                val data = tag.transceive(apduCommand)
                                processResponse(data)
                            }
                        }
                    }
                )
            }
        }
    }

    fun writeTag() {
        nfc.write(
            NdefMessage(
                records: [
                    NdefRecord.text("Hello, NFC!"),
                    NdefRecord.uri("https://example.com")
                ]
            ),
            callback: { success ->
                if (success) showToast("Tag written!")
            }
        )
    }

    fun stopScanning() {
        nfc.stopSession()
    }
}
```

### API Reference

| Method | Description |
|--------|-------------|
| `nfc.isAvailable` | Whether device supports NFC |
| `nfc.isEnabled` | Whether NFC is enabled on device |
| `nfc.startSession(options, callback)` | Start NFC tag reading |
| `nfc.stopSession()` | Stop NFC session |
| `nfc.write(message, callback)` | Write NDEF message to tag |
| `nfc.readNdefRecords(tag)` | Parse NDEF records from tag |

## Bluetooth

```i
import device.bluetooth.*

component BluetoothDemo {
    use bluetooth()

    fun scanDevices() {
        async {
            val granted = await permissions.request("bluetooth")
            if (granted) {
                bluetooth.startScanning(
                    services: ["180D"], // Heart rate service UUID
                    timeout: 10000
                ) { device ->
                    addDeviceToList(device)
                }
            }
        }
    }

    fun connect(device: BLEDevice) {
        async {
            bluetooth.connect(device)
            bluetooth.discoverServices()
            val service = bluetooth.getService("180D")
            val characteristic = service?.getCharacteristic("2A37")
            characteristic?.notify { value ->
                val heartRate = value[1].toInt()
                updateHeartRate(heartRate)
            }
        }
    }

    // Classic Bluetooth
    fun sendData(data: ByteArray) {
        bluetooth.write(
            data: data,
            type: .withResponse
        )
    }
}
```

### API Reference

| Method | Description |
|--------|-------------|
| `bluetooth.startScanning(options, callback)` | Start discovering BLE devices |
| `bluetooth.stopScanning()` | Stop scanning |
| `bluetooth.connect(device)` | Connect to a BLE device |
| `bluetooth.disconnect()` | Disconnect current device |
| `bluetooth.discoverServices()` | Discover services on connected device |
| `bluetooth.getService(uuid)` | Get service by UUID |
| `bluetooth.getCharacteristic(uuid)` | Get characteristic by UUID |
| `bluetooth.write(data, type)` | Write data to device |
| `bluetooth.read()` | Read data from device |
| `bluetooth.isBluetoothEnabled` | Whether BT is on |
| `bluetooth.isConnected` | Whether device is connected |

## Calendar

```i
import device.calendar.*

component CalendarDemo {
    use calendar()

    fun addEvent() {
        async {
            val granted = await permissions.request("calendar")
            if (granted) {
                val event = CalendarEvent(
                    title: "Team Meeting",
                    startDate: DateTime(2026, 7, 30, 10, 0),
                    endDate: DateTime(2026, 7, 30, 11, 0),
                    location: "Conference Room A",
                    notes: "Weekly sync",
                    isAllDay: false,
                    recurrence: .weekly
                )
                try {
                    val eventId = await calendar.addEvent(event)
                    showToast("Event created!")
                } catch (e: CalendarException) {
                    showError(e.message)
                }
            }
        }
    }

    fun queryEvents() async -> [CalendarEvent] {
        val startOfDay = DateTime.now().startOfDay()
        val endOfWeek = DateTime.now().endOfWeek()
        return await calendar.queryEvents(
            startDate: startOfDay,
            endDate: endOfWeek,
            calendars: null // All calendars
        )
    }
}
```

### API Reference

| Method | Description |
|--------|-------------|
| `calendar.requestPermission()` | Request calendar access |
| `calendar.getCalendars()` | List available calendars |
| `calendar.addEvent(event)` | Create new event |
| `calendar.updateEvent(event)` | Update existing event |
| `calendar.deleteEvent(eventId)` | Delete an event |
| `calendar.queryEvents(options)` | Query events in date range |
| `calendar.getEvent(eventId)` | Get event by ID |
| `calendar.openEventInApp(eventId)` | Open in system calendar app |

## Contacts

```i
import device.contacts.*

component ContactPicker {
    use contacts()

    fun pickContact() {
        async {
            val granted = await permissions.request("contacts")
            if (granted) {
                val contact = await contacts.pickContact()
                if (contact != null) {
                    displayContact(contact)
                }
            }
        }
    }

    fun addContact() {
        async {
            val contact = Contact(
                givenName: "John",
                familyName: "Doe",
                phoneNumbers: [
                    PhoneNumber(label: "mobile", number: "+1234567890")
                ],
                emailAddresses: [
                    EmailAddress(label: "work", address: "john@example.com")
                ],
                postalAddresses: [
                    PostalAddress(
                        street: "123 Main St",
                        city: "New York",
                        state: "NY",
                        postalCode: "10001",
                        country: "USA"
                    )
                ]
            )
            try {
                await contacts.addContact(contact)
            } catch (e: ContactException) {
                handleError(e)
            }
        }
    }

    fun searchContacts(query: String) async -> [Contact] {
        return await contacts.search(name: query)
    }
}
```

### API Reference

| Method | Description |
|--------|-------------|
| `contacts.requestPermission()` | Request contacts access |
| `contacts.getAll()` | Fetch all contacts |
| `contacts.search(options)` | Search contacts by name/phone/email |
| `contacts.getContact(id)` | Get contact by ID |
| `contacts.addContact(contact)` | Create new contact |
| `contacts.updateContact(contact)` | Update existing contact |
| `contacts.deleteContact(id)` | Delete a contact |
| `contacts.pickContact()` | Open system contact picker |
| `contacts.groups` | Access contact groups |

## Permission Management

### Requesting Permissions

```i
// Request single permission
async {
    val granted = await permissions.request("camera")
    if (granted) {
        initializeCamera()
    }
}

// Request multiple permissions
async {
    val results = await permissions.requestMany([
        "camera",
        "microphone",
        "location"
    ])
    if (results.allGranted()) {
        startRecording()
    }
}

// Check permission status
val status = permissions.check("location")
when (status) {
    .granted -> startTracking()
    .denied -> showPermissionPrompt()
    .restricted -> showSettingsRedirect()
    .notDetermined -> requestPermission()
}
```

### Rationale Dialog

```i
permissions.request(
    "location",
    rationale: "We need location access to show nearby restaurants"
) { granted ->
    if (granted) {
        showNearbyPlaces()
    }
}
```

---

## Error Handling

All device APIs follow a consistent error handling pattern:

```i
async {
    try {
        val result = await camera.capturePhoto()
        processPhoto(result)
    } catch (e: DeviceError) {
        when (e) {
            is PermissionDenied -> showPermissionSettings()
            is DeviceNotAvailable -> showFeatureNotSupported()
            is TimeoutError -> retryOperation()
            else -> showGenericError(e.message)
        }
    }
}
```

## Best Practices

1. **Always check permissions** before accessing device features
2. **Clean up resources** — stop sensors, cameras, and location when not needed
3. **Handle feature unavailability** gracefully (e.g., no NFC, no biometrics)
4. **Use appropriate accuracy** — request only what you need to conserve battery
5. **Batch operations** where possible (e.g., calendar queries vs. multiple calls)
6. **Test on real devices** — simulators/emulators have limited sensor support
7. **Respect privacy** — explain why you need each permission
