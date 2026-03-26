from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import List, Optional
from ..database import get_db
from ..models.order import Order, OrderItem, OrderStatus, PaymentStatus
from ..models.product import StoreProduct, Product
from ..models.user import User, UserRole
from ..models.store import Store
from ..schemas.schemas import OrderStatusUpdate
from .auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def _require_admin(current_user: User):
    if current_user.role.value not in ("store_owner", "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/dashboard")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)

    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.payment_status == PaymentStatus.completed
    ).scalar() or 0.0

    total_orders = db.query(func.count(Order.id)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_products = db.query(func.count(Product.id)).scalar() or 0

    # Orders breakdown by status
    status_counts = dict(
        db.query(Order.status, func.count(Order.id))
        .group_by(Order.status)
        .all()
    )
    orders_by_status = {s.value: status_counts.get(s, 0) for s in OrderStatus}

    # Revenue by store (top 5)
    revenue_by_store = (
        db.query(Store.name, func.sum(Order.total_amount).label("revenue"))
        .join(Order, Order.store_id == Store.id)
        .filter(Order.payment_status == PaymentStatus.completed)
        .group_by(Store.name)
        .order_by(desc("revenue"))
        .limit(5)
        .all()
    )

    # Recent 7 orders
    recent_orders = (
        db.query(Order)
        .options(joinedload(Order.items), joinedload(Order.user), joinedload(Order.store))
        .order_by(Order.created_at.desc())
        .limit(7)
        .all()
    )

    return {
        "kpis": {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "total_users": total_users,
            "total_products": total_products,
        },
        "orders_by_status": orders_by_status,
        "revenue_by_store": [{"store": r[0], "revenue": round(r[1] or 0, 2)} for r in revenue_by_store],
        "recent_orders": [
            {
                "id": o.id,
                "user": o.user.name if o.user else "Unknown",
                "store": o.store.name if o.store else "Unknown",
                "total": o.total_amount,
                "status": o.status.value,
                "payment_status": o.payment_status.value,
                "created_at": o.created_at.isoformat(),
            }
            for o in recent_orders
        ],
    }


@router.get("/orders")
def get_all_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    orders = (
        db.query(Order)
        .options(
            joinedload(Order.items).joinedload(OrderItem.store_product).joinedload(StoreProduct.product),
            joinedload(Order.user),
            joinedload(Order.store),
        )
        .order_by(Order.created_at.desc())
        .all()
    )
    result = []
    for o in orders:
        items = [
            {
                "product_name": (i.store_product.product.name if i.store_product and i.store_product.product else f"Product #{i.store_product_id}"),
                "quantity": i.quantity,
                "unit_price": i.unit_price,
            }
            for i in o.items
        ]
        result.append({
            "id": o.id,
            "user": o.user.name if o.user else "Unknown",
            "user_email": o.user.email if o.user else "",
            "store": o.store.name if o.store else "Unknown",
            "items": items,
            "subtotal": o.subtotal,
            "discount_amount": o.discount_amount,
            "gst_amount": o.gst_amount,
            "total_amount": o.total_amount,
            "status": o.status.value,
            "payment_method": o.payment_method.value,
            "payment_status": o.payment_status.value,
            "created_at": o.created_at.isoformat(),
        })
    return result


@router.patch("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    body: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    try:
        order.status = OrderStatus(body.status)
    except ValueError:
        valid = [s.value for s in OrderStatus]
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid values: {valid}")
    db.commit()
    return {"message": f"Order #{order_id} updated to '{body.status}'"}

@router.get("/users")
def get_all_users(
    role: Optional[str] = Query(None, description="Filter by role: customer, store_owner, admin"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    query = db.query(User)
    if role:
        try:
            query = query.filter(User.role == UserRole(role))
        except ValueError:
            pass
    users = query.order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        order_count = db.query(func.count(Order.id)).filter(Order.user_id == u.id).scalar() or 0
        total_spend = db.query(func.sum(Order.total_amount)).filter(
            Order.user_id == u.id,
            Order.payment_status == PaymentStatus.completed
        ).scalar() or 0.0
        result.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "phone": u.phone,
            "country": u.country,
            "role": u.role.value,
            "order_count": order_count,
            "total_spend": round(total_spend, 2),
            "created_at": u.created_at.isoformat(),
        })
    return result


@router.get("/products")
def get_product_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    # Top products by revenue
    top_products = (
        db.query(
            Product.name,
            Product.image_url,
            Product.category,
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(OrderItem.unit_price * OrderItem.quantity).label("total_revenue"),
        )
        .join(StoreProduct, StoreProduct.product_id == Product.id)
        .join(OrderItem, OrderItem.store_product_id == StoreProduct.id)
        .group_by(Product.id)
        .order_by(desc("total_revenue"))
        .limit(20)
        .all()
    )
    return [
        {
            "name": r[0],
            "image_url": r[1],
            "category": r[2],
            "total_qty": r[3] or 0,
            "total_revenue": round(r[4] or 0, 2),
        }
        for r in top_products
    ]
