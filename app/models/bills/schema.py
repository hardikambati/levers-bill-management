from typing import (
    List,
    Optional,
)
from pydantic import (
    BaseModel,
    Field,
)


class SubBillBase(BaseModel):

    amount: float = Field(..., description="Amount of the sub bill (required)")
    reference: Optional[str] = Field(None, description="Reference tag for identification", max_length=255, case_sensitive=False)


class SubBill(SubBillBase):

    id: int = None

    class Config:
        orm_mode = True


class BillBase(BaseModel):

    total: float = Field(..., description="Total amount of sub bill (required)")
    sub_bills: List[SubBillBase] = Field(..., description="List of sub bills")


class Bill(BillBase):

    id: int = None

    class Config:
        orm_mode = True