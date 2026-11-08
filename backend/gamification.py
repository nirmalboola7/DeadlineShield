from datetime import datetime, timezone


# XP awarded for each activity type
BASE_POINTS = {
    "Assignment": 20,
    "Project": 50,
    "Exam": 30,
    "Lab Record": 20,
    "Other": 10
}


def calculate_points(activity):
    points = BASE_POINTS.get(activity.get("activity_type"), 10)

    try:
        due = datetime.fromisoformat(
            activity["due_date"].replace("Z", "+00:00")
        )

        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)

        if activity.get("completed_at"):
            completed = datetime.fromisoformat(
                activity["completed_at"].replace("Z", "+00:00")
            )
            if completed <= due:
                points += 10

    except (ValueError, TypeError, KeyError):
        pass

    return points


def get_student_performance(db):
    awards = db.setdefault("completion_awards", [])
    students = []

    for user in db.get("users", []):
        user_id = user["user_id"]

        student_awards = [
            a for a in awards
            if a["user_id"] == user_id
        ]

        completed_count = len(student_awards)

        xp = sum(a["points"] for a in student_awards)

        projects = sum(
            1 for a in student_awards
            if a.get("activity_type") == "Project"
        )

        exams = sum(
            1 for a in student_awards
            if a.get("activity_type") == "Exam"
        )

        badges = []

        definitions = [
            ("First Step", "🌱", "Complete your first activity",
             completed_count >= 1),

            ("Focused Learner", "🔥", "Complete 5 activities",
             completed_count >= 5),

            ("Task Master", "🏆", "Complete 10 activities",
             completed_count >= 10),

            ("Project Finisher", "🚀", "Complete 2 projects",
             projects >= 2),

            ("Exam Champion", "🎓", "Complete 2 exams",
             exams >= 2),

            ("XP Champion", "💎", "Earn 500 XP",
             xp >= 500),
        ]

        for name, icon, description, earned in definitions:
            if earned:
                badges.append({
                    "name": name,
                    "icon": icon,
                    "description": description
                })

        students.append({
            "user_id": user_id,
            "name": user.get("name", "Student"),
            "college": user.get("college", ""),
            "department": user.get("department", ""),
            "xp": xp,
            "completed": completed_count,
            "projects": projects,
            "exams": exams,
            "badges": badges
        })

    students.sort(
        key=lambda s: (-s["xp"], -s["completed"], s["name"].lower())
    )

    for index, student in enumerate(students, start=1):
        student["rank"] = index

    return students


def award_completion(db, activity):
    db.setdefault("completion_awards", [])

    already_awarded = any(
        a["activity_id"] == activity["activity_id"]
        for a in db["completion_awards"]
    )

    if already_awarded:
        return 0

    points = calculate_points(activity)

    db["completion_awards"].append({
        "activity_id": activity["activity_id"],
        "user_id": activity["user_id"],
        "activity_type": activity["activity_type"],
        "points": points,
        "awarded_at": datetime.now(timezone.utc).isoformat()
    })

    return points