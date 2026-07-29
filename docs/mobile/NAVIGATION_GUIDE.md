# Navigation Guide

## Overview

The I Language provides a declarative navigation system built on platform-native navigators. Supports stack, tab, drawer, and advanced patterns with deep linking and state restoration.

---

## Navigation Setup

### Basic Configuration

```i
// In your main app entry point
component App {
    view {
        Navigator {
            Screen("home") { HomeScreen() }
            Screen("profile") { ProfileScreen() }
            Screen("settings") { SettingsScreen() }
        }
    }
}
```

### Navigation Root

```json
// iglu.json navigation config
{
  "navigation": {
    "initialRoute": "home",
    "deepLinks": true,
    "restoreState": true,
    "animation": "default"
  }
}
```

---

## Stack Navigation

### Basic Stack

```i
component StackDemo {
    use navigator()

    view {
        StackNavigator {
            Screen("list") {
                VStack {
                    Button("Go to Detail") {
                        navigate("detail", params: { id: 42 })
                    }
                }
            }
            Screen("detail", params: { id: Int }) {
                DetailScreen(id: route.params.id)
            }
        }
    }
}
```

### Push, Pop, Replace

```i
component NavigationActions {
    use navigator()

    fun handleNavigation() {
        // Push a new screen onto the stack
        navigator.push("profile", params: { userId: currentUser.id })

        // Go back
        navigator.pop()
        navigator.popToRoot()

        // Replace current screen
        navigator.replace("login")

        // Pop to specific route
        navigator.popTo("home")

        // Conditional navigation
        if (isLoggedIn) {
            navigator.push("dashboard")
        } else {
            navigator.replace("login")
        }
    }
}
```

### Screen Transitions

```i
StackNavigator(
    transition: .slide,       // .slide (default), .fade, .scale, .none
    gestureEnabled: true,
    animationDuration: 350
) {
    Screen("a") { ScreenA() }
    Screen("b") { ScreenB() }
}

// Per-screen transition override
Screen("modal", transition: .modal) {
    ModalScreen()
}

// Custom animation
Screen("custom", transition: .custom(
    enter: { view, duration ->
        view.alpha = 0
        view.transform = CGAffineTransform(translationX: 0, y: 100)
        UIView.animate(withDuration: duration) {
            view.alpha = 1
            view.transform = .identity
        }
    },
    exit: { view, duration ->
        UIView.animate(withDuration: duration) {
            view.alpha = 0
            view.transform = CGAffineTransform(scaleX: 0.8, y: 0.8)
        }
    }
)) {
    CustomAnimatedScreen()
}
```

### Stack API

| Method | Description |
|--------|-------------|
| `push(route, params)` | Push screen onto stack |
| `pop()` | Go back one screen |
| `popTo(route)` | Pop to specific route |
| `popToRoot()` | Pop all screens to root |
| `replace(route, params)` | Replace current screen |
| `canGoBack()` | Whether there's a screen to pop to |
| `stackSize()` | Current stack depth |

---

## Tab Navigation

### Bottom Tabs

```i
component TabDemo {
    use navigator()

    view {
        TabNavigator(
            style: .bottom,    // .bottom, .top, .segmented
            tint: .blue,
            unselectedTint: .gray,
            badgeStyle: .redDot
        ) {
            Tab(
                route: "home",
                label: "Home",
                icon: .house,
                selectedIcon: .houseFill,
                badge: unreadCount.value
            ) {
                HomeScreen()
            }

            Tab(
                route: "search",
                label: "Search",
                icon: .magnifyingGlass
            ) {
                SearchScreen()
            }

            Tab(
                route: "profile",
                label: "Profile",
                icon: .person
            ) {
                ProfileScreen()
            }
        }
    }
}
```

### Material Top Tabs

```i
TabNavigator(
    style: .top,
    indicatorColor: .primary,
    indicatorHeight: 3,
    scrollable: true
) {
    Tab("tab1", label: "Tab 1") { Content1() }
    Tab("tab2", label: "Tab 2") { Content2() }
    Tab("tab3", label: "Tab 3") { Content3() }
}
```

### Nested Tab Configuration

```i
// Combine stack inside tab
TabNavigator {
    Tab("feed", label: "Feed", icon: .newspaper) {
        StackNavigator {
            Screen("feedList") { FeedListScreen() }
            Screen("feedDetail", params: { id: Int }) { FeedDetail() }
        }
    }
}
```

