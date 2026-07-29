# Accessibility Guide

## Overview

The I Language provides built-in accessibility support across Android and iOS platforms, aligned with WCAG 2.1 AA standards. This guide covers implementation, testing, and best practices for creating inclusive mobile experiences.

---

## Screen Reader Support

### Basic Labels

[source,i]
----
import accessibility.*

component AccessibleButton {
    use accessibility()

    view {
        Button("Submit Form") {
            handleSubmit()
        }
        .accessibility {
            label = "Submit the registration form"
            hint = "Double tap to submit your information"
            traits = [.button]
        }
    }
}
----

### Semantic Elements

[source,i]
----
component SemanticLayout {
    view {
        VStack {
            // Headers
            Text("Welcome Back")
                .accessibility {
                    traits = [.header]
                    headerLevel = 1
                }

            // Groups
            VStack {
                Text("Profile")
                Text("John Doe")
                Text("john@example.com")
            }
            .accessibility {
                label = "User profile information"
                traits = [.summaryElement]
                isGroup = true
            }

            // Lists
            List {
                ForEach(items) { item ->
                    Text(item.name)
                        .accessibility {
                            index = items.indexOf(item)
                            count = items.size
                        }
                }
            }
            .accessibility {
                label = "Items list"
                traits = [.list]
            }
        }
    }
}
----

### Live Regions

[source,i]
----
component LiveRegionDemo {
    val statusMessage = state("")

    fun updateStatus(message: String) {
        statusMessage.value = message
    }

    view {
        Text(statusMessage.value)
            .accessibility {
                liveRegion = .polite  // Announce when idle
                // .assertive for urgent announcements
            }
    }
}
----

### Custom Actions

[source,i]
----
component CustomAccessibilityActions {
    view {
        Card {
            Text("Shopping Cart")
            Text("\(itemCount) items - Total: $\(total)")
        }
        .accessibility {
            label = "Shopping cart with  items totaling "
            actions = [
                AccessibilityAction(
                    name: "Checkout",
                    handler: { navigateToCheckout() }
                ),
                AccessibilityAction(
                    name: "Clear cart",
                    handler: { clearCart() }
                )
            ]
            customRotors = [
                AccessibilityRotor(
                    name: "Cart Items",
                    entries: cartItems.map { item ->
                        RotorEntry(
                            label: item.name,
                            handler: { focusOnItem(item) }
                        )
                    }
                )
            ]
        }
    }
}
----

### Screen Reader API Reference

| Method | Description |
|--------|-------------|
| .accessibility { } | Configure accessibility properties |
| .label | VoiceOver/TalkBack label |
| .hint | Action hint text |
| .traits | Element traits (.button, .header, .link, etc.) |
| .value | Current value for adjustable elements |
| .isGroup | Group child elements as one unit |
| .headerLevel | Heading level (1-6) |
| .liveRegion | .polite, .assertive, .off |
| .actions | Custom accessibility actions |
| .customRotors | Custom rotor entries |
| .magicTap | Handler for Magic Tap gesture |
| .escape | Handler for escape gesture |

---

## Accessibility Labels and Hints

### Labeling Guidelines

[source,i]
----
// DO: Descriptive, context-aware
Button("X")
    .accessibility {
        label = "Close"
        hint = "Closes the settings panel"
    }

// DO: Include state
Checkbox(isChecked = true)
    .accessibility {
        label = "Remember me: checked"
    }

// DO: Combine text
VStack {
    Text("Temperature")
    Text("72°F")
}
.accessibility {
    label = "Temperature is 72 degrees Fahrenheit"
}

// DON'T: Redundant
Button("Submit")
    .accessibility {
        label = "Submit button" // "Button" is already announced
        hint = "Submits the form" // Better: no hint needed
    }

// DON'T: Generic
Image("icon.png")
    .accessibility {
        label = "Image" // Useless — describe the content
    }
----

### Dynamic Labels

[source,i]
----
component DynamicLabel {
    val cartCount = state(3)
    val itemName = state("blue sweater")

    val accessibilityLabel = computed {
        if (cartCount.value == 0) {
            "Cart is empty"
        } else {
            "Cart:  items, last added "
        }
    }

    view {
        CartIcon(count: cartCount.value)
            .accessibility {
                label = accessibilityLabel.value
                traits = [.button]
            }
    }
}
----

