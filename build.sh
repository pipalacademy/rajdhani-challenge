# NOTE: by hamr convention, this should ideally be in $APP_ROOT/private/
# directory, but all the rajdhani projects also follow the same convention
# that the database will be in the same folder as the app directory.
sqlite3 $APP_ROOT/app/rajdhani.db < $APP_ROOT/app/schema.sql
