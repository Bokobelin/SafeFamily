"""Scheduler for automated rule execution."""

from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.safe_family.auto_git.auto_git import rule_auto_commit
from src.safe_family.core.auth import admin_required
from src.safe_family.core.extensions import get_db_connection, local_tz
from src.safe_family.urls.blocker import (
    rule_allow_traffic_all,
    rule_disable_all,
    rule_enable_ai,
    rule_enable_all_except_ai,
    rule_stop_traffic_all,
)
from src.safe_family.utils.constants import DAYS_IN_WEEK

schedule_rules_bp = Blueprint("schedule_rules", __name__, template_folder="templates")


# Example mapping of rule names to Python functions
def run_rule_a():
    """Test Run Rule A."""
    print("hello A at " + str(datetime.now(local_tz)))


def run_rule_b():
    """Test Run Rule B."""
    print("hello B at " + str(datetime.now(local_tz)))


RULE_FUNCTIONS = {
    "Rule enable all except AI": rule_enable_all_except_ai,
    "Rule disable all": rule_disable_all,
    "Rule enable AI": rule_enable_ai,
    "Rule stop traffic all": rule_stop_traffic_all,
    "Rule allow traffic all": rule_allow_traffic_all,
    "Rule auto commit": rule_auto_commit,
}

# 0-6 → Sunday to Saturday (APScheduler uses 0=Monday, 6=Sunday).
scheduler = BackgroundScheduler()
scheduler.start()


def load_schedules():
    """Clear existing jobs and reload from DB."""
    scheduler.remove_all_jobs()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, rule_name, start_time, day_of_week, enabled FROM schedule_rules WHERE enabled = TRUE",
    )
    for rule_id, rule_name, start_time, day_of_week, enabled in cur.fetchall():
        if rule_name in RULE_FUNCTIONS:
            func = RULE_FUNCTIONS.get(rule_name)
            if func:
                scheduler.add_job(
                    func,
                    "cron",
                    id=f"rule_{rule_id}",  # important: job ID tied to DB row
                    hour=start_time.hour,
                    minute=start_time.minute,
                    day_of_week=day_of_week or "*",
                )
    cur.close()


def remove_job(rule_id):
    """Remove a job when a rule is deleted."""
    job_id = f"rule_{rule_id}"
    try:
        scheduler.remove_job(job_id)
        print(f"Removed job {job_id}")
    except Exception as e:
        print(f"Job {job_id} not found: {e}")


@schedule_rules_bp.route("/schedule_rules", methods=["GET", "POST"])
@admin_required
def schedule_rules():
    """View and manage scheduled rules."""
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "update":
            rule_id = request.form["rule_id"]
            start_time = request.form["start_time"]
            end_time = request.form["end_time"]
            selected_days = request.form.getlist("day_of_week")
            if not selected_days or len(selected_days) == DAYS_IN_WEEK:
                day_of_week = "*"  # all days
            else:
                day_of_week = ",".join(selected_days)
            cur.execute(
                "UPDATE schedule_rules SET start_time = %s, end_time = %s, day_of_week = %s WHERE id = %s",
                (start_time, end_time if end_time else None, day_of_week, rule_id),
            )
            conn.commit()
            load_schedules()

        elif action == "add":
            rule_name = request.form["rule_name"]
            start_time = request.form["start_time"]
            end_time = request.form["end_time"] or None

            cur.execute(
                """
                INSERT INTO schedule_rules (rule_name, start_time, end_time, enabled)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (rule_name, start_time, end_time if end_time else None, True),
            )
            new_rule = cur.fetchone()
            if new_rule:  # always check
                rule_id = new_rule[0]
                print("Inserted rule with id:", rule_id)
            conn.commit()
            load_schedules()

        elif action == "delete":
            rule_id = request.form["rule_id"]
            remove_job(rule_id)
            cur.execute("DELETE FROM schedule_rules WHERE id = %s", (rule_id,))
            conn.commit()
            load_schedules()

        elif action == "enable":
            rule_id = request.form["rule_id"]
            cur.execute(
                "UPDATE schedule_rules SET enabled = TRUE WHERE id = %s",
                (rule_id,),
            )
            conn.commit()
            load_schedules()

        elif action == "disable":
            rule_id = request.form["rule_id"]
            cur.execute(
                "UPDATE schedule_rules SET enabled = FALSE WHERE id = %s",
                (rule_id,),
            )
            conn.commit()
            load_schedules()

        elif action == "assign":
            for key, value in request.form.items():
                print("Processing:", key, value)
                if key.startswith("rule_"):
                    uid = key.split("_")[1]
                    cur.execute(
                        """
                        INSERT INTO user_rule_assignment (user_id, assigned_rule)
                        VALUES (%s, %s)
                        ON CONFLICT (user_id)
                        DO UPDATE SET assigned_rule = EXCLUDED.assigned_rule
                    """,
                        (uid, value),
                    )
            conn.commit()
            flash("Rule assignments updated.", "success")

        return redirect(url_for("schedule_rules.schedule_rules"))

    cur.execute("""
        SELECT u.id AS user_id, u.username, a.assigned_rule
        FROM users u
        LEFT JOIN user_rule_assignment a
        ON u.id = a.user_id
        ORDER BY u.username;
    """)
    assigned_rules = cur.fetchall()
    cur.execute("""
        SELECT id, rule_name, start_time,
        end_time, day_of_week, enabled
        FROM schedule_rules
        ORDER BY enabled DESC, start_time ASC
    """)
    rules = cur.fetchall()
    cur.close()

    return render_template(
        "rules/schedule_rules.html",
        rules=rules,
        assigned_rules=assigned_rules,
        available_rules=RULE_FUNCTIONS.keys(),
    )
