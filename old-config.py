class Config:
    CREDENTIALS_FILE = 'config/credentials.json'
    TOKEN_FILE = 'token.pickle'
    SCOPES = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events'
    ]