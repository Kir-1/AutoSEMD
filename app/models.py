from sqlalchemy import Column, Integer, String, Text, ForeignKey, BOOLEAN
from sqlalchemy.orm import relationship

from app.database import Base


# Определение таблиц
class Semd(Base):
    __tablename__ = "Semd"
    id = Column(Integer, primary_key=True, autoincrement=True)
    oid = Column(String(255), unique=True, nullable=False)
    code = Column(Integer, nullable=False)


class SemdPropertyType(Base):
    __tablename__ = "SemdPropertyType"
    id = Column(Integer, primary_key=True, autoincrement=True)
    db_name = Column(String(255), nullable=True)
    alias = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    sql_query_id = Column(Integer, ForeignKey("SemdSQL.id"))


class SemdProperty(Base):
    __tablename__ = "SemdProperty"
    id = Column(Integer, primary_key=True, autoincrement=True)
    xpath_name = Column(Text, nullable=False)
    semdPropertyType_id = Column(Integer, ForeignKey("SemdPropertyType.id"))
    semdPropertyType = relationship("SemdPropertyType")


class Semd_SemdProperty(Base):
    __tablename__ = "Semd_SemdProperty"
    semd_id = Column(Integer, ForeignKey("Semd.id"), primary_key=True)
    semdProperty_id = Column(Integer, ForeignKey("SemdProperty.id"), primary_key=True)


class SemdSQL(Base):
    __tablename__ = "SemdSQL"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sql_query = Column(Text, nullable=True)
    is_const = Column(BOOLEAN, nullable=True)

