
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
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
        for potion in potions_delivered:
            if potion.potion_type == [0, 100, 0, 0]:
                connection.execute(
                    sqlalchemy.text(
                        "UPDATE global_inventory SET num_green_potions = num_green_potions + :potion_quantity, num_green_ml = num_green_ml - :ml_quantity;"
                    ),
                    {
                        "potion_quantity": potion.quantity,
                        "ml_quantity": potion.quantity * 100,
                    },
                )
            elif potion.potion_type == [0, 0, 100, 0]:
                connection.execute(
                    sqlalchemy.text(
                        "UPDATE global_inventory SET num_blue_potions = num_blue_potions + :potion_quantity, num_blue_ml = num_blue_ml - :ml_quantity;"
                    ),
                    {
                        "potion_quantity": potion.quantity,
                        "ml_quantity": potion.quantity * 100,
                    },
                )
            elif potion.potion_type == [100, 0, 0, 0]:
                connection.execute(
                    sqlalchemy.text(
                        "UPDATE global_inventory SET num_red_potions = num_red_potions + :potion_quantity, num_red_ml = num_red_ml - :ml_quantity;"
                    ),
                    {
                        "potion_quantity": potion.quantity,
                        "ml_quantity": potion.quantity * 100,
                    },
                )
            else:
                continue

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                "SELECT num_green_ml, num_blue_ml, num_red_ml FROM global_inventory LIMIT 1;"
            )
        )

        row = result.fetchone()
        green_ml = row[0]
        blue_ml = row[1]
        red_ml = row[2]

        order = []

        if green_ml >= 100:
            order.append(
                {
                    "potion_type": [0, 100, 0, 0],
                    "quantity": green_ml // 100,
                }
            )
        if blue_ml >= 100:
            order.append(
                {
                    "potion_type": [0, 0, 100, 0],
                    "quantity": blue_ml // 100,
                }
            )
        if red_ml >= 100:
            order.append(
                {
                    "potion_type": [100, 0, 0, 0],
                    "quantity": red_ml // 100,
                }
            )

        return order
    
    

if __name__ == "__main__":
    print(get_bottle_plan())
