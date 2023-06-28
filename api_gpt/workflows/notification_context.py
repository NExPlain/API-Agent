from typing import Dict, Optional


class NotificationContext:
    """A context for managing notifications."""

    def __init__(
        self,
        email_dict: Dict[str, str],
        workflow_id: str,
        user_id: str,
        user_name: str,
        user_email: str,
        context: Optional[str] = None,
    ):
        """
        Initialize a new notification context.

        Args:
            email_dict (Dict[str, str]): A dictionary containing the email details. It should have the following structure:
                {
                    'id': id,
                    'subject': subject,
                    'from': email_from,
                    'to': email_to,
                    'timestamp': timestamp,
                    'content': content,
                    'snippet': snippet,
                    'html': html
                }

            workflow_id (str): The ID associated with the workflow.

            user_id (str): The ID associated with the user.

            user_name (str): The name of the user.

            user_email (str): The email address of the user.

            context (Optional[str], optional): Additional context for the notification. Defaults to None.
        """

        self.email_dict = email_dict
        self.workflow_id = workflow_id
        self.user_id = user_id
        self.user_name = user_name
        self.user_email = user_email
        self.context = context
