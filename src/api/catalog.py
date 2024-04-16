from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                "SELECT num_green_potions, num_blue_potions, num_red_potions FROM global_inventory LIMIT 1;"
            )
        )
        row = result.fetchone()
        num_green_potions = row[0]
        num_blue_potions = row[1]
        num_red_potions = row[2]

        catalog = []
        if num_green_potions != 0:
            catalog.append(
                {
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "price": 50,
                    "potion_type": [0, 100, 0, 0],
                }
            )
        if num_blue_potions != 0:
            catalog.append(
                {
                    "sku": "BLUE_POTION_0",
                    "name": "blue potion",
                    "price": 50,
                    "potion_type": [0, 0, 100, 0],
                }
            )
        if num_red_potions != 0:
            catalog.append(
                {
                    "sku": "RED_POTION_0",
                    "name": "red potion",
                    "price": 50,
                    "potion_type": [100, 0, 0, 0],
                }
            )

    return catalog