## Technologies Used

- **Backend**: Django, Django REST Framework
- **Frontend**: Django Admin Interface
- **Testing**: Django's Test Framework, Selenium, coverage
- **CI/CD**: GitHub Actions
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Hosting**: PythonAnywhere
- **Version Control**: Git, GitHub

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package installer)
- Virtual Environment tool (`venv` or `virtualenv`)
- Git

### Setup Steps

1. **Clone the Repository**

   ```bash
   git clone <repo>
   cd TodoList
   ```

2. **Create and Activate Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Apply Migrations**

   ```bash
   python manage.py migrate
   ```

5. **Create a Superuser**

   ```bash
   python manage.py createsuperuser
   ```

   Follow the prompts to set up your admin credentials.

6. **Collect Static Files**

   ```bash
   python manage.py collectstatic
   ```

7. **Run the Development Server**

   ```bash
   python manage.py runserver
   ```

   Access the application at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Usage

### Running the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) to access the application.

### Accessing the Admin Panel

1. Navigate to the admin panel at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).
2. Log in using the superuser credentials you created during installation.
3. Manage tasks through the admin interface.

## API Documentation

Interactive API documentation is available using Swagger UI.

- [http://127.0.0.1:8000/api/schema/docs
