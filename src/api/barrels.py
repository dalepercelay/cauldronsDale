
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
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            connection.execute(
                sqlalchemy.text(
                    f"""
                    INSERT INTO global_inventory (num_red_ml, num_green_ml, num_blue_ml, gold, description) VALUES (
                    {barrel.potion_type[0] * barrel.quantity * barrel.ml_per_barrel},
                    {barrel.potion_type[1] * barrel.quantity * barrel.ml_per_barrel},
                    {barrel.potion_type[2] * barrel.quantity * barrel.ml_per_barrel},
                    {-barrel.price},
                    'Barrel order {order_id}: {barrel.sku} delivered');
                    """
                ),
            )

    return "OK"


@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        inventory = connection.execute(
            sqlalchemy.text(
                "SELECT SUM(num_red_ml), SUM(num_green_ml), SUM(num_blue_ml), SUM(gold) FROM global_inventory;"
            )
        ).fetchone()

        num_red_ml = inventory[0]
        num_green_ml = inventory[1]
        num_blue_ml = inventory[2]
        gold = inventory[3]

        if num_green_ml <= num_blue_ml and num_green_ml <= num_red_ml:
            for barrel in wholesale_catalog:
                if barrel.potion_type == [0, 1, 0, 0]:
                    if gold >= barrel.price:
                        return [
                            {
                                "sku": barrel.sku,
                                "quantity": 1,
                            }
                        ]
        if num_blue_ml <= num_green_ml and num_blue_ml <= num_red_ml:
            for barrel in wholesale_catalog:
                if barrel.potion_type == [0, 0, 1, 0]:
                    if gold >= barrel.price:
                        return [
                            {
                                "sku": barrel.sku,
                                "quantity": 1,
                            }
                        ]
        if num_red_ml <= num_green_ml and num_red_ml <= num_blue_ml:
            for barrel in wholesale_catalog:
                if barrel.potion_type == [1, 0, 0, 0]:
                    if gold >= barrel.price:
                        return [
                            {
                                "sku": barrel.sku,
                                "quantity": 1,
                            }
                        ]

    return []