# Security Reference

## Overview

The I Language provides security primitives covering device integrity, data protection, network security, and runtime permissions, aligned with OWASP Mobile Top 10 best practices.

---

## Root / Jailbreak Detection

### Detecting Root (Android)

[source,i]
----
import security.integrity.*

component RootDetector {
    use integrity()

    fun checkRootStatus() {
        when (integrity.rootStatus()) {
            .rooted -> {
                analytics.track("rooted_device")
                showSecurityWarning()
                maybeBlockAccess()
            }
            .suspicious -> {
                log("Suspicious root indicators")
                enableExtraChecks()
            }
            .secure -> {
                // Device is secure
            }
        }
    }

    fun additionalChecks(): Boolean {
        val checks = listOf(
            integrity.checkBinary("su"),
            integrity.checkBinary("busybox"),
            integrity.checkPath("/system/app/Superuser.apk"),
            integrity.checkProperty("ro.debuggable", "1"),
            integrity.checkBuildTags("test-keys"),
            integrity.checkPackage("com.thirdparty.superuser")
        )
        return checks.any { it }
    }
}
----

### Detecting Jailbreak (iOS)

[source,i]
----
component JailbreakDetector {
    use integrity()

    fun checkJailbreak() {
        val isJailbroken = integrity.checkURLScheme("cydia") ||
            integrity.checkFileExists("/Applications/Cydia.app") ||
            integrity.checkFileExists("/Library/MobileSubstrate") ||
            integrity.checkFileExists("/bin/bash") ||
            integrity.checkFileExists("/usr/sbin/sshd")

        if (isJailbroken) {
            handleJailbreak()
        }
    }
}
----

### Defense Strategy

- Run checks at app startup and periodically
- Never block immediately (avoid giving attackers a signal)
- Use multiple obfuscated checks
- Fail gracefully with a generic error
- Report to backend analytics for monitoring

---

## Certificate Pinning

### Configuration

[source,json]
----
{
  "security": {
    "certificatePinning": {
      "enabled": true,
      "pins": [
        {
          "host": "api.example.com",
          "sha256": "KL8r4a...base64hash...",
          "backupPin": "E9b3c...base64hash..."
        },
        {
          "host": "auth.example.com",
          "sha256": "F7a2d...base64hash..."
        }
      ],
      "includeSubdomains": true,
      "expirationDays": 180
    }
  }
}
----

### Programmatic Pinning

[source,i]
----
import security.network.*

component SecureClient {
    use sslPinning()

    val apiClient = httpClient {
        sslPinning.pin(
            host = "api.example.com",
            pins = [
                Pin(algorithm: .sha256, hash: "KL8r4a..."),
                Pin(algorithm: .sha256, hash: "E9b3c...")
            ],
            policy = .strict   // .strict, .report, .disable
        )
    }

    // Report-only mode for gradual rollout
    val reportClient = httpClient {
        sslPinning.pin(
            host = "new-api.example.com",
            policy = .report  // Log violations but allow
        ) { violation ->
            analytics.track("pinning_violation", {
                host: violation.host,
                hash: violation.receivedHash
            })
        }
    }
}
----

### Preloading Pins

[source,i]
----
fun setupPins() {
    // Preload from remote config for emergency pin updates
    async {
        val remotePins = await configService.getPins()
        sslPinning.updatePins(remotePins)
    }
}
----

### API Reference

| Method | Description |
|--------|-------------|
| sslPinning.pin(options) | Pin certificate for host |
| sslPinning.unpin(host) | Remove pin for host |
| sslPinning.updatePins(pins) | Update pins from config |
| sslPinning.getPins() | Get current pins |
| sslPinning.isValid(host, cert) | Check certificate validity |

---

## Secure Storage

### Encrypted Preferences

[source,i]
----
import security.storage.*

component SecureStorageDemo {
    use secureStorage()

    fun storeCredentials() {
        secureStorage.store(
            key: "auth_token",
            value: "eyJhbGciOiJIUzI1NiIs...",
            encryption: .aes256_gcm,
            authentication: .biometryRequired
        )
    }

    fun retrieveCredentials() async -> String? {
        return await secureStorage.retrieve(
            key: "auth_token",
            authentication: .biometryRequired
        )
    }

    fun deleteCredentials() {
        secureStorage.delete("auth_token")
    }
}
----

