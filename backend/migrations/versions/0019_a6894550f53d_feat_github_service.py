"""Feat: github service

Revision ID: a6894550f53d
Revises: 16637cc39d03
Create Date: 2025-01-16 00:36:42.262452

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'a6894550f53d'
down_revision: Union[str, None] = '16637cc39d03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    # Check if GitHub service already exists
    existing_services = conn.execute(text("SELECT name FROM services")).fetchall()
    existing_service_names = {row[0] for row in existing_services}

    if "github" not in existing_service_names:
        # Insert GitHub service
        conn.execute(
            text(
                "INSERT INTO services (name, description, created_at, updated_at) "
                "VALUES ('github', 'GitHub integration', now(), now())"
            )
        )

    # Add GitHub-specific actions
    existing_actions = conn.execute(text("SELECT name FROM actions")).fetchall()
    existing_action_names = {row[0] for row in existing_actions}
    github_actions = [
        {"name": "push_received", "description": "Detects when a push is made to a repository"},
        {"name": "issue_opened", "description": "Detects when an issue is opened"},
        {"name": "pr_created", "description": "Detects when a pull request is created"},
        {"name": "repo_starred", "description": "Detects when someone stars a repository"}
    ]

    for action in github_actions:
        if action["name"] not in existing_action_names:
            conn.execute(
                text(
                    "INSERT INTO actions (service_id, name, description, created_at, updated_at) "
                    "VALUES ((SELECT id FROM services WHERE name = 'github'), :name, :description, now(), now())"
                ),
                {"name": action["name"], "description": action["description"]},
            )

    # Add GitHub-specific reactions
    existing_reactions = conn.execute(text("SELECT name FROM reactions")).fetchall()
    existing_reaction_names = {row[0] for row in existing_reactions}
    github_reactions = [
        {"name": "create_issue", "description": "Creates a new issue in a repository"},
        {"name": "create_pr", "description": "Creates a new pull request"},
        {"name": "star_repo", "description": "Stars a repository"},
        {"name": "comment_issue", "description": "Comments on an issue"}
    ]

    for reaction in github_reactions:
        if reaction["name"] not in existing_reaction_names:
            conn.execute(
                text(
                    "INSERT INTO reactions (service_id, name, description, created_at, updated_at) "
                    "VALUES ((SELECT id FROM services WHERE name = 'github'), :name, :description, now(), now())"
                ),
                {"name": reaction["name"], "description": reaction["description"]},
            )

def downgrade() -> None:
    conn = op.get_bind()
    # Delete GitHub-related reactions
    conn.execute(
        text("DELETE FROM reactions WHERE service_id = (SELECT id FROM services WHERE name = 'github')")
    )
    # Delete GitHub-related actions
    conn.execute(
        text("DELETE FROM actions WHERE service_id = (SELECT id FROM services WHERE name = 'github')")
    )
    # Delete GitHub service
    conn.execute(
        text("DELETE FROM services WHERE name = 'github'")
    )
