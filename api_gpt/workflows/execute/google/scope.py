from typing import List


def get_scope_for_app(app_name: str) -> List[str]:
    lower_name = app_name.lower()
    scopes = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    if 'calendar' in lower_name:
        return scopes + [
            'https://www.googleapis.com/auth/calendar.events',
        ]
    elif 'gmail' in lower_name or 'email' in lower_name:
        return scopes + [
            'https://www.googleapis.com/auth/gmail.modify',
        ]
    elif 'slide' in lower_name:
        return scopes + [
            'https://www.googleapis.com/auth/presentations',
        ]
    elif 'docs' in lower_name:
        return scopes + ['https://www.googleapis.com/auth/documents']
    return scopes