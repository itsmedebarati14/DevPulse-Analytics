import streamlit as st
import pandas as pd
import plotly.express as px

from db import run_query


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="DevPulse Analytics",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📊 DevPulse Analytics Dashboard")

st.caption(
    "Engineering productivity, delivery, issue and deployment analytics"
)


# ============================================================
# SIDEBAR - DATE FILTER
# ============================================================

st.sidebar.header("🔎 Filter Analytics")

today = pd.Timestamp.today().normalize()

default_start = today - pd.Timedelta(days=90)

date_range = st.sidebar.date_input(
    "Date Range",
    value=(default_start.date(), today.date())
)


# Make sure a valid two-date range exists
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])

    end_date = (
        pd.Timestamp(date_range[1])
        + pd.Timedelta(days=1)
    )

else:

    start_date = default_start

    end_date = today + pd.Timedelta(days=1)


start_sql = start_date.strftime("%Y-%m-%d %H:%M:%S")

end_sql = end_date.strftime("%Y-%m-%d %H:%M:%S")


st.sidebar.info(
    f"Showing data from "
    f"{start_date.strftime('%d %b %Y')} "
    f"to "
    f"{(end_date - pd.Timedelta(days=1)).strftime('%d %b %Y')}"
)


# ============================================================
# NAVIGATION
# ============================================================