### Keychain / EncryptedSharedPreferences

[source,i]
----
component KeychainDemo {
    use keychain()

    // iOS: Uses Keychain Services
    // Android: Uses EncryptedSharedPreferences

    fun saveAPIKey() {
        keychain.set(
            key: "api_key",
            value: "sk-abc123",
            accessibility: .whenUnlockedThisDeviceOnly,
            service: "com.example.myapp.api"
        )
    }

    fun getAPIKey() -> String? {
        return keychain.get("api_key")
    }

    // Store binary data
    fun savePrivateKey(key: PrivateKey) {
        keychain.setData(
            key: "private_key",
            data: key.encoded,
            accessibility: .afterFirstUnlock
        )
    }
}
----

### File Encryption

[source,i]
----
component FileEncryption {
    use encryption()

    fun encryptFile(path: String) {
        val plaintext = fileSystem.readBytes(path)
        val encrypted = encryption.encrypt(
            data: plaintext,
            algorithm: .aes256_gcm,
            key: encryptionKey
        )
        fileSystem.writeBytes(path + ".enc", encrypted)
    }

    fun decryptFile(path: String): ByteArray {
        val encrypted = fileSystem.readBytes(path)
        return encryption.decrypt(
            data: encrypted,
            algorithm: .aes256_gcm,
            key: encryptionKey
        )
    }
}
----

### API Reference

| Method | Description |
|--------|-------------|
| secureStorage.store(key, value, opts) | Store encrypted value |
| secureStorage.retrieve(key, opts) | Retrieve encrypted value |
| secureStorage.delete(key) | Delete stored value |
| secureStorage.containsKey(key) | Check if key exists |
| secureStorage.clear() | Delete all stored values |
| keychain.set(key, value, opts) | Store in OS keychain |
| keychain.get(key) | Retrieve from OS keychain |
| encryption.encrypt(data, algorithm, key) | Encrypt data |
| encryption.decrypt(data, algorithm, key) | Decrypt data |

---

## Encryption

### Symmetric Encryption

[source,i]
----
component SymmetricEncryption {
    use encryption()

    fun encryptMessage(plaintext: String, key: SecretKey): String {
        val encrypted = encryption.aesEncrypt(
            data: plaintext.toByteArray(),
            key: key,
            mode: .gcm,         // GCM, CBC, CTR
            padding: .pkcs7,
            iv: generateIV()    // Auto-generated if not provided
        )
        return encrypted.toBase64()
    }

    fun decryptMessage(ciphertext: String, key: SecretKey): String {
        val decrypted = encryption.aesDecrypt(
            data: ciphertext.fromBase64(),
            key: key,
            mode: .gcm
        )
        return String(decrypted)
    }
}
----

### Asymmetric Encryption

[source,i]
----
component AsymmetricEncryption {
    use encryption()

    val keyPair = encryption.generateKeyPair(
        algorithm: .rsa,
        keySize: 2048
    )

    fun encryptWithPublicKey(data: ByteArray): ByteArray {
        return encryption.rsaEncrypt(
            data: data,
            publicKey: keyPair.public,
            padding: .oaep_sha256
        )
    }

    fun decryptWithPrivateKey(encrypted: ByteArray): ByteArray {
        return encryption.rsaDecrypt(
            data: encrypted,
            privateKey: keyPair.private,
            padding: .oaep_sha256
        )
    }
}
----

### Hashing

[source,i]
----
fun hashPassword(password: String): String {
    val salt = encryption.generateSalt(32)
    val hash = encryption.hash(
        data: password.toByteArray(),
        algorithm: .argon2id,
        salt: salt,
        iterations: 3,
        memory: 65536,    // 64 MB
        parallelism: 4
    )
    return salt.toHex() + ":" + hash.toHex()
}

fun verifyPassword(password: String, stored: String): Boolean {
    val parts = stored.split(":")
    val salt = parts[0].fromHex()
    val expectedHash = parts[1].fromHex()
    val actualHash = encryption.hash(
        data: password.toByteArray(),
        algorithm: .argon2id,
        salt: salt,
        iterations: 3,
        memory: 65536,
        parallelism: 4
    )
    return encryption.constantTimeEquals(expectedHash, actualHash)
}
----

### Key Generation & Management

