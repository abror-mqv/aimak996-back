from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    name = 'fb'

    def ready(self):
        # connect signals within this app
        from . import signals  # noqa: F401

        # initialize Firebase Admin SDK once, if credentials JSON is present
        try:
            import os
            import firebase_admin
            from firebase_admin import credentials

            if not firebase_admin._apps:  # ensure single initialization
                app_dir = os.path.dirname(__file__)
                cred_path = os.path.join(app_dir, 'nookat-996-bfc91-firebase-adminsdk-fbsvc-a1374e00cd.json')

                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # Credentials file not found; skip initialization
                    pass
        except Exception:
            # Do not block app startup/migrations if Firebase init fails
            pass
