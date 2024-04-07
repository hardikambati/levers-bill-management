from fastapi import (
    Query,
    FastAPI,
    status,
    Depends,
    HTTPException,
)
from typing import (
    List,
    Optional,
)
from dotenv import load_dotenv
from fastapi_sqlalchemy import DBSessionMiddleware
from sqlalchemy.orm import Session

# custom imports
from .database import (
    engine,
    get_db,
    Base,
    SQLALCHEMY_DATABASE_URL,
)
from .models.bills import schema
from .models.bills import bill as bill_model


# ============ APP CONFIG ============


# FastAPI app instance
app = FastAPI(
    title="Bill Management",
    description="API's that deliver RESTful endpoints for bills management",
    version="1.0.0",
    contact={
        "name": "Hardik Ambati",
        "email": "hardikambati99@gmail.com",
        "url": "https://github.com/hardikambati"
    }
)

# Add session middleware
app.add_middleware(
    DBSessionMiddleware,
    db_url=SQLALCHEMY_DATABASE_URL
)

# Load env variables
load_dotenv()

# Bind tables with engine
Base.metadata.create_all(bind=engine)


# ============ API's ============


@app.get("/")
def root() -> dict:
    """
    Root path page/response
    """
    return {"payload": "Go to http://0.0.0.0:8000/docs"}


@app.get(
    "/health",
    status_code=status.HTTP_200_OK, 
    summary="Health check API"
)
def read_health() -> dict:
    """
    API to read app's health
    """
    return {"payload": "Up and running"}


@app.get(
    "/bills",
    status_code=status.HTTP_200_OK,
    summary="List of bills",
    response_model=List[schema.Bill]
)
def read_bills(
        reference: Optional[str] = Query(None, description="Substring search for reference attribute"),
        total_from: Optional[float] = Query(None, description="Bill amount search for total attribute"),
        db: Session = Depends(get_db)
    ):
    """
    API to read bills
    """
    
    query = db.query(bill_model.Bill)
    
    # filter according to `reference`
    if reference:
        query = query.join(bill_model.SubBill).filter(bill_model.SubBill.reference.ilike(f"%{reference}%"))
    # filter according to `amount`
    if total_from:
        query = query.filter(bill_model.Bill.total==total_from)

    query = query.all()

    response = []
    for bill in query:
        sub_bills_list = []
        for item in bill.sub_bills:
            sub_bills_list.append(
                schema.SubBillBase(amount=item.amount, reference=item.reference)
            )
        response.append(
            schema.Bill(total=bill.total, sub_bills=sub_bills_list)
        )

    return response


@app.post(
    "/bills", 
    status_code=status.HTTP_201_CREATED, 
    summary="Create a bill", 
    response_model=schema.Bill
)
def create_bill(bill: schema.BillBase, db: Session = Depends(get_db)):
    """
    API to create a bill
    """

    total_amount_req = bill.total
    sub_bills_req = bill.sub_bills
    
    sub_bills_list = []
    
    # extract sub_bills
    for item in sub_bills_req:
        # check whether sub-bill with same reference exists or not
        if db.query(bill_model.SubBill).filter(bill_model.SubBill.reference == item.reference).first():
            raise HTTPException(
                status_code=400,
                detail=f"Subbill with reference {item.reference} already exists"
            )
        
        db_sub_bill = bill_model.SubBill(amount=item.amount, reference=item.reference)
        sub_bills_list.append(db_sub_bill)

    # create bill
    db_bill = bill_model.Bill(
        total=total_amount_req,
        sub_bills=sub_bills_list
    )

    # commit bill
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    
    # construct response
    response = {
        "total": db_bill.total,
        "id": db_bill.id,
        "sub_bills": [
            {"amount": item.amount, "reference": item.reference} 
            for item in sub_bills_list
        ]
    }

    return response