---

## Focus Management

### Programmatic Focus

[source,i]
----
component FocusDemo {
    val errorRef = useRef<AccessibilityElement>()
    val firstFieldRef = useRef<AccessibilityElement>()

    fun onError() {
        // Move focus to error message
        errorRef.current?.focus()
    }

    fun onFormOpen() {
        // Move focus to first field
        firstFieldRef.current?.focus()
    }

    view {
        VStack {
            Text("Please correct the errors above")
                .accessibility(ref: errorRef, traits = [.alert])

            TextField(label: "Email")
                .accessibility(ref: firstFieldRef)

            Button("Submit") { validate() }
        }
    }
}
----

### Focus Order

[source,i]
----
component FocusOrderDemo {
    view {
        VStack {
            // Natural order: top to bottom
            TextField(label: "Username")
            TextField(label: "Password")

            // Explicit focus order
            HStack {
                Button("Cancel") { goBack() }
                    .accessibility(sortPriority: 2)
                Button("Submit") { submit() }
                    .accessibility(sortPriority: 1) // Focused first
                Button("Help") { showHelp() }
                    .accessibility(sortPriority: 3)
            }
        }
        .accessibility {
            // Modal traps focus inside
            isModal = true
            // View is dismissed on escape
            onEscape = { dismiss() }
        }
    }
}
----

### Focus Management API

| Method | Description |
|--------|-------------|
| element.focus() | Move accessibility focus to element |
| element.isFocused | Whether element is focused |
| .accessibility(sortPriority) | Focus order priority |
| .accessibility(ref:) | Reference for programmatic focus |
| .accessibility { isModal = true } | Trap focus within modal |
| .accessibility { onEscape } | Handle escape gesture |

---

## Touch Target Sizes

### Minimum Sizes

[source,i]
----
component TouchTargets {
    view {
        // Minimum 44x44 points (iOS HIG)
        // Minimum 48x48 dp (Android Material)

        // DO: Sufficient size
        Button("Submit")
            .frame(minWidth: 48, minHeight: 48)

        // DO: Increased padding for small icons
        IconButton(icon: .trash)
            .padding(12) // 24 + 12*2 = 48 total
            .accessibility {
                label = "Delete item"
            }

        // DO: Use .touchTarget modifier
        Text("Tap here")
            .touchTarget(minimum: 48) // Expands hit area

        // DON'T: Too small
        Text("x")
            .onTap { close() }
            .frame(width: 20, height: 20) // Too small!

        // Custom hit area
        Image("profile.jpg")
            .frame(width: 32, height: 32)
            .hitSlop(top: 8, bottom: 8, left: 8, right: 8)
            .onTap { openProfile() }
    }
}
----

### Recommended Sizes

| Platform | Minimum | Recommended |
|----------|---------|-------------|
| iOS | 44x44 pt | 48x48 pt |
| Android | 48x48 dp | 56x56 dp |
| watchOS | 44x44 pt | 52x52 pt |
| Android TV | 64x64 dp | 72x72 dp |

---

## Color Contrast

### Contrast Ratios

[source,i]
----
component ContrastDemo {
    view {
        // WCAG AA requires:
        // - Normal text: 4.5:1
        // - Large text (18pt+): 3:1
        // - UI components: 3:1

        // DO: Sufficient contrast
        Text("Body Text")
            .foregroundColor(Color(hex: "#333333"))     // Dark gray
            .background(Color(hex: "#FFFFFF"))          // White bg
            // Contrast ratio: ~10.5:1 ✓

        // DO: Large text can use slightly less contrast
        Text("Heading")
            .font(.title)
            .foregroundColor(Color(hex: "#666666"))     // Medium gray
            .background(Color(hex: "#FFFFFF"))
            // Contrast ratio: ~5.1:1 ✓ (large text)

        // DON'T: Insufficient contrast
        Text("Light Text")
            .foregroundColor(Color(hex: "#999999"))     // Light gray
            .background(Color(hex: "#FFFFFF"))
            // Contrast ratio: ~2.7:1 ✗ (fails AA)

        // DO: Use system colors (already accessible)
        Text("Primary")
            .foregroundColor(.primary)
        Text("Secondary")
            .foregroundColor(.secondary)
    }
}
----

### Dynamic Contrast

