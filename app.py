from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Student, Module, Enrolment


app = Flask(__name__)
app.config["SECRET_KEY"] = "devkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ---------------- UTILS ----------------
def init_modules():
    if Module.query.count() == 0:
        demo = [
            ("CS101", "Introduction to Programming"),
            ("CS102", "Web Development"),
            ("CS201", "Software Testing"),
            ("CS202", "Databases"),
            ("CS301", "Networks"),
            ("CS302", "Operating Systems"),
            ("CS303", "Machine Learning"),
        ]
        for code, title in demo:
            db.session.add(Module(code=code, title=title))
        db.session.commit()

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    students = Student.query.all()
    return render_template("index.html", students=students)

@app.route("/student/<int:student_id>")
def student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    modules = Module.query.all()
    return render_template("student_detail.html", student=student, modules=modules)

@app.route("/register", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        sid = request.form["student_id"].strip()

        if not name or not email or not sid:
            flash("All fields are required.", "danger")
            return redirect(url_for("register_student"))

        if "@" not in email:
            flash("Invalid email format.", "danger")
            return redirect(url_for("register_student"))

        if Student.query.filter_by(student_id=sid).first():
            flash("Student ID already exists.", "danger")
            return redirect(url_for("register_student"))

        student = Student(name=name, email=email, student_id=sid)
        db.session.add(student)
        db.session.commit()

        flash("Student registered successfully.", "success")
        return redirect(url_for("index"))

    return render_template("register_student.html")

@app.route("/enrol/<int:student_id>", methods=["GET", "POST"])
@app.route("/enrol/<int:student_id>", methods=["GET", "POST"])
def enrol(student_id):
    student = Student.query.get_or_404(student_id)
    modules = Module.query.all()

    if request.method == "POST":
        module_id = int(request.form["module_id"])
        module = Module.query.get_or_404(module_id)

        # Get current enrolments for this student
        current_enrolments = Enrolment.query.filter_by(student_id=student.id).all()

        # Enrolment limit
        if len(current_enrolments) >= 6:
            flash("Enrolment limit reached (max 6 modules).", "danger")
            return redirect(url_for("student_detail", student_id=student.id))

        # Prevent duplicate enrolment
        for e in current_enrolments:
            if e.module_id == module.id:
                flash("Student already enrolled in this module.", "warning")
                return redirect(url_for("student_detail", student_id=student.id))

        # Create enrolment
        enrolment = Enrolment(student_id=student.id, module_id=module.id)
        db.session.add(enrolment)
        db.session.commit()

        flash(f"Enrolled in {module.code} - {module.title}.", "success")
        return redirect(url_for("student_detail", student_id=student.id))

    return render_template("enrol.html", student=student, modules=modules)

# ---------------- APP STARTUP ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        init_modules()
    app.run(debug=True)
