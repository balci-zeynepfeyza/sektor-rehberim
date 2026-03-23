from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone

from backend.app.db.store import CommentStore
from backend.app.models.comments import (
    CommentArea,
    CommentCreateRequest,
    CommentRatings,
    CommentResponse,
    EmploymentStatus,
)
from backend.app.models.companies import CompanyRatingSummary
from backend.app.models.reports import ReportCreateRequest, ReportResponse
from backend.app.models.reactions import (
    CommentReactionCounts,
    CommentReactionCreateRequest,
    CommentReactionResponse,
)
from backend.app.models.interview_questions import (
    InterviewQuestionCreateRequest,
    InterviewQuestionResponse,
    InterviewQuestionCategory,
)


class LocalSQLiteCommentStore(CommentStore):
    def __init__(self, *, sqlite_path: str) -> None:
        self._sqlite_path = sqlite_path

    def init(self) -> None:
        conn = sqlite3.connect(self._sqlite_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS comments (
                  id TEXT PRIMARY KEY,
                  company_id TEXT NOT NULL,
                  display_name TEXT NOT NULL,
                  area TEXT NOT NULL DEFAULT 'software',
                  employment_status TEXT NOT NULL DEFAULT 'prefer_not_to_say',
                  area_note TEXT,
                  message TEXT NOT NULL,
                  difficulty INTEGER NOT NULL,
                  balance INTEGER NOT NULL,
                  office INTEGER NOT NULL,
                  created_at TEXT NOT NULL
                );
                """
            )
            # Backward compatibility for older DB files.
            comment_cols = conn.execute("PRAGMA table_info(comments);").fetchall()
            comment_col_names = {c[1] for c in comment_cols}
            if "area" not in comment_col_names:
                conn.execute(
                    "ALTER TABLE comments ADD COLUMN area TEXT NOT NULL DEFAULT 'software';"
                )
            if "employment_status" not in comment_col_names:
                conn.execute(
                    "ALTER TABLE comments ADD COLUMN employment_status TEXT NOT NULL DEFAULT 'prefer_not_to_say';"
                )
            if "area_note" not in comment_col_names:
                conn.execute("ALTER TABLE comments ADD COLUMN area_note TEXT;")

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reports (
                  id TEXT PRIMARY KEY,
                  comment_id TEXT NOT NULL,
                  company_id TEXT NOT NULL,
                  reason TEXT NOT NULL,
                  status TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS interview_questions (
                  id TEXT PRIMARY KEY,
                  company_id TEXT NOT NULL,
                  category TEXT NOT NULL,
                  topic TEXT NOT NULL DEFAULT 'Genel',
                  question TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                """
            )
            # Backward compatibility for older DB files.
            iq_cols = conn.execute("PRAGMA table_info(interview_questions);").fetchall()
            iq_col_names = {c[1] for c in iq_cols}
            if "topic" not in iq_col_names:
                conn.execute(
                    "ALTER TABLE interview_questions ADD COLUMN topic TEXT NOT NULL DEFAULT 'Genel';"
                )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS comment_reactions (
                  id TEXT PRIMARY KEY,
                  comment_id TEXT NOT NULL,
                  actor_key TEXT NOT NULL,
                  reaction_type TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                """
            )

            # Backward compatibility for older DBs created before actor_key existed.
            cols = conn.execute("PRAGMA table_info(comment_reactions);").fetchall()
            col_names = {c[1] for c in cols}
            if "actor_key" not in col_names:
                conn.execute("ALTER TABLE comment_reactions ADD COLUMN actor_key TEXT;")
                conn.execute(
                    """
                    UPDATE comment_reactions
                    SET actor_key = id
                    WHERE actor_key IS NULL OR actor_key = '';
                    """
                )
            conn.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_comment_reactions_comment_actor
                ON comment_reactions(comment_id, actor_key);
                """
            )
            conn.commit()
        finally:
            conn.close()

    def create_comment(
        self, *, company_id: str, request: CommentCreateRequest, display_name: str
    ) -> CommentResponse:
        comment_id = str(uuid.uuid4())
        created_at = datetime.now(tz=timezone.utc)
        ratings: CommentRatings = request.ratings

        conn = sqlite3.connect(self._sqlite_path)
        try:
            conn.execute(
                """
                INSERT INTO comments (
                  id,
                  company_id,
                  display_name,
                  area,
                  employment_status,
                  area_note,
                  message,
                  difficulty,
                  balance,
                  office,
                  created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    comment_id,
                    company_id,
                    display_name,
                    request.area.value,
                    request.employment_status.value,
                    request.area_note,
                    request.message,
                    ratings.difficulty,
                    ratings.balance,
                    ratings.office,
                    created_at.isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return CommentResponse(
            id=comment_id,
            company_id=company_id,
            display_name=display_name,
            area=request.area,
            employment_status=request.employment_status,
            area_note=request.area_note,
            message=request.message,
            ratings=ratings,
            created_at=created_at,
        )

    def list_comments(
        self, *, company_id: str, limit: int = 50, actor_key: str | None = None
    ) -> list[CommentResponse]:
        conn = sqlite3.connect(self._sqlite_path)
        try:
            rows = conn.execute(
                """
                SELECT
                  id,
                  company_id,
                  display_name,
                  area,
                  employment_status,
                  area_note,
                  message,
                  difficulty,
                  balance,
                  office,
                  created_at
                FROM comments
                WHERE company_id = ?
                ORDER BY created_at DESC
                LIMIT ?;
                """,
                (company_id, limit),
            ).fetchall()

            comment_ids = [row[0] for row in rows]
            reaction_counts_by_id: dict[str, CommentReactionCounts] = {}
            user_reaction_by_id: dict[str, str] = {}
            if comment_ids:
                placeholders = ", ".join("?" for _ in comment_ids)
                reaction_rows = conn.execute(
                    f"""
                    SELECT comment_id, reaction_type, COUNT(*) as cnt
                    FROM comment_reactions
                    WHERE comment_id IN ({placeholders})
                    GROUP BY comment_id, reaction_type;
                    """,
                    comment_ids,
                ).fetchall()

                for comment_id, reaction_type, cnt in reaction_rows:
                    if comment_id not in reaction_counts_by_id:
                        reaction_counts_by_id[comment_id] = CommentReactionCounts()
                    counts = reaction_counts_by_id[comment_id]
                    if reaction_type == "like":
                        counts.like = int(cnt)
                    elif reaction_type == "dislike":
                        counts.dislike = int(cnt)
                    elif reaction_type == "report":
                        counts.report = int(cnt)

                if actor_key:
                    user_rows = conn.execute(
                        f"""
                        SELECT comment_id, reaction_type
                        FROM comment_reactions
                        WHERE comment_id IN ({placeholders}) AND actor_key = ?;
                        """,
                        [*comment_ids, actor_key],
                    ).fetchall()
                    for cid, reaction_type in user_rows:
                        user_reaction_by_id[cid] = reaction_type
        finally:
            conn.close()

        comments: list[CommentResponse] = []
        for row in rows:
            (
                comment_id,
                cid,
                display_name,
                area,
                employment_status,
                area_note,
                message,
                difficulty,
                balance,
                office,
                created_at_str,
            ) = row
            comments.append(
                CommentResponse(
                    id=comment_id,
                    company_id=cid,
                    display_name=display_name,
                    area=CommentArea(area),
                    employment_status=EmploymentStatus(employment_status),
                    area_note=area_note,
                    message=message,
                    ratings=CommentRatings(
                        difficulty=int(difficulty),
                        balance=int(balance),
                        office=int(office),
                    ),
                    reaction_counts=reaction_counts_by_id.get(comment_id, CommentReactionCounts()),
                    user_reaction=user_reaction_by_id.get(comment_id),
                    created_at=datetime.fromisoformat(created_at_str),
                )
            )

        return comments

    def create_report(self, *, comment_id: str, request: ReportCreateRequest) -> ReportResponse:
        conn = sqlite3.connect(self._sqlite_path)
        try:
            company_id_row = conn.execute(
                "SELECT company_id FROM comments WHERE id = ?;",
                (comment_id,),
            ).fetchone()

            if company_id_row is None:
                raise ValueError("comment_not_found")

            (company_id,) = company_id_row

            report_id = str(uuid.uuid4())
            created_at = datetime.now(tz=timezone.utc)

            conn.execute(
                """
                INSERT INTO reports (id, comment_id, company_id, reason, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    report_id,
                    comment_id,
                    company_id,
                    request.reason,
                    "open",
                    created_at.isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return ReportResponse(
            id=report_id,
            comment_id=comment_id,
            company_id=company_id,
            reason=request.reason,
            status="open",
            created_at=created_at,
        )

    def get_company_rating_summary(self, *, company_id: str) -> CompanyRatingSummary:
        conn = sqlite3.connect(self._sqlite_path)
        try:
            row = conn.execute(
                """
                SELECT
                  COUNT(*) as rating_count,
                  AVG(difficulty) as avg_difficulty,
                  AVG(balance) as avg_balance,
                  AVG(office) as avg_office
                FROM comments
                WHERE company_id = ?;
                """,
                (company_id,),
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            return CompanyRatingSummary(company_id=company_id, rating_count=0)

        rating_count, avg_difficulty, avg_balance, avg_office = row
        if int(rating_count) == 0:
            return CompanyRatingSummary(company_id=company_id, rating_count=0)

        # With COUNT(*) > 0, SQLite should return non-null AVG values for numeric columns.
        avg_overall = (float(avg_difficulty) + float(avg_balance) + float(avg_office)) / 3.0
        return CompanyRatingSummary(
            company_id=company_id,
            rating_count=int(rating_count),
            avg_difficulty=float(avg_difficulty),
            avg_balance=float(avg_balance),
            avg_office=float(avg_office),
            avg_overall=avg_overall,
        )

    def create_interview_question(
        self, *, company_id: str, request: InterviewQuestionCreateRequest
    ) -> InterviewQuestionResponse:
        question_id = str(uuid.uuid4())
        created_at = datetime.now(tz=timezone.utc)

        conn = sqlite3.connect(self._sqlite_path)
        try:
            conn.execute(
                """
                INSERT INTO interview_questions (id, company_id, category, topic, question, created_at)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    question_id,
                    company_id,
                    request.category.value,
                    request.topic,
                    request.question,
                    created_at.isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return InterviewQuestionResponse(
            id=question_id,
            company_id=company_id,
            category=request.category,
            topic=request.topic,
            question=request.question,
            created_at=created_at,
        )

    def list_interview_questions(
        self, *, company_id: str, limit: int = 50, category: str | None = None
    ) -> list[InterviewQuestionResponse]:
        if limit < 1 or limit > 100:
            return []

        conn = sqlite3.connect(self._sqlite_path)
        try:
            if category:
                rows = conn.execute(
                    """
                    SELECT id, company_id, category, topic, question, created_at
                    FROM interview_questions
                    WHERE company_id = ? AND category = ?
                    ORDER BY created_at DESC
                    LIMIT ?;
                    """,
                    (company_id, category, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT id, company_id, category, topic, question, created_at
                    FROM interview_questions
                    WHERE company_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?;
                    """,
                    (company_id, limit),
                ).fetchall()
        finally:
            conn.close()

        questions: list[InterviewQuestionResponse] = []
        for row in rows:
            (
                question_id,
                cid,
                category_str,
                topic_text,
                question_text,
                created_at_str,
            ) = row
            questions.append(
                InterviewQuestionResponse(
                    id=question_id,
                    company_id=cid,
                    category=InterviewQuestionCategory(category_str),
                    topic=topic_text,
                    question=question_text,
                    created_at=datetime.fromisoformat(created_at_str),
                )
            )

        return questions

    def create_comment_reaction(
        self, *, comment_id: str, request: CommentReactionCreateRequest
    ) -> CommentReactionResponse:
        conn = sqlite3.connect(self._sqlite_path)
        try:
            row = conn.execute(
                "SELECT id FROM comments WHERE id = ?;",
                (comment_id,),
            ).fetchone()
            if row is None:
                raise ValueError("comment_not_found")

            actor_key = request.actor_key.strip()
            if not actor_key:
                raise ValueError("actor_key_required")

            current = conn.execute(
                """
                SELECT id, reaction_type FROM comment_reactions
                WHERE comment_id = ? AND actor_key = ?;
                """,
                (comment_id, actor_key),
            ).fetchone()

            created_at = datetime.now(tz=timezone.utc)
            user_reaction: str | None = request.reaction_type.value
            if current is None:
                reaction_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO comment_reactions (id, comment_id, actor_key, reaction_type, created_at)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (
                        reaction_id,
                        comment_id,
                        actor_key,
                        request.reaction_type.value,
                        created_at.isoformat(),
                    ),
                )
            else:
                existing_id, existing_type = current
                if existing_type == request.reaction_type.value:
                    # Toggle off if same reaction tapped again.
                    conn.execute(
                        "DELETE FROM comment_reactions WHERE id = ?;",
                        (existing_id,),
                    )
                    user_reaction = None
                else:
                    # Radio behavior: replace old reaction with new.
                    conn.execute(
                        """
                        UPDATE comment_reactions
                        SET reaction_type = ?, created_at = ?
                        WHERE id = ?;
                        """,
                        (request.reaction_type.value, created_at.isoformat(), existing_id),
                    )

            reaction_rows = conn.execute(
                """
                SELECT reaction_type, COUNT(*) as cnt
                FROM comment_reactions
                WHERE comment_id = ?
                GROUP BY reaction_type;
                """,
                (comment_id,),
            ).fetchall()
            conn.commit()
        finally:
            conn.close()

        counts = CommentReactionCounts()
        for reaction_type, cnt in reaction_rows:
            if reaction_type == "like":
                counts.like = int(cnt)
            elif reaction_type == "dislike":
                counts.dislike = int(cnt)
            elif reaction_type == "report":
                counts.report = int(cnt)

        return CommentReactionResponse(
            comment_id=comment_id,
            counts=counts,
            user_reaction=user_reaction,
        )

