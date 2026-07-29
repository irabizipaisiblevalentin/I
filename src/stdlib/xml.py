"""xml — XML parsing and generation for the I language.

Provides lightweight XML parsing and element tree operations.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse(source: str) -> ET.ElementTree:
    """Parse XML string or file path."""
    if "<" in source:
        return ET.fromstring(source)
    return ET.parse(source)


def from_string(s: str) -> ET.Element:
    """Parse XML string, return root element."""
    return ET.fromstring(s)


def from_file(path: str) -> ET.ElementTree:
    """Parse XML file."""
    return ET.parse(path)


# ---------------------------------------------------------------------------
# Element operations
# ---------------------------------------------------------------------------

def tag(elem: ET.Element) -> str:
    """Element tag name."""
    return elem.tag


def text(elem: ET.Element) -> Optional[str]:
    """Element text content."""
    return elem.text


def attrs(elem: ET.Element) -> Dict[str, str]:
    """Element attributes as dict."""
    return dict(elem.attrib)


def attr(elem: ET.Element, name: str, default: str = "") -> str:
    """Get attribute value with default."""
    return elem.get(name, default)


def children(elem: ET.Element) -> List[ET.Element]:
    """List of child elements."""
    return list(elem)


def find(elem: ET.Element, path: str) -> Optional[ET.Element]:
    """Find first matching child."""
    return elem.find(path)


def findall(elem: ET.Element, path: str) -> List[ET.Element]:
    """Find all matching children."""
    return elem.findall(path)


def findtext(elem: ET.Element, path: str, default: str = "") -> str:
    """Find text of first matching child."""
    return elem.findtext(path, default)


def parent(root: ET.Element, child: ET.Element) -> Optional[ET.Element]:
    """Find parent of child element."""
    for elem in root.iter():
        for c in elem:
            if c is child:
                return elem
    return None


# ---------------------------------------------------------------------------
# Building
# ---------------------------------------------------------------------------

def make_element(tag: str, text: Optional[str] = None,
                 attrib: Optional[Dict[str, str]] = None) -> ET.Element:
    """Create a new XML element."""
    elem = ET.Element(tag, attrib or {})
    if text is not None:
        elem.text = text
    return elem


def make_tree(root_tag: str, children: Optional[List[ET.Element]] = None,
              attrib: Optional[Dict[str, str]] = None) -> ET.Element:
    """Create an XML tree with root element."""
    root = make_element(root_tag, attrib=attrib)
    for child in (children or []):
        root.append(child)
    return root


def add_child(parent: ET.Element, tag: str, text: Optional[str] = None,
              attrib: Optional[Dict[str, str]] = None) -> ET.Element:
    """Add a child element."""
    child = make_element(tag, text, attrib)
    parent.append(child)
    return child


def set_attr(elem: ET.Element, name: str, value: str) -> None:
    """Set attribute on element."""
    elem.set(name, value)


def remove_child(parent: ET.Element, child: ET.Element) -> None:
    """Remove child from parent."""
    parent.remove(child)


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

def to_string(elem: ET.Element, encoding: str = "unicode") -> str:
    """Serialize element to string."""
    return ET.tostring(elem, encoding=encoding)


def to_file(elem: ET.Element, path: str, encoding: str = "utf-8") -> None:
    """Serialize element tree to file."""
    tree = ET.ElementTree(elem)
    ET.indent(tree)
    tree.write(path, encoding=encoding, xml_declaration=True)


def pretty(elem: ET.Element) -> str:
    """Pretty-print XML."""
    ET.indent(elem)
    return to_string(elem)


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

def xpath(root: ET.Element, path: str) -> List[ET.Element]:
    """Simple XPath-like query (uses findall)."""
    return root.findall(path)


def get_text(elem: ET.Element, path: str, default: str = "") -> str:
    """Get text content by path."""
    found = elem.find(path)
    if found is not None and found.text:
        return found.text
    return default
