"""create initial core tables

Revision ID: 4a9c2d7d8e61
Revises:
Create Date: 2026-03-31 18:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "4a9c2d7d8e61"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_password_reset_tokens_id"),
        "password_reset_tokens",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_tokens_token"),
        "password_reset_tokens",
        ["token"],
        unique=True,
    )

    op.create_table(
        "prediction_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("input_data", sa.String(), nullable=True),
        sa.Column("prediction", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_prediction_history_id"),
        "prediction_history",
        ["id"],
        unique=False,
    )

    op.create_table(
        "user_profile",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("gender", sa.String(), nullable=True),
        sa.Column("height_m", sa.Float(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("bmi", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_profile_id"), "user_profile", ["id"], unique=False)

    op.create_table(
        "user_health_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("gender", sa.String(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("height_m", sa.Float(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("bmi", sa.Float(), nullable=True),
        sa.Column("family_overweight_history", sa.String(), nullable=True),
        sa.Column("high_calorie_food", sa.String(), nullable=True),
        sa.Column("vegetable_intake_freq", sa.Integer(), nullable=True),
        sa.Column("main_meals_per_day", sa.Integer(), nullable=True),
        sa.Column("snack_frequency", sa.String(), nullable=True),
        sa.Column("smokes", sa.String(), nullable=True),
        sa.Column("water_intake_liters", sa.Float(), nullable=True),
        sa.Column("calorie_tracking", sa.String(), nullable=True),
        sa.Column("physical_activity_hours", sa.Float(), nullable=True),
        sa.Column("screentime_hours", sa.Float(), nullable=True),
        sa.Column("alcohol_consumption", sa.String(), nullable=True),
        sa.Column("travel_mode", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(
        op.f("ix_user_health_profiles_id"),
        "user_health_profiles",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_health_profiles_id"), table_name="user_health_profiles")
    op.drop_table("user_health_profiles")
    op.drop_index(op.f("ix_user_profile_id"), table_name="user_profile")
    op.drop_table("user_profile")
    op.drop_index(op.f("ix_prediction_history_id"), table_name="prediction_history")
    op.drop_table("prediction_history")
    op.drop_index(
        op.f("ix_password_reset_tokens_token"),
        table_name="password_reset_tokens",
    )
    op.drop_index(
        op.f("ix_password_reset_tokens_id"),
        table_name="password_reset_tokens",
    )
    op.drop_table("password_reset_tokens")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