[source,i]
----
component DynamicContrast {
    use colorScheme()

    val textColor = computed {
        if (colorScheme.isDark) {
            Color(hex: "#E0E0E0") // Light text on dark bg
        } else {
            Color(hex: "#333333") // Dark text on light bg
        }
    }

    val linkColor = computed {
        // Ensure minimum 4.5:1 on current background
        if (colorScheme.isDark) {
            Color(hex: "#82B1FF") // Brighter blue for dark mode
        } else {
            Color(hex: "#1565C0") // Standard blue for light mode
        }
    }

    view {
        Text("Accessible content")
            .foregroundColor(textColor.value)
        Link("Learn more", url: "https://...")
            .foregroundColor(linkColor.value)
    }
}
----

### Contrast Testing

[source,i]
----
// Runtime contrast check
fun verifyContrast() {
    val foreground = Color(hex: "#999999")
    val background = Color(hex: "#FFFFFF")
    val ratio = foreground.contrastRatio(background)

    if (ratio < 4.5) {
        log("Warning: Low contrast ratio: ")
        analytics.track("low_contrast", {
            foreground: foreground.toHex(),
            background: background.toHex(),
            ratio: ratio
        })
    }
}
----

---

## Dynamic Text Sizing

### Supporting Dynamic Type (iOS)

[source,i]
----
component DynamicText {
    view {
        // Use system text styles — automatically scale
        Text("Headline")
            .font(.headline)          // Scaled with Dynamic Type
        Text("Body")
            .font(.body)              // Default: 17pt
        Text("Caption")
            .font(.caption)           // Small, scaled

        // Custom font that scales
        Text("Custom")
            .font(.custom("Georgia", size: 16, relativeTo: .body))
            // Scales relative to body text size

        // Fixed size (not recommended)
        Text("Fixed")
            .font(.system(size: 14))
            // Does NOT scale — avoid for body text
    }
}
----

### Supporting Font Scaling (Android)

[source,i]
----
component ScalableText {
    view {
        // Uses sp units — scales with system font size
        Text("Content")
            .fontSize(16.sp)  // Scales with user preference

        // Non-scaling dp (use sparingly)
        Text("Fixed Label")
            .fontSize(14.dp)  // Does not scale

        // Respect font weight preferences
        Text("Readable")
            .fontWeight(FontWeight.normal)
            // Avoid bold for all text — some users prefer
    }
}
----

### Custom Scaling

[source,i]
----
component CustomScaling {
    use accessibilitySettings()

    val scaleFactor = computed {
        when (accessibilitySettings.fontScale) {
            .extraSmall -> 0.85
            .small -> 0.93
            .normal -> 1.0
            .large -> 1.15
            .extraLarge -> 1.30
            .extraExtraLarge -> 1.50
            .extraExtraExtraLarge -> 1.80
        }
    }

    view {
        Text("Adaptive Text")
            .scaleEffect(scaleFactor.value)
    }
}
----

### Layout Adaptation

[source,i]
----
// ❌ Bad: Fixed width breaks with large text
view {
    Text("Long text that might need more space")
        .frame(width: 200)
}

// ✅ Good: Flexible layout
view {
    Text("Long text that adjusts to size")
        .fixedSize(horizontal: false, vertical: true)
        .padding(.horizontal)
}

// ✅ Good: Dynamic sizing with max width
view {
    Text("Adaptive paragraph")
        .lineLimit(nil)  // No limit
        .minimumScaleFactor(0.5)  // Shrink if needed
}
----

### Text Size API Reference

| Method | iOS | Android |
|--------|-----|---------|
| System font scale | .font(.body) | 16.sp |
| Custom scaling | .scaleEffect(factor) | ontScale |
| Min scale factor | .minimumScaleFactor(0.5) | utoSizeMinTextSize |
| Line limit | .lineLimit(n) | maxLines |
| Font weight | .fontWeight(.bold) | ontWeight = FontWeight.Bold |

---

## Reduced Motion

### Respecting Motion Preferences

[source,i]
----
component MotionAware {
    use accessibilitySettings()

    val isReducedMotion = accessibilitySettings.reduceMotion

    view {
        if (isReducedMotion.value) {
            // No animation — instant transition
            ContentView()
                .transition(.identity)
        } else {
            // Full animation
            ContentView()
                .transition(.slide)
                .animation(.spring())
        }
    }
}
----

