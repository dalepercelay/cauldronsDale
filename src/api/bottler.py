
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
            connection.execute(
                sqlalchemy.text(
                    f"""
                    UPDATE global_inventory SET
                    num_red_ml = num_red_ml - {potion.potion_type[0] * potion.quantity},
                    num_green_ml = num_green_ml - {potion.potion_type[1] * potion.quantity},
                    num_blue_ml = num_blue_ml - {potion.potion_type[2] * potion.quantity};
                    UPDATE potions SET quantity = quantity + {potion.quantity}
                    WHERE potion_type = ARRAY{potion.potion_type}::int[];
                    """
                ),
            )

    return "OK"


@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    with db.engine.begin() as connection:
        inventory = connection.execute(
            sqlalchemy.text(
                "SELECT num_green_ml, num_blue_ml, num_red_ml FROM global_inventory LIMIT 1;"
            )
        ).fetchone()

        green_ml = inventory[0]
        blue_ml = inventory[1]
        red_ml = inventory[2]

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
        if blue_ml >= 50 and green_ml >= 50:
            order.append(
                {
                    "potion_type": [0, 50, 50, 0],
                    "quantity": blue    _ml // 50,
                }
            )

        return order
    
    

if __name__ == "__main__":
    print(get_bottle_plan())
