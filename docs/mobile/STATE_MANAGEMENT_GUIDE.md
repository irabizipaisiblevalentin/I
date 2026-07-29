# State Management Guide

## Overview

I Language offers three complementary state management paradigms: **Imiterere** (basic state), **Ibonwa** (observable/reactive), and **Ubuzima** (lifecycle-aware). Together they form a powerful, composable system inspired by Riverpod, BLoC, and Redux while remaining idiomatic to I.

---

## Imiterere (Basic State)

Imiterere (`state`) is the foundational state primitive — a simple reactive value holder.

### Basic Usage

```i
component Counter {
    val count = state(0)

    view {
        VStack {
            Text("Count: \(count.value)")
            Button("Increment") {
                count.value++
            }
            Button("Decrement") {
                count.value--
            }
        }
    }
}
```

### Derived State

```i
component DerivedDemo {
    val items = state<List<String>>(emptyList())
    val searchQuery = state("")

    // Derived state — recomputes when dependencies change
    val filteredItems = items.derive { list ->
        if (searchQuery.value.isEmpty()) list
        else list.filter { it.contains(searchQuery.value) }
    }

    // Or as computed property
    val itemCount = computed { items.value.size }
    val hasItems = computed { items.value.isNotEmpty() }
}
```

### State with Validation

```i
component FormExample {
    val email = state("")
    val password = state("")

    // State with validation
    val emailError = email.validate { value ->
        if (!value.contains("@")) "Invalid email"
        else null
    }

    val passwordError = password.validate { value ->
        if (value.length < 8) "Too short"
        else null
    }

    val isValid = computed {
        emailError.value == null && passwordError.value == null
    }
}
```

### State Actions

```i
component AsyncActionDemo {
    val data = state<AsyncValue<List<User>>>(AsyncValue.loading())

    fun loadUsers() {
        data.value = AsyncValue.loading()
        async {
            try {
                val users = await api.getUsers()
                data.value = AsyncValue.data(users)
            } catch (e: Exception) {
                data.value = AsyncValue.error(e)
            }
        }
    }
}
```

### API Reference

| Method | Description |
|--------|-------------|
| `state(initial)` | Create a reactive state variable |
| `state.value` | Get/set current value |
| `state.derive(transform)` | Create derived state from transform |
| `state.validate(validator)` | Add validation to state |
| `state.watch(callback)` | Watch for changes |
| `state.reset()` | Reset to initial value |
| `computed { expr }` | Computed read-only value |
| `AsyncValue` | Wrapper: `.loading()`, `.data(v)`, `.error(e)` |

---

## Ibonwa (Observable / Reactive)

Ibonwa (`observable`) provides full reactive streams with transformation, filtering, and combination operators, similar to RxJS/Riverpod.

### Creating Observables

```i
import ibonwa.*

component ObservableDemo {
    // From value
    val counter = observable(0)

    // From async operation
    val userStream = observableFrom { userId ->
        await api.getUser(userId)
    }

    // From event
    val buttonClicks = observableFromEvent<Unit>()

    // Periodic timer
    val ticker = observableInterval(1000)
}
```

### Transformation Operators

```i
component OperatorsDemo {
    val input = observable("")

    // Map
    val length = input.map { it.length }

    // Filter
    val validInput = input.filter { it.length >= 3 }

    // Debounce (for search)
    val debounced = input.debounce(300)

    // Distinct until changed
    val unique = input.distinctUntilChanged()

    // Combine latest
    val email = observable("")
    val password = observable("")
    val formValid = email.combineLatest(password) { e, p ->
        e.contains("@") && p.length >= 8
    }

    // Merge multiple streams
    val allEvents = event1.merge(event2)

    // Scan (accumulate)
    val accumulated = counter.scan(0) { acc, next -> acc + next }

    // SwitchMap (cancel previous)
    val searchResults = query.switchMap { q ->
        observableFrom { await api.search(q) }
    }
}
```

### Subjects (Multi-cast)