[source,i]
----
component KeyManager {
    use encryption()

    // Generate key
    val secretKey = encryption.generateKey(
        algorithm: .aes,
        keySize: 256
    )

    // Derived key from password
    val derivedKey = encryption.deriveKey(
        password: userPassword,
        salt: storedSalt,
        algorithm: .pbkdf2_sha256,
        iterations: 100000,
        keyLength: 256
    )

    // Store securely
    fun saveKey(alias: String, key: SecretKey) {
        encryption.storeKey(
            alias: alias,
            key: key,
            accessLevel: .biometryRequired
        )
    }

    fun loadKey(alias: String) async -> SecretKey? {
        return await encryption.loadKey(alias)
    }
}
----

### API Reference

| Algorithm | Method | Key Size |
|-----------|--------|----------|
| AES-GCM | esEncrypt, esDecrypt | 128, 192, 256 |
| RSA-OAEP | saEncrypt, saDecrypt | 2048, 4096 |
| Argon2id | hash | Salt: 16-32 bytes |
| PBKDF2 | deriveKey | Iterations: 100k+ |
| HMAC-SHA256 | hmac | Key: 32 bytes |
| HKDF | hkdfExpand | Varies |

---

## App Integrity

### Android Play Integrity

[source,i]
----
import security.integrity.*

component PlayIntegrity {
    use playIntegrity()

    fun verifyIntegrity() {
        async {
            val result = await playIntegrity.verify(
                nonce: generateNonce(),
                cloudProject: 123456789  // Google Cloud project #
            )

            when (result) {
                is IntegrityResult.Valid -> {
                    val deviceState = result.deviceState
                    // .meetsDeviceIntegrity, .meetsBasicIntegrity
                    // .hasStrongVerification
                    log("Device integrity: ")
                }
                is IntegrityResult.Invalid -> {
                    log("Integrity check failed: ")
                    showBlockScreen()
                }
                is IntegrityResult.Error -> {
                    log("Integrity error: ")
                    // Don't block — could be network issue
                }
            }
        }
    }
}
----

### iOS App Attest

[source,i]
----
import security.integrity.*

component AppAttest {
    use appAttest()

    fun attestKey() {
        async {
            val keyId = await appAttest.generateKey()
            val challenge = server.getAttestChallenge()

            val attestation = await appAttest.attestKey(
                keyId: keyId,
                challenge: challenge
            )

            // Send attestation to server for verification
            server.verifyAttestation(attestation)
        }
    }

    fun assertChallenge() {
        async {
            val challenge = server.getAssertionChallenge()
            val keyId = appAttest.storedKeyId

            val assertion = await appAttest.generateAssertion(
                keyId: keyId,
                challenge: challenge
            )

            server.verifyAssertion(assertion)
        }
    }
}
----

### App Integrity API Reference

| Method | Platform | Description |
|--------|----------|-------------|
| playIntegrity.verify(options) | Android | Google Play Integrity check |
| ppAttest.generateKey() | iOS | Generate attestation key |
| ppAttest.attestKey(keyId) | iOS | Attest key with Apple |
| ppAttest.generateAssertion(kid) | iOS | Assert key for challenge |
| integrity.rootStatus() | Both | Check root/jailbreak |
| integrity.checkBinary(name) | Both | Check if binary exists |
| integrity.checkSignature() | Android | Verify APK signature |
| integrity.verifyEnvironment() | Both | Comprehensive check |

---

## Runtime Permission Management

### Request Pattern

[source,i]
----
import security.permissions.*

component PermissionManager {
    use permissions()

    fun requestCamera() {
        val status = permissions.check("android.permission.CAMERA")
        // or: permissions.check("ios.camera")

        when (status) {
            .granted -> openCamera()
            .denied -> {
                // First denial — show rationale
                if (permissions.shouldShowRationale("camera")) {
                    showDialog(
                        title: "Camera Access Needed",
                        message: "We need camera access to scan documents",
                        onConfirm: { permissions.request("camera") }
                    )
                } else {
                    // Permanently denied — redirect to settings
                    showSettingsDialog()
                }
            }
            .notDetermined -> {
                permissions.request("camera") { granted ->
                    if (granted) openCamera()
                }
            }
            .restricted -> {
                // Parental controls, device policy
                showRestrictedMessage()
            }
        }
    }
}
----

