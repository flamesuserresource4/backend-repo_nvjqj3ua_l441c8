"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date

# Example schemas (you can keep or remove if not needed):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# --------------------------------------------------
# Coinflow app schemas
# --------------------------------------------------

class Expense(BaseModel):
    """Expenses collection schema
    Collection: "expense"
    """
    amount: float = Field(..., gt=0, description="Amount spent")
    currency: str = Field("USD", min_length=3, max_length=3, description="ISO currency code")
    date: Optional[date] = Field(None, description="Date of expense")
    merchant: Optional[str] = Field(None, description="Merchant or payee name")
    note: Optional[str] = Field(None, description="Optional note")
    category: Optional[str] = Field(None, description="Auto-assigned or user-selected category")
    account: Optional[str] = Field(None, description="Account name or source")
    type: Literal["debit", "credit"] = Field("debit", description="Expense type")

class Budget(BaseModel):
    """Budgets collection schema
    Collection: "budget"
    """
    category: str = Field(..., description="Budget category")
    amount: float = Field(..., gt=0, description="Monthly budget amount")
    month: Optional[str] = Field(None, description="YYYY-MM for budget period. Defaults to current month.")

class Goal(BaseModel):
    """Financial goals collection schema
    Collection: "goal"
    """
    name: str = Field(..., description="Goal name")
    target_amount: float = Field(..., gt=0, description="Target savings amount")
    current_amount: float = Field(0, ge=0, description="Current saved amount")
    deadline: Optional[date] = Field(None, description="Deadline for the goal")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