```i
component SubjectDemo {
    // PublishSubject — emits new events to subscribers
    val events = PublishSubject<String>()

    // BehaviorSubject — emits current + new events
    val currentUser = BehaviorSubject<User?>(null)

    // ReplaySubject — replays N past events
    val recentMessages = ReplaySubject<String>(5)

    fun sendMessage(msg: String) {
        events.emit(msg)
    }

    fun onStart() {
        events.subscribe { msg ->
            handleEvent(msg)
        }
    }
}
```

### Reactive Bindings

```i
component BindDemo {
    val name = observable("")
    val age = observable(0)

    // Two-way binding with UI
    view {
        TextField(value: name.binding())
        Slider(value: age.binding(), in: 0...120)

        Text("Hello \(name.value), age \(age.value)")
    }
}
```

### API Reference

| Operator | Description |
|----------|-------------|
| `observable(value)` | Create observable from initial value |
| `observableFrom { asyncFn }` | Observable from async function |
| `observableInterval(ms)` | Emit periodic tick |
| `observableFromEvent()` | Create from event emitter |
| `.map(fn)` | Transform values |
| `.filter(predicate)` | Filter values |
| `.debounce(ms)` | Debounce emissions |
| `.distinctUntilChanged()` | Skip duplicate values |
| `.combineLatest(other, fn)` | Combine with latest from other |
| `.merge(other)` | Merge multiple observables |
| `.scan(initial, fn)` | Accumulate values |
| `.switchMap(fn)` | Map to new observable, cancel previous |
| `.subscribe(observer)` | Subscribe to emissions |
| `.dispose()` | Dispose and clean up |
| `.binding()` | Create two-way UI binding |

---

## Ubuzima (Lifecycle-Aware)

Ubuzima (`lifecycle`) manages state tied to component lifecycle — auto-cleanup on dispose, cached across recompositions, and scoped to navigation destinations.

### Lifecycle Scopes

```i
import ubuzima.*

component LifecycleDemo {
    // State scoped to component — destroyed on unmount
    val localCounter = lifecycle.state(0, scope = .component)

    // State scoped to navigation destination — survives config changes
    val navigationData = lifecycle.state<ScreenData>(
        scope = .destination
    )

    // State scoped to app — survives everything
    val appConfig = lifecycle.state<Config>(
        scope = .app
    )

    // State scoped to user session
    val sessionToken = lifecycle.state<String?>(
        scope = .session
    )
}
```

### Lifecycle Callbacks

```i
component LifecycleCallbacks {
    use lifecycle()

    onInit {
        // Called once when component is created
        initializeAnalytics()
        loadPreferences()
    }

    onMount {
        // Called after first render
        startLocationUpdates()
    }

    onUnmount {
        // Called when component is removed
        stopLocationUpdates()
        cancelPendingRequests()
    }

    onActivate {
        // Component becomes visible (foreground)
        resumeAnimations()
    }

    onDeactivate {
        // Component becomes invisible (background)
        pauseAnimations()
    }

    onError { error ->
        // Handle lifecycle errors
        logError(error)
        showFallbackUI()
    }
}
```

### Auto-Dispose Observables

```i
component AutoDisposeDemo {
    use lifecycle()

    // Observables auto-dispose on unmount
    val location = lifecycle.observable<Position>()
    val batteryLevel = lifecycle.observable(100)

    onMount {
        locationStream()
            .takeUntil(lifecycle.disposeSignal)
            .subscribe { pos -> updateMap(pos) }

        // Or use lifecycle-safe scope
        lifecycle.scope {
            val data = await api.fetchData()
            // Canceled if component unmounts
        }
    }
}
```

### Scoped Providers

```i
component UserDetailScreen {
    // Provider scoped to this component tree
    val userProvider = lifecycle.provider { userId ->
        await api.getUser(userId)
    }

    // Usage
    val user = userProvider.watch()

    view {
        when (user) {
            is AsyncValue.Loading -> LoadingSpinner()
            is AsyncValue.Data -> UserProfile(user.value)
            is AsyncValue.Error -> ErrorView(user.error)
        }
    }
}
```

### API Reference

