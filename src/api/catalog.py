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
        potions = connection.execute(
            sqlalchemy.text(
                "SELECT sku, name, quantity, price, potion_type from potions;"
            )
        ).fetchall()

        catalog = [
            {
                "sku": row[0],
                "name": row[1],
                "quantity": row[2],
                "price": row[3],
                "potion_type": row[4],
            }
            for row in potions
        ]

    return catalog