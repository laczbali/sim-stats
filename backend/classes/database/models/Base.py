from sqlalchemy.ext.declarative import declarative_base

# modell classes need to inherit from this, so that sqlalchemy knows how to handle them
Base = declarative_base()