### Tab API

| Method | Description |
|--------|-------------|
| `switchTab(route)` | Programmatically switch tab |
| `currentTab` | Currently active tab route |
| `setBadge(route, value)` | Set badge count on tab |
| `clearBadge(route)` | Clear badge on tab |
| `showTab(route, show)` | Show/hide a tab |
| `lockTabs(locked)` | Lock tab switching |

---

## Drawer Navigation

### Side Drawer

```i
component DrawerDemo {
    view {
        DrawerNavigator(
            drawerWidth: 280,
            edge: .left,        // .left, .right
            gestureEnabled: true,
            overlayColor: Color.black.opacity(0.3),
            animationDuration: 250
        ) {
            Drawer {
                // Drawer content
                VStack(alignment: .leading) {
                    UserHeader()
                    Divider()

                    DrawerItem("Home", icon: .house) {
                        navigate("home")
                    }
                    DrawerItem("Orders", icon: .bag) {
                        navigate("orders")
                    }
                    DrawerItem("Settings", icon: .gear) {
                        navigate("settings")
                    }

                    Spacer()

                    DrawerItem("Logout", icon: .arrowLeft, color: .red) {
                        logout()
                    }
                }
                .padding()
            }

            // Main content
            StackNavigator {
                Screen("home") { HomeScreen() }
                Screen("orders") { OrdersScreen() }
                Screen("settings") { SettingsScreen() }
            }
        }
    }
}
```

### Drawer API

| Method | Description |
|--------|-------------|
| `openDrawer()` | Open the drawer |
| `closeDrawer()` | Close the drawer |
| `toggleDrawer()` | Toggle drawer open/closed |
| `isDrawerOpen` | Whether drawer is currently open |
| `setDrawerEnabled(enabled)` | Enable/disable drawer gestures |

---

## Named Routes

### Route Definitions

```i
// Centralized route definitions
val routes = Routes {
    route("home", path: "/") { HomeScreen() }
    route("profile", path: "/profile/{userId}") { params ->
        ProfileScreen(userId: params["userId"])
    }
    route("settings", path: "/settings") { SettingsScreen() }
    route("product", path: "/product/{category}/{id}") { params ->
        ProductScreen(category: params["category"], id: params["id"])
    }
}

// Type-safe params
@Route("profile")
data class ProfileParams(val userId: String)

@Route("product")
data class ProductParams(val category: String, val id: Int)
```

### Route Groups

```i
// Organize routes by feature
routes {
    group("auth") {
        route("login") { LoginScreen() }
        route("register") { RegisterScreen() }
        route("forgotPassword") { ForgotPasswordScreen() }
    }
    group("main") {
        route("dashboard") { DashboardScreen() }
        route("analytics") { AnalyticsScreen() }
    }
}
```

---

## Parameter Passing

### Basic Parameters

```i
// Sending parameters
navigate("profile", params: {
    userId: "abc123",
    showEditButton: true,
    initialTab: 2
})

// Receiving parameters
Screen("profile", params: { userId: String, showEditButton: Boolean?, initialTab: Int? }) {
    ProfileScreen(
        userId: route.params.userId,
        showEdit: route.params.showEditButton ?: false
    )
}
```

### Complex Parameters

```i
// Passing objects (serialized)
navigate("checkout", params: {
    order: Order(
        id: "ORD-123",
        items: [
            OrderItem(product: "Widget", qty: 2, price: 9.99)
        ],
        total: 19.98
    )
})

// Receiving with typed deserialization
Screen("checkout", params: { order: Order }) {
    CheckoutScreen(order: route.params.order)
}
```

### Returning Results

```i
// From detail screen — pop with result
navigator.popWithResult(result: {
    selected: true,
    item: selectedItem
})

// From calling screen — await result
async {
    val result = await navigator.pushForResult("picker", params: {
        filter: "documents"
    })
    if (result != null) {
        val selected = result["item"] as Document
        processDocument(selected)
    }
}
```

---

## Deep Linking

### Configuration

```json
{
  "navigation": {
    "deepLinks": {
      "schemes": ["myapp", "https"],
      "hosts": ["myapp.example.com", "example.com"],
      "prefixes": ["myapp://", "https://example.com/app/"]
    }
  }
}
```

### Route Mapping

