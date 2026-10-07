-- ============================================================
-- DevPulse Analytics
-- SQLite Database Schema
-- ============================================================

PRAGMA foreign_keys = ON;


-- ============================================================
-- Remove Existing Tables
-- ============================================================

DROP TABLE IF EXISTS deployments;
DROP TABLE IF EXISTS commits;
DROP TABLE IF EXISTS pull_requests;
DROP TABLE IF EXISTS issues;
DROP TABLE IF EXISTS sprints;
DROP TABLE IF EXISTS repositories;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS developers;


-- ============================================================
-- 1. DEVELOPERS
-- ============================================================

CREATE TABLE developers (
    developer_id INTEGER PRIMARY KEY AUTOINCREMENT,

    full_name TEXT NOT NULL,

    email TEXT NOT NULL UNIQUE,

    team TEXT NOT NULL
        CHECK (
            team IN (
                'Platform',
                'Backend',
                'Frontend',
                'Mobile',
                'Data',
                'DevOps'
            )
        ),

    role TEXT NOT NULL
        CHECK (
            role IN (
                'Engineer',
                'Senior Engineer',
                'Staff Engineer',
                'Engineering Manager',
                'QA Engineer'
            )
        ),

    hire_date DATE NOT NULL,

    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 2. PROJECTS
-- ============================================================

CREATE TABLE projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL UNIQUE,

    description TEXT,

    status TEXT NOT NULL
        CHECK (
            status IN (
                'planning',
                'active',
                'on_hold',
                'completed'
            )
        ),

    priority TEXT NOT NULL
        CHECK (
            priority IN (
                'low',
                'medium',
                'high',
                'critical'
            )
        ),

    start_date DATE NOT NULL,

    target_end_date DATE,

    lead_developer_id INTEGER,

    FOREIGN KEY (lead_developer_id)
        REFERENCES developers(developer_id)
        ON DELETE SET NULL
);


-- ============================================================
-- 3. REPOSITORIES
-- ============================================================

CREATE TABLE repositories (
    repo_id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER NOT NULL,

    name TEXT NOT NULL UNIQUE,

    primary_language TEXT NOT NULL
        CHECK (
            primary_language IN (
                'Python',
                'Java',
                'TypeScript',
                'Go',
                'Kotlin',
                'SQL'
            )
        ),

    is_archived INTEGER DEFAULT 0
        CHECK (is_archived IN (0, 1)),

    created_at DATETIME NOT NULL,

    FOREIGN KEY (project_id)
        REFERENCES projects(project_id)
        ON DELETE CASCADE
);


-- ============================================================
-- 4. SPRINTS
-- ============================================================

CREATE TABLE sprints (
    sprint_id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER NOT NULL,

    name TEXT NOT NULL,

    start_date DATE NOT NULL,

    end_date DATE NOT NULL,

    planned_points INTEGER NOT NULL
        CHECK (planned_points > 0),

    completed_points INTEGER NOT NULL
        CHECK (completed_points >= 0),

    status TEXT NOT NULL
        CHECK (
            status IN (
                'planned',
                'active',
                'completed'
            )
        ),

    FOREIGN KEY (project_id)
        REFERENCES projects(project_id)
        ON DELETE CASCADE,

    CHECK (end_date > start_date)
);


-- ============================================================
-- 5. ISSUES
-- ============================================================

CREATE TABLE issues (
    issue_id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER NOT NULL,

    repo_id INTEGER,

    sprint_id INTEGER,

    reporter_id INTEGER NOT NULL,

    assignee_id INTEGER,

    title TEXT NOT NULL,

    issue_type TEXT NOT NULL
        CHECK (
            issue_type IN (
                'bug',
                'feature',
                'task',
                'improvement'
            )
        ),

    priority TEXT NOT NULL
        CHECK (
            priority IN (
                'low',
                'medium',
                'high',
                'critical'
            )
        ),

    status TEXT NOT NULL
        CHECK (
            status IN (
                'open',
                'in_progress',
                'resolved',
                'closed'
            )
        ),

    story_points INTEGER
        CHECK (
            story_points IN (
                1,
                2,
                3,
                5,
                8,
                13
            )
        ),

    created_at DATETIME NOT NULL,

    resolved_at DATETIME,

    FOREIGN KEY (project_id)
        REFERENCES projects(project_id)
        ON DELETE CASCADE,

    FOREIGN KEY (repo_id)
        REFERENCES repositories(repo_id)
        ON DELETE SET NULL,

    FOREIGN KEY (sprint_id)
        REFERENCES sprints(sprint_id)
        ON DELETE SET NULL,

    FOREIGN KEY (reporter_id)
        REFERENCES developers(developer_id),

    FOREIGN KEY (assignee_id)
        REFERENCES developers(developer_id)
        ON DELETE SET NULL,

    CHECK (
        resolved_at IS NULL
        OR resolved_at >= created_at
    )
);


