"""scope accounts to user: add user_id and composite unique

Revision ID: a1c7e2f94b30
Revises: 54954ad40988
"""
from alembic import op
import sqlalchemy as sa

revision = "a1c7e2f94b30"
down_revision = "54954ad40988"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("accounts", sa.Column("user_id", sa.Integer(), nullable=True))
    op.execute("UPDATE accounts SET user_id = 1 WHERE user_id IS NULL")
    op.alter_column("accounts", "user_id", nullable=False)
    op.create_foreign_key(
        "accounts_user_id_fkey", "accounts", "users", ["user_id"], ["id"]
    )
    op.create_index(op.f("ix_accounts_user_id"), "accounts", ["user_id"])

    op.drop_index(op.f("ix_accounts_account_number"), table_name="accounts")
    op.create_index(
        op.f("ix_accounts_account_number"), "accounts", ["account_number"]
    )
    op.create_unique_constraint(
        "uq_account_user_account_number", "accounts", ["user_id", "account_number"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_account_user_account_number", "accounts", type_="unique")
    op.drop_index(op.f("ix_accounts_account_number"), table_name="accounts")
    op.create_index(
        op.f("ix_accounts_account_number"), "accounts", ["account_number"], unique=True
    )
    op.drop_index(op.f("ix_accounts_user_id"), table_name="accounts")
    op.drop_constraint("accounts_user_id_fkey", "accounts", type_="foreignkey")
    op.drop_column("accounts", "user_id")