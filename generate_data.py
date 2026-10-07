import random
import hashlib
from datetime import datetime, timedelta

from faker import Faker
import numpy as np

from config import RANDOM_SEED
from db import execute_script, bulk_insert


# ============================================================
# INITIALIZATION
# ============================================================

fake = Faker()

Faker.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ============================================================
# CONSTANTS
# ============================================================

BASE_DIR = __import__("os").path.dirname(
    __import__("os").path.abspath(__file__)
)

SCHEMA_FILE = __import__("os").path.join(
    BASE_DIR,
    "schema.sql"
)


# ============================================================
# MAIN DATA GENERATOR
# ============================================================

def generate_all_data():

    print("=" * 60)
    print("       DEVPULSE ANALYTICS DATABASE INITIALIZATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Create / Reset Database
    # --------------------------------------------------------

    print("\n[1/8] Initializing database schema...")

    execute_script(SCHEMA_FILE)

    print("Database schema created successfully.")


    # --------------------------------------------------------
    # Date Range
    # --------------------------------------------------------

    end_date = datetime.now()

    start_date = end_date - timedelta(days=365)

    print(
        f"\nGenerating data from "
        f"{start_date.date()} to {end_date.date()}"
    )


    # ========================================================
    # 1. DEVELOPERS
    # ========================================================

    print("\n[2/8] Generating developers...")

    teams = [
        "Platform",
        "Backend",
        "Frontend",
        "Mobile",
        "Data",
        "DevOps"
    ]

    roles = [
        "Engineer",
        "Senior Engineer",
        "Staff Engineer",
        "Engineering Manager",
        "QA Engineer"
    ]

    dev_rows = []

    for i in range(1, 61):

        dev_rows.append(
            (
                fake.name(),
                fake.unique.email(),
                random.choice(teams),
                random.choice(roles),

                fake.date_between(
                    start_date=start_date - timedelta(days=700),
                    end_date=start_date
                ),

                1 if i <= 54 else 0
            )
        )

    bulk_insert(
        "developers",
        [
            "full_name",
            "email",
            "team",
            "role",
            "hire_date",
            "is_active"
        ],
        dev_rows
    )

    print("60 developers created.")


    # ========================================================
    # 2. PROJECTS
    # ========================================================

    print("\n[3/8] Generating projects...")

    project_names = [
        "Payments Gateway",
        "Customer Portal",
        "Mobile App",
        "Data Pipeline",
        "Auth Service",
        "Analytics Engine",
        "Notification Hub",
        "Internal Tools"
    ]

    project_rows = []

    project_statuses = [
        "planning",
        "active",
        "completed"
    ]

    priorities = [
        "low",
        "medium",
        "high",
        "critical"
    ]

    for project_id, name in enumerate(project_names, start=1):

        project_rows.append(
            (
                name,

                f"Core system component for {name}",

                random.choice(project_statuses),

                random.choice(priorities),

                start_date.date(),

                end_date.date(),

                random.randint(1, 60)
            )
        )

    bulk_insert(
        "projects",
        [
            "name",
            "description",
            "status",
            "priority",
            "start_date",
            "target_end_date",
            "lead_developer_id"
        ],
        project_rows
    )

    print("8 projects created.")


    # ========================================================
    # 3. REPOSITORIES
    # ========================================================

    print("\n[4/8] Generating repositories...")

    repo_rows = []

    languages = [
        "Python",
        "Java",
        "TypeScript",
        "Go",
        "Kotlin",
        "SQL"
    ]

    for project_id in range(1, 9):

        for repo_number in range(1, 4):

            repo_rows.append(
                (
                    project_id,

                    f"repo-{project_id}-{repo_number}",

                    random.choice(languages),

                    0,

                    start_date
                )
            )

    bulk_insert(
        "repositories",
        [
            "project_id",
            "name",
            "primary_language",
            "is_archived",
            "created_at"
        ],
        repo_rows
    )

    print("24 repositories created.")


    # ========================================================
    # 4. SPRINTS
    # ========================================================

    print("\n[5/8] Generating sprints...")

    sprint_rows = []

    sprint_id = 1

    sprint_map = {}

    for project_id in range(1, 9):

        sprint_start = start_date

        for sprint_number in range(1, 13):

            sprint_end = sprint_start + timedelta(days=14)

            planned_points = random.randint(30, 80)

            # Keep completion realistic.
            completion_ratio = random.uniform(
                0.65,
                1.0
            )

            completed_points = int(
                planned_points * completion_ratio
            )

            if completed_points < 1:
                completed_points = 1

            if sprint_end <= end_date:

                status = "completed"

            else:

                status = "active"

            sprint_rows.append(
                (
                    project_id,

                    f"Sprint {sprint_number}",

                    sprint_start.date(),

                    sprint_end.date(),

                    planned_points,

                    completed_points,

                    status
                )
            )

            sprint_map[
                (project_id, sprint_number)
            ] = sprint_id

            sprint_id += 1

            sprint_start = sprint_end

    bulk_insert(
        "sprints",
        [
            "project_id",
            "name",
            "start_date",
            "end_date",
            "planned_points",
            "completed_points",
            "status"
        ],
        sprint_rows
    )

    print("96 sprints created.")


    # ========================================================
    # 5. ISSUES
    # ========================================================

    print("\n[6/8] Generating issues...")

    issue_rows = []

    issue_types = [
        "bug",
        "feature",
        "task",
        "improvement"
    ]

    issue_priorities = [
        "low",
        "medium",
        "high",
        "critical"
    ]

    story_points_options = [
        1,
        2,
        3,
        5,
        8,
        13
    ]

    issue_count = 3500

    for i in range(issue_count):

        project_id = random.randint(1, 8)

        # Each project has 3 repositories
        repo_number = random.randint(1, 3)

        repo_id = (
            (project_id - 1) * 3
            + repo_number
        )

        # Each project has 12 sprints
        sprint_number = random.randint(1, 12)

        sprint_id = sprint_map[
            (project_id, sprint_number)
        ]

        reporter_id = random.randint(1, 60)

        assignee_id = random.randint(1, 60)

        created_at = fake.date_time_between(
            start_date=start_date,
            end_date=end_date
        )

        # 80% resolved
        is_resolved = random.random() < 0.80

        if is_resolved:

            resolved_at = created_at + timedelta(
                hours=random.randint(2, 120)
            )

            status = random.choice(
                [
                    "resolved",
                    "closed"
                ]
            )

        else:

            resolved_at = None

            status = random.choice(
                [
                    "open",
                    "in_progress"
                ]
            )

        issue_rows.append(
            (
                project_id,

                repo_id,

                sprint_id,

                reporter_id,

                assignee_id,

                fake.sentence(
                    nb_words=6
                ),

                random.choice(issue_types),

                random.choice(issue_priorities),

                status,

                random.choice(
                    story_points_options
                ),

                created_at,

                resolved_at
            )
        )

    bulk_insert(
        "issues",
        [
            "project_id",
            "repo_id",
            "sprint_id",
            "reporter_id",
            "assignee_id",
            "title",
            "issue_type",
            "priority",
            "status",
            "story_points",
            "created_at",
            "resolved_at"
        ],
        issue_rows
    )

    print("3,500 issues created.")


    # ========================================================
    # 6. PULL REQUESTS
    # ========================================================

    print("\n[7/8] Generating pull requests...")

    pr_rows = []

    pr_count = 2200

    for i in range(pr_count):

        repo_id = random.randint(1, 24)

        author_id = random.randint(1, 60)

        # Ensure reviewer is different
        reviewer_id = random.randint(1, 60)

        while reviewer_id == author_id:
            reviewer_id = random.randint(1, 60)

        issue_id = random.randint(
            1,
            issue_count
        )

        created_at = fake.date_time_between(
            start_date=start_date,
            end_date=end_date
        )

        status = random.choice(
            [
                "open",
                "merged",
                "merged",
                "merged",
                "closed"
            ]
        )

        # Review time
        first_review_at = created_at + timedelta(
            hours=random.randint(1, 48)
        )

        if status == "merged":

            merged_at = first_review_at + timedelta(
                hours=random.randint(1, 72)
            )

        else:

            merged_at = None

        lines_added = random.randint(
            5,
            1500
        )

        lines_deleted = random.randint(
            0,
            700
        )

        files_changed = random.randint(
            1,
            25
        )

        review_comments = random.randint(
            0,
            30
        )

        pr_rows.append(
            (
                repo_id,

                author_id,

                reviewer_id,

                issue_id,

                fake.sentence(
                    nb_words=7
                ),

                status,

                created_at,

                first_review_at,

                merged_at,

                lines_added,

                lines_deleted,

                files_changed,

                review_comments
            )
        )

    bulk_insert(
        "pull_requests",
        [
            "repo_id",
            "author_id",
            "reviewer_id",
            "issue_id",
            "title",
            "status",
            "created_at",
            "first_review_at",
            "merged_at",
            "lines_added",
            "lines_deleted",
            "files_changed",
            "review_comments"
        ],
        pr_rows
    )

    print("2,200 pull requests created.")


    # ========================================================
    # 7. COMMITS
    # ========================================================

    print("\nGenerating commits...")

    commit_rows = []

    commit_count = 10000

    commit_messages = [
        "Fix authentication issue",
        "Update API endpoint",
        "Improve database performance",
        "Add validation logic",
        "Fix UI bug",
        "Implement new feature",
        "Refactor service layer",
        "Update documentation",
        "Optimize query",
        "Add unit tests",
        "Improve error handling",
        "Update configuration",
        "Fix deployment issue",
        "Add logging",
        "Improve security"
    ]

    for i in range(commit_count):

        repo_id = random.randint(
            1,
            24
        )

        developer_id = random.randint(
            1,
            60
        )

        # Approximately 60% of commits linked to PR
        if random.random() < 0.60:

            pr_id = random.randint(
                1,
                pr_count
            )

        else:

            pr_id = None

        committed_at = fake.date_time_between(
            start_date=start_date,
            end_date=end_date
        )

        # Create deterministic unique hash
        raw_hash = (
            f"{RANDOM_SEED}-"
            f"{i}-"
            f"{repo_id}-"
            f"{developer_id}-"
            f"{committed_at}"
        )

        commit_hash = hashlib.sha1(
            raw_hash.encode("utf-8")
        ).hexdigest()

        lines_added = random.randint(
            1,
            1000
        )

        lines_deleted = random.randint(
            0,
            500
        )

        commit_rows.append(
            (
                repo_id,

                developer_id,

                pr_id,

                commit_hash,

                random.choice(
                    commit_messages
                ),

                committed_at,

                lines_added,

                lines_deleted
            )
        )

    bulk_insert(
        "commits",
        [
            "repo_id",
            "developer_id",
            "pr_id",
            "commit_hash",
            "message",
            "committed_at",
            "lines_added",
            "lines_deleted"
        ],
        commit_rows
    )

    print("10,000 commits created.")


    # ========================================================
    # 8. DEPLOYMENTS
    # ========================================================

    print("\n[8/8] Generating deployments...")

    deployment_rows = []

    deployment_count = 1800

    for i in range(deployment_count):

        project_id = random.randint(
            1,
            8
        )

        # Three repositories per project
        repo_number = random.randint(
            1,
            3
        )

        repo_id = (
            (project_id - 1) * 3
            + repo_number
        )

        deployed_by = random.randint(
            1,
            60
        )

        environment = random.choice(
            [
                "staging",
                "production"
            ]
        )

        version = (
            f"{random.randint(1, 3)}."
            f"{random.randint(0, 9)}."
            f"{random.randint(0, 9)}"
        )

        status = random.choices(
            [
                "success",
                "failed",
                "rolled_back"
            ],
            weights=[
                82,
                10,
                8
            ],
            k=1
        )[0]

        deployed_at = fake.date_time_between(
            start_date=start_date,
            end_date=end_date
        )

        duration_seconds = random.randint(
            60,
            900
        )

        deployment_rows.append(
            (
                project_id,

                repo_id,

                deployed_by,

                environment,

                version,

                status,

                deployed_at,

                duration_seconds
            )
        )

    bulk_insert(
        "deployments",
        [
            "project_id",
            "repo_id",
            "deployed_by",
            "environment",
            "version",
            "status",
            "deployed_at",
            "duration_seconds"
        ],
        deployment_rows
    )

    print("1,800 deployments created.")


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 60)
    print("       DATABASE SEEDING COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print("""
    Developers       : 60
    Projects         : 8
    Repositories     : 24
    Sprints          : 96
    Issues           : 3,500
    Pull Requests    : 2,200
    Commits          : 10,000
    Deployments      : 1,800
    """)

    print("=" * 60)
    print("SQLite database: devpulse.db")
    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    generate_all_data()