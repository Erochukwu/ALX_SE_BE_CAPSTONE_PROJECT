## Users API (Vendors & Customers)

### Overview
This API provides registration, authentication, and CRUD operations for vendor and customer profiles.

### Authentication
- Uses **DRF Token Authentication**
- Obtain a token on signup or login
- Include token in headers:

## 🧱 Vendors & Sheds API

### Overview
The Vendors module allows vendors to manage their allocated sheds, while admins can view and manage all.

### Authentication
All endpoints require authentication (Token or Session-based).

### Endpoints

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/api/vendors/sheds/` | GET | List all sheds (admin) or own (vendor). |
| `/api/vendors/sheds/?domain=FB` | GET | Filter sheds by domain. |
| `/api/vendors/sheds/?vendor=3` | GET | Filter sheds by vendor ID. |
| `/api/vendors/sheds/` | POST | Create a new shed (vendor only). |
| `/api/vendors/sheds/<id>/` | GET | Retrieve shed details. |
| `/api/vendors/sheds/<id>/` | PUT/PATCH | Update shed info (vendor or admin). |
| `/api/vendors/sheds/<id>/` | DELETE | Delete a shed (admin or owner). |
| `/api/vendors/sheds/available/` | GET | Shows available shed slots per domain. |

### Example Response (Available Sheds)
```json
{
  "Clothing and Bedding": {"total": 100, "used": 24, "available": 76},
  "Food and Beverages": {"total": 100, "used": 18, "available": 82},
  "Jewelries and Accessories": {"total": 100, "used": 5, "available": 95},
  "Electronics and Computer Wares": {"total": 100, "used": 12, "available": 88}
}

## 🛍️ Products API

### Overview
The Products API allows vendors to manage the products they sell at their assigned sheds.

### Authentication
- Vendors must be logged in (Token Auth).
- Guests/customers can browse products without login.

### Endpoints

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/api/products/products/` | GET | List all products. |
| `/api/products/products/<id>/` | GET | Retrieve details for a product. |
| `/api/products/products/` | POST | Create new product (vendor only). |
| `/api/products/products/<id>/` | PUT/PATCH | Update product (vendor only). |
| `/api/products/products/<id>/` | DELETE | Delete product (vendor only). |

### Fields
| Field | Type | Description |
|--------|------|-------------|
| shed | FK | The vendor’s shed ID. |
| name | String | Product name. |
| description | Text | Short description. |
| price | Decimal | Product price. |
| image | File | Optional product image. |

### Example Response
```json
{
  "id": 4,
  "shed": 1,
  "shed_name": "Ero Snacks Corner",
  "vendor_name": "Ero Ventures",
  "name": "Wireless Headphones",
  "description": "Noise-cancelling headphones with Bluetooth connectivity.",
  "price": "14500.00",
  "image": "/media/product_images/headphones.jpg",
  "created_at": "2025-10-05T12:10:32Z",
  "updated_at": "2025-10-05T12:10:32Z"
}