| Method | Description |
|--------|-------------|
| `lifecycle.state(initial, scope)` | Lifecycle-scoped state |
| `lifecycle.observable(value)` | Lifecycle-scoped observable |
| `lifecycle.provider(fn)` | Scoped async data provider |
| `lifecycle.scope { ... }` | Run code in lifecycle scope |
| `lifecycle.disposeSignal` | Signal fires on dispose |
| `onInit { }` | Called once on creation |
| `onMount { }` | Called after first render |
| `onUnmount { }` | Called on removal |
| `onActivate { }` | Foreground callback |
| `onDeactivate { }` | Background callback |
| `onError { }` | Error handler |

Scopes: `.component`, `.destination`, `.app`, `.session`

---

## State Persistence

### Automatic Persistence

```i
// Persistent state — auto-saves to disk
val preferences = state(
    defaultValue = Preferences(),
    persist = true,
    key = "user_prefs" // Storage key
)

// Persistent observable
val theme = observable(
    defaultValue = Theme.system,
    persist = true,
    storage = .sharedPreferences // or .keychain, .file
)
```

### Manual Persistence

```i
import persistence.*

component PersistenceDemo {
    use persistence()

    fun saveState() {
        persistence.save("onboarding_complete", true)
        persistence.save("last_position", Position(40.71, -74.00))
        persistence.saveObject("user_profile", userProfile)
    }

    fun loadState() {
        val completed = persistence.getBoolean("onboarding_complete", false)
        val position = persistence.getObject<Position>("last_position")
    }

    // Scoped to lifecycle
    lifecycle.onUnmount {
        persistence.save("counter", counter.value)
    }
}
```

### Storage Backends

| Backend | Platform | Use Case |
|---------|----------|----------|
| `.sharedPreferences` | Android | Simple key-value settings |
| `.userDefaults` | iOS | Simple key-value settings |
| `.keychain` | iOS | Secure sensitive data |
| `.encryptedSharedPreferences` | Android | Secure sensitive data |
| `.file` | Both | Complex/large data (JSON) |
| `.database` | Both | Structured relational data |
| `.datastore` | Android | Modern preferences |

---

## Best Practices

### 1. Choose the Right Primitive

```i
// Simple local state
val showDetails = state(false)

// Reactive transformations needed
val filteredItems = observable(allItems)
    .debounce(300)
    .distinctUntilChanged()

// Lifecycle-dependent
onMount { startTimer() }
onUnmount { stopTimer() }
```

### 2. Lift State Up

```i
// Parent manages state
component Parent {
    val count = state(0)

    view {
        Child(count: count, onIncrement: { count.value++ })
    }
}

// Child receives props
component Child(props: { count: State<Int>, onIncrement: () -> Unit }) {
    view {
        Button("Count: \(props.count.value)") {
            props.onIncrement()
        }
    }
}
```

### 3. Avoid Unnecessary Recomputations

```i
// ❌ Bad: creates new list every render
val doubled = computed { items.value.map { it * 2 } }

// ✅ Good: memoize with equality check
val doubled = items.derive(
    transform = { list -> list.map { it * 2 } },
    equality = structuralEquality()
)
```

### 4. Clean Up Resources

```i
component CleanupExample {
    val subscription = observable.interval(1000)
        .subscribe { tick -> update(tick) }

    // Never forget this
    onUnmount {
        subscription.dispose()
    }

    // Or use lifecycle-scoped variant
    val autoSubscription = lifecycle.observableInterval(1000)
        .subscribe { tick -> update(tick) }
    // Auto-disposed!
}
```

### 5. Use Providers for Dependencies

```i
// Provide dependencies at root
component App {
    val apiProvider = lifecycle.provider { ApiClient() }
    val authProvider = lifecycle.provider { AuthService() }
    val userProvider = lifecycle.provider { UserRepository() }

    view {
        ProviderScope(providers: [
            apiProvider, authProvider, userProvider
        ]) {
            MainApp()
        }
    }
}

// Consume anywhere in tree
component DeepChild {
    val api = consume(apiProvider)
    val user = consume(userProvider)
}
```

---

## Performance Considerations

