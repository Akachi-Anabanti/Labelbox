import os
import secrets
from flask import Flask, json, jsonify, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate


app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///annotation.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["ALLOWED_EXTENSIONS"] = ["jpeg", "png", "jpg", "gif"]
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config['SECRET_KEY'] = secrets.token_hex(16)

db = SQLAlchemy(app)
Migrate(app, db)

class Project(db.Model):
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('Image', backref='project', lazy=True)


class Image(db.Model):
    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    annotated_filename = db.Column(db.String(255))
    annotated = db.Column(db.Boolean, default=False)
    annotations = db.relationship('Annotation', backref='image', lazy=True)


class Annotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    width = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
        db.create_all()

def allowed_file(filename):
     return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]



@app.route("/", methods=["GET"])
def index():
    projects = Project.query.all()
    # return render_template("index.html", projects=projects)
        # Convert projects to a serializable format (list of dictionaries)
    projects_json = [{'id': project.id, 'name': project.name, "img_count": len(project.images)} for project in projects]

    return render_template("index.html", projects=projects_json)


@app.route('/project/<int:project_id>/')
def project_details(project_id):
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Show 5 images per page
    project = Project.query.get_or_404(project_id)
    images = Image.query.filter(Image.project_id == project.id).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('project_details.html', project=project, images=images.items, page=page)



# API to get all projects
@app.route('/api/projects')
def get_projects():
    projects = Project.query.all()
    return jsonify([{'_id': project.id, 'name': project.name, 'image_urls': [image.filename for image in project.images]} for project in projects])


@app.route('/project/create', methods=['POST'])
def create_project():
    name = request.form.get('name')
    description = request.form.get('description')
    
    new_project = Project(name=name, description=description)
    db.session.add(new_project)
    db.session.commit()
    return redirect(url_for('project_details', project_id=new_project.id))


@app.route('/image/upload/<int:project_id>', methods=['POST', "PUT"])
def upload_image(project_id):
    if 'file' not in request.files:
        flash("No file part", 'error')
        return redirect(url_for('project_details', project_id=project_id))
    
    file = request.files['file']
    if file.filename == '':
        flash("No selected file", 'error')
        return redirect(url_for('project_details', project_id=project_id)) 
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        new_image = Image(filename=filename, project_id=project_id)
        db.session.add(new_image)
        db.session.commit()
        flash("File uploaded successfully!", "info")
        return redirect(url_for('project_details', project_id=project_id))
    flash("Inavlid file format", "warning")
    return redirect(url_for("project_details",project_id=project_id ))


@app.route("/annotation/<int:image_id>", methods=["GET"])
def image_annotation(image_id):
    image = Image.query.get_or_404(image_id)
    return render_template("annotation.html", image=image)

@app.route('/api/annotations', methods=['POST'])
def save_annotation():
    try:
        # Get the JSON data
        data = json.loads(request.form.get('data'))
        if not data:
            flash('No data provided', 'error')
            return redirect(url_for('image_annotation', image_id=image.id))
        
        project_id = data.get('project_id')
        image_url = data.get('image_url')
        annotations = data.get('annotations')
        
        if not all([project_id, image_url, annotations]):
            flash('Missing required fields', 'error')
            return redirect(url_for('image_annotation', image_id=image.id))
            
        # Extract filename from image_url
        filename = image_url.split('/')[-1]
        
        # Get the image record
        image = Image.query.filter_by(
            filename=filename,
            project_id=project_id
        ).first()
        
        if not image:
            flash('Image not found', 'error')
            return redirect(url_for('index'))
        
        try:
            # Save the annotated image
            if 'annotated_image' in request.files:
                # Delete old annotated image if it exists
                if image.annotated_filename:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], image.annotated_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Save new annotated image
                annotated_file = request.files['annotated_image']
                annotated_filename = f"annotated_{secure_filename(filename)}"
                annotated_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
                annotated_file.save(annotated_path)
                
                # Update database record
                image.annotated_filename = annotated_filename
            
            # Save annotations
            for ann in annotations:
                new_annotation = Annotation(
                    label=ann['label'],
                    x=float(ann['coordinates']['x']),
                    y=float(ann['coordinates']['y']),
                    width=float(ann['coordinates']['width']),
                    height=float(ann['coordinates']['height']),
                    image_id=image.id
                )
                db.session.add(new_annotation)
            
            # Mark image as annotated
            image.annotated = True
            
            # Commit all changes
            db.session.commit()
            
            flash("Successfully saved annotations and updated image!", "message")
            return redirect(url_for('image_annotation', image_id=image.id))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Database error occurred while saving annotations', 'error')
            return redirect(url_for('image_annotation', image_id=image.id))
            
    except Exception as e:
        flash(f'Error occurred: {str(e)}', 'error')
        return redirect(url_for('image_annotation', image_id=image.id))

if __name__  == "__main__":
    app.run(host="localhost", port="5000", debug=True)