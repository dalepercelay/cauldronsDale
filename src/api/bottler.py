
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"Delievered Potions: {potions_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
        for potion in potions_delivered:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions + :potion_quantity, num_green_ml = num_green_ml - :ml_quantity;"), {"potion_quantity": potion.quantity, "ml_quantity": potion.quantity * 100})

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """


    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory LIMIT 1;"))

        green_ml = result.scalar()
        bottled_quantity = green_ml // 100

        if bottled_quantity == 0:
            return []

        return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": bottled_quantity,
            }
        ]
    
    

if __name__ == "__main__":
    print(get_bottle_plan())
