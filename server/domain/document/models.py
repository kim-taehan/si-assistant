from sqlalchemy import Column, BigInteger, String, DateTime, func, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Document(Base):
    __tablename__ = "document"

    id = Column(BigInteger, primary_key=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    uploaded_by = Column(String(50), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    expire_at = Column(Date, nullable=False)
    status = Column(String(20), default="active")
