from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..models.order import Order, OrderItem, OrderStatus, PaymentMethod, PaymentStatus
from ..models.product import StoreProduct, Product
from ..models.user import User, UserAddress
from ..models.store import Store
from ..schemas.schemas import OrderCreate, OrderOut, OrderStatusUpdate
from .auth import get_current_user

router = APIRouter(prefix="/api/orders", tags=["Orders"])

# Payment methods allowed per region
INDIA_METHODS = {"cod", "upi", "card"}
INTERNATIONAL_METHODS = {"card", "razorpay", "paypal"}


def format_address(addr) -> str:
    """Convert structured address fields to a readable string."""
    parts = [
        addr.full_name,
        addr.flat_building,
        addr.area_street,
    ]
    if addr.landmark:
        parts.append(f"Landmark: {addr.landmark}")
    parts.append(f"{addr.city}, {addr.state} - {addr.pincode}")
    parts.append(f"Mobile: {addr.mobile}")
    return "\n".join(parts)


@router.post("/", response_model=OrderOut, status_code=201)
def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate payment method based on user country
    is_india = current_user.country.lower() == "india"
    allowed = INDIA_METHODS if is_india else INTERNATIONAL_METHODS
    if data.payment_method not in allowed:
        region_label = "India" if is_india else "International"
        raise HTTPException(
            status_code=400,
            detail=f"Payment method '{data.payment_method}' not available for {region_label} customers. Allowed: {', '.join(allowed)}",
        )

    # Resolve Delivery Address
    if data.address_id:
        addr = db.query(UserAddress).filter(UserAddress.id == data.address_id, UserAddress.user_id == current_user.id).first()
        if not addr:
            raise HTTPException(status_code=404, detail="Saved address not found")
        delivery_state = addr.state
        delivery_address_str = format_address(addr)
    elif data.delivery_address:
        delivery_state = data.delivery_address.state
        delivery_address_str = format_address(data.delivery_address)
    else:
        raise HTTPException(status_code=400, detail="Must provide either address_id or delivery_address")

    # Fetch store for GST calculation state comparison
    store_model = db.query(Store).filter(Store.id == data.store_id).first()
    if not store_model:
        raise HTTPException(status_code=404, detail="Store not found")
    store_state = store_model.region

    # Calculate subtotal and GST from items
    if len(data.items) > 50:
        raise HTTPException(status_code=400, detail="Cannot order more than 50 distinct items at once")
    
    subtotal = 0.0
    gst_total = 0.0
    order_items = []
    for item in data.items:
        if item.quantity <= 0 or item.quantity > 100:
            raise HTTPException(status_code=400, detail=f"Invalid quantity {item.quantity}. Must be between 1 and 100")
            
        sp = db.query(StoreProduct).filter(StoreProduct.id == item.store_product_id).first()
        if not sp:
            raise HTTPException(status_code=404, detail=f"StoreProduct {item.store_product_id} not found")
        if not sp.in_stock:
            raise HTTPException(status_code=400, detail=f"Product is out of stock")
        if sp.store_id != data.store_id:
            raise HTTPException(status_code=400, detail="All items must belong to the same store")

        line_total = sp.price * item.quantity
        gst_rate = sp.product.gst_rate if sp.product.gst_rate else 12.0
        line_gst = line_total * (gst_rate / 100)

        subtotal += line_total
        gst_total += line_gst

        order_items.append(OrderItem(
            store_product_id=sp.id,
            quantity=item.quantity,
            unit_price=sp.price,
        ))

    # Apply 10% bulk discount if subtotal > 1500
    discount_amount = 0.0
    if subtotal > 1500.0:
        discount_amount = subtotal * 0.10
        # GST is usually calculated on the discounted price
        
    # Recalculate GST on the discounted amounts
    discounted_subtotal = subtotal - discount_amount
    gst_total = 0.0
    for item in data.items:
         sp = db.query(StoreProduct).filter(StoreProduct.id == item.store_product_id).first()
         line_total = sp.price * item.quantity
         
         # Prorate the discount across items for accurate GST calculation
         prorated_discount = discount_amount * (line_total / subtotal) if subtotal > 0 else 0
         discounted_line_total = line_total - prorated_discount
         
         gst_rate = sp.product.gst_rate if sp.product.gst_rate else 12.0
         gst_total += discounted_line_total * (gst_rate / 100)

    total_amount = discounted_subtotal + gst_total

    # Calculate GST splits based on inter vs intra state
    ds = delivery_state.lower().strip()
    ss = store_state.lower().strip()
    if ds == ss:
        cgst_amount = round(gst_total / 2, 2)
        sgst_amount = round(gst_total / 2, 2)
        igst_amount = 0.0
    else:
        cgst_amount = 0.0
        sgst_amount = 0.0
        igst_amount = round(gst_total, 2)

    # For COD, payment is pending until delivery; for others, simulate "completed"
    payment_status = PaymentStatus.pending if data.payment_method == "cod" else PaymentStatus.completed

    order = Order(
        user_id=current_user.id,
        store_id=data.store_id,
        subtotal=round(subtotal, 2),
        discount_amount=round(discount_amount, 2),
        gst_amount=round(gst_total, 2),
        cgst_amount=cgst_amount,
        sgst_amount=sgst_amount,
        igst_amount=igst_amount,
        total_amount=round(total_amount, 2),
        delivery_address=delivery_address_str,
        is_gift=data.is_gift,
        gift_message=data.gift_message,
        payment_method=PaymentMethod(data.payment_method),
        payment_status=payment_status,
        items=order_items,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/", response_model=List[OrderOut])
def list_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    orders = (
        db.query(Order)
        .options(
            joinedload(Order.items)
            .joinedload(OrderItem.store_product)
            .joinedload(StoreProduct.product)
        )
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    # Enrich items with product name/image
    for order in orders:
        for item in order.items:
            if item.store_product and item.store_product.product:
                item.product_name = item.store_product.product.name
                item.product_image = item.store_product.product.image_url
    return orders


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = (
        db.query(Order)
        .options(
            joinedload(Order.items)
            .joinedload(OrderItem.store_product)
            .joinedload(StoreProduct.product)
        )
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    for item in order.items:
        if item.store_product and item.store_product.product:
            item.product_name = item.store_product.product.name
            item.product_image = item.store_product.product.image_url
    return order


@router.patch("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in (OrderStatus.pending, OrderStatus.confirmed):
        raise HTTPException(status_code=400, detail=f"Cannot cancel an order with status '{order.status.value}'")
    order.status = OrderStatus.cancelled
    if order.payment_status == PaymentStatus.completed:
        order.payment_status = PaymentStatus.refunded
    db.commit()
    return {"message": "Order cancelled successfully", "order_id": order_id}


# ─── Admin Endpoints ───

@router.get("/admin/all", response_model=List[OrderOut])
def admin_list_all_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role.value != "store_owner":
        raise HTTPException(status_code=403, detail="Admin access required")
    orders = (
        db.query(Order)
        .options(
            joinedload(Order.items)
            .joinedload(OrderItem.store_product)
            .joinedload(StoreProduct.product)
        )
        .order_by(Order.created_at.desc())
        .all()
    )
    for order in orders:
        for item in order.items:
            if item.store_product and item.store_product.product:
                item.product_name = item.store_product.product.name
                item.product_image = item.store_product.product.image_url
    return orders


@router.patch("/admin/{order_id}/status")
def admin_update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role.value != "store_owner":
        raise HTTPException(status_code=403, detail="Admin access required")
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    try:
        order.status = OrderStatus(data.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status '{data.status}'. Valid values: {[s.value for s in OrderStatus]}")
    db.commit()
    return {"message": f"Order #{order_id} status updated to '{data.status}'"}
