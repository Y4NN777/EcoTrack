# EcoTrack - Waste Management System Documentation

## Team Members and Contributions

**Development Team**: Triple A (Axel, Ali, Aslane)

### 1. DABO R Yanis Axel
**Role**: Full Stack Developer  
**Contributions**:
- Designed and implemented database models and relationships
- Developed the authentication system with secure password hashing
- Integrated admin functionality for system and user management
- Implemented robust data validation to ensure data integrity

### 2. OUEDRAOGO Yanis Aslane & DABO R Yanis Axel
**Roles**: UI/UX Designer & Frontend Developer (Aslane) and Full Stack Developer (Axel)  
**Contributions**:
- Crafted user-friendly interface designs
- Developed responsive templates
- Integrated client-side validation for enhanced user experience
- Implemented the user dashboard for streamlined navigation

### 3. GUISSOU Ali & DABO R Yanis Axel
**Roles**: Backend Developer (Ali) and Full Stack Developer (Axel)  
**Contributions**:
- Seamlessly integrated frontend and backend components
- Developed a comprehensive reporting system
- Created data visualization features for insightful analysis
- Managed waste collection functionality
- Authored technical documentation

**Project Supervision**  
**Instructor**: Mr. Porgo  
**Course**: Python Programming II

## Software Overview

### Purpose
EcoTrack is a web-based waste management system designed to streamline and enhance the management of waste collection activities. The platform enables organizations to monitor waste collection processes, schedule pickups, and generate basic performance reports, thereby promoting efficient resource utilization.

### Features

#### 1. User Management
- Three-tier role system:
  - Administrator: System management and user control
  - Operator: Collection and schedule handling
  - Reporter: View and export basic reports
- Secure authentication with password hashing
- User profile management

#### 2. Waste Collection Management
- Record waste collections with:
  - Waste type
  - Quantity
  - Collection date
  - Location
  - Status tracking
- View and edit collection records
- Basic filtering and sorting

#### 3. Schedule Management
- Create collection schedules
- Assign teams to routes
- Track schedule status
- View upcoming collections

#### 4. Basic Reporting
- Collection statistics dashboard
- Waste type distribution
- Export collection data
- Basic performance metrics

## Technical Implementation

### Technology Stack
- **Backend**: Python 3.12 with Flask
- **Database**: SQLite via SQLAlchemy
- **Frontend**:
  - HTML5, CSS, Bootstrap 5
  - JavaScript
  - Chart.js for basic graphs
  - SweetAlert2 for notifications

### Project Structure
```
wms/
├── app.py                    # Application configuration and initialization
├── routes.py                 # Main route handlers
├── models.py                 # Database models
├── requirements.txt          # Project dependencies
│
├── blueprints/              # Feature modules
│   ├── admin.py             # Admin functionality
│   ├── auth.py              # Authentication
│   ├── operator.py          # Collection operations
│   └── reporting.py         # Basic reporting
│
├── static/                  # Static assets
│   ├── css/
│   │   └── styles.css      # Custom styling
│   └── js/
│       └── main.js         # Core JavaScript
│
├── templates/               # HTML templates
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   └── waste_types.html
│   ├── operator/
│   │   ├── collections.html
│   │   └── schedules.html
│   ├── reporting/
│   │   ├── dashboard.html
│   │   └── reports.html
│   └── auth/
│       ├── login.html
│       └── register.html
│
├── instance/
│   └── wms.db              # SQLite database with initial data
│
└── reports/                # Directory for CSV report files
```

### Database Models

#### User
- Username and password
- Email and personal info
- Role-based access
- Account status

#### WasteType
- Name and description
- Disposal method
- Created timestamp

#### Collection
- Waste type reference
- Quantity collected
- Collection date
- Location
- Status tracking

#### Schedule
- Route information
- Pickup date
- Team assignment
- Status tracking

#### Report
- Report type
- Time period
- Format (CSV)
- Generation timestamp

## Setup Guide

### Prerequisites
- Python 3.12
- pip package manager
- Web browser (Chrome/Firefox recommended)

### Installation Steps

1. **Setup Python Environment**
```bash
python -m venv venv   # Create a virtual environment
venv\Scripts\activate  # Activate the virtual environment
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt   # Install the software dependencies
```

3. **Initialize Database**
```bash
flask db upgrade
```

**Note**: Database comes pre-configured with:
- Admin user credentials
- Operator user credentials
- Reporting user credentials
- Initial waste types
- Sample collections and schedules

4. **Run Application**
```bash
flask run  # or python app.py
```

## Security Features
- Password hashing
- Role-based access control
- Form validation
- CSRF protection
- Session management

## Technical Excellence

### Complexity
- **Multi-Role Functionality**: Three distinct user roles with specific privileges
- **Integrated Modules**: Seamless combination of user management, tracking, and reporting
- **Real-Time Updates**: Dynamic data presentation using JavaScript and Flask
- **Data Security**: Comprehensive validation and protection measures

### Demonstrated Skills
- **Frontend Development**: Responsive interfaces with modern frameworks
- **Backend Development**: Robust database and server logic
- **Data Visualization**: Intuitive data representation with Chart.js
- **Team Collaboration**: Effective task division and communication
- **Problem-Solving**: Addressing technical challenges and optimization

## Support

For technical assistance, contact the project lead developer:

**DABO R Yanis Axel**
- Email: axel.studiesmail@gmail.com
- WhatsApp: +226 67 26 08 83

## License

This project was developed as an educational assignment for the Python Programming II course at the Burkina Institute of Technology (BIT). Authors have no affiliation with any organization but are grateful for the opportunity to learn and contribute to this project.

The source code and documentation are free to use, modify, and distribute for both commercial and non-commercial purposes.
