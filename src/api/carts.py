
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku,
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    sort_col_mapping = {
        search_sort_options.customer_name: "customer_name",
        search_sort_options.item_sku: "sku",
        search_sort_options.line_item_total: "total",
        search_sort_options.timestamp: "created_at",
    }

    sort_col = sort_col_mapping.get(sort_col)

    offset = int(search_page) if search_page else 0
    limit = 5

    with db.engine.begin() as connection:
        results = connection.execute(
            sqlalchemy.text(
                f"""
                SELECT cart_items.id, cart_items.sku, carts.customer_name, (potions.price * cart_items.quantity) as total, cart_items.created_at
                FROM cart_items
                JOIN carts ON cart_items.cart_id = carts.id
                JOIN potions ON cart_items.sku = potions.sku
                WHERE carts.customer_name ILIKE '%{customer_name}%'
                AND cart_items.sku ILIKE '%{potion_sku}%'
                ORDER BY {sort_col} {sort_order.value}
                LIMIT {limit} OFFSET {offset};
                """
            ),
        ).fetchall()

    previous = "" if offset == 0 else str(offset - limit)
    next = "" if len(results) < limit else str(offset + limit)
    results = [{
                "line_item_id": row[0],
                "item_sku": row[1],
                "customer_name": row[2],
                "line_item_total": row[3],
                "timestamp": row[4].isoformat(),
                } for row in results]

    return {
        "previous": previous,
        "next": next,
        "results": results,
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int


@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"



@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    with db.engine.begin() as connection:
        id = connection.execute(
            sqlalchemy.text(
                f"""
                INSERT INTO carts (customer_name)
                VALUES ('{new_cart.customer_name}')
                RETURNING id;
                """
            ),
        ).fetchone()[0]

    return {"cart_id": id}



class CartItem(BaseModel):
    quantity: int



@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                f"""
                INSERT INTO cart_items (cart_id, sku, quantity)
                VALUES ({cart_id}, '{item_sku}', {cart_item.quantity});
                """
            ),
        )
    return "OK"




class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
        cart_items = connection.execute(
            sqlalchemy.text(
                f"""
                SELECT cart_items.sku, cart_items.quantity, potions.price 
                FROM cart_items 
                JOIN potions ON cart_items.sku = potions.sku 
                WHERE cart_id = {cart_id};
                """
            ),
        ).fetchall()

        transaction = connection.execute(
            sqlalchemy.text(
                f"""
                INSERT INTO potion_transactions (description) VALUES ('Cart {cart_id} checkout')
                RETURNING id;
                """
            ),
        ).fetchone()[0]

        for item_sku, quantity, _ in cart_items:
            connection.execute(
                sqlalchemy.text(
                    f"""
                    INSERT INTO ledger_entries (sku, quantity, transaction) VALUES (
                    '{item_sku}',
                    {-quantity},
                    {transaction});
                    """
                ),
            )

        total_potions = sum(quantity for _, quantity, _ in cart_items)
        total_gold = sum((price * quantity) for _, quantity, price in cart_items)

        connection.execute(
            sqlalchemy.text(
                f"""
                INSERT INTO global_inventory (num_red_ml, num_green_ml, num_blue_ml, gold, description) VALUES (
                0,
                0,
                0,
                {total_gold},
                'Cart {cart_id} checkout');
                """
            ),
        )


        return {
            "total_potions_bought": total_potions,
            "total_gold_paid": total_gold,
        }