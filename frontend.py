import datetime
import schema
import validations
import os
from logger import logging
from flask_session import Session
from flask import Flask, render_template, request, session, redirect, url_for, flash
from pms import add_user, compare_hash, update_accpass, lookup_role, query_acc, gen_apppass, add_apppwd, \
    update_user, upd_apppwd, lookup_app, del_apppwd, delete_user, pass_retention, read_pol, \
    check_status, gen_policy, add_pol, lookup_appperms, update_appperms, lookup_acc
from wtforms import Form, BooleanField, StringField, PasswordField, validators, IntegerRangeField, IntegerField, \
    SelectField
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.exceptions import NotFound
from flask_wtf import csrf, FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired


# DV1, DV2, DV4
# Server Side form validation configurations
class RegistrationForm(Form):
    uid = StringField('Username',
                      [validators.Length(min=4, max=25), validators.input_required()])
    fname = StringField('First Name', [validators.input_required()])
    lname = StringField('Last Name', [validators.input_required()])
    email = StringField('Email Address', [validators.Email(),
                                          validators.input_required()])
    address = StringField('Address', [validators.input_required()])


class LoginForm(Form):
    uid = StringField('Username',
                      [validators.Length(min=4), validators.input_required()])
    passw = PasswordField('Password', [validators.input_required()])


class ForgotForm(Form):
    email = StringField('Email Address', [validators.Email(),
                                          validators.input_required()])


class ProfileForm(Form):
    uid = StringField('Username')
    fname = StringField('First Name', [validators.input_required()])
    lname = StringField('Last Name', [validators.input_required()])
    email = StringField('Email Address')
    address = StringField('Address', [validators.input_required()])


class PasswordForm(Form):
    appname = StringField('App Name', [validators.input_required()])
    letters = BooleanField('Letters', [validators.input_required()])
    digits = BooleanField('Digits')
    special = BooleanField('Special Chars')
    length = IntegerRangeField('Length', [validators.input_required(), validators.NumberRange(min=6, max=25)])


class AppForm(Form):
    appname = StringField('App Name')
    letters = BooleanField('Letters', [validators.input_required()])
    digits = BooleanField('Digits')
    special = BooleanField('Special Chars')
    length = IntegerRangeField('Length', [validators.input_required(), validators.NumberRange(min=6, max=25)])


class PolicyForm(Form):
    length = IntegerField('Password Length(6-30)', [validators.input_required(),
                                                    validators.NumberRange(min=6, max=30)])
    upper = IntegerField('Uppercase Letters(Min 1)', [validators.input_required(),
                                                      validators.NumberRange(min=1)])
    lower = IntegerField('Lowercase Letters(Min 1)', [validators.input_required(),
                                                      validators.NumberRange(min=1)])
    digits = IntegerField('Digits(Min 1)', [validators.input_required(),
                                            validators.NumberRange(min=1)])
    special = IntegerField('Special Chars(Min 1)', [validators.input_required(),
                                                    validators.NumberRange(min=1)])
    age = IntegerField('Password Retention Period(10-60)', [validators.input_required(),
                                                            validators.NumberRange(min=10, max=60)])


class UploadForm(FlaskForm):
    file = FileField('Upload JSON', validators=[FileAllowed(['json', 'JSON']), FileRequired()])


class ShareForm(Form):
    uid = SelectField('User', coerce=int)
    perms = SelectField('Permission', choices=[("o", "owner"), ("v", "viewer"), ("e", "editor")])


# Flask app configuration
app = Flask(__name__)

# AH1, AH9, AH15, AO1, AO3, DH5, HT5
# Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(seconds=900)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_THRESHOLD"] = 10
app.config["SESSION_COOKIE_SECURE"] = True  # HT4
app.config["SESSION_COOKIE_HTTPONLY"] = True
Session(app)

# HT5
# CSRF Configuration
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
csrf = csrf.CSRFProtect(app)

# File upload configuration
app.config['UPLOAD_FOLDER'] = r"C:\Users\BrijitSarkar\Desktop\pms\temp"

# Logging configuration
root = logging.getLogger("root")

# Global Variable
global flag


