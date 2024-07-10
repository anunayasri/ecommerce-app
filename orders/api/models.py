from pydantic.dataclasses import dataclass

@dataclass
class CreateOrderReq:
    buyer_id: int

