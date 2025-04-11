from sqlalchemy import Column, Integer, Float, String
from database import Base

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    curr_level = Column(Integer, nullable=False)
    num_employees = Column(Integer, nullable=False)
    curr_coefficient = Column(Float, nullable=False)
    next_coefficient = Column(Float, nullable=False)
    curr_total_income = Column(Float, nullable=False)
    gold_to_upgrade = Column(Float, nullable=False)
    idol_income = Column(Float, nullable=False, default=0.0)