-- ============================================================
-- 6. PULL REQUESTS
-- ============================================================

CREATE TABLE pull_requests (
    pr_id INTEGER PRIMARY KEY AUTOINCREMENT,

    repo_id INTEGER NOT NULL,

    author_id INTEGER NOT NULL,

    reviewer_id INTEGER,

    issue_id INTEGER,

    title TEXT NOT NULL,

    status TEXT NOT NULL
        CHECK (
            status IN (
                'open',
                'merged',
                'closed'
            )
        ),

    created_at DATETIME NOT NULL,

    first_review_at DATETIME,

    merged_at DATETIME,

    lines_added INTEGER NOT NULL
        CHECK (lines_added >= 0),

    lines_deleted INTEGER NOT NULL
        CHECK (lines_deleted >= 0),

    files_changed INTEGER NOT NULL
        CHECK (files_changed >= 0),

    review_comments INTEGER NOT NULL DEFAULT 0
        CHECK (review_comments >= 0),

    FOREIGN KEY (repo_id)
        REFERENCES repositories(repo_id)
        ON DELETE CASCADE,

    FOREIGN KEY (author_id)
        REFERENCES developers(developer_id),

    FOREIGN KEY (reviewer_id)
        REFERENCES developers(developer_id)
        ON DELETE SET NULL,

    FOREIGN KEY (issue_id)
        REFERENCES issues(issue_id)
        ON DELETE SET NULL,

    CHECK (
        reviewer_id IS NULL
        OR author_id <> reviewer_id
    ),

    CHECK (
        first_review_at IS NULL
        OR first_review_at >= created_at
    ),

    CHECK (
        merged_at IS NULL
        OR merged_at >= created_at
    )
);


-- ============================================================
-- 7. COMMITS
-- ============================================================

CREATE TABLE commits (
    commit_id INTEGER PRIMARY KEY AUTOINCREMENT,

    repo_id INTEGER NOT NULL,

    developer_id INTEGER NOT NULL,

    pr_id INTEGER,

    commit_hash TEXT NOT NULL UNIQUE,

    message TEXT NOT NULL,

    committed_at DATETIME NOT NULL,

    lines_added INTEGER NOT NULL
        CHECK (lines_added >= 0),

    lines_deleted INTEGER NOT NULL
        CHECK (lines_deleted >= 0),

    FOREIGN KEY (repo_id)
        REFERENCES repositories(repo_id)
        ON DELETE CASCADE,

    FOREIGN KEY (developer_id)
        REFERENCES developers(developer_id),

    FOREIGN KEY (pr_id)
        REFERENCES pull_requests(pr_id)
        ON DELETE SET NULL
);


-- ============================================================
-- 8. DEPLOYMENTS
-- ============================================================

CREATE TABLE deployments (
    deployment_id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER NOT NULL,

    repo_id INTEGER NOT NULL,

    deployed_by INTEGER NOT NULL,

    environment TEXT NOT NULL
        CHECK (
            environment IN (
                'staging',
                'production'
            )
        ),

    version TEXT NOT NULL,

    status TEXT NOT NULL
        CHECK (
            status IN (
                'success',
                'failed',
                'rolled_back'
            )
        ),

    deployed_at DATETIME NOT NULL,

    duration_seconds INTEGER NOT NULL
        CHECK (duration_seconds >= 0),

    FOREIGN KEY (project_id)
        REFERENCES projects(project_id)
        ON DELETE CASCADE,

    FOREIGN KEY (repo_id)
        REFERENCES repositories(repo_id)
        ON DELETE CASCADE,

    FOREIGN KEY (deployed_by)
        REFERENCES developers(developer_id)
);


-- ============================================================
-- ANALYTICS INDEXES
-- ============================================================

CREATE INDEX idx_commits_dev_time
ON commits(developer_id, committed_at);


CREATE INDEX idx_commits_repo_time
ON commits(repo_id, committed_at);


CREATE INDEX idx_pr_repo_time
ON pull_requests(repo_id, created_at);


CREATE INDEX idx_pr_author
ON pull_requests(author_id);


CREATE INDEX idx_pr_reviewer
ON pull_requests(reviewer_id);


CREATE INDEX idx_pr_status
ON pull_requests(status);


CREATE INDEX idx_issues_proj_status
ON issues(project_id, status);


CREATE INDEX idx_issues_assignee
ON issues(assignee_id);


CREATE INDEX idx_issues_type_time
ON issues(issue_type, created_at);


CREATE INDEX idx_issues_sprint
ON issues(sprint_id);


CREATE INDEX idx_deployments_proj_time
ON deployments(project_id, deployed_at);


CREATE INDEX idx_deployments_env_time
ON deployments(environment, deployed_at);


CREATE INDEX idx_sprints_proj_start
ON sprints(project_id, start_date);


-- ============================================================
-- END OF SCHEMA
-- ============================================================