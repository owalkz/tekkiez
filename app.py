import datetime
import os
import random

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tekkiez.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    account_type = request.form.get("account-type")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email address", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        if account_type == "caretaker":
            rows = db.execute(
                "SELECT * FROM caretakers WHERE email_address = ?",
                request.form.get("email"),
            )
        elif account_type == "home-owner":
            rows = db.execute(
                "SELECT * FROM homeowners WHERE email_address = ?",
                request.form.get("email"),
            )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password_hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        if account_type == "caretaker":
            session["user_id"] = rows[0]["ct_id"]
        elif account_type == "home-owner":
            session["user_id"] = rows[0]["h_id"]
        session["user_type"] = account_type

        # Redirect user to home page
        if account_type == "caretaker":
            return redirect("/ctdashboard")
        elif account_type == "home-owner":
            return redirect("/hdashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # retrieving usernames from database and responses from the HTML form
        name = request.form.get("name")
        email_address = request.form.get("email")
        account_type = request.form.get("account-type")
        address = request.form.get("address")
        id_number = request.form.get("id-number")
        date_of_birth = request.form.get("dob")
        password = request.form.get("password")
        date_joined = datetime.date.today()
        hired_status = 0
        profile_visibility = 0

        # checking for empty password or mismatch with the confirmation
        if (
            not email_address
            or not address
            or not id_number
            or not date_of_birth
            or not password
        ):
            return apology("All fields must be filled!")

        # generating password hash
        password_hash = generate_password_hash(password)

        # inserting new user into database
        if account_type == "home-owner":
            try:
                db.execute(
                    "INSERT INTO homeowners (h_name, email_address, address, date_of_birth, id_number, password_hash, date_joined) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    name,
                    email_address,
                    address,
                    date_of_birth,
                    id_number,
                    password_hash,
                    date_joined,
                )
            except ValueError:
                return apology("user already exists")
        elif account_type == "caretaker":
            try:
                db.execute(
                    "INSERT INTO caretakers (ct_name, email_address, address, date_of_birth, id_number, password_hash, hired_status, profile_visibility) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    name,
                    email_address,
                    address,
                    date_of_birth,
                    id_number,
                    password_hash,
                    hired_status,
                    profile_visibility,
                )
            except ValueError:
                return apology("user already exists")

        # redirecting to login page
        redirect("/login")

    else:
        return render_template("register.html")

    return redirect("/login")


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


@app.route("/")
def index():
    # Number of properties
    property_count = db.execute("SELECT COUNT(p_id) AS property_number FROM properties")
    property_count = property_count[0]["property_number"]
    if not property_count:
        property_count = 0

    # Number of caretakers
    caretaker_count = db.execute(
        "SELECT COUNT(ct_id) AS caretaker_number FROM caretakers"
    )
    caretaker_count = caretaker_count[0]["caretaker_number"]
    if not caretaker_count:
        caretaker_count = 0

    # Number of jobs offered
    job_count = db.execute(
        "SELECT COUNT(application_id) AS job_number FROM applications WHERE status = ?",
        1,
    )
    job_count = job_count[0]["job_number"]
    if not job_count:
        job_count = 0
    return render_template(
        "index.html",
        property_count=property_count,
        caretaker_count=caretaker_count,
        job_count=job_count,
    )


# Caretaker Routes
@app.route("/ctdashboard")
@login_required
def ctdashboard():
    application_count = db.execute(
        "SELECT COUNT(application_id) AS application_number FROM applications WHERE ct_id = ?",
        session["user_id"],
    )
    application_count = application_count[0]["application_number"]
    if not application_count:
        application_count = 0
    property_count = db.execute(
        "SELECT COUNT(p_id) AS property_number FROM properties WHERE p_visibility = ?",
        0,
    )
    property_count = property_count[0]["property_number"]
    if not property_count:
        property_count = 0
    return render_template(
        "ctdashboard.html",
        application_count=application_count,
        property_count=property_count,
    )


@app.route("/ctprofile", methods=["GET", "POST"])
@login_required
def ctprofile():
    ct_details = db.execute(
        "SELECT ct_name, email_address, address, id_number, date_of_birth, profile_photo, profile_description FROM caretakers WHERE ct_id = ?",
        session["user_id"],
    )
    if request.method == "POST":
        if ct_details[0]["profile_photo"] == None:
            address = request.form.get("address")
            profile_description = request.form.get("description")
            profile_photo = request.files["profile"]
            id_scan = request.files["id_scan"]
            prepend = random.randint(10, 1000)

            profile_photo_filename = (
                f"{session['user_id']}{secure_filename(profile_photo.filename)}"
            )
            id_scan_filename = f"{prepend}{secure_filename(id_scan.filename)}"

            profile_photo.save(f"static/profile_pictures/{profile_photo_filename}")
            id_scan.save(f"id_scans/{id_scan_filename}")

            db.execute(
                "UPDATE caretakers SET profile_photo = ?, id_scan = ?, profile_description = ?, profile_visibility = ? WHERE ct_id = ?",
                profile_photo_filename,
                id_scan_filename,
                profile_description,
                1,
                session["user_id"],
            )
        else:
            address = request.form.get("address")
            profile_description = request.form.get("description")
            profile_photo = request.files["profile"]

            if address:
                db.execute(
                    "UPDATE caretakers SET address = ? WHERE ct_id = ?",
                    address,
                    session["user_id"],
                )
            if profile_description:
                db.execute(
                    "UPDATE caretakers SET profile_description = ? WHERE ct_id = ?",
                    profile_description,
                    session["user_id"],
                )
            if profile_photo:
                # Deleting old profile photo
                os.remove("static/profile_pictures/" + ct_details[0]["profile_photo"])
                # Saving new profile photo
                profile_photo_filename = (
                    f"{session['user_id']}{secure_filename(profile_photo.filename)}"
                )
                profile_photo.save(f"static/profile_pictures/{profile_photo_filename}")
                db.execute(
                    "UPDATE caretakers SET profile_photo = ? WHERE ct_id = ?",
                    profile_photo_filename,
                    session["user_id"],
                )
        return redirect("/ctprofile")

    else:
        return render_template("ctprofile.html", ct_details=ct_details)
    return render_template("ctprofile.html", ct_details=ct_details)


@app.route("/ctapplication", methods=["GET", "POST"])
@login_required
def ctapplication():
    if request.method == "POST":
        property_id = request.form.get("property_id")
        path = f"/ctapplicationpage/{property_id}"
        return redirect(path)
    else:
        properties = db.execute("SELECT * FROM properties WHERE p_visibility = ?", 1)
        eligibility = db.execute(
            "SELECT profile_visibility FROM caretakers WHERE ct_id = ?",
            session["user_id"],
        )
        render_template(
            "ctapplication.html", properties=properties, eligibility=eligibility
        )
    return render_template(
        "ctapplication.html", properties=properties, eligibility=eligibility
    )


@app.route("/ctapplicationpage/<int:property_id>", methods=["GET", "POST"])
@login_required
def ctapplicationpage(property_id):
    property = db.execute("SELECT * FROM properties WHERE p_id = ?", property_id)
    if request.method == "POST":
        supporting_text = request.form.get("supp_text")
        db.execute(
            "INSERT INTO applications (ct_id, h_id, p_id, date_of_application, supporting_text) VALUES (?, ?, ?, ?, ?)",
            session["user_id"],
            property[0]["h_id"],
            property_id,
            datetime.date.today(),
            supporting_text,
        )
        return redirect("/ctapplication")
    else:
        render_template("ctapplicationpage.html", property=property)
    return render_template("ctapplicationpage.html", property=property)


@app.route("/ctapplicationsmade", methods=["GET", "POST"])
@login_required
def ctapplicationsmade():
    applications = db.execute(
        "SELECT application_id, date_of_application, status, properties.img_1 AS image, properties.p_name AS property_name, properties.p_description AS property_description FROM applications INNER JOIN properties ON applications.p_id = properties.p_id WHERE applications.ct_id = ? ORDER BY status ASC",
        session["user_id"],
    )
    if request.method == "POST":
        application_id = request.form.get("application_id")
        db.execute(
            "UPDATE applications SET status = ? WHERE application_id = ?",
            3,
            application_id,
        )
        return redirect("/ctapplicationsmade")
    else:
        render_template("ctapplicationsmade.html", applications=applications)
    return render_template("ctapplicationsmade.html", applications=applications)


# Home owner routes
@app.route("/hdashboard")
@login_required
def hdashboard():
    property_count = db.execute(
        "SELECT COUNT(p_id) AS property_number FROM properties WHERE h_id = ?",
        session["user_id"],
    )
    property_count = property_count[0]["property_number"]
    if not property_count:
        property_count = 0
    pending_applications = db.execute(
        "SELECT COUNT(application_id) AS application_number FROM applications WHERE h_id = ? AND status = ?",
        session["user_id"],
        0,
    )
    pending_applications = pending_applications[0]["application_number"]
    if not pending_applications:
        pending_applications = 0
    return render_template(
        "hdashboard.html",
        property_count=property_count,
        pending_applications=pending_applications,
    )


@app.route("/postproperty", methods=["GET", "POST"])
@login_required
def postproperty():
    if request.method == "POST":
        prepend = random.randint(10, 100000)
        pic_1 = request.files["pic_1"]
        pic_2 = request.files["pic_2"]
        pic_3 = request.files["pic_3"]
        pic_4 = request.files["pic_4"]
        pic_5 = request.files["pic_5"]
        property_name = request.form.get("property_name")
        property_description = request.form.get("property_description")
        property_location = request.form.get("property_location")
        job_description = request.form.get("job_description")

        # Saving the images
        pic_1_filename = f"{prepend}{secure_filename(pic_1.filename)}"
        pic_1.save(f"static/property_images/{pic_1_filename}")
        if pic_2:
            pic_2_filename = f"{prepend}{secure_filename(pic_2.filename)}"
            pic_2.save(f"static/property_images/{pic_2_filename}")
            pic_2 = pic_2_filename
        else:
            pic_2 = None
        if pic_3:
            pic_3_filename = f"{prepend}{secure_filename(pic_3.filename)}"
            pic_3.save(f"static/property_images/{pic_3_filename}")
            pic_3 = pic_3_filename
        else:
            pic_3 = None
        if pic_4:
            pic_4_filename = f"{prepend}{secure_filename(pic_4.filename)}"
            pic_4.save(f"static/property_images/{pic_4_filename}")
            pic_4 = pic_4_filename
        else:
            pic_4 = None
        if pic_5:
            pic_5_filename = f"{prepend}{secure_filename(pic_5.filename)}"
            pic_5.save(f"static/property_images/{pic_5_filename}")
            pic_5 = pic_5_filename
        else:
            pic_5 = None
        # Inserting into database
        db.execute(
            "INSERT INTO properties (h_id, p_name, date_posted, p_description, p_location, img_1, img_2, img_3, img_4, img_5, job_requirements) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            session["user_id"],
            property_name,
            datetime.date.today(),
            property_description,
            property_location,
            pic_1_filename,
            pic_2,
            pic_3,
            pic_4,
            pic_5,
            job_description,
        )

        return redirect("/postproperty")

    else:
        return render_template("postproperty.html")
    return render_template("postproperty.html")


@app.route("/hpropertymanagement", methods=["GET", "POST"])
@login_required
def hpropertymanagement():
    if request.method == "POST":
        property_id = request.form.get("property_id")
        path = f"/hpropertyview/{property_id}"
        return redirect(path)
    else:
        properties = db.execute(
            "SELECT p_id, p_name, date_posted, p_description, p_location, img_1, img_2, img_3, img_4, img_5, job_requirements FROM properties WHERE h_id = ?",
            session["user_id"],
        )
        return render_template("hpropertymanagement.html", properties=properties)
    return render_template("hpropertymanagement.html")


@app.route("/hpropertyview/<int:property_id>", methods=["GET", "POST"])
@login_required
def hpropertyview(property_id):
    selected_property = db.execute(
        "SELECT * FROM properties WHERE p_id = ?", property_id
    )
    if request.method == "POST":
        prepend = random.randint(10, 100000)
        pic_1 = request.files["pic_1"]
        pic_2 = request.files["pic_2"]
        pic_3 = request.files["pic_3"]
        pic_4 = request.files["pic_4"]
        pic_5 = request.files["pic_5"]

        if pic_1 and selected_property[0]["img_1"] != None:
            os.remove("static/property_images/" + selected_property[0]["img_1"])
            pic_1_filename = f"{prepend}{secure_filename(pic_1.filename)}"
            pic_1.save(f"static/property_images/{pic_1_filename}")
            db.execute(
                "UPDATE properties SET img_1 = ? WHERE p_id = ?",
                pic_1_filename,
                property_id,
            )
        if pic_2 and selected_property[0]["img_2"] != None:
            os.remove("static/property_images/" + selected_property[0]["img_2"])
            pic_2_filename = f"{prepend}{secure_filename(pic_2.filename)}"
            pic_2.save(f"static/property_images/{pic_2_filename}")
            pic_2 = pic_2_filename
            db.execute(
                "UPDATE properties SET img_2 = ? WHERE p_id = ?",
                pic_2_filename,
                property_id,
            )
        if pic_3 and selected_property[0]["img_3"] != None:
            os.remove("static/property_images/" + selected_property[0]["img_3"])
            pic_3_filename = f"{prepend}{secure_filename(pic_3.filename)}"
            pic_3.save(f"static/property_images/{pic_3_filename}")
            pic_3 = pic_3_filename
            db.execute(
                "UPDATE properties SET img_3 = ? WHERE p_id = ?",
                pic_3_filename,
                property_id,
            )
        if pic_4 and selected_property[0]["img_4"] != None:
            os.remove("static/property_images/" + selected_property[0]["img_4"])
            pic_4_filename = f"{prepend}{secure_filename(pic_4.filename)}"
            pic_4.save(f"static/property_images/{pic_4_filename}")
            pic_4 = pic_4_filename
            db.execute(
                "UPDATE properties SET img_4 = ? WHERE p_id = ?",
                pic_4_filename,
                property_id,
            )
        if pic_5 and selected_property[0]["img_5"] != None:
            os.remove("static/property_images/" + selected_property[0]["img_5"])
            pic_5_filename = f"{prepend}{secure_filename(pic_5.filename)}"
            pic_5.save(f"static/property_images/{pic_5_filename}")
            pic_5 = pic_5_filename
            db.execute(
                "UPDATE properties SET img_5 = ? WHERE p_id = ?",
                pic_5_filename,
                property_id,
            )

        path = f"/hpropertyview/{property_id}"
        return redirect(path)
    else:
        return render_template(
            "hpropertyview.html", selected_property=selected_property
        )
    return render_template("hpropertyview.html", selected_property=selected_property)


@app.route("/happlicationmanagement", methods=["GET", "POST"])
@login_required
def happlicationmanagement():
    applications = db.execute(
        "SELECT application_id, date_of_application, properties.img_1 AS image, properties.p_name AS property_name, properties.p_description AS property_description, caretakers.ct_name AS caretaker_name, caretakers.profile_photo AS caretaker_picture FROM applications INNER JOIN caretakers ON applications.ct_id = caretakers.ct_id INNER JOIN properties ON applications.p_id = properties.p_id WHERE applications.ct_id = ? AND applications.status = ? ORDER BY status ASC",
        session["user_id"],
        0,
    )
    if request.method == "POST":
        application_id = request.form.get("application_id")
        path = f"/happlicationsview/{application_id}"
        return redirect(path)
    else:
        render_template("happlicationmanagement.html", applications=applications)
    return render_template("happlicationmanagement.html", applications=applications)


@app.route("/happlicationsview/<int:application_id>", methods=["GET", "POST"])
@login_required
def happlicationsview(application_id):
    application = db.execute(
        "SELECT application_id, applications.ct_id, applications.p_id, supporting_text, properties.img_1, properties.img_2, properties.img_3, properties.img_4, properties.img_5, properties.p_name AS property_name, properties.p_description AS property_description, caretakers.ct_name AS caretaker_name, caretakers.profile_photo FROM applications INNER JOIN caretakers ON applications.ct_id = caretakers.ct_id INNER JOIN properties ON applications.p_id = properties.p_id WHERE applications.status != ? ORDER BY status ASC",
        2,
    )
    if request.method == "POST":
        opval = request.form.get("opval")
        if opval == "Approve":
            db.execute(
                "UPDATE applications SET status = ? WHERE application_id = ?",
                1,
                application_id,
            )
            db.execute(
                "UPDATE caretakers SET hired_status = ? WHERE ct_id = ?",
                1,
                application[0]["ct_id"],
            )
            db.execute(
                "UPDATE properties SET p_visibility = ? WHERE p_id = ?",
                0,
                application[0]["p_id"],
            )
        elif opval == "Reject":
            db.execute(
                "UPDATE applications SET status = ? WHERE application_id = ?",
                2,
                application_id,
            )
        return redirect("/happlicationmanagement")
    else:
        return render_template("happlicationsview.html", application=application)
    return render_template("happlicationsview.html", application=application)
