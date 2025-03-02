# EcoTrack - Waste Management System Documentation

## Team Members and Contributions

### Development Team : Triple A (Axel, Ali, Aslane)

1. **DABO R Yanis Axel**
   - Role: Full stack developer
   - Contributions:
     - Database models and relationships
     - Authentication system
     - Admin functionality
     - Data validation

2. **OUEDRAOGO Yanis Aslane & DABO R Yanis Axel**
   - Role: UI/UX Designer & Frontend Developer (Aslane) & Full stack developer (Yanis Axel)
   - Contributions:
     - User interface design
     - Template development
     - Client-side validation
     - Dashboard implementation

3. **GUISSOU Ali & DABO R Yanis Axel**
   - Role: Backend Developer (Ali) & Full Stack Developer (Yanis Axel) 
   - Contributions:
     - Full stack integration
     - Reporting system
     - Data visualization
     - Collection management
     - Documentation

### Project Supervision
- **Mr Porgo**
  - Course: Python Programming II
  - Instructor: Mr Porgo

## Software Overview

### Purpose
EcoTrack is a web-based waste management system developed for tracking and managing waste collections. It enables organizations to monitor waste collection activities, schedule pickups, and generate basic reports.

### Actual Features

#### 1. User Management
- Three-tier role system:
  - Administrator: System management and user control
  - Operator: Collection and schedule handling
  - Reporting: View and export basic reports
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
```plaintext
wms/
├── app.py                 # Application configuration and initialization
├── routes.py             # Main route handlers
├── models.py             # Database models
├── requirements.txt      # Project dependencies
│
├── blueprints/           # Feature modules
│   ├── admin.py         # Admin functionality
│   ├── auth.py          # Authentication
│   ├── operator.py      # Collection operations
│   └── reporting.py     # Basic reporting
│
├── static/              # Static assets
│   ├── css/
│   │   └── styles.css  # Custom styling
│   └── js/
│       └── main.js     # Core JavaScript
│
├── templates/           # HTML templates
│   ├── admin/          # Admin interface
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   └── waste_types.html
│   ├── operator/       # Operator interface
│   │   ├── collections.html
│   │   └── schedules.html
│   ├── reporting/      # Reporting interface
│   │   ├── dashboard.html
│   │   └── reports.html
│   └── auth/           # Authentication
│       ├── login.html
│       └── register.html
│
└── instance/           # Instance data
    ├── wms.db         # SQLite database with initial data
    └── reports/       # Directory for CSV report files
```

## Database Models

### User
- Username and password
- Email and personal info
- Role-based access
- Account status

### WasteType
- Name and description
- Disposal method
- Created timestamp

### Collection
- Waste type reference
- Quantity collected
- Collection date
- Location
- Status tracking

### Schedule
- Route information
- Pickup date
- Team assignment
- Status tracking

### Report
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
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Database**
   ```bash
   flask db upgrade
   ```
   Note:This step is optional because the database will be initialized with pre-configured data including:
   - Admin user credentials
   - Operator user credentials
   - Reporting user credentials
   - Initial waste types
   - Sample collections and schedules
   
   All credentials will be provided for testing all roles.

4. **Run Application**
   ```bash
   flask run or python app.py
   ```

## Usage Guide

### Administrator Functions
1. **User Management**
   - Create/edit user accounts
   - Assign roles
   - Manage access

2. **Waste Type Configuration**
   - Define waste categories
   - Set disposal methods
   - Update descriptions

### Operator Functions
1. **Collection Management**
   - Log new collections
   - Update collection status
   - View collection history

2. **Schedule Management**
   - Create collection schedules
   - Assign teams
   - Track completion

### Reporting Functions
1. **View Statistics**
   - Collection totals
   - Waste type distribution
   - Schedule status

2. **Generate Reports**
   - Export collection data
   - View basic metrics
   - Download CSV files

## Security Features
- Password hashing
- Role-based access control
- Form validation
- CSRF protection
- Session management

## Known Limitations
1. Basic reporting capabilities only
2. No advanced analytics
3. Limited data visualization
4. Single database support
5. No API endpoints

## Technical Notes and Known Issues

### JavaScript Chart Implementation
- The charts in reporting templates use inline JavaScript within script tags
- This approach was chosen for direct integration with Flask template variables
- While this generates syntax warnings in IDE/editors, it does not affect functionality
- Example implementation:
  ```html
  <script>
    // Warning appears here but functionality works
    const data = {{ chart_data|tojson|safe }};
    // Chart initialization code
  </script>
  ```
- Alternative approaches were considered but this method proved most effective for:
  - Direct access to Flask template variables
  - Real-time data updates
  - Simplified maintenance

### Browser Console Warnings
- JavaScript console may show template syntax warnings
- These are related to Jinja2 template variables in JavaScript context
- The warnings do not impact system functionality or data visualization
- Charts render and update correctly despite warnings

### Best Practices Note
While the current implementation generates warnings, it was chosen as a practical compromise between:
- Functionality requirements
- Development timeline
- Maintenance simplicity
- Real-time data integration

Future improvements could include:
- External JavaScript files with API data fetching
- Modular chart components
- Advanced error handling

## Support
For technical assistance and trouble-shooting due to any issues, please contact the project lead developer:
- **DABO R Yanis Axel**
- Email: `axel.studiesmail@gmail.com`
- Whatsapp: `+226 67 26 08 83`

## License
This project was developed as an educational assignment for Python Programming II course at the Burkina Institute of Technology (BIT). While authors have no affiliation with any organization, they are grateful for the opportunity to learn and contribute to this project.
They are free to use and modify the source code and documentation in addition to continue the development and distribute this software with free will for commercial or non-commercial purposes.
