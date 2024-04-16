
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"Delivered: {barrels_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml + :quantity, gold = gold - :price;"), {"quantity": barrel.quantity * barrel.ml_per_barrel, "price": barrel.price})

    return "OK"


def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory ORDER BY created_at DESC LIMIT 1;"))

        inventory = result.fetchone()
        for barrel in wholesale_catalog:  
            if barrel.sku == "SMALL_GREEN_BARREL":
                if inventory[2] < 10 and inventory[4] >= barrel.price:
                    return [
                        {
                            "sku": barrel.sku,
                            "quantity": 1,
                        }
                    ]

    return []
