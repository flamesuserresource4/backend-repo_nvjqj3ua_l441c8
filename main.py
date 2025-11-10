import os
from datetime import datetime
from typing import Optional, List, Dict

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents

app = FastAPI(title="Coinflow API", description="Smart Budget and Expense Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExpenseIn(BaseModel):
    amount: float
    currency: str = "USD"
    date: Optional[str] = None  # ISO string
    merchant: Optional[str] = None
    note: Optional[str] = None
    category: Optional[str] = None
    account: Optional[str] = None
    type: str = "debit"


class BudgetIn(BaseModel):
    category: str
    amount: float
    month: Optional[str] = None  # YYYY-MM


class GoalIn(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0
    deadline: Optional[str] = None  # ISO date


@app.get("/")
def read_root():
    return {"message": "Coinflow Backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# -----------------------------
# Expense Endpoints
# -----------------------------
@app.post("/api/expenses")
def add_expense(expense: ExpenseIn):
    try:
        data = expense.model_dump()
        data["date"] = data.get("date") or datetime.utcnow().isoformat()
        inserted_id = create_document("expense", data)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/expenses")
def list_expenses(category: Optional[str] = None, limit: int = Query(50, ge=1, le=500)):
    try:
        filter_query: Dict = {"type": "debit"}
        if category:
            filter_query["category"] = category
        docs = get_documents("expense", filter_query, limit=limit)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"ok": True, "items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# Budget Endpoints
# -----------------------------
@app.post("/api/budgets")
def add_budget(budget: BudgetIn):
    try:
        data = budget.model_dump()
        inserted_id = create_document("budget", data)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/budgets")
def list_budgets(month: Optional[str] = None, limit: int = Query(50, ge=1, le=200)):
    try:
        filter_query: Dict = {}
        if month:
            filter_query["month"] = month
        docs = get_documents("budget", filter_query, limit=limit)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"ok": True, "items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# Goals Endpoints
# -----------------------------
@app.post("/api/goals")
def add_goal(goal: GoalIn):
    try:
        data = goal.model_dump()
        inserted_id = create_document("goal", data)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/goals")
def list_goals(limit: int = Query(50, ge=1, le=200)):
    try:
        docs = get_documents("goal", {}, limit=limit)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"ok": True, "items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