# AH11
@app.before_request
def before_request():
    now = datetime.datetime.now()
    try:
        last_active = session['last_active']
        delta = now - last_active
        if delta.seconds > 900:
            flash("Session has expired. Please login again", "Error")
            session.clear()
            return redirect(url_for('index'))
    except:
        pass
    try:
        session['last_active'] = now
    except:
        pass


# HT2
@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("id") or request.remote_addr != session.get("IP"):  # AH14
        return render_template("index.html", mimetypes="UTF-8")
    else:
        pass_retention()
        return redirect(url_for('dashboard'))


@app.route('/register', methods=["GET", "POST"])
def register():
    global flag
    flag = 0
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():  # DH3
        rows = lookup_acc(form.uid.data, "NULL", 1)
        if not rows:
            r, count = query_acc("NULL", 1)
            if r:
                for i in range(len(r)):
                    if form.email.data == r[i][3]:
                        flag = 1
                        form.email.errors.append("Email already in use")
                        break
                if flag == 0:
                    uid = form.uid.data
                    fname = form.fname.data
                    lname = form.lname.data
                    email = form.email.data
                    addr = form.address.data
                    resp = add_user(uid, fname, lname, email, addr, 1)
                    if resp:
                        flash("Account created. Check registered email for login credentials", "Success")
                        root.info("New User created")
                        return redirect(url_for('login'))
                    else:
                        flash("Invalid details provided", "Error")
                        return redirect(url_for('register'))
            else:
                uid = form.uid.data
                fname = form.fname.data
                lname = form.lname.data
                email = form.email.data
                addr = form.address.data
                resp = add_user(uid, fname, lname, email, addr, 1)
                if resp:
                    flash("Account created. Check registered email for login credentials", "Success")
                    root.info("New User created")
                    return redirect(url_for('login'))
                else:
                    flash("Invalid details provided", "Error")
                    return redirect(url_for('register'))
        else:
            form.uid.errors.append("Username already in use")
    return render_template('register.html', form=form, mimetypes="UTF-8")


# AH3, AH6
@app.route("/login", methods=["GET", "POST"])
def login():
    pass_retention()
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        uid = form.uid.data
        passw = form.passw.data
        log = {"uid": uid, "pass": passw}
        isValid = validations.validate_json(log, schema.loginSchema)
        if isValid:
            resp = compare_hash(uid, passw)
            if resp:
                r = lookup_acc(form.uid.data, "NULL", 1)
                session["id"] = r[0][10]
                session["IP"] = request.remote_addr
                session["last_active"] = datetime.datetime.now()
                if check_status(r[0][10]):
                    ID = session["id"]
                    r = lookup_acc("NULL", ID, 2)
                    update_accpass(ID, uid, r[0][3], 3)
                    flash("New login credentials emailed as per new Password Policy", "Success")
                root.info("Access granted")
                return redirect(url_for('dashboard'))
            else:
                form.passw.errors.append("Invalid Username/Password. Please try again...")
                root.info("Access denied")
        else:
            form.passw.errors.append("Invalid Username/Password. Please try again...")
            root.info("Access denied")
    return render_template("login.html", form=form, mimetypes="UTF-8")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("id") or request.remote_addr != session.get("IP"):
        return redirect(url_for('login'))
    else:
        ID = session.get("id")
        rows = lookup_acc("NULL", ID, 2)
        r = lookup_role(ID)
        if r[0][1] == "admin":
            return render_template("admin.html", fname=rows[0][1], lname=rows[0][2], mimetypes="UTF-8")  # HT7
        elif r[0][1] == "user":
            return render_template("user.html", fname=rows[0][1], lname=rows[0][2], mimetypes="UTF-8")
        else:
            session.clear()
            return render_template("index.html", mimetypes="UTF-8")


# AH8
@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("index.html", mimetypes="UTF-8")


@app.route('/forgot', methods=["POST"])
def forgot():
    global flag
    flag = 0
    form = ForgotForm(request.form)
    if request.method == "POST" and form.validate():
        r, count = query_acc("NULL", 1)
        if r:
            for i in range(len(r)):
                if form.email.data == r[i][3]:
                    resp = update_accpass(r[i][10], r[i][0], r[i][3], 2)
                    if resp:
                        flash("Login credentials sent to registered email", "Success")
                        return redirect(url_for('forgot'))
            if flag == 0:
                form.email.errors.append("Not a valid email address...")
    return render_template('forgot-password.html', form=form, mimetypes="UTF-8")


