# Seabasket - FastAPI E-Commerce Backend

Seabasket is a professional e-commerce REST API built using the Python FastAPI framework. It includes advanced features such as JWT authentication, role-based access control, integrated Stripe payments, and internationalization support.

---
## Prerequisites

* **Python**: ^3.9
* **Database**: MySQL, Liquibase
* **Dependency Management**: Pip or Poetry

---

## Features

* **Secure**:  Authentication: JWT-based login and registration system.

* **Product Management**: Full CRUD operations for categories and products.

* **Shopping Cart**: User-specific cart management and item tracking.

* **Payments**: Seamless integration with the Stripe payment gateway.

* **Localization**: Multi-language support powered by python-i18n.

* **Database Migrations**: Consistent schema updates managed via Liquibase.

* **Auto-generated Docs**: Interactive API documentation via Swagger and ReDoc.

---
## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Harsh9220/Legal-Management-FastAPI.git
cd Legal-Management-FastAPI
```
---
### 2. Create a Virtual Environment
Create a virtual environment to manage your project's dependencies.

**For Windows (PowerShell)**
```bash
python -m venv venv
venv\Scripts\activate
```

**For macOS/Linux**
```bash
python -m venv venv
source venv/bin/activate
```
---
### 3. Install Dependencies

**Using pip**
```bash
pip install -r requirements.txt
```
**Using Poetry**
```bash
poetry install
```
---

### 4. Create Database
```sql
CREATE DATABASE seabasket;
```
---
### 5. Environment Setup
Copy and configure the environment file(.env) in your virtual environment
```bash
cp .env.example .env
```

Update the `.env` file with your specific configuration:
```env
DATABASE_USERNAME=your_database_username
DATABASE_PASSWORD=your_database_password
DATABASE_URL=localhost
DATABASE_PORT=3306
DATABASE_NAME=seabasket
CORS_DOMAIN=your_frontend_domain
STRIPE_KEY=your stripe_key
SMTP_KEY=your SMTP key
...
```
---

### 6. Liquibase Setup
Copy and configure the  liquibase property file.
```bash
cp liquibase/liquibase.properties.example liquibase/liquibase.properties
```

Update `liquibase.properties` with your database credentials:
```properties
driver=com.mysql.cj.jdbc.Driver
url=jdbc:mysql://localhost:3306/legal_management
username=your_username
password=your_password
```

Then run the migrations:
```bash
cd liquibase
liquibase status
liquibase update
```
---
## Running the FastAPI Application

### Start the Application
```bash
uvicorn main:app --reload
```

### Start Application on Specific Port
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation
Once the application is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure
```
Legal-Management-FastAPI/
├── config/             # Database configuration
├── controllers/        # Business logic for each module
│   ├── auth_controller.py
│   ├── case_controller.py
│   ├── client_controller.py
│   ├── document_controller.py
│   ├── invoice_controller.py
│   ├── lawyer_controller.py
│   ├── session_controller.py
│   ├── staff_controller.py
│   └── task_controller.py
├── dtos/              # Data transfer objects
├── helper/            # Helper functions
│   ├── api_helper.py
│   ├── cors_helper.py
│   ├── date_helper.py
│   ├── hashing.py
│   ├── logger_helper.py
│   ├── role_helper.py
│   ├── token_helper.py
│   └── validation_helper.py
├── language/          # Internationalization files
├── liquibase/         # Database migrations
│   ├── changelog/
│   └── liquibase.properties.example
├── models/           # Database models
├── routes/           # API endpoints
├── utils/            # Utility functions
├── .env.example      # Example environment variables
├── .gitignore       # Git ignore rules
├── main.py          # Application entry point
└── requirements.txt  # Project dependencies
```

## Additional Notes
- The `.env` and `liquibase.properties` files are not tracked in git for security
- Use the provided `.env.example` and `liquibase.properties.example` as templates
- The system supports multiple languages through i18n
- Database migrations are handled through Liquibase

## Troubleshooting

If you encounter any issues, try:
1. Checking Python and pip versions:
   ```bash
   python --version
   pip --version
   ```
2. Ensuring dependencies are installed correctly:
   ```bash
   pip list
   ```
3. Verifying database connection:
   ```bash
   mysql -u your_username -p -h localhost
   ```
4. Checking environment variables are set correctly in `.env`
5. Ensuring Liquibase migrations are up to date
6. Verifying the virtual environment is activated

To exit the virtual environment when done, use:
```bash
deactivate
```