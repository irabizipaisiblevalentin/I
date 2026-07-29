"""I Developer Platform — Learning Platform (Amashuri)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ibikoreshingiro import (
    Achievement,
    AchievementType,
    Assignment,
    AssignmentStatus,
    Course,
    CourseLevel,
    LearningPath,
    Lesson,
    Module,
)


class LearningPlatform:
    def __init__(self):
        self._courses: Dict[str, Course] = {}
        self._enrollments: Dict[str, List[str]] = {}
        self._progress: Dict[str, Dict[str, float]] = {}
        self._playground_sessions: List[Dict[str, Any]] = []
        self._challenges: List[Dict[str, Any]] = []
        self._teacher_resources: List[Dict[str, Any]] = []
        self._university_curricula: List[Dict[str, Any]] = []
        self._learning_paths: Dict[str, LearningPath] = {}
        self._path_enrollments: Dict[str, set] = {}
        self._achievements: List[Achievement] = []
        self._assignments: Dict[str, Assignment] = {}

    def add_course(self, course: Course) -> str:
        if not course.id:
            course.id = f"course_{len(self._courses) + 1}"
        self._courses[course.id] = course
        return course.id

    def get_course(self, course_id: str) -> Optional[Course]:
        return self._courses.get(course_id)

    def search_courses(self, query: str, level: Optional[CourseLevel] = None) -> List[Course]:
        q = query.lower()
        results = []
        for course in self._courses.values():
            if level and course.level != level:
                continue
            if q in course.title.lower() or q in course.description.lower() or any(q in t.lower() for t in course.tags):
                results.append(course)
        return results

    def enroll(self, user_id: str, course_id: str) -> bool:
        if course_id not in self._courses:
            return False
        self._enrollments.setdefault(course_id, [])
        if user_id not in self._enrollments[course_id]:
            self._enrollments[course_id].append(user_id)
            self._courses[course_id].enrolled_count = len(self._enrollments[course_id])
        return True

    def update_progress(self, user_id: str, course_id: str, lesson_id: str, progress: float) -> None:
        self._progress.setdefault(user_id, {})
        key = f"{course_id}:{lesson_id}"
        old = self._progress[user_id].get(key, 0.0)
        self._progress[user_id][key] = max(old, progress)
        if progress >= 1.0:
            course = self._courses.get(course_id)
            if course:
                completed = sum(1 for k, v in self._progress[user_id].items() if k.startswith(f"{course_id}:") and v >= 1.0)
                total = sum(len(m.lessons) for m in course.modules)
                if total > 0:
                    course.completion_rate = (completed / total) * 100

    def get_progress(self, user_id: str, course_id: str) -> float:
        keys = [k for k in self._progress.get(user_id, {}) if k.startswith(f"{course_id}:")]
        if not keys:
            return 0.0
        return sum(self._progress[user_id][k] for k in keys) / len(keys)

    def create_playground_session(self, code: str, language: str = "i") -> Dict[str, Any]:
        session = {
            "id": f"play_{len(self._playground_sessions) + 1}",
            "code": code,
            "language": language,
            "output": "",
        }
        self._playground_sessions.append(session)
        return session

    def add_challenge(self, title: str, description: str, difficulty: str = "easy") -> Dict[str, Any]:
        challenge = {
            "id": f"challenge_{len(self._challenges) + 1}",
            "title": title,
            "description": description,
            "difficulty": difficulty,
            "solutions_count": 0,
        }
        self._challenges.append(challenge)
        return challenge

    def get_challenges(self, difficulty: Optional[str] = None) -> List[Dict[str, Any]]:
        if difficulty:
            return [c for c in self._challenges if c["difficulty"] == difficulty]
        return list(self._challenges)

    def add_teacher_resource(self, title: str, resource_type: str, content: str) -> Dict[str, Any]:
        resource = {"id": f"resource_{len(self._teacher_resources) + 1}", "title": title, "type": resource_type, "content": content}
        self._teacher_resources.append(resource)
        return resource

    def add_university_curriculum(self, name: str, courses: List[str],credits: int = 0) -> Dict[str, Any]:
        curriculum = {"id": f"curriculum_{len(self._university_curricula) + 1}", "name": name, "courses": courses, "credits": credits}
        self._university_curricula.append(curriculum)
        return curriculum

    def get_enrolled_courses(self, user_id: str) -> List[Course]:
        return [self._courses[cid] for cid, users in self._enrollments.items() if user_id in users]

    # ── I Academy: Learning Paths ──────────────────────────────────────

    def create_learning_path(self, path: LearningPath) -> str:
        if not path.id:
            path.id = f"path_{len(self._learning_paths) + 1}"
        self._learning_paths[path.id] = path
        return path.id

    def get_learning_path(self, path_id: str) -> Optional[LearningPath]:
        return self._learning_paths.get(path_id)

    def list_learning_paths(self, level: Optional[CourseLevel] = None) -> List[LearningPath]:
        if level:
            return [p for p in self._learning_paths.values() if p.level == level]
        return list(self._learning_paths.values())

    def enroll_in_path(self, user_id: str, path_id: str) -> bool:
        path = self._learning_paths.get(path_id)
        if not path:
            return False
        self._path_enrollments.setdefault(path_id, set()).add(user_id)
        for cid in path.course_ids:
            self.enroll(user_id, cid)
        return True

    def get_path_progress(self, user_id: str, path_id: str) -> float:
        path = self._learning_paths.get(path_id)
        if not path or not path.course_ids:
            return 0.0
        scores = [self.get_progress(user_id, cid) for cid in path.course_ids]
        return sum(scores) / len(scores)

    # ── I Academy: Achievements ────────────────────────────────────────

    def award_achievement(self, achievement: Achievement) -> str:
        if not achievement.id:
            achievement.id = f"ach_{len(self._achievements) + 1}"
        self._achievements.append(achievement)
        return achievement.id

    def get_user_achievements(self, user_id: str) -> List[Achievement]:
        return [a for a in self._achievements if a.user_id == user_id]

    def check_course_achievements(self, user_id: str, course_id: str) -> List[Achievement]:
        earned = []
        prog = self.get_progress(user_id, course_id)
        if prog >= 1.0:
            ach = Achievement(
                user_id=user_id, type=AchievementType.COURSE_COMPLETE,
                title="Course Complete", description=f"Completed course {course_id}",
                progress=1.0,
            )
            self.award_achievement(ach)
            earned.append(ach)
        return earned

    # ── I Playground: Sandbox ──────────────────────────────────────────

    def create_playground_session(self, code: str, language: str = "i") -> Dict[str, Any]:
        session = {
            "id": f"play_{len(self._playground_sessions) + 1}",
            "code": code,
            "language": language,
            "output": "",
            "share_url": "",
        }
        self._playground_sessions.append(session)
        return session

    def share_playground_session(self, session_id: str) -> Optional[str]:
        for s in self._playground_sessions:
            if s["id"] == session_id:
                url = f"https://i-lang.org/play/{session_id}"
                s["share_url"] = url
                return url
        return None

    def fork_playground_session(self, session_id: str, new_code: str = "") -> Optional[Dict[str, Any]]:
        for s in self._playground_sessions:
            if s["id"] == session_id:
                return self.create_playground_session(new_code or s["code"], s["language"])
        return None

    def get_playground_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        for s in self._playground_sessions:
            if s["id"] == session_id:
                return s
        return None

    def run_playground_code(self, session_id: str) -> Optional[str]:
        for s in self._playground_sessions:
            if s["id"] == session_id:
                s["output"] = f"[sandbox] Executed {len(s['code'])} chars of {s['language']} code"
                return s["output"]
        return None

    # ── I Classroom: Assignments & Grading ─────────────────────────────

    def create_assignment(self, assignment: Assignment) -> str:
        if not assignment.id:
            assignment.id = f"assign_{len(self._assignments) + 1}"
        self._assignments[assignment.id] = assignment
        return assignment.id

    def get_assignment(self, assignment_id: str) -> Optional[Assignment]:
        return self._assignments.get(assignment_id)

    def list_assignments(self, course_id: str) -> List[Assignment]:
        return [a for a in self._assignments.values() if a.course_id == course_id]

    def submit_assignment(self, assignment_id: str, user_id: str, content: str, files: Optional[List[str]] = None) -> bool:
        assignment = self._assignments.get(assignment_id)
        if not assignment:
            return False
        submission = {
            "user_id": user_id,
            "content": content,
            "files": files or [],
            "submitted_at": "",
            "score": None,
            "feedback": "",
        }
        assignment.submissions.append(submission)
        assignment.status = AssignmentStatus.SUBMITTED
        return True

    def grade_submission(self, assignment_id: str, user_id: str, score: int, feedback: str) -> bool:
        assignment = self._assignments.get(assignment_id)
        if not assignment:
            return False
        for sub in assignment.submissions:
            if sub["user_id"] == user_id:
                sub["score"] = min(score, assignment.max_score)
                sub["feedback"] = feedback
                assignment.status = AssignmentStatus.GRADED
                return True
        return False

    def get_student_dashboard(self, user_id: str) -> Dict[str, Any]:
        enrolled = self.get_enrolled_courses(user_id)
        achievements = self.get_user_achievements(user_id)
        total_progress = sum(self.get_progress(user_id, c.id) for c in enrolled)
        avg_progress = (total_progress / len(enrolled) * 100) if enrolled else 0.0
        return {
            "user_id": user_id,
            "enrolled_courses": len(enrolled),
            "average_progress_pct": round(avg_progress, 1),
            "achievements": len(achievements),
            "completed_lessons": sum(1 for k, v in self._progress.get(user_id, {}).items() if v >= 1.0),
        }

    # ── I Academy: Search Helper ───────────────────────────────────────

    def search_learning_paths(self, query: str) -> List[LearningPath]:
        q = query.lower()
        return [p for p in self._learning_paths.values()
                if q in p.title.lower() or q in p.description.lower()]
