import sqlite3
import json
import datetime
from typing import Optional, List
from .storage import Storage
from ..models.candidate import Candidate
from ..models.question import Question
from ..models.interview import Interview
from ..models.result import Result

class InterviewRepository(Storage):
    """SQLite-based implementation of the interview persistence layer."""

    def __init__(self, db_path: str = "interview_bot.db") -> None:
        self.db_path: str = db_path
        self._conn: Optional[sqlite3.Connection] = None
        
        # If it is an in-memory database, we MUST hold a single persistent connection
        # so the schema and data do not get cleared when closing the connection.
        if self.db_path == ":memory:":
            self._conn = sqlite3.connect(self.db_path)
            self._conn.execute("PRAGMA foreign_keys = ON;")
            
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _close_connection(self, conn: sqlite3.Connection) -> None:
        if self.db_path != ":memory:":
            conn.close()

    def _init_db(self) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS candidates (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS interviews (
                        id TEXT PRIMARY KEY,
                        candidate_id TEXT NOT NULL,
                        topic TEXT NOT NULL,
                        status TEXT NOT NULL,
                        current_question_index INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        score REAL,
                        feedback TEXT,
                        strengths TEXT,
                        weaknesses TEXT,
                        FOREIGN KEY(candidate_id) REFERENCES candidates(id)
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS questions (
                        interview_id TEXT NOT NULL,
                        question_id TEXT NOT NULL,
                        topic TEXT NOT NULL,
                        difficulty TEXT NOT NULL,
                        question_text TEXT NOT NULL,
                        expected_concepts TEXT NOT NULL,
                        sort_order INTEGER NOT NULL,
                        PRIMARY KEY(interview_id, question_id),
                        FOREIGN KEY(interview_id) REFERENCES interviews(id)
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS answers (
                        interview_id TEXT NOT NULL,
                        question_id TEXT NOT NULL,
                        answer_text TEXT NOT NULL,
                        PRIMARY KEY(interview_id, question_id),
                        FOREIGN KEY(interview_id) REFERENCES interviews(id)
                    );
                """)
        finally:
            self._close_connection(conn)

    def save_interview(self, interview: Interview) -> None:
        """Saves or updates an interview session."""
        candidate = interview.candidate
        result = interview.result
        score = result.score if result else None
        feedback = result.feedback if result else None
        strengths_json = json.dumps(result.strengths) if result else None
        weaknesses_json = json.dumps(result.weaknesses) if result else None
        
        saved_date = datetime.datetime.now().isoformat()
        
        conn = self._get_connection()
        try:
            with conn:
                # Check if interview already exists to preserve its creation date
                cursor = conn.execute("SELECT date FROM interviews WHERE id = ?", (interview.interview_id,))
                row = cursor.fetchone()
                if row:
                    saved_date = row[0]

                # 1. Save candidate details
                conn.execute(
                    "INSERT OR REPLACE INTO candidates (id, name, email) VALUES (?, ?, ?);",
                    (candidate.id, candidate.name, candidate.email)
                )

                # 2. Save interview session state
                topic = interview.questions[0].topic if interview.questions else "Unknown"
                conn.execute(
                    """
                    INSERT OR REPLACE INTO interviews 
                    (id, candidate_id, topic, status, current_question_index, date, score, feedback, strengths, weaknesses) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        interview.interview_id,
                        candidate.id,
                        topic,
                        interview.status,
                        interview.current_question_index,
                        saved_date,
                        score,
                        feedback,
                        strengths_json,
                        weaknesses_json
                    )
                )

                # 3. Save questions associated with this interview
                for idx, q in enumerate(interview.questions):
                    expected_concepts_json = json.dumps(q.expected_concepts)
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO questions 
                        (interview_id, question_id, topic, difficulty, question_text, expected_concepts, sort_order) 
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                        """,
                        (interview.interview_id, q.id, q.topic, q.difficulty, q.question_text, expected_concepts_json, idx)
                    )

                # 4. Save submitted answers
                for q_id, ans in interview.answers.items():
                    conn.execute(
                        "INSERT OR REPLACE INTO answers (interview_id, question_id, answer_text) VALUES (?, ?, ?);",
                        (interview.interview_id, q_id, ans)
                    )
        finally:
            self._close_connection(conn)

    def get_interview(self, interview_id: str) -> Optional[Interview]:
        """Retrieves a fully reconstructed Interview session by its unique ID."""
        conn = self._get_connection()
        try:
            # 1. Fetch interview row
            cursor = conn.execute(
                """
                SELECT candidate_id, status, current_question_index, score, feedback, strengths, weaknesses 
                FROM interviews WHERE id = ?;
                """,
                (interview_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            
            candidate_id, status, current_question_index, score, feedback, strengths_json, weaknesses_json = row

            # 2. Fetch candidate row
            cursor = conn.execute("SELECT name, email FROM candidates WHERE id = ?;", (candidate_id,))
            c_row = cursor.fetchone()
            if not c_row:
                raise ValueError(f"Candidate for interview '{interview_id}' is missing in the database.")
            c_name, c_email = c_row

            # Reconstruct candidate
            candidate = Candidate(id=candidate_id, name=c_name, email=c_email)

            # 3. Fetch questions sorted by sort_order
            cursor = conn.execute(
                """
                SELECT question_id, topic, difficulty, question_text, expected_concepts 
                FROM questions WHERE interview_id = ? ORDER BY sort_order ASC;
                """,
                (interview_id,)
            )
            q_rows = cursor.fetchall()
            
            questions = []
            for q_id, topic, difficulty, q_text, expected_concepts_json in q_rows:
                expected_concepts = json.loads(expected_concepts_json)
                questions.append(Question(
                    id=q_id,
                    topic=topic,
                    difficulty=difficulty,
                    question_text=q_text,
                    expected_concepts=expected_concepts
                ))

            # Reconstruct Interview
            interview = Interview(interview_id=interview_id, candidate=candidate, questions=questions)
            interview._status = status
            interview._current_question_index = current_question_index

            # 4. Fetch answers
            cursor = conn.execute("SELECT question_id, answer_text FROM answers WHERE interview_id = ?;", (interview_id,))
            ans_rows = cursor.fetchall()
            for q_id, ans in ans_rows:
                interview.answers[q_id] = ans

            # 5. Reconstruct Result if present
            if score is not None or feedback is not None:
                strengths = json.loads(strengths_json) if strengths_json else []
                weaknesses = json.loads(weaknesses_json) if weaknesses_json else []
                interview.result = Result(
                    score=score,
                    feedback=feedback,
                    strengths=strengths,
                    weaknesses=weaknesses,
                    interview_id=interview_id
                )

            return interview
        finally:
            self._close_connection(conn)

    def get_interview_history(self, candidate_id: str) -> List[Interview]:
        """Retrieves all past interview sessions taken by a candidate."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT id FROM interviews WHERE candidate_id = ? ORDER BY date DESC, rowid DESC;", (candidate_id,))
            rows = cursor.fetchall()
        finally:
            self._close_connection(conn)
            
        interviews = []
        shared_candidate = None
        
        for (interview_id,) in rows:
            interview = self.get_interview(interview_id)
            if interview:
                if shared_candidate is None:
                    shared_candidate = interview.candidate
                else:
                    interview._candidate = shared_candidate
                interviews.append(interview)
                
        if shared_candidate is not None:
            shared_candidate._interview_history = []
            for interview in interviews:
                if interview not in shared_candidate.interview_history:
                    shared_candidate.interview_history.append(interview)
                    
        return interviews

    # CamelCase aliases for backwards compatibility
    def saveInterview(self, interview: Interview) -> None:
        """CamelCase alias for save_interview."""
        self.save_interview(interview)

    def getInterview(self, id: str) -> Optional[Interview]:
        """CamelCase alias for get_interview."""
        return self.get_interview(id)

    def getInterviewHistory(self, candidateId: str) -> List[Interview]:
        """CamelCase alias for get_interview_history."""
        return self.get_interview_history(candidateId)
