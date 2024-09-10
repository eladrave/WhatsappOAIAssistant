import time
from .Session import Session

import logging

logger = logging.getLogger(__name__)



class SessionManager:
    def __init__(self, timeout:float =180):
        self.sessions = {}
        self.timeout = timeout

    def create_session(self, session: Session):
        """
        Create a new session for a user.
        """
        session_obj = {
            "user_id": session.user_id,
            "timestamp": time.time(),
            "session": session
        }

        logger.info(f"Creating session: {session.user_id}")

        self.sessions[session.user_id] = session_obj


    def delete_session(self, user_id: str):
        """
        Delete a session for a user.
        """

        logger.info(f"Deleting session: {user_id}")

        if user_id in self.sessions:
            del self.sessions[user_id]

    def is_session_active(self, user_id: str):
        """
        Check if a session is active for a user.
        """
        logger.info(f"Checking if session is active for user {user_id}")
        if user_id in self.sessions:
            return time.time() - self.sessions[user_id]['timestamp'] < self.timeout
        return False

    def get_session(self, user_id: str):
        """
        Retrieve the session data by id.
        does not check if session is active (causes error if session is not active)
        """

        # does not check if session is active
        return self.sessions.get(user_id, None)['session']        

    def update_sessions(self):
        """
        Update the session timestamps and delete expired sessions.
        """
        logger.info("Updating sessions")
        outdated_sessions = []
        for session_id in list(self.sessions.keys()):
            if not self.is_session_active(session_id):
                outdated_sessions.append(session_id)
                self.delete_session(session_id)

        logger.info(f"Deleted sessions: {outdated_sessions}")
        return outdated_sessions

    def refresh_session(self, user_id: str):
        """
        Reset the session timestamp.
        """
        logger.info(f"Resetting session: {user_id}")
        if user_id in self.sessions:
            self.sessions[user_id]['timestamp'] = time.time()
        else:
            logger.info(f"Session not found: {user_id}")

