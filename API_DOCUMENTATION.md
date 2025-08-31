# Relief Application API Documentation

## Base URL
```
http://127.0.0.1:8000/api/
```

## Authentication
- Most supervisor endpoints require authentication
- Use Django's session authentication or token authentication
- Login at `/api/auth/login/`

## Application APIs

### Submit Application (Anonymous)
```http
POST /api/applications/submit/
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "08012345678",
    "email": "john@example.com",
    "address": "123 Main Street, Lagos",
    "family_size": "4",
    "children_count": "2",
    "elderly_count": "0",
    "employment_status": "unemployed",
    "special_needs": "",
    "situation_description": "Lost job due to economic situation",
    "selected_package": "medium_basic",
    "package_flexibility": true,
    "preferred_date": "2024-01-15",
    "preferred_time": "morning",
    "alternative_date": "2024-01-16",
    "alternative_time": "afternoon",
    "transportation_help": false,
    "delivery_request": false,
    "terms_agreement": true
}
```

**Response:**
```json
{
    "success": true,
    "message": "Application submitted successfully!",
    "reference_number": "GCR24011234",
    "data": {
        "id": "uuid-here",
        "reference_number": "GCR24011234",
        "full_name": "John Doe",
        "phone": "08012345678",
        "selected_package": "medium_basic",
        "status": "PENDING"
    }
}
```

### List Applications (Supervisor)
```http
GET /api/applications/list/
GET /api/applications/list/?status=PENDING
```

### Get Application Details (Supervisor)
```http
GET /api/applications/{application_id}/
```

### Approve Application (Supervisor)
```http
POST /api/applications/{application_id}/approve/
Content-Type: application/json

{
    "notes": "Approved for immediate pickup"
}
```

### Reject Application (Supervisor)
```http
POST /api/applications/{application_id}/reject/
Content-Type: application/json

{
    "notes": "Incomplete documentation"
}
```

## Package APIs

### List Available Packages (Public)
```http
GET /api/packages/available/
```

**Response:**
```json
[
    {
        "package_type": "small_basic",
        "name": "Small Family Basic",
        "description": "Basic relief package for small families (1-3 people)",
        "cash_amount": "5000.00",
        "is_available": true
    }
]
```

### Manage Packages (Supervisor)
```http
GET /api/packages/manage/
POST /api/packages/manage/
GET /api/packages/manage/{package_id}/
PUT /api/packages/manage/{package_id}/
DELETE /api/packages/manage/{package_id}/
```

### Restock Package (Supervisor)
```http
POST /api/packages/{package_id}/restock/
Content-Type: application/json

{
    "quantity": 25
}
```

## Pickup/QR Code APIs

### List Pickups (Supervisor)
```http
GET /api/pickups/list/
GET /api/pickups/list/?status=SCHEDULED
GET /api/pickups/list/?date=2024-01-15
```

### Verify QR Code (Supervisor)
```http
POST /api/pickups/verify-qr/
Content-Type: application/json

{
    "pickup_code": "GCRABCD123456789"
}
```

**Response:**
```json
{
    "success": true,
    "pickup": {
        "id": 1,
        "pickup_code": "GCRABCD123456789",
        "applicant_name": "John Doe",
        "phone": "08012345678",
        "selected_package": "medium_basic",
        "scheduled_date": "2024-01-15",
        "scheduled_time": "morning",
        "status": "SCHEDULED"
    }
}
```

### Complete Pickup (Supervisor)
```http
POST /api/pickups/{pickup_id}/complete/
Content-Type: application/json

{
    "notes": "Package collected successfully"
}
```

### Check Pickup Status (Public)
```http
GET /api/pickups/status/{pickup_code}/
```

## Error Responses

All APIs return consistent error responses:

```json
{
    "success": false,
    "message": "Error description",
    "errors": {
        "field_name": ["Field-specific error messages"]
    }
}
```

## Status Codes

- `200` - Success
- `201` - Created successfully
- `400` - Bad request/validation errors
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not found
- `500` - Server error

## Setup Commands

1. Run migrations: `python manage.py migrate`
2. Create superuser: `python manage.py createsuperuser`
3. Create sample packages: `python manage.py create_sample_packages`
4. Start server: `python manage.py runserver`

## Testing the API

You can test the APIs using:
- Django admin at `/admin/`
- REST framework browsable API at `/api/applications/submit/`
- Tools like Postman, curl, or browser fetch requests