### Multiple Permissions

[source,i]
----
fun requestMultiple() {
    async {
        val results = await permissions.requestMany([
            "camera",
            "microphone",
            "location"
        ], rationale: "These permissions are needed for video recording")

        if (results.allGranted()) {
            startRecording()
        } else {
            val denied = results.denied
            showMissingPermissions(denied)
        }
    }
}
----

### Permission Groups

[source,i]
----
// Define permission groups
val locationGroup = PermissionGroup(
    id: "location",
    permissions: ["location"],
    title: "Location Access",
    description: "Used to show nearby places",
    icon: .mapPin
)

fun requestGroup(group: PermissionGroup) {
    permissions.requestGroup(group) { result ->
        if (result.granted) {
            group.onGranted()
        }
    }
}
----

### API Reference

| Method | Description |
|--------|-------------|
| permissions.check(permission) | Check permission status |
| permissions.request(permission, cb) | Request single permission |
| permissions.requestMany(perms) | Request multiple permissions |
| permissions.requestGroup(group) | Request permission group |
| permissions.shouldShowRationale(perm) | Whether to show rationale |
| permissions.openSettings() | Open app settings |
| permissions.getGranted() | List granted permissions |
| permissions.getDenied() | List denied permissions |

---

## Network Security

### TLS Configuration

[source,i]
----
component SecureNetwork {
    use networkSecurity()

    val secureClient = httpClient {
        networkSecurity.apply {
            minimumTlsVersion(.tls12)
            // or .tls13

            ciphers([
                .tls_aes_256_gcm_sha384,
                .tls_aes_128_gcm_sha256,
                .tls_chacha20_poly1305_sha256
            ])

            // Disable weak ciphers
            excludeCiphers([
                .tls_rsa_with_aes_128_cbc_sha,
                .tls_rsa_with_3des_ede_cbc_sha
            ])
        }
    }
}
----

### Network Security Config (Android)

[source,xml]
----
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Production: pin certs, deny cleartext -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2027-01-01">
            <pin digest="SHA-256">KL8r4a...base64...=</pin>
            <pin digest="SHA-256">E9b3c...base64...=</pin>
        </pin-set>
    </domain-config>

    <!-- Debug: allow localhost -->
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">localhost</domain>
        <domain includeSubdomains="true">10.0.2.2</domain>
    </domain-config>
</network-security-config>
----

### ATS (iOS)

[source,xml]
----
<!-- Info.plist -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>api.example.com</key>
        <dict>
            <key>NSIncludesSubdomains</key>
            <true/>
            <key>NSTemporaryExceptionMinimumTLSVersion</key>
            <string>TLSv1.2</string>
        </dict>
    </dict>
</dict>
----

### End-to-End Encryption

[source,i]
----
component E2EEChat {
    use encryption()

    // Generate ephemeral key per conversation
    fun sendEncryptedMessage(recipientId: String, text: String) {
        val recipientPublicKey = keyStore.getPublicKey(recipientId)
        val ephemeralKey = encryption.generateEphemeralKey()
        val sharedSecret = encryption.ecdh(
            privateKey: ephemeralKey.private,
            publicKey: recipientPublicKey
        )
        val ciphertext = encryption.aesEncrypt(
            data: text.toByteArray(),
            key: sharedSecret,
            mode: .gcm
        )

        api.sendMessage(
            recipientId: recipientId,
            ephemeralPublicKey: ephemeralKey.public.encode(),
            ciphertext: ciphertext
        )
    }
}
----

---

## Data Privacy

### Minimization

[source,i]
----
// Collect only what you need
data class UserProfile(
    val id: String,
    val displayName: String,
    // NO: val email: String,
    // NO: val phoneNumber: String,
    // NO: val exactLocation: Position
)
----

### Data Classification

[source,i]
----
enum DataSensitivity {
    public,         // Username, avatar URL
    internal,       // Feature flags, preferences
    confidential,   // Email, name
    restricted      // Auth tokens, payment info, health data
}

@Sensitivity(DataSensitivity.confidential)
data class UserEmail(val address: String)

@Sensitivity(DataSensitivity.restricted)
data class AuthToken(val value: String)
----

### Deletion