| Strategy | Description |
|----------|-------------|
| **Granularity** | Keep state objects small — split large models |
| **Equality** | Use structural equality to prevent unnecessary rebuilds |
| **Debounce** | Debounce fast-changing values (search, scroll position) |
| **Lazy** | Use `lazy { }` for expensive computations |
| **Batch** | Batch state updates together (Android: `setState` coalescing) |
| **Select** | Select only needed fields from large state objects |
| **Dispose** | Always dispose subscriptions no longer needed |

### Profiling State

```i
instrumentedState("counter") {
    val counter = state(0)

    // Automatically logs:
    // - Number of reads/writes
    // - Subscriber count
    // - Rebuild frequency
}
```

---

## Comparison with Other Frameworks

### Riverpod

| Feature | I | Riverpod |
|---------|---|----------|
| Scoped providers | `lifecycle.provider` | `ProviderScope` |
| Auto-dispose | Built-in via lifecycle | `.autoDispose` |
| Family | `provider { id -> }` | `.family` |
| Async | `AsyncValue` | `AsyncValue` |
| Compile-time safety | ✅ | ✅ (code gen) |

### BLoC

| Feature | I | BLoC |
|---------|---|----------|
| Event-driven | `observableFromEvent` | `Event` class |
| Stream processing | `map`, `filter`, `debounce` | `map`, `where`, `debounce` |
| Testability | Isolate providers | Easy to test |
| Boilerplate | Minimal | Significant |

### Redux / Zustand

| Feature | I | Redux | Zustand |
|---------|---|-------|---------|
| Store | `state()` or `observable()` | Single store | Store |
| Actions | Functions | Action types | Functions |
| Reducers | `state`, `scan` | Pure reducers | `set` |
| Middleware | `observable.pipe()` | Middleware chain | Middleware |
| DevTools | `instrumentedState()` | Redux DevTools | Built-in |

---

## Complete Example

```i
import imiterere.*
import ibonwa.*
import ubuzima.*
import persistence.*

component TodoApp {
    // --- State ---
    val todos = state<List<Todo>>(
        emptyList(),
        persist = true,
        key = "todos"
    )
    val filter = state(Filter.all)
    val newTodoText = state("")

    // --- Derived ---
    val filteredTodos = todos.derive { list ->
        when (filter.value) {
            Filter.all -> list
            Filter.active -> list.filter { !it.completed }
            Filter.completed -> list.filter { it.completed }
        }
    }

    val activeCount = computed {
        todos.value.count { !it.completed }
    }

    // --- Observables for reactive effects ---
    val todoChanges = observable(todos.value)

    // --- Lifecycle ---
    onMount {
        // Log when todos change
        todoChanges
            .distinctUntilChanged()
            .debounce(1000)
            .subscribe { list ->
                log("Todos updated: ${list.size} items")
            }
    }

    // --- Actions ---
    fun addTodo() {
        if (newTodoText.value.isNotBlank()) {
            todos.value += Todo(
                id = uuid(),
                text = newTodoText.value,
                completed = false
            )
            newTodoText.value = ""
        }
    }

    fun toggleTodo(id: String) {
        todos.value = todos.value.map {
            if (it.id == id) it.copy(completed = !it.completed)
            else it
        }
    }

    fun clearCompleted() {
        todos.value = todos.value.filter { !it.completed }
    }

    // --- View ---
    view {
        VStack {
            // Add todo input
            HStack {
                TextField(
                    value: newTodoText.binding(),
                    placeholder: "What needs to be done?"
                )
                Button("Add", onTap: ::addTodo)
            }

            // Filter buttons
            HStack {
                ForEach(Filter.values()) { f ->
                    Button(f.name) { filter.value = f }
                        .tint(if (filter.value == f) .blue else .gray)
                }
            }

            // Todo list
            List {
                ForEach(filteredTodos.value) { todo ->
                    HStack {
                        Checkbox(todo.completed) { toggleTodo(todo.id) }
                        Text(todo.text)
                            .strikethrough(todo.completed)
                            .opacity(todo.completed ? 0.5 : 1.0)
                    }
                }
            }

            // Footer
            Text("\(activeCount.value) items remaining")
            Button("Clear Completed", onTap: ::clearCompleted)
        }
    }
}

enum Filter { all, active, completed }

data class Todo(
    val id: String,
    val text: String,
    val completed: Boolean
)
```