```i
val routes = Routes {
    // Simple path
    deepLink("myapp://profile/{userId}") { params ->
        navigate("profile", params: params)
    }

    // URL with query parameters
    deepLink("https://example.com/app/product") { url ->
        navigate("product", params: {
            id: url.queryParam("id"),
            category: url.queryParam("cat")
        })
    }

    // Wildcard
    deepLink("myapp://*") { url ->
        if (url.pathSegments.size >= 1) {
            navigate(url.pathSegments[0], params: url.params)
        }
    }
}
```

### Handling Deep Links at App Start

```i
component DeepLinkHandler {
    use deepLink()

    onAppStart {
        val pendingLink = deepLink.getInitialLink()
        if (pendingLink != null) {
            handleDeepLink(pendingLink)
        }
    }

    onDeepLink { url ->
        handleDeepLink(url)
    }

    fun handleDeepLink(url: String) {
        router.navigate(url)
    }
}
```

---

## Universal Links (iOS) / App Links (Android)

### Setup

```json
// iglu.json
{
  "navigation": {
    "universalLinks": {
      "domains": ["example.com", "www.example.com"],
      "teamId": "ABCDEF1234",  // iOS Team ID
      "appId": "com.example.myapp"
    }
  }
}
```

### iOS Associated Domain

```json
// apple-app-site-association (serve at /.well-known/)
{
  "applinks": {
    "apps": [],
    "details": [
      {
        "appID": "ABCDEF1234.com.example.myapp",
        "paths": ["*", "/profile/*", "/product/*"]
      }
    ]
  }
}
```

### Android App Links

```xml
<!-- AndroidManifest.xml auto-generated -->
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="https" android:host="example.com" />
</intent-filter>
```

### Verification

```bash
# iOS: Validate association file
curl -v https://example.com/.well-known/apple-app-site-association

# Android: Verify digital asset links
curl "https://example.com/.well-known/assetlinks.json"
```

---

## Animation Customization

### Navigation Animations

```i
Navigator(
    animation: NavigationAnimation(
        push: AnimationSpec(
            duration: 300,
            easing: .easeInOut,
            spring: null // Use spring instead
        ),
        pop: AnimationSpec(
            duration: 250,
            easing: .easeOut
        ),
        modal: AnimationSpec(
            duration: 400,
            spring: SpringSpec(
                damping: 0.8,
                stiffness: 200
            )
        )
    )
)
```

### Custom Transitions

```i
// Per-navigator transition
StackNavigator(
    transition: .custom { operation, from, to, callback ->
        val offset = if (operation == .push) 1.0 else -1.0
        to?.transform = CGAffineTransform(
            translationX: to.frame.width * offset, y: 0
        )
        UIView.animate(withDuration: 0.35, animations = {
            from?.transform = CGAffineTransform(
                translationX: -from.frame.width * offset / 2, y: 0
            )
            to?.transform = .identity
        }, completion = { _ -> callback() })
    }
)
```

### Shared Element Transition

```i
component SharedElementDemo {
    view {
        StackNavigator(sharedElementTransitions: true) {
            Screen("grid") {
                LazyVGrid {
                    ForEach(products) { product ->
                        NavigationLink("detail", params: { id: product.id }) {
                            ProductCard(product)
                                .sharedTransition(id: "product_\(product.id)")
                        }
                    }
                }
            }

            Screen("detail", params: { id: Int }) {
                ProductDetail(productId: route.params.id)
                    .sharedTransition(id: "product_\(route.params.id)")
            }
        }
    }
}
```

### Gesture-Driven Animations

```i
StackNavigator(
    gestureEnabled: true,
    gestureResponseDistance: 20,
    gestureVelocityThreshold: 500,
    gestureCompleteThreshold: 0.3,
    gestureAnimation: .interactiveSpring(
        stiffness: 300,
        damping: 30
    )
)
```

---

## State Restoration

### Automatic Restoration

```json
{
  "navigation": {
    "restoreState": true,
    "restoreDebounce": 2000,
    "maxRestoreDepth": 10
  }
}
```

### Manual State Saving

```i
component NavigationStateManager {
    use navigator()
    use persistence()

    fun saveNavigationState() {
        val state = navigator.saveState()
        persistence.saveObject("nav_state", state)
    }

    fun restoreNavigationState() {
        val saved = persistence.getObject<NavigationState>("nav_state")
        if (saved != null) {
            navigator.restoreState(saved)
        }
    }

    // Auto-save on background
    onDeactivate {
        saveNavigationState()
    }

    // Restore on foreground
    onActivate {
        restoreNavigationState()
    }
}
```

