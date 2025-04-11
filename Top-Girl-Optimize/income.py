from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import heapq

app = FastAPI()

SESSION_DURATION_SECONDS = 10800  # 3 hours
MAX_BUILDINGS = 40

# In-memory fake database
buildings_db: Dict[int, 'BuildingInput'] = {}
building_id_counter = 1  # Auto-increment ID tracker


class BuildingInput(BaseModel):
    id: int
    name: str
    curr_level: int
    num_employees: int
    curr_coefficient: float
    next_coefficient: float
    curr_total_income: float
    gold_to_upgrade: float


class OptimizeRequest(BaseModel):
    current_money: float
    current_gold: float
    trade_x: float  # money needed = x * 5
    trade_y: float  # gold received
    buildings: List[BuildingInput]
    session_seconds: int = SESSION_DURATION_SECONDS


class UpgradeAction(BaseModel):
    building_id: int
    building_name: str
    upgrade_time: int  # seconds since session start
    new_total_income: float
    curr_level: int


class OptimizeResponse(BaseModel):
    total_income_earned: float
    final_income_per_second: float
    upgrade_plan: List[UpgradeAction]


@app.post("/optimize", response_model=OptimizeResponse)
def optimize_income_plan(request: OptimizeRequest):
    buildings = request.buildings
    current_gold = request.current_gold
    current_money = request.current_money
    trade_x = request.trade_x
    trade_y = request.trade_y
    session_time = request.session_seconds

    global LAST_OPTIMIZE_INPUT
    LAST_OPTIMIZE_INPUT = {
        "current_money": request.current_money,
        "current_gold": request.current_gold,
        "trade_x": request.trade_x,
        "trade_y": request.trade_y,
        "session_seconds": request.session_seconds
    }

    def calculate_income(buildings):
        return sum((b.num_employees * 645 + 2433.3 * b.curr_coefficient) for b in buildings)

    def trade_money_to_gold(money):
        return (money // (trade_x * 5)) * trade_y

    def simulate():
        time = 0
        gold = current_gold
        money = current_money
        buildings_state = [b.copy(update={}) for b in buildings]
        income_per_sec = calculate_income(buildings_state)
        total_earned = 0
        actions = []

        while time < session_time:
            if time > 0:
                money += income_per_sec
                total_earned += income_per_sec

            traded_gold = trade_money_to_gold(money)
            if traded_gold >= 1:
                trade_cost = (trade_x * 5) * (traded_gold / trade_y)
                money -= trade_cost
                gold += traded_gold

            affordable = [
                (b.gold_to_upgrade, i, b)
                for i, b in enumerate(buildings_state)
                if b.gold_to_upgrade <= gold
            ]
            if affordable:
                best_upgrade = max(affordable, key=lambda item: (
                    (item[2].num_employees * 645 + 2433.3 * item[2].next_coefficient) -
                    (item[2].num_employees * 645 + 2433.3 * item[2].curr_coefficient)
                ))
                _, idx, b = best_upgrade

                gold -= b.gold_to_upgrade
                b.curr_level += 1
                b.curr_coefficient = b.next_coefficient
                b.curr_total_income = b.num_employees * 645 + 2433.3 * b.curr_coefficient
                b.next_coefficient += 0.1  # Placeholder logic
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

    return simulate()


@app.get("/buildings", response_model=List[BuildingInput])
def get_buildings():
    return list(buildings_db.values())


@app.get("/buildings/{building_id}", response_model=BuildingInput)
def get_building(building_id: int):
    if building_id not in buildings_db:
        raise HTTPException(status_code=404, detail="Building not found")
    return buildings_db[building_id]


@app.post("/buildings", response_model=BuildingInput)
def create_building(building: BuildingInput):
    global building_id_counter
    if len(buildings_db) >= MAX_BUILDINGS:
        raise HTTPException(status_code=400, detail="Max number of buildings reached")

    building_id = building_id_counter
    building_id_counter += 1

    new_building = BuildingInput(
        id=building_id,
        name=building.name,
        curr_level=building.curr_level,
        num_employees=building.num_employees,
        curr_coefficient=building.curr_coefficient,
        next_coefficient=building.next_coefficient,
        curr_total_income=building.num_employees * 645 + 2433.3 * building.curr_coefficient,
        gold_to_upgrade=building.gold_to_upgrade
    )
    buildings_db[building_id] = new_building
    return new_building


@app.put("/buildings/{building_id}", response_model=BuildingInput)
def update_building(building_id: int, update: BuildingInput):
    if building_id not in buildings_db:
        raise HTTPException(status_code=404, detail="Building not found")
    update.curr_total_income = update.num_employees * 645 + 2433.3 * update.curr_coefficient
    buildings_db[building_id] = update
    return update


@app.post("/buildings/{building_id}/upgrade", response_model=BuildingInput)
def upgrade_building(building_id: int):
    if building_id not in buildings_db:
        raise HTTPException(status_code=404, detail="Building not found")
    building = buildings_db[building_id]
    building.curr_level += 1
    building.curr_coefficient = building.next_coefficient
    building.curr_total_income = building.num_employees * 645 + 2433.3 * building.curr_coefficient
    building.next_coefficient += 0.1  # Placeholder logic for next level
    return building

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