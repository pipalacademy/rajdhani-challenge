create table app (
    id integer primary key,
    domain text,
    current_task text,
    score int,
    healthy int default 1,
    created text,
    last_updated text
);

-- the completed_tasks table maintains the list of tasks that are
-- completed for each app. When a completed task is broken due to
-- a subsequent change, it is marked as broken.
create table completed_tasks (
    id integer primary key,
    app_id integer references app(id),
    task text,
    broken integer default 0,
    timestamp text
);

-- changelog maintains all the changes to an app
-- entries could be one of the following types
--   deployed
--   task-done
--   site-unhealthy
--   site-healthy
--   tasks-broken
create table changelog (
    id integer primary key,
    app_id integer references app(id),
    timestamp text,
    type text,
    message text
);