[source,i]
----
fun deleteUserData(userId: String) {
    async {
        // Delete from local storage
        secureStorage.delete("user_\(userId)")
        localDatabase.deleteUser(userId)
        imageCache.deleteUserImages(userId)

        // Request deletion from server
        api.requestDataDeletion(userId)

        // Log deletion
        auditLog("Data deleted for user ")
    }
}
----

### Privacy Labels

[iOS Privacy Manifest]
[source,xml]
----
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSPrivacyTracking</key>
    <false/>
    <key>NSPrivacyCollectedDataTypes</key>
    <array>
        <dict>
            <key>NSPrivacyCollectedDataType</key>
            <string>NSPrivacyCollectedDataTypeName</string>
            <key>NSPrivacyCollectedDataTypeLinked</key>
            <true/>
            <key>NSPrivacyCollectedDataTypePurpose</key>
            <string>App Functionality</string>
        </dict>
    </array>
</dict>
</plist>
----

---

## OWASP Mobile Top 10 Coverage

| # | OWASP Category | I Security Feature |
|---|----------------|-------------------|
| M1 | Improper Platform Usage | Intents validated, URL schemes checked |
| M2 | Insecure Data Storage | Encrypted storage, keychain, file encryption |
| M3 | Insecure Communication | TLS 1.2+, cert pinning, ATS enforcement |
| M4 | Insecure Authentication | Biometric auth, session management |
| M5 | Insufficient Cryptography | AES-256-GCM, Argon2id, RSA-2048 |
| M6 | Insecure Authorization | Runtime permission model, scoped access |
| M7 | Client Code Quality | Static analysis, ProGuard, code obfuscation |
| M8 | Code Tampering | Play Integrity, App Attest, integrity checks |
| M9 | Reverse Engineering | ProGuard/R8, obfuscation, string encryption |
| M10 | Extraneous Functionality | Minification, unused code removal |

---

## Secure Development Checklist

### Code
- [ ] ProGuard/R8 enabled with proper rules
- [ ] No API keys or secrets in source code
- [ ] Logging does not expose sensitive data
- [ ] Deep link URLs validated before handling
- [ ] WebView JavaScript disabled unless required
- [ ] SQLite queries use parameterized statements

### Data
- [ ] All user data encrypted at rest
- [ ] Auth tokens stored in secure storage only
- [ ] Cache directory excluded from backups
- [ ] Clipboard access restricted for sensitive fields
- [ ] Screenshot blocking for sensitive screens

### Network
- [ ] TLS 1.2 minimum enforced
- [ ] Certificate pinning enabled for production
- [ ] No cleartext traffic in production
- [ ] API responses validated before use
- [ ] Custom URL schemes validated

### Permissions
- [ ] Only request permissions when needed
- [ ] Show rationale before requesting
- [ ] Handle denial gracefully
- [ ] Respect revoked permissions at runtime

### Distribution
- [ ] Debuggable=false in release builds
- [ ] Backup=false in manifest
- [ ] AllowBackup configured properly
- [ ] APK signature verified at runtime
- [ ] SafetyNet/Attestation for high-risk actions

---

## Incident Response

[source,i]
----
component SecurityIncidentHandler {
    fun handleSecurityEvent(event: SecurityEvent) {
        when (event) {
            is RootDetected -> {
                analytics.report("security.root_detected")
                secureStorage.deleteAll()
                api.reportCompromised()
                showSecurityAlert()
            }
            is IntegrityFailure -> {
                analytics.report("security.integrity_failure")
                forceLogout()
            }
            is CertificateMismatch -> {
                analytics.report("security.cert_mismatch")
                blockRequest()
            }
        }
    }
}
----

---

## Platform-Specific Notes

### Android

- Use EncryptedSharedPreferences for key-value storage
- Enable llowBackup=false in manifest to prevent ADB backup leaks
- Use AndroidKeyStore for hardware-backed key storage
- SafetyNet is deprecated — migrate to Play Integrity API
- Use AutofillFramework with caution (can leak data)

### iOS

- Use kSecAttrAccessibleWhenUnlockedThisDeviceOnly for keychain items
- Enable NSFaceIDUsageDescription in Info.plist
- iOS 16+: Use DeviceCheck for device attestation
- UIApplicationProtectedDataDidBecomeAvailable for file protection
- Use UIPasteboard detection for clipboard monitoring
