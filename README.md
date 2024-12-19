# LabelBox Web Application

LabelBox is a web-based image annotation tool that allows users to create projects, upload images, and add bounding box annotations. Built with Flask and modern frontend technologies, it provides an intuitive interface for managing and annotating image datasets.

## Features

- **Project Management**
  - Create and organize multiple annotation projects
  - View project details and progress
  - Track image count per project

- **Image Handling**
  - Upload images to specific projects
  - Support for various image formats
  - View original and annotated versions
  - Responsive image grid display

- **Annotation Tools**
  - Draw bounding boxes on images
  - Save annotations with coordinates
  - View and edit existing annotations
  - Real-time annotation preview

- **User Interface**
  - Modern, responsive design
  - Intuitive navigation
  - Progress tracking
  - Flash messages for user feedback

## Technology Stack

- **Backend**
  - Flask (Python web framework)
  - SQLAlchemy (ORM)
  - Flask-Migrate (Database migrations)
  - Werkzeug (File handling)

- **Frontend**
  - HTML5 Canvas for annotations
  - Tailwind CSS for styling
  - Vanilla JavaScript
  - Jinja2 templating

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Akachi-Anabanti/Labelbox.git
cd labelbox
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Create upload directory:
```bash
mkdir static/uploads
```

## Configuration

Create a `.env` file in the project root:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
UPLOAD_FOLDER=static/uploads
```

## Database Models

### Project
```python
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    images = db.relationship('Image', backref='project', lazy=True)
```

### Image
```python
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    annotated_filename = db.Column(db.String(255))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    annotated = db.Column(db.Boolean, default=False)
```

### Annotation
```python
class Annotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    width = db.Column(db.Float)
    height = db.Column(db.Float)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
```

## Running the Application

1. Start the Flask development server:
```bash
flask run
```

2. Access the application at `http://localhost:5000`

## Usage

1. **Creating a Project**
   - Click "New Project" on the home page
   - Enter project name and description
   - Submit the form

2. **Uploading Images**
   - Navigate to a project
   - Use the upload form at the bottom
   - Select image files to upload

3. **Annotating Images**
   - Click on an image in the project view
   - Draw bounding boxes by clicking and dragging
   - Annotations are saved automatically

## TODOs
0. **User Account**
   - Implement user authentication, authorization and session

2. **Delete Functionality**
   - Implement project deletion with cascade
   - Add image deletion capability
   - Add confirmation dialogs for deletions

3. **Pagination**
   - Fix pagination for project images
   - Add proper page size limits
   - Implement page navigation

4. **Future Enhancements**
   - Add user authentication
   - Implement annotation categories
   - Add export functionality
   - Enable batch image upload
   - Add annotation statistics

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask documentation and community
- Tailwind CSS for the UI framework
- All contributors and users of the application

