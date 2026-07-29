# Plugin Guide

## Creating a Plugin
```python
from imikino.guhindura import Plugin

class MyPlugin(Plugin):
    def __init__(self):
        super().__init__(name="MyPlugin", version="1.0.0")

    def on_register(self, engine):
        print(f"{self.name} registered")

    def on_update(self, dt):
        pass

    def on_unregister(self):
        print(f"{self.name} unregistered")
```

## Registering
```python
from imikino.guhindura import get_plugins

pm = get_plugins()
pm.register(MyPlugin())
plugin = pm.get("MyPlugin")
```
