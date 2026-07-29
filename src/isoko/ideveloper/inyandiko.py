"""I Developer Platform — Documentation Platform (Inyandiko)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class DocumentationPlatform:
    def __init__(self):
        self._versions: List[str] = ["0.1.0"]
        self._docs: Dict[str, Dict[str, str]] = {}
        self._guides: List[Dict[str, Any]] = []
        self._tutorials: List[Dict[str, Any]] = []
        self._search_index: Dict[str, List[str]] = {}
        self._translations: Dict[str, Dict[str, str]] = {}
        self._offline_packs: List[str] = []
        self._textbooks: Dict[str, Dict[str, Any]] = {}
        self._annotations: Dict[str, List[Dict[str, Any]]] = {}

    def add_version(self, version: str) -> None:
        if version not in self._versions:
            self._versions.append(version)
            self._versions.sort()

    def get_versions(self) -> List[str]:
        return list(self._versions)

    def set_document(self, path: str, content: str, version: str = "0.1.0") -> None:
        self._docs.setdefault(version, {})[path] = content
        self._index_search(path, content)

    def get_document(self, path: str, version: str = "0.1.0") -> Optional[str]:
        return self._docs.get(version, {}).get(path)

    def _index_search(self, path: str, content: str) -> None:
        for word in content.lower().split()[:200]:
            if len(word) > 3:
                self._search_index.setdefault(word, []).append(path)

    def search(self, query: str, version: str = "0.1.0") -> List[str]:
        words = query.lower().split()
        results = set()
        for w in words:
            for key, paths in self._search_index.items():
                if w in key:
                    results.update(paths)
        return [p for p in results if version in self._docs and p in self._docs[version]]

    def add_guide(self, title: str, content: str, category: str = "general") -> Dict[str, Any]:
        guide = {"id": f"guide_{len(self._guides) + 1}", "title": title, "content": content, "category": category}
        self._guides.append(guide)
        return guide

    def get_guides(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        if category:
            return [g for g in self._guides if g["category"] == category]
        return list(self._guides)

    def add_tutorial(self, title: str, steps: List[str], difficulty: str = "beginner") -> Dict[str, Any]:
        tutorial = {
            "id": f"tutorial_{len(self._tutorials) + 1}",
            "title": title,
            "steps": steps,
            "difficulty": difficulty,
        }
        self._tutorials.append(tutorial)
        return tutorial

    def get_tutorials(self, difficulty: Optional[str] = None) -> List[Dict[str, Any]]:
        if difficulty:
            return [t for t in self._tutorials if t["difficulty"] == difficulty]
        return list(self._tutorials)

    def set_translation(self, locale: str, path: str, content: str) -> None:
        self._translations.setdefault(locale, {})[path] = content

    def get_translation(self, locale: str, path: str) -> Optional[str]:
        return self._translations.get(locale, {}).get(path)

    def add_offline_pack(self, version: str) -> str:
        pack_id = f"offline_{version}_{len(self._offline_packs)}"
        self._offline_packs.append(pack_id)
        return pack_id

    def get_offline_packs(self) -> List[str]:
        return list(self._offline_packs)

    def get_api_reference(self, symbol: str, version: str = "0.1.0") -> Optional[Dict[str, str]]:
        for path, content in self._docs.get(version, {}).items():
            if path.endswith(f"/{symbol}") or f"/{symbol}." in path:
                return {"path": path, "content": content, "symbol": symbol}
        return None

    # ── I Books: Interactive Textbooks ─────────────────────────────────

    def create_textbook(self, book_id: str, title: str, author: str, description: str = "") -> Dict[str, Any]:
        book = {
            "id": book_id,
            "title": title,
            "author": author,
            "description": description,
            "version": "1.0",
            "chapters": [],
            "is_interactive": True,
            "license": "CC-BY-SA",
        }
        self._textbooks[book_id] = book
        return book

    def get_textbook(self, book_id: str) -> Optional[Dict[str, Any]]:
        return self._textbooks.get(book_id)

    def list_textbooks(self) -> List[Dict[str, Any]]:
        return list(self._textbooks.values())

    def add_chapter(self, book_id: str, title: str, content: str, exercises: Optional[List[Dict[str, Any]]] = None) -> bool:
        book = self._textbooks.get(book_id)
        if not book:
            return False
        chapter = {
            "id": f"ch{len(book['chapters']) + 1}",
            "title": title,
            "content": content,
            "exercises": exercises or [],
        }
        book["chapters"].append(chapter)
        return True

    def get_chapter(self, book_id: str, chapter_id: str) -> Optional[Dict[str, Any]]:
        book = self._textbooks.get(book_id)
        if not book:
            return None
        for ch in book["chapters"]:
            if ch["id"] == chapter_id:
                return ch
        return None

    def add_exercise(self, book_id: str, chapter_id: str, question: str, answer: str, exercise_type: str = "quiz") -> bool:
        book = self._textbooks.get(book_id)
        if not book:
            return False
        for ch in book["chapters"]:
            if ch["id"] == chapter_id:
                ch["exercises"].append({
                    "id": f"ex{len(ch['exercises']) + 1}",
                    "type": exercise_type,
                    "question": question,
                    "answer": answer,
                })
                return True
        return False

    def check_exercise(self, book_id: str, chapter_id: str, exercise_id: str, user_answer: str) -> Optional[Dict[str, bool]]:
        book = self._textbooks.get(book_id)
        if not book:
            return None
        for ch in book["chapters"]:
            if ch["id"] == chapter_id:
                for ex in ch["exercises"]:
                    if ex["id"] == exercise_id:
                        return {"correct": user_answer.strip().lower() == ex["answer"].strip().lower()}
        return None

    def add_annotation(self, user_id: str, doc_path: str, content: str, selection: str = "") -> Dict[str, Any]:
        annotation = {
            "id": f"ann_{len(self._annotations.get(doc_path, [])) + 1}",
            "user_id": user_id,
            "doc_path": doc_path,
            "content": content,
            "selection": selection,
            "created_at": "",
        }
        self._annotations.setdefault(doc_path, []).append(annotation)
        return annotation

    def get_annotations(self, doc_path: str) -> List[Dict[str, Any]]:
        return self._annotations.get(doc_path, [])