page = st.sidebar.radio(
    "Navigate Pages",
    [
        "Overview",
        "Developers",
        "Issues & Sprints",
        "Deployments"
    ]
)


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    st.header("📈 Executive Overview")

    # --------------------------------------------------------
    # KPI ROW
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)


    # Active Developers
    dev_df = run_query(
        """
        SELECT COUNT(DISTINCT developer_id) AS count
        FROM commits
        WHERE committed_at >= ?
        AND committed_at < ?
        """,
        (start_sql, end_sql)
    )

    active_devs = (
        int(dev_df["count"].iloc[0])
        if not dev_df.empty
        else 0
    )

    col1.metric(
        "Active Developers",
        active_devs
    )


    # Open Issues
    issues_df = run_query(
        """
        SELECT COUNT(*) AS count
        FROM issues
        WHERE status IN ('open', 'in_progress')
        AND created_at >= ?
        AND created_at < ?
        """,
        (start_sql, end_sql)
    )

    open_issues = (
        int(issues_df["count"].iloc[0])
        if not issues_df.empty
        else 0
    )

    col2.metric(
        "Open Issues",
        open_issues
    )


    # Production Deployments
    deploy_df = run_query(
        """
        SELECT COUNT(*) AS count
        FROM deployments
        WHERE environment = 'production'
        AND deployed_at >= ?
        AND deployed_at < ?
        """,
        (start_sql, end_sql)
    )

    prod_deploys = (
        int(deploy_df["count"].iloc[0])
        if not deploy_df.empty
        else 0
    )

    col3.metric(
        "Production Deployments",
        prod_deploys
    )


    # Sprint Completion
    sprint_df = run_query(
        """
        SELECT
            AVG(
                CASE
                    WHEN planned_points > 0
                    THEN completed_points * 100.0 / planned_points
                END
            ) AS avg_rate
        FROM sprints
        WHERE status = 'completed'
        AND start_date >= ?
        AND start_date < ?
        """,
        (
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
    )

    if (
        not sprint_df.empty
        and pd.notna(sprint_df["avg_rate"].iloc[0])
    ):

        avg_rate = round(
            float(sprint_df["avg_rate"].iloc[0]),
            1
        )

    else:

        avg_rate = 0


    col4.metric(
        "Avg Sprint Completion",
        f"{avg_rate}%"
    )


    st.markdown("---")


    # ========================================================
    # COMMIT TREND + DEPLOYMENT STATUS
    # ========================================================

    chart_col1, chart_col2 = st.columns(2)


    # --------------------------------------------------------
    # Weekly Commit Activity
    # --------------------------------------------------------

    with chart_col1:

        st.subheader("📊 Weekly Commit Activity")

        commit_trend = run_query(
            """
            SELECT
                strftime('%Y-%W', committed_at) AS week,
                COUNT(*) AS commits
            FROM commits
            WHERE committed_at >= ?
            AND committed_at < ?
            GROUP BY week
            ORDER BY week
            """,
            (start_sql, end_sql)
        )

        if not commit_trend.empty:

            fig = px.line(
                commit_trend,
                x="week",
                y="commits",
                markers=True,
                title="Weekly Commits"
            )

            fig.update_layout(
                xaxis_title="Week",
                yaxis_title="Commits"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No commit data available.")


    # --------------------------------------------------------
    # Deployment Status
    # --------------------------------------------------------

    with chart_col2:

        st.subheader("🚀 Deployments by Status")

        status_df = run_query(
            """
            SELECT
                status,
                COUNT(*) AS count
            FROM deployments
            WHERE deployed_at >= ?
            AND deployed_at < ?
            GROUP BY status
            ORDER BY count DESC
            """,
            (start_sql, end_sql)
        )

        if not status_df.empty:

            fig = px.pie(
                status_df,
                values="count",
                names="status",
                title="Deployment Status",
                hole=0.4
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No deployment data available.")


    # ========================================================
    # ISSUE + PR SUMMARY
    # ========================================================

    st.markdown("---")

    st.subheader("📌 Engineering Activity Summary")

    summary_col1, summary_col2, summary_col3 = st.columns(3)


    # Issues
    total_issues_df = run_query(
        """
        SELECT COUNT(*) AS count
        FROM issues
        WHERE created_at >= ?
        AND created_at < ?
        """,
        (start_sql, end_sql)
    )

    total_issues = int(
        total_issues_df["count"].iloc[0]
    )

    summary_col1.metric(
        "Issues Created",
        total_issues
    )


    # Pull Requests
    pr_df = run_query(
        """
        SELECT COUNT(*) AS count
        FROM pull_requests
        WHERE created_at >= ?
        AND created_at < ?
        """,
        (start_sql, end_sql)
    )

    total_prs = int(
        pr_df["count"].iloc[0]
    )

    summary_col2.metric(
        "Pull Requests",
        total_prs
    )


    # Commits
    commits_df = run_query(
        """
        SELECT COUNT(*) AS count
        FROM commits
        WHERE committed_at >= ?
        AND committed_at < ?
        """,
        (start_sql, end_sql)
    )

    total_commits = int(
        commits_df["count"].iloc[0]
    )

    summary_col3.metric(
        "Commits",
        total_commits
    )


# ============================================================
# DEVELOPERS
# ============================================================

elif page == "Developers":

    st.header("👨‍💻 Developer Performance & Workload")


    dev_metrics = run_query(
        """
        SELECT
            d.full_name,
            d.team,
            d.role,
            COUNT(c.commit_id) AS commits,
            COALESCE(SUM(c.lines_added), 0) AS lines_added,
            COALESCE(SUM(c.lines_deleted), 0) AS lines_deleted
        FROM developers d

        LEFT JOIN commits c
            ON d.developer_id = c.developer_id
            AND c.committed_at >= ?
            AND c.committed_at < ?

        GROUP BY
            d.developer_id,
            d.full_name,
            d.team,
            d.role

        ORDER BY commits DESC

        LIMIT 15
        """,
        (start_sql, end_sql)
    )


    if not dev_metrics.empty:

        fig = px.bar(
            dev_metrics,
            x="commits",
            y="full_name",
            color="team",
            orientation="h",
            title="Top 15 Developers by Commits"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


        # Developer table

        display_df = dev_metrics.copy()

        display_df.columns = [
            "Developer",
            "Team",
            "Role",
            "Commits",
            "Lines Added",
            "Lines Deleted"
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No developer activity found.")


# ============================================================
# ISSUES & SPRINTS
# ============================================================

elif page == "Issues & Sprints":

    st.header("🐞 Issues & Sprint Delivery Metrics")


    # ========================================================
    # ISSUE TYPE
    # ========================================================

    col1, col2 = st.columns(2)


    with col1:

        st.subheader("Issue Breakdown by Type")

        issue_type_df = run_query(
            """
            SELECT
                issue_type,
                COUNT(*) AS count
            FROM issues
            WHERE created_at >= ?
            AND created_at < ?
            GROUP BY issue_type
            ORDER BY count DESC
            """,
            (start_sql, end_sql)
        )


        if not issue_type_df.empty:

            fig = px.bar(
                issue_type_df,
                x="issue_type",
                y="count",
                title="Issues by Type"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No issue data available.")


    # ========================================================
    # ISSUE STATUS
    # ========================================================

    with col2:

        st.subheader("Issue Status")

        issue_status_df = run_query(
            """
            SELECT
                status,
                COUNT(*) AS count
            FROM issues
            WHERE created_at >= ?
            AND created_at < ?
            GROUP BY status
            ORDER BY count DESC
            """,
            (start_sql, end_sql)
        )


        if not issue_status_df.empty:

            fig = px.pie(
                issue_status_df,
                values="count",
                names="status",
                hole=0.4,
                title="Issue Status Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No issue status data available.")


    # ========================================================
    # SPRINT PERFORMANCE
    # ========================================================

    st.markdown("---")

    st.subheader("🏃 Sprint Performance")


    sprint_metrics = run_query(
        """
        SELECT
            p.name AS project,
            s.name AS sprint,
            s.start_date,
            s.end_date,
            s.planned_points,
            s.completed_points,

            ROUND(
                s.completed_points * 100.0
                / NULLIF(s.planned_points, 0),
                1
            ) AS completion_rate,

            s.status

        FROM sprints s

        JOIN projects p
            ON s.project_id = p.project_id

        WHERE s.start_date >= ?
        AND s.start_date < ?

        ORDER BY s.start_date DESC
        """,
        (
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
    )


    if not sprint_metrics.empty:

        fig = px.bar(
            sprint_metrics,
            x="sprint",
            y="completion_rate",
            color="project",
            title="Sprint Completion Rate",
            hover_data=[
                "planned_points",
                "completed_points",
                "status"
            ]
        )

        fig.add_hline(
            y=100,
            line_dash="dash",
            annotation_text="100%"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


        st.dataframe(
            sprint_metrics,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No sprint data available for the selected period."
        )


# ============================================================
# DEPLOYMENTS
# ============================================================

elif page == "Deployments":

    st.header("🚀 Deployment Frequency & Quality")


    # ========================================================
    # DAILY DEPLOYMENTS
    # ========================================================

    deploy_freq = run_query(
        """
        SELECT
            DATE(deployed_at) AS date,
            environment,
            COUNT(*) AS count
        FROM deployments
        WHERE deployed_at >= ?
        AND deployed_at < ?
        GROUP BY date, environment
        ORDER BY date
        """,
        (start_sql, end_sql)
    )


    if not deploy_freq.empty:

        fig = px.bar(
            deploy_freq,
            x="date",
            y="count",
            color="environment",
            title="Daily Deployments"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No deployment data available.")


    # ========================================================
    # DEPLOYMENT STATUS
    # ========================================================

    st.markdown("---")

    col1, col2, col3 = st.columns(3)


    # Success
    success_df = run_query(
        """
        SELECT COUNT(*) AS count
        FROM deployments
        WHERE status = 'success'
        AND deployed_at >= ?
        AND deployed_at < ?
        """,
        (start_sql, end_sql)
    )

    success_count = int(
        success_df["count"].iloc[0]
    )

    col1.metric(
        "Successful Deployments",
        success_count
    )


    # Failed
    failed_df = run_query(
        """
        SELECT COUNT(*) AS count
        FROM deployments
        WHERE status = 'failed'
        AND deployed_at >= ?
        AND deployed_at < ?
        """,
        (start_sql, end_sql)
    )

    failed_count = int(
        failed_df["count"].iloc[0]
    )

    col2.metric(
        "Failed Deployments",
        failed_count
    )


    # Rollbacks
    rollback_df = run_query(
        """
        SELECT COUNT(*) AS count
        FROM deployments
        WHERE status = 'rolled_back'
        AND deployed_at >= ?
        AND deployed_at < ?
        """,
        (start_sql, end_sql)
    )

    rollback_count = int(
        rollback_df["count"].iloc[0]
    )

    col3.metric(
        "Rollbacks",
        rollback_count
    )


    # ========================================================
    # DEPLOYMENT QUALITY
    # ========================================================

    total_deployments = (
        success_count
        + failed_count
        + rollback_count
    )


    if total_deployments > 0:

        success_rate = (
            success_count
            / total_deployments
            * 100
        )

    else:

        success_rate = 0


    st.markdown("---")

    st.subheader("📊 Deployment Quality")

    quality_col1, quality_col2 = st.columns(2)


    with quality_col1:

        st.metric(
            "Deployment Success Rate",
            f"{success_rate:.1f}%"
        )


    with quality_col2:

        avg_duration_df = run_query(
            """
            SELECT
                AVG(duration_seconds) AS avg_duration
            FROM deployments
            WHERE deployed_at >= ?
            AND deployed_at < ?
            """,
            (start_sql, end_sql)
        )


        if (
            not avg_duration_df.empty
            and pd.notna(
                avg_duration_df["avg_duration"].iloc[0]
            )
        ):

            avg_duration = round(
                float(
                    avg_duration_df[
                        "avg_duration"
                    ].iloc[0]
                ),
                1
            )

        else:

            avg_duration = 0


        st.metric(
            "Average Deployment Duration",
            f"{avg_duration} sec"
        )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "DevPulse Analytics • SQLite Edition"
)

st.sidebar.caption(
    "Synthetic engineering analytics platform"
)