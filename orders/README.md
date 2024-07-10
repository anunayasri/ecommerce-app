Order:
    id: int
    buyer_id: int
    address_id: int
    payable: float
    payable_currency: str
    status: str : CREATED, PAYMENT_FAILED, PAYMENT_SUCCESS
    created_at: datetime
    updated_at: datetime
    
OrderItems:
    id: int
    order_id: int
    product_id: int
    quantity: int
    created_at: datetime
    updated_at: datetime

```python
from db.sql_repository import *

create_db()


ord = Order(id=1, buyer_id=10)
repo = OrderSrvSQLRepo()
repo.create_order(ord)
repo.get_order_by_id(1)

```