@app.route('/profile', methods=["GET", "POST"])
def profile():
    if not session.get("id") or request.remote_addr != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        form = ProfileForm(request.form)
        ID = session.get("id")
        rows = lookup_acc("NULL", ID, 2)
        r = lookup_role(ID)
        if r[0][1] == "admin":
            form.uid.data = rows[0][0]
            form.fname.data = rows[0][1]
            form.lname.data = rows[0][2]
            form.email.data = rows[0][3]
            form.address.data = rows[0][4]
            return render_template("profile.html", form=form, template="admin.html", fname=rows[0][1],
                                   lname=rows[0][2], mimetypes="UTF-8")
        elif r[0][1] == "user":
            form.uid.data = rows[0][0]
            form.fname.data = rows[0][1]
            form.lname.data = rows[0][2]
            form.email.data = rows[0][3]
            form.address.data = rows[0][4]
            return render_template("profile.html", form=form, template="user.html", fname=rows[0][1],
                                   lname=rows[0][2], mimetypes="UTF-8")


@app.route('/update', methods=["GET", "POST"])
def update():
    if not session.get("id") or request.remote_addr != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        form = ProfileForm(request.form)
        if request.method == "POST":
            ID = session.get("id")
            rows = lookup_acc("NULL", ID, 2)
            r = lookup_role(ID)
            if r[0][1] == "admin" or r[0][1] == "user":
                if rows:
                    if "upd_dets" in request.form:
                        if form.validate():
                            fname = form.fname.data
                            lname = form.lname.data
                            address = form.address.data
                            if fname != rows[0][1] or lname != rows[0][2] or address != rows[0][4]:
                                resp = update_user(ID, fname, lname, address)
                                if resp:
                                    flash("Profile updated successfully!!", "Success")
                                    return redirect(url_for('profile'))
                                else:
                                    flash("Invalid information provided", "Error")
                                    return redirect(url_for('profile'))
                            else:
                                flash("No changes were made...", "Error")
                                return redirect(url_for('profile'))
                        else:
                            flash("Invalid information provided", "Error")
                    elif "res_pass" in request.form and form.validate():
                        resp = update_accpass(rows[0][10], rows[0][0], rows[0][3], 2)
                        if resp:
                            flash("Login credentials sent to registered email", "Success")
                            return redirect(url_for('profile'))
                        else:
                            flash("Login credentials not changed", "Error")
                            return redirect(url_for('profile'))
        return redirect(url_for('profile'))


@app.route('/pwd', methods=["GET", "POST"])
def pwd():
    if not session.get("id") or request.remote_addr != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        form = PasswordForm(request.form)
        ID = session.get("id")
        rows = lookup_acc("NULL", ID, 2)
        r = lookup_role(ID)
        if r[0][1] == "admin":
            return render_template("add-pwd.html", form=form, template="admin.html", fname=rows[0][1],
                                   lname=rows[0][2], mimetypes="UTF-8")
        elif r[0][1] == "user":
            return render_template("add-pwd.html", form=form, template="user.html", fname=rows[0][1],
                                   lname=rows[0][2], mimetypes="UTF-8")
        else:
            session.clear()
            return render_template("index.html", mimetypes="UTF-8")


