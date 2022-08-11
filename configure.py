import os

from app.extension.database import metadata
from app.extension.database import servers
from app.extension.database import sqlalchemy


engine = sqlalchemy.create_engine(os.environ.get("DATABASE_URL"))
metadata.create_all(engine, tables=[servers])
