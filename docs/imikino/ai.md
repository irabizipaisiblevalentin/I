# AI Guide

## Behaviour Trees
```python
from imikino.inyenzure import (
    BehaviourTree, SelectorNode, SequenceNode, ConditionNode, ActionNode,
)

root = SelectorNode(name="Root")
patrol = SequenceNode(name="Patrol Sequence")
patrol.children.append(ConditionNode(name="See Enemy?"))
patrol.children.append(ActionNode(name="Attack"))
root.children.append(patrol)

tree = BehaviourTree(root=root)
```

## Navigation Mesh
```python
from imikino.inyenzure import NavigationMesh, NavMeshAgentComponent

navmesh = NavigationMesh(vertices=[...], triangles=[...])
agent = NavMeshAgentComponent(speed=5.0, nav_mesh=navmesh)
agent.set_destination(Vector3(10, 0, 10))
```

## Dialogue System
```python
from imikino.inyenzure import DialogueSystem, DialogueNode

dialogue = DialogueSystem()
root = DialogueNode(text="Hello, traveler!")
root.responses["Who are you?"] = DialogueNode(text="I am the village elder.")
root.responses["Goodbye"] = DialogueNode(text="Farewell!")

dialogue.register("elder", root)
dialogue.start("elder")
```
