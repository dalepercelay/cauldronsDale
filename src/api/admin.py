from fastapi import APIRouter, Depends
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM global_inventory;
                DELETE FROM ledger_entries;
                DELETE FROM potion_transactions;
                DELETE FROM carts;
                DELETE FROM cart_items;
                INSERT INTO global_inventory (num_red_ml, num_green_ml, num_blue_ml, gold, description)
                VALUES (0, 0, 0, 100, 'Game reset');
                """
            )
        )


    return "OK"

