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
                """
                SELECT p.sku, p.name, SUM(ple.quantity), p.price, p.potion_type 
                FROM potions p
                JOIN ledger_entries ple ON p.sku = ple.sku
                GROUP BY p.sku, p.name, p.price, p.potion_type
                HAVING SUM(ple.quantity) > 0;
                """
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