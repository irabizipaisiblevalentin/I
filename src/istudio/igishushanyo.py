"""I STUDIO — Visual Designers (Igishushanyo)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class UIComponent:
    id: str
    type: str = "container"
    label: str = ""
    x: int = 0
    y: int = 0
    width: int = 100
    height: int = 50
    properties: Dict[str, Any] = field(default_factory=dict)
    children: List[UIComponent] = field(default_factory=list)
    events: Dict[str, str] = field(default_factory=dict)
    bindings: Dict[str, str] = field(default_factory=dict)

@dataclass
class FormField:
    name: str
    type: str = "text"
    label: str = ""
    placeholder: str = ""
    required: bool = False
    default_value: Any = None
    validation: Dict[str, Any] = field(default_factory=dict)
    options: List[str] = field(default_factory=list)

@dataclass
class FormLayout:
    title: str = ""
    fields: List[FormField] = field(default_factory=list)
    submit_label: str = "Submit"
    layout: str = "vertical"


class VisualDesigner:
    def __init__(self):
        self._components: Dict[str, UIComponent] = {}
        self._clipboard: Optional[UIComponent] = None

    def add_component(self, component: UIComponent) -> str:
        self._components[component.id] = component
        return component.id

    def remove_component(self, component_id: str) -> bool:
        return self._components.pop(component_id, None) is not None

    def get_component(self, component_id: str) -> Optional[UIComponent]:
        return self._components.get(component_id)

    def update_component(self, component_id: str, **kwargs) -> Optional[UIComponent]:
        component = self._components.get(component_id)
        if not component:
            return None
        for key, value in kwargs.items():
            if hasattr(component, key):
                setattr(component, key, value)
        return component

    def list_components(self) -> List[UIComponent]:
        return list(self._components.values())

    def copy_component(self, component_id: str) -> Optional[str]:
        component = self._components.get(component_id)
        if not component:
            return None
        import copy
        new_component = copy.deepcopy(component)
        new_component.id = f"{component.id}_copy"
        self._components[new_component.id] = new_component
        self._clipboard = new_component
        return new_component.id

    def add_child(self, parent_id: str, child: UIComponent) -> bool:
        parent = self._components.get(parent_id)
        if not parent:
            return False
        parent.children.append(child)
        self._components[child.id] = child
        return True

    def remove_child(self, parent_id: str, child_id: str) -> bool:
        parent = self._components.get(parent_id)
        if not parent:
            return False
        parent.children = [c for c in parent.children if c.id != child_id]
        self._components.pop(child_id, None)
        return True

    def generate_code(self, component_id: str, language: str = "i") -> str:
        component = self._components.get(component_id)
        if not component:
            return ""
        return self._render_component(component, language, 0)

    def _render_component(self, component: UIComponent, language: str, indent: int) -> str:
        pad = "    " * indent
        if component.type == "container":
            code = f"{pad}{component.id} = container()\n"
            for child in component.children:
                code += self._render_component(child, language, indent + 1)
            return code
        elif component.type == "button":
            return f"{pad}{component.id} = button(label=\"{component.label}\")\n"
        elif component.type == "label":
            return f"{pad}{component.id} = label(text=\"{component.label}\")\n"
        elif component.type == "input":
            return f"{pad}{component.id} = input(placeholder=\"{component.properties.get('placeholder', '')}\")\n"
        elif component.type == "image":
            return f"{pad}{component.id} = image(src=\"{component.properties.get('src', '')}\")\n"
        elif component.type == "table":
            return f"{pad}{component.id} = table(columns={component.properties.get('columns', [])})\n"
        else:
            return f"{pad}{component.id} = {component.type}({component.label})\n"

    def generate_form_code(self, form: FormLayout, language: str = "i") -> str:
        code = f"form = form_layout(title=\"{form.title}\")\n"
        for field in form.fields:
            code += f"form.add_field(name=\"{field.name}\", type=\"{field.type}\", label=\"{field.label}\""
            if field.placeholder:
                code += f", placeholder=\"{field.placeholder}\""
            if field.required:
                code += ", required=True"
            if field.default_value is not None:
                code += f", default={field.default_value}"
            code += ")\n"
        return code

    def clear(self) -> None:
        self._components.clear()
        self._clipboard = None


class FormDesigner:
    def __init__(self):
        self._forms: Dict[str, FormLayout] = {}

    def create_form(self, name: str, title: str = "") -> FormLayout:
        form = FormLayout(title=title or name)
        self._forms[name] = form
        return form

    def add_field(self, form_name: str, field: FormField) -> bool:
        form = self._forms.get(form_name)
        if not form:
            return False
        form.fields.append(field)
        return True

    def remove_field(self, form_name: str, field_name: str) -> bool:
        form = self._forms.get(form_name)
        if not form:
            return False
        form.fields = [f for f in form.fields if f.name != field_name]
        return True

    def get_form(self, name: str) -> Optional[FormLayout]:
        return self._forms.get(name)

    def list_forms(self) -> List[Dict[str, Any]]:
        return [{"name": n, "fields": len(f.fields), "title": f.title} for n, f in self._forms.items()]