### Alternative Animations

[source,i]
----
component ReducedMotionAnimations {
    use accessibilitySettings()

    val isReducedMotion = accessibilitySettings.reduceMotion

    fun animateElement(element: View) {
        if (isReducedMotion.value) {
            // Cross-fade instead of slide
            element.animate(
                opacity: 1.0,
                duration: 150  // Shorter duration
            )
        } else {
            // Full animation
            element.animate(
                translationX: 100,
                opacity: 1.0,
                duration: 300,
                easing: .spring()
            )
        }
    }

    // Parallax effects
    view {
        ParallaxHeader()
            .parallax(intensity: isReducedMotion.value ? 0 : 0.3)
    }

    // Auto-play video
    view {
        VideoPlayer(src: "intro.mp4")
            .autoPlay(!isReducedMotion.value)
    }
}
----

### Animations to Avoid

- Continuous scrolling/rotation
- Flashing/strobing effects (can trigger seizures)
- Large scale animations (can cause dizziness)
- Rapid parallax effects

### API Reference

| Setting | Property | Values |
|---------|----------|--------|
| Reduce motion | ccessibilitySettings.reduceMotion | 	rue, alse |
| Reduce transparency | ccessibilitySettings.reduceTransparency | 	rue, alse |
| Invert colors | ccessibilitySettings.invertColors | 	rue, alse |
| Bold text | ccessibilitySettings.boldText | 	rue, alse |
| Button shapes | ccessibilitySettings.buttonShapes | 	rue, alse |
| On/off labels | ccessibilitySettings.onOffLabels | 	rue, alse |
| Grayscale | ccessibilitySettings.grayscale | 	rue, alse |

---

## Testing for Accessibility

### Automated Testing

[source,i]
----
import testing.accessibility.*

@Test
fun testAccessibilityLabels() {
    val screen = render(ProfileScreen())
    val result = screen.checkAccessibility()

    // Check for missing labels
    assert(result.missingLabels.isEmpty()) {
        "Found elements without accessibility labels"
    }

    // Check touch target sizes
    val smallTargets = result.targetsBelowMinimum
    assert(smallTargets.isEmpty()) {
        "Found  small touch targets"
    }
}

@Test
fun testContrastRatios() {
    val screen = render(SettingsScreen())
    val violations = screen.checkContrast(
        minimum: 4.5,
        largeTextMinimum: 3.0
    )
    assert(violations.isEmpty()) {
        "Found  contrast violations"
    }
}

@Test
fun testFocusOrder() {
    val screen = render(LoginForm())
    val focusOrder = screen.getAccessibilityFocusOrder()

    // Verify logical order
    assert(focusOrder[0].label == "Username")
    assert(focusOrder[1].label == "Password")
    assert(focusOrder[2].label == "Submit")
}
----

### CI Pipeline Integration

[source,json]
----
{
  "quality": {
    "accessibility": {
      "enabled": true,
      "rules": {
        "missingLabels": "error",
        "contrast": "error",
        "smallTargets": "warning",
        "focusOrder": "warning"
      },
      "thresholds": {
        "maxViolations": 5
      }
    }
  }
}
----

[source,bash]
----
# Run accessibility checks
iglu test --accessibility

# Generate report
iglu test --accessibility --report a11y-report.html

# Check specific WCAG level
iglu test --accessibility --level AA
----

### Manual Testing Checklist

- [ ] Navigate entire app with screen reader only
- [ ] Verify all interactive elements have labels
- [ ] Test with system font size set to largest
- [ ] Test with reduced motion enabled
- [ ] Test with high contrast / invert colors
- [ ] Verify all touch targets >= 44pt / 48dp
- [ ] Test orientation changes
- [ ] Test with keyboard navigation (external keyboard)
- [ ] Verify focus order is logical
- [ ] Test with color blindness simulator
- [ ] Test with voice control / switch access
- [ ] Verify closed captions for media

### Testing Tools

| Tool | Platform | Purpose |
|------|----------|---------|
| VoiceOver | iOS | Screen reader |
| TalkBack | Android | Screen reader |
| Accessibility Inspector | iOS (Xcode) | Audit accessibility |
| Accessibility Scanner | Android | Audit accessibility |
| Color Contrast Analyzer | Both | Check contrast ratios |
| axe DevTools | Web views | Web accessibility |
| Dynamic Type tester | iOS | Test font scaling |
| Layout bounds | Android | Check touch targets |

