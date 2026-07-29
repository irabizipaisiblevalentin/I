# Editor Guide

## Using the Editor
```python
from imikino.uguhindura import Editor, EditorLayer, EditorTool

editor = Editor()
editor.active_tool = EditorTool.MOVE

# Toggle windows
editor.toggle_window("inspector")
editor.is_window_open("scene")
```

## Undo/Redo
```python
editor.push_undo({"entity_id": "...", "previous_position": [0, 0, 0]})
editor.undo()
editor.redo()
```

## Selection
```python
editor.select_entity("entity_123")
editor.is_selected("entity_123")
editor.deselect_all()
```
