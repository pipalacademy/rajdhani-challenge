import web
import datetime

db = web.database("sqlite:///rajdhani.db")

def get_apps():
    apps = db.select("app", order="score desc")
    return [process_app(app) for app in apps]

def get_app(name):
    row = db.where("app", name=name).first()
    if row:
        return process_app(row)

def process_app(app):
    app.created = parse_timestamp(app.created)
    app.last_updated = parse_timestamp(app.last_updated)
    return app

class App:
    def __init__(self, row):
        self.id = row.id
        self.name = row.name
        self.current_task = row.current_task
        self.score = row.score
        self.created = self.parse_timestamp(row.created)
        self.last_updated = self.parse_timestamp(row.last_updated)

    def parse_timestamp(self, timestamp):
        return datetime.datetime.fromisoformat(timestamp)

    @classmethod
    def find_all(cls):
        rows = db.select("app", order="score desc")
        return [cls(row) for row in rows]

    @classmethod
    def find(cls, name):
        row = db.where("app", name=name).first()
        if row:
            return cls(row)

    def is_task_done(self, task_name):
        rows = db.where("completed_tasks", app_id=self.id, task=task_name)
        return bool(rows)

    def mark_task_as_done(self, task_name):
        self.add_changelog("task-done", f"Completed task {task_name}.")
        db.insert("completed_tasks", app_id=self.id, task=task_name)

    def get_changelog(self):
        rows = db.where("changelog", app_id=self.id, order="timestamp desc")
        return [self._process_changelog(row) for row in rows]

    def _process_changelog(self, row):
        row.timestamp = self.parse_timestamp(row.timestamp)
        return row

    def add_changelog(self, type, message):
        db.insert("changelog", app_id=self.id, type=type, message=message)

    def _update(self, **kwargs):
        db.update("app", **kwargs, where="id=$id", vars={"id": self.id})

    def update_score(self):
        rows = db.where("completed_tasks", app_id=self.id).list()
        score = len(rows)
        self._update(score=score)

    def update_status(self, status):
        self.add_changelog("deploy", "Deployed the app")
        self._update(current_task=status['current_task'])

        completed_tasks = [task for task, done in status['status'].items() if done]
        for task in completed_tasks:
            if not self.is_task_done(task):
                self.mark_task_as_done(task)

        self.update_score()

def main():
    import sys
    app_name = sys.argv[1]
    db.insert("app", name=app_name, score=0, current_task="homepage")
    print("Created new app", app_name)

if __name__ == "__main__":
    main()
