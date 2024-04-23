from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        inventory = connection.execute(
            sqlalchemy.text(
                "SELECT num_red_ml, num_green_ml, num_blue_ml, gold FROM global_inventory LIMIT 1;"
            )
        ).fetchone()

        red_ml = inventory[0]
        green_ml = inventory[1]
        blue_ml = inventory[2]
        gold = inventory[3]

        num_potions = connection.execute(
            sqlalchemy.text("SELECT SUM(quantity) FROM potions;")
        ).fetchone()[0]

    return {
        "number_of_potions": num_potions,
        "ml_in_barrels": green_ml + blue_ml + red_ml,
        "gold": gold,
    }

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"
