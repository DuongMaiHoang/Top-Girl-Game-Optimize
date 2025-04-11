from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models import Building
from database import get_db
from pydantic import BaseModel
from typing import List, Optional
import math
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSION_DURATION_SECONDS = 10800  # 3 hours
LAST_OPTIMIZE_INPUT = None

def calculate_base_income(employees: int, coefficient: float) -> float:
    return employees * 645 + 2433.3 * coefficient

class BuildingCreate(BaseModel):
    name: str
    curr_level: int
    num_employees: int
    curr_coefficient: float
    next_coefficient: float
    gold_to_upgrade: float
    curr_total_income: float

class BuildingUpdate(BaseModel):
    name: Optional[str] = None
    curr_level: Optional[int] = None
    num_employees: Optional[int] = None
    curr_coefficient: Optional[float] = None
    next_coefficient: Optional[float] = None
    gold_to_upgrade: Optional[float] = None
    curr_total_income: float

class BuildingLevelUp(BaseModel):
    curr_level: int
    curr_coefficient: float
    next_coefficient: float

class BuildingRead(BaseModel):
    id: int
    name: str
    curr_level: int
    num_employees: int
    curr_coefficient: float
    next_coefficient: float
    curr_total_income: float
    gold_to_upgrade: float
    idol_income: float

    class Config:
        orm_mode = True

class OptimizeRequest(BaseModel):
    current_money: float
    current_gold: float
    trade_x: float
    trade_y: float
    session_seconds: int = SESSION_DURATION_SECONDS

class UpgradeAction(BaseModel):
    building_id: int
    building_name: str
    upgrade_time: int
    new_total_income: float
    curr_level: int

class OptimizeResponse(BaseModel):
    total_income_earned: float
    final_income_per_second: float
    upgrade_plan: List[UpgradeAction]



@app.post("/buildings", response_model=BuildingRead)
async def create_building(building: BuildingCreate, db: AsyncSession = Depends(get_db)):
    base_income = calculate_base_income(building.num_employees, building.curr_coefficient)
    idol_income = building.curr_total_income - base_income
    new_building = Building(**building.dict(), idol_income=idol_income)
    db.add(new_building)
    await db.commit()
    await db.refresh(new_building)
    return new_building

@app.get("/buildings", response_model=List[BuildingRead])
async def get_all_buildings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Building))
    return result.scalars().all()

@app.get("/buildings/{building_id}", response_model=BuildingRead)
async def get_building(building_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building

@app.patch("/buildings/{building_id}", response_model=BuildingRead)
async def patch_building(building_id: int, update: BuildingUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    for field, value in update.dict(exclude_unset=True).items():
        setattr(building, field, value)

    base_income = calculate_base_income(building.num_employees, building.curr_coefficient)
    building.idol_income = update.curr_total_income - base_income
    building.curr_total_income = update.curr_total_income

    await db.commit()
    await db.refresh(building)
    return building

@app.patch("/buildings/{building_id}/levelup", response_model=BuildingRead)
async def patch_level_up(building_id: int, payload: BuildingLevelUp, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    building.curr_level = payload.curr_level
    building.curr_coefficient = payload.curr_coefficient
    building.next_coefficient = payload.next_coefficient

    base_income = calculate_base_income(building.num_employees, building.curr_coefficient)
    building.curr_total_income = base_income + building.idol_income

    await db.commit()
    await db.refresh(building)
    return building

@app.delete("/buildings/{building_id}", response_model=dict)
async def delete_building(building_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    await db.delete(building)
    await db.commit()
    return {"message": "Building deleted successfully"}

@app.post("/buildings/{building_id}/upgrade", response_model=BuildingRead)
async def upgrade_building(building_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    building.curr_level += 1
    building.curr_coefficient = building.next_coefficient
    base_income = calculate_base_income(building.num_employees, building.curr_coefficient)
    building.curr_total_income = base_income + building.idol_income
    building.next_coefficient += 0.1  # placeholder logic

    await db.commit()
    await db.refresh(building)
    return building

@app.post("/optimize", response_model=OptimizeResponse)
async def optimize_income_plan(request: OptimizeRequest, db: AsyncSession = Depends(get_db)):
    global LAST_OPTIMIZE_INPUT
    LAST_OPTIMIZE_INPUT = {
        "current_money": request.current_money,
        "current_gold": request.current_gold,
        "trade_x": request.trade_x,
        "trade_y": request.trade_y,
        "session_seconds": request.session_seconds
    }

    result = await db.execute(select(Building))
    buildings = result.scalars().all()

    def calculate_income(buildings):
        return sum((b.num_employees * 645 + 2433.3 * b.curr_coefficient + b.idol_income) for b in buildings)

    def trade_money_to_gold(money):
        return math.floor(money / (request.trade_x * 5)) * request.trade_y

    time = 0
    gold = request.current_gold
    money = request.current_money
    buildings_state = [b for b in buildings]
    income_per_sec = calculate_income(buildings_state)
    total_earned = 0
    actions = []

    while time < request.session_seconds:
        if time > 0:
            money += income_per_sec
            total_earned += income_per_sec

        traded_gold = trade_money_to_gold(money)
        if traded_gold >= 1:
            trade_cost = (request.trade_x * 5) * (traded_gold / request.trade_y)
            money -= trade_cost
            gold += traded_gold

        affordable = [
            (b.gold_to_upgrade, i, b)
            for i, b in enumerate(buildings_state)
            if b.gold_to_upgrade <= gold
        ]
        if affordable:
            best_upgrade = max(affordable, key=lambda item: (
                (item[2].num_employees * 645 + 2433.3 * item[2].next_coefficient + item[2].idol_income) -
                (item[2].num_employees * 645 + 2433.3 * item[2].curr_coefficient + item[2].idol_income)
            ))
            _, idx, b = best_upgrade

            gold -= b.gold_to_upgrade
            b.curr_level += 1
            b.curr_coefficient = b.next_coefficient
            b.curr_total_income = b.num_employees * 645 + 2433.3 * b.curr_coefficient + b.idol_income
            b.next_coefficient += 0.1
            income_per_sec = calculate_income(buildings_state)

            actions.append(UpgradeAction(
                building_id=b.id,
                building_name=b.name,
                upgrade_time=time,
                new_total_income=b.curr_total_income,
                curr_level=b.curr_level
            ))

        time += 1

    return OptimizeResponse(
        total_income_earned=round(total_earned, 2),
        final_income_per_second=round(income_per_sec, 2),
        upgrade_plan=actions
    )

@app.get("/optimize/last")
async def get_last_optimize_input():
    if not LAST_OPTIMIZE_INPUT: 
        return {
        "current_money": 123456789,
        "current_gold": 123456,
        "trade_x": 123,
        "trade_y": 123,
        "session_seconds": 10800
    }
    return LAST_OPTIMIZE_INPUT