---

## WCAG Compliance

### WCAG 2.1 Level AA Checklist

| Guideline | Description | Implementation |
|-----------|-------------|----------------|
| 1.1.1 | Non-text Content | .accessibility { label } on all images/icons |
| 1.3.1 | Info and Relationships | Semantic elements, headers, groups |
| 1.3.2 | Meaningful Sequence | Logical focus order |
| 1.3.4 | Orientation | Support portrait and landscape |
| 1.4.1 | Use of Color | Don't rely solely on color |
| 1.4.3 | Contrast (Minimum) | 4.5:1 normal, 3:1 large text |
| 1.4.4 | Resize Text | Support dynamic type / font scaling |
| 1.4.10 | Reflow | Content readable at 320px width |
| 1.4.11 | Non-text Contrast | 3:1 for UI components |
| 1.4.12 | Text Spacing | No loss of content with spacing overrides |
| 2.1.1 | Keyboard | All actions accessible via keyboard |
| 2.2.2 | Pause, Stop, Hide | Auto-playing content can be paused |
| 2.3.1 | Three Flashes | No flashing more than 3x per second |
| 2.4.3 | Focus Order | Logical tab order |
| 2.4.6 | Headings and Labels | Descriptive headings and labels |
| 2.5.5 | Target Size | Minimum 44x44 pt touch targets |
| 2.5.8 | Target Size (Enhanced) | Minimum 24x24 CSS px |
| 3.2.1 | On Focus | No unexpected context changes on focus |
| 3.3.2 | Labels or Instructions | Form fields have labels |
| 3.3.3 | Error Suggestion | Descriptive error messages |
| 4.1.2 | Name, Role, Value | Elements expose correct accessibility info |
| 4.1.3 | Status Messages | Live regions for dynamic updates |

### Declaring Conformance

[source,json]
----
{
  "accessibility": {
    "wcag": {
      "level": "AA",
      "version": "2.1",
      "conformanceDate": "2026-06-01",
      "exceptions": [
        {
          "criteria": "1.2.1",
          "reason": "Pre-recorded audio-only content",
          "plannedFix": "Q3 2026"
        }
      ]
    }
  }
}
----

### Accessibility Statement

[source,html]
----
<!-- In app settings or website -->
<h2>Accessibility Statement</h2>
<p>We are committed to making our app accessible to everyone.
Our goal is to meet WCAG 2.1 Level AA standards.</p>
<h3>Features</h3>
<ul>
  <li>Full VoiceOver and TalkBack support</li>
  <li>Dynamic Type and font scaling</li>
  <li>High contrast design</li>
  <li>Reduced motion support</li>
  <li>Descriptive labels on all controls</li>
</ul>
<h3>Contact</h3>
<p>If you experience accessibility issues, please contact
<a href="mailto:accessibility@example.com">accessibility@example.com</a></p>
----

---

## Platform-Specific Notes

### iOS

- VoiceOver: Use .accessibility for all UIKit/ SwiftUI views
- UIAccessibility.post(notification:) for announcements
- ccessibilityElementsHidden for decorative elements
- UIAccessibilityIsVoiceOverRunning() to check state
- Use @AccessibilityFocusState for focus management
- preferredContentSizeCategory for Dynamic Type

### Android

- TalkBack: Use contentDescription via .accessibility { label }
- View.announceForAccessibility() for announcements
- importantForAccessibility for decorative views
- View.AccessibilityDelegate for custom behavior
- Use sp units for text that should scale
- AccessibilityNodeInfo for complex custom views

---

## Best Practices Summary

1. **Label everything** — every interactive element needs an accessibility label
2. **Test with screen readers** — use the app blindfolded
3. **Support Dynamic Type** — test at largest font size
4. **Respect Reduced Motion** — provide alternatives
5. **Check contrast** — use tools, don't guess
6. **Logical focus order** — test with keyboard/TalkBack swipe
7. **Error messages** — associate with fields, provide suggestions
8. **Don't rely on color alone** — use shapes, text, icons
9. **Touch targets >= 44pt** — don't make users struggle
10. **Write automated tests** — catch regressions early
