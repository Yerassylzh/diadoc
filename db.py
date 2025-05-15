from datetime import datetime
import os
from supabase import create_client, Client


class Supabase:
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    @property
    def db(self):
        return self.supabase


class UserManager:
    def __init__(self, db: Client):
        self.table = db.table("user")

    def create(self, **kwargs):
        """Creates a brand new user"""
        return self.table.insert(kwargs).execute()

    def get_all(self):
        return self.table.select("*").execute().data


class FeedbackManager:
    def __init__(self, db: Client):
        self.table = db.table("feedback")

    def create(self, **kwargs):
        return self.table.insert(kwargs).execute()

    def get(self, user_id, start_date: None | datetime = None):
        if not start_date:
            return self.table.select("*").eq("user_id", user_id).execute().data
        return (
            self.table.select("*")
            .eq("user_id", user_id)
            .gte("created_at", start_date.isoformat())
            .execute()
            .data
        )
