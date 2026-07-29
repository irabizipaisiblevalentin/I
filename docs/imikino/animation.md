# Animation Guide

## Skeleton
```python
from imikino.imikorere_animation import Skeleton

skeleton = Skeleton()
root = skeleton.add_bone("hips")
spine = skeleton.add_bone("spine", parent=root)
head = skeleton.add_bone("head", parent=spine)
```

## Animation Clips
```python
from imikino.imikorere_animation import AnimationClip, AnimationCurve, Keyframe

clip = AnimationClip(name="walk", duration=1.0)
curve = AnimationCurve(keyframes=[
    Keyframe(time=0.0, value=0.0),
    Keyframe(time=0.5, value=1.0),
    Keyframe(time=1.0, value=0.0),
])
clip.curves["head"]["rotation_x"] = curve
```

## Animator
```python
from imikino.imikorere_animation import AnimatorComponent

animator = AnimatorComponent()
animator.add_state("idle", idle_clip)
animator.add_state("walk", walk_clip)
animator.play("walk")
```