### View Model Restoration

```i
component RestorableScreen {
    use navigator()

    // State auto-restored with navigation
    val scrollPosition = state(0.0, restoreKey = "scroll_pos")
    val selectedTab = state(0, restoreKey = "selected_tab")
    val formData = state<FormData>(
        FormData(),
        restoreKey = "form_data"
    )
}
```

---

## Complete Examples

### E-Commerce App Navigation

```i
component EcommerceApp {
    view {
        TabNavigator {
            Tab("home", label: "Home", icon: .house) {
                StackNavigator {
                    Screen("home") { HomeScreen() }
                    Screen("category", params: { id: String }) { CategoryScreen() }
                    Screen("product", params: { id: String }) { ProductScreen() }
                    Screen("search") { SearchScreen() }
                }
            }

            Tab("cart", label: "Cart", icon: .cart, badge: cartCount.value) {
                StackNavigator {
                    Screen("cart") { CartScreen() }
                    Screen("checkout") { CheckoutScreen() }
                    Screen("payment") { PaymentScreen() }
                    Screen("orderSuccess", params: { id: String }) { OrderSuccessScreen() }
                }
            }

            Tab("profile", label: "Profile", icon: .person) {
                StackNavigator {
                    Screen("profile") { ProfileScreen() }
                    Screen("orders") { OrdersScreen() }
                    Screen("orderDetail", params: { id: String }) { OrderDetailScreen() }
                    Screen("settings") { SettingsScreen() }
                    Screen("addresses") { AddressesScreen() }
                }
            }
        }
    }
}
```

### Authentication Flow

```i
component AuthFlow {
    val isAuthenticated = state(false)

    view {
        if (isAuthenticated.value) {
            // Main app
            DrawerNavigator {
                Drawer { DrawerContent() }
                StackNavigator {
                    Screen("dashboard") { DashboardScreen() }
                    Screen("settings") { SettingsScreen() }
                }
            }
        } else {
            // Auth stack
            StackNavigator(transition: .fade) {
                Screen("login") { LoginScreen(onLogin: { isAuthenticated.value = true }) }
                Screen("register") { RegisterScreen() }
                Screen("forgotPassword") { ForgotPasswordScreen() }
            }
        }
    }
}
```

### Navigation with Middleware

```i
component NavigationMiddleware {
    use navigator()

    // Route guards
    onBeforeNavigate { route, params ->
        if (route == "admin" && !isAdmin) {
            navigator.replace("login")
            return false // Cancel navigation
        }
        if (route == "checkout" && cart.isEmpty()) {
            showToast("Cart is empty")
            return false
        }
        return true // Allow navigation
    }

    // Analytics tracking
    onAfterNavigate { route, params ->
        analytics.track("screen_view", {
            screen: route,
            params: params
        })
    }
}
```

---

## Platform-Specific Notes

### iOS

- **Interactive pop gesture** enabled by default for stack navigators
- **`prefersLargeTitles`** supported via `navigation.largeTitleDisplayMode`
- **`navigationBarHidden`** available per-screen
- **Tab bar** uses `UITabBar` natively
- **`hidesBottomBarWhenPushed`** — set in navigation options

### Android

- **Back gesture** handled automatically; intercept via `backHandler()`
- **`Activity` based** — each stack is a single Activity with Fragment management
- **`onNewIntent`** handled for deep links
- **Transition animations** use `ActivityOptions` / `FragmentTransaction` animations
- **Predictive back gesture** supported on Android 14+

---

## Navigation API Reference

| Method | Description |
|--------|-------------|
| `navigate(route, params)` | Navigate to route |
| `push(route, params)` | Push onto stack |
| `pop()` | Go back |
| `popTo(route)` | Pop to specific route |
| `popToRoot()` | Pop to root |
| `replace(route, params)` | Replace current screen |
| `pushForResult(route, params)` | Push and await result |
| `popWithResult(result)` | Pop and return result |
| `switchTab(route)` | Switch active tab |
| `openDrawer()` | Open drawer |
| `closeDrawer()` | Close drawer |
| `currentRoute` | Currently active route |
| `currentParams` | Current route parameters |
| `canGoBack()` | Whether back is available |
| `saveState()` | Save navigation state |
| `restoreState(state)` | Restore navigation state |