@app.route('/addpwd', methods=["GET", "POST"])
def addpwd():
    if not session.get("id") or request.remote_addr != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        if request.method == "POST":
            ID = session.get("id")
            r = lookup_role(ID)
            if r[0][1] == "admin" or r[0][1] == "user":
                y, ref = request.referrer.rsplit("/", 1)
                if request.method == "POST":
                    if ref == "listpwd":
                        form = AppForm(request.form)
                        if form.validate():
                            appname = request.form['appname']
                            owner = request.form['owner']
                            lett = form.letters.data
                            digi = form.digits.data
                            spc = form.special.data
                            le = form.length.data
                            own = lookup_acc("NULL", owner, 2)
                            rows = lookup_app(own[0][10], appname, "NULL", 1)
                            passw = gen_apppass(lett, digi, spc, le)
                            resp = upd_apppwd(rows[0][0], ID, appname, passw)
                            if resp:
                                flash("Application password updated", "Success")
                                return redirect(url_for('listpwd'))
                            else:
                                flash("Application password update failed", "Error")
                                return redirect(url_for('listpwd'))
                    elif ref == "pwd":
                        form = PasswordForm(request.form)
                        ID = session.get("id")
                        if form.validate():
                            appname = form.appname.data
                            rows = lookup_app(ID, appname, "NULL", 1)
                            if not rows:
                                lett = form.letters.data
                                digi = form.digits.data
                                spc = form.special.data
                                le = form.length.data
                                appn = {"appname": appname, "len": le}
                                isValid = validations.validate_json(appn, schema.appSchema)
                                if isValid:
                                    passw = gen_apppass(lett, digi, spc, le)
                                    resp = add_apppwd(ID, appname, passw)
                                    if resp:
                                        flash("Application entry added", "Success")
                                        return redirect(url_for('pwd'))
                                    else:
                                        flash("Application entry add failed", "Error")
                                        return redirect(url_for('pwd'))
                                else:
                                    flash("Application entry add failed", "Error")
                                    return redirect(url_for('pwd'))
                            else:
                                flash("Entry is already present...", "Error")
                if ref == "pwd":
                    return redirect(url_for('pwd'))
                elif ref == "listpwd":
                    return redirect(url_for('listpwd'))
            else:
                session.clear()
                return render_template("index.html", mimetypes="UTF-8")
        else:
            session.clear()
            return render_template("index.html", mimetypes="UTF-8")


@app.route("/listpwd", methods=["GET", "POST"])
def listpwd():
    if not session.get("id") or request.remote_addr != session.get("IP"):
        return redirect(url_for('login'))
    else:
        group_list = list()
        form = PasswordForm(request.form)
        form1 = ShareForm(request.form)
        ID = session.get("id")
        rows = lookup_acc("NULL", ID, 2)
        pa = lookup_appperms(ID, "NULL", 3)
        pm = lookup_appperms(ID, "NULL", 2)
        r = lookup_role(ID)
        users, c = query_acc("NULL", 1)
        for i in range(len(users)):
            if ID != users[i][10]:
                group_list.append((users[i][10], users[i][0]))
        form1.uid.choices = group_list
        if r[0][1] == "admin":
            return render_template("list-pwd.html", form=form, form1=form1, pdata=pa, share_data=pm,
                                   udata=users,
                                   template="admin.html",
                                   fname=rows[0][1],
                                   lname=rows[0][2], mimetypes="UTF-8")
        elif r[0][1] == "user":
            return render_template("list-pwd.html", form=form, form1=form1, pdata=pa, share_data=pm,
                                   udata=users,
                                   template="user.html",
                                   fname=rows[0][1],
                                   lname=rows[0][2], mimetypes="UTF-8")
        else:
            session.clear()
            return render_template("index.html", mimetypes="UTF-8")


@app.route('/share', methods=["GET", "POST"])
def share():
    if not session.get("id") or request.remote_addr != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        if request.method == "POST":
            ID = session.get("id")
            r = lookup_role(ID)
            if r[0][1] == "admin" or r[0][1] == "user":
                form = ShareForm(request.form)
                appid = request.form['id']
                if form.perms.data == "o":
                    resp = update_appperms(form.perms.data, form.uid.data, appid, 2)
                    if resp:
                        flash("Owner changed", "Success")
                        return redirect(url_for('listpwd'))
                    else:
                        flash("Owner was not changed", "Error")
                        return redirect(url_for('listpwd'))
                else:
                    resp = update_appperms(form.perms.data, form.uid.data, appid, 1)
                    if resp:
                        flash("Permissions changed", "Success")
                        return redirect(url_for('listpwd'))
                    else:
                        flash("Permissions were not changed", "Error")
                        return redirect(url_for('listpwd'))
            else:
                return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard'))


@app.route('/delpwd', methods=["GET", "POST"])
def delpwd():
    if not session.get("id") or request.remote_addr != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        if request.method == "POST":
            ID = session.get("id")
            r = lookup_role(ID)
            if r[0][1] == "admin" or r[0][1] == "user":
                appid = request.form['id']
                del_apppwd(appid)
                flash("Application entry deleted", "Success")
                return redirect(url_for('listpwd'))
            else:
                return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard'))


@app.route('/passpol', methods=["GET", "POST"])
def passpol():
    if not session.get("id") or request.remote_addr != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        form = PolicyForm(request.form)
        form1 = UploadForm(request.form)
        ID = session.get("id")
        rows = lookup_acc("NULL", ID, 2)
        r = lookup_role(ID)
        poli = read_pol()
        form.length.data = poli['Length']
        form.upper.data = poli['Upper']
        form.lower.data = poli['Lower']
        form.digits.data = poli['Digits']
        form.special.data = poli['Special']
        form.age.data = poli['Age']
        if r[0][1] == "admin":
            return render_template("pass-pol.html", form=form, form1=form1, template="admin.html", fname=rows[0][1],
                                   lname=rows[0][2], mimetypes="UTF-8")
        elif r[0][1] == "user":
            return redirect(url_for('dashboard'))
        else:
            session.clear()
            return render_template("index.html", mimetypes="UTF-8")


@app.route('/updpol', methods=["GET", "POST"])
def updpol():
    if not session.get("id") or request.remote_addr != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        ID = session.get("id")
        r = lookup_role(ID)
        if request.method == 'POST' and r[0][1] == "admin":
            form = PolicyForm(request.form)
            if "add_pol" in request.form:
                if form.validate():
                    le = form.length.data
                    up = form.upper.data
                    lo = form.lower.data
                    digi = form.digits.data
                    spcl = form.special.data
                    age = form.age.data
                    resp = gen_policy(le, up, lo, digi, spcl, age)
                    if resp:
                        flash('Policy updated!!', 'Success')
                        root.info("New Password Policy added")
                        return redirect(url_for('passpol'))
                    else:
                        root.info("Password Policy update failed")
                        flash('Please make sure the individual parameters do not exceed the max selected length',
                              'Error')
                else:
                    flash('Invalid/Empty policy information provided', 'Error')
            elif "upload_pol" in request.form:
                form = UploadForm()
                if form.validate_on_submit():
                    filedata = form.file.data
                    filedata.save(os.path.join(app.config['UPLOAD_FOLDER'], "temp_policy.json"))
                    resp = add_pol()
                    if resp:
                        flash('Policy updated!!', 'Success')
                        root.info("New Password Policy added")
                        return redirect(url_for('passpol'))
                    else:
                        root.info("Password Policy update failed")
                        flash('Invalid JSON file uploaded', "Error")
                else:
                    root.info("Password Policy update failed")
                    flash('Invalid JSON file uploaded', "Error")
        elif r[0][1] == "user":
            return redirect(url_for('dashboard'))
        else:
            session.clear()
            return render_template("index.html", mimetypes="UTF-8")


@app.route("/listuser", methods=["GET", "POST"])
def listuser():
    if not session.get("id") or request.remote_addr != session.get("IP"):
        return redirect(url_for('login'))
    else:
        ID = session.get("id")
        rows = lookup_acc("NULL", ID, 2)
        users = query_acc(ID, 2)
        r = lookup_role(ID)
        if r[0][1] == "admin":
            return render_template("list-user.html", all_data=users, template="admin.html",
                                   fname=rows[0][1],
                                   lname=rows[0][2], mimetypes="UTF-8")
        elif r[0][1] == "user":
            return redirect(url_for('dashboard'))
        else:
            session.clear()
            return render_template("index.html", mimetypes="UTF-8")


@app.route('/deluser', methods=["GET", "POST"])
def deluser():
    if not session.get("id") or request.remote_addr != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        ID = session.get("id")
        r = lookup_role(ID)
        if request.method == 'POST' and r[0][1] == "admin":
            ID = request.form['id']
            resp = delete_user(ID)
            if resp:
                flash("User removed successfully", "Success")
                return redirect(url_for('listuser'))
            else:
                flash("User removal failed", "Success")
                return redirect(url_for('listuser'))
        elif r[0][1] == "user":
            return redirect(url_for('dashboard'))
        else:
            session.clear()
            return render_template("index.html", mimetypes="UTF-8")


# Reverse proxy settings
hostedApp = Flask(__name__)
hostedApp.wsgi_app = DispatcherMiddleware(NotFound(), {
    "/app": app
})

hostedApp.run(host="0.0.0.0", port=9050, debug=True)