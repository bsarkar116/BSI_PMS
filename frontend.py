import datetime
import os
from logger import logging
from flask_session import Session
from flask import Flask, render_template, request, session, redirect, url_for, flash
from pms import *
from forms import *
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.exceptions import NotFound
from flask_wtf import csrf
from validations import validate_json

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

# AO8
# Logging configuration
root = logging.getLogger("root")

# Global Variable
global flag


# AH11
@app.before_request
def before_request():
    try:
        now = datetime.datetime.now()
        if session:
            if 'last_active' in session:
                last_active = session['last_active']
                delta = now - last_active
                if delta.seconds > 900:
                    session.clear()
                    root.info("Session has expired")
                    return redirect(url_for('login'))
        session['last_active'] = now
        root.info("Session updated with current time")
    except KeyError:
        pass


@app.route("/", methods=["GET", "POST"])  # HT2
def index():
    if not session.get("id") or request.environ.get('HTTP_X_REAL_IP', request.remote_addr) != session.get("IP"):  # AH14
        return render_template("index.html", mimetypes="UTF-8")  # HT7
    else:
        pass_retention()
        return redirect(url_for('dashboard'))


@app.route('/register', methods=["GET", "POST"])
def register():
    global flag
    flag = 0
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():  # DH3
        uid = form.uid.data
        fname = form.fname.data
        lname = form.lname.data
        email = form.email.data
        addr = form.address.data
        rows = lookup_acc(uid, None, 1)
        if not rows:
            r, count = query_acc(None, 1)
            if r:
                for i in range(len(r)):
                    if form.email.data == r[i][3]:
                        flag = 1
                        form.email.errors.append("Email already in use")
                        break
                if flag == 0:
                    resp = add_user(uid, fname, lname, email, addr, 1)
                    if resp:
                        flash("Account created. Check registered email for login credentials", "Success")
                        root.info("New User created")
                        return redirect(url_for('login'))
                    else:
                        flash("Invalid details provided", "Error")
                        return redirect(url_for('register'))
            else:
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
                r = lookup_acc(form.uid.data, None, 1)
                session["id"] = r[10]
                session["IP"] = request.remote_addr
                session["last_active"] = datetime.datetime.now()
                if check_status(r[10]):
                    ID = session["id"]
                    r = lookup_acc(None, ID, 2)
                    update_accpass(ID, uid, r[3], 3)
                    flash("New login credentials emailed as per new Password Policy", "Success")
                root.info("Access granted") # AO8
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
    if not session.get("id") or request.environ.get('HTTP_X_REAL_IP', request.remote_addr) != session.get("IP"):
        return redirect(url_for('login'))
    else:
        ID = session.get("id")
        rows = lookup_acc(None, ID, 2)
        r = lookup_role(ID, 1)
        role_templates = {
            "admin": "admin.html",
            "user": "user.html"
        }
        template = role_templates.get(r[1], "index.html")
        return render_template(template, fname=rows[1], lname=rows[2], mimetypes="UTF-8")


# AH8, AH12
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
        r, count = query_acc(None, 1)
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
    if not session.get("id") or request.environ.get('HTTP_X_REAL_IP', request.remote_addr) != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        form = ProfileForm(request.form)
        ID = session.get("id")
        rows = lookup_acc(None, ID, 2)
        r = lookup_role(ID, 1)
        role_templates = {
            "admin": {"template": "admin.html", "fname": rows[1], "lname": rows[2]},
            "user": {"template": "user.html", "fname": rows[1], "lname": rows[2]}
        }
        form.uid.data = rows[0]
        form.fname.data = rows[1]
        form.lname.data = rows[2]
        form.email.data = rows[3]
        form.address.data = rows[4]
        return render_template("profile.html", form=form, template=role_templates[r[1]]["template"],
                               fname=role_templates[r[1]]["fname"], lname=role_templates[r[1]]["lname"],
                               mimetypes="UTF-8")


@app.route('/update', methods=["GET", "POST"])
def update():
    if not session.get("id") or request.environ.get('HTTP_X_REAL_IP', request.remote_addr) != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        form = ProfileForm(request.form)
        if request.method == "POST":
            ID = session.get("id")
            rows = lookup_acc(None, ID, 2)
            r = lookup_role(ID, 1)
            if r[1] == "admin" or r[1] == "user":
                if rows:
                    if "upd_dets" in request.form:
                        if form.validate():
                            fname = form.fname.data
                            lname = form.lname.data
                            address = form.address.data
                            if fname != rows[1] or lname != rows[2] or address != rows[4]:
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
                        resp = update_accpass(rows[10], rows[0], rows[3], 2)
                        if resp:
                            flash("Login credentials sent to registered email", "Success")
                            return redirect(url_for('profile'))
                        else:
                            flash("Login credentials not changed", "Error")
                            return redirect(url_for('profile'))
        return redirect(url_for('profile'))


@app.route('/pwd', methods=["GET", "POST"])
def pwd():
    if not session.get("id") or request.environ.get('HTTP_X_REAL_IP', request.remote_addr) != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        form = PasswordForm(request.form)
        ID = session.get("id")
        rows = lookup_acc("NULL", ID, 2)
        r = lookup_role(ID, 1)
        role_templates = {
            "admin": {"template": "admin.html", "fname": rows[1], "lname": rows[2]},
            "user": {"template": "user.html", "fname": rows[1], "lname": rows[2]}
        }
        return render_template("add-pwd.html", form=form, template=role_templates[r[1]]["template"],
                               fname=role_templates[r[1]]["fname"], lname=role_templates[r[1]]["lname"],
                               mimetypes="UTF-8")


@app.route('/addpwd', methods=["GET", "POST"])
def addpwd():
    if not session.get("id") or request.environ.get('HTTP_X_REAL_IP', request.remote_addr) != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        if request.method == "POST":
            ID = session.get("id")
            r = lookup_role(ID, 1)
            if r[1] == "admin" or r[1] == "user":
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
                            own = lookup_acc(None, owner, 2)
                            rows = lookup_app(own[10], appname, None, 1)
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
                            rows = lookup_app(ID, appname, None, 1)
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
    if not session.get("id") or request.environ.get('HTTP_X_REAL_IP', request.remote_addr) != session.get("IP"):
        return redirect(url_for('login'))
    else:
        user_list = list()
        form = PasswordForm(request.form)
        form1 = ShareForm(request.form)
        ID = session.get("id")
        rows = lookup_acc(None, ID, 2)
        pa = lookup_appperms(ID, None, 3)
        pm = lookup_appperms(ID, None, 2)
        r = lookup_role(ID, 1)
        users, c = query_acc(None, 1)
        for i in range(len(users)):
            if ID != users[i][10]:
                user_list.append((users[i][10], users[i][0]))
        form1.uid.choices = user_list
        role_templates = {
            "admin": {"template": "admin.html", "fname": rows[1], "lname": rows[2]},
            "user": {"template": "user.html", "fname": rows[1], "lname": rows[2]}
        }
        return render_template("list-pwd.html", form=form, form1=form1, pdata=pa, share_data=pm,
                               template=role_templates[r[1]]["template"],
                               fname=role_templates[r[1]]["fname"], lname=role_templates[r[1]]["lname"],
                               mimetypes="UTF-8", udata=users, uid=ID)


@app.route('/share', methods=["GET", "POST"])
def share():
    if not session.get("id") or request.environ.get('HTTP_X_REAL_IP', request.remote_addr) != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        if request.method == "POST":
            ID = session.get("id")
            r = lookup_role(ID, 1)
            y, ref = request.referrer.rsplit("/", 1)
            form = ShareForm(request.form)
            if ref == "listpwd":
                if r[1] == "admin" or r[1] == "user":
                    appid = request.form['id']
                    perms = form.perms1.data
                    perms1 = form.perms2.data
                    if perms and perms == "o":
                        resp = upd_appperms(perms, form.uid.data, appid, 2)
                        if resp:
                            flash("Owner changed", "Success")
                            return redirect(url_for('listpwd'))
                        else:
                            flash("Owner was not changed", "Error")
                            return redirect(url_for('listpwd'))
                    elif perms1 and perms1 == "o":
                        resp = upd_appperms(perms1, form.uid.data, appid, 2)
                        if resp:
                            flash("Owner changed", "Success")
                            return redirect(url_for('listpwd'))
                        else:
                            flash("Owner was not changed", "Error")
                            return redirect(url_for('listpwd'))
                    elif perms and perms != "o":
                        resp = upd_appperms(perms, form.uid.data, appid, 1)
                        if resp:
                            flash("Permissions changed", "Success")
                            return redirect(url_for('listpwd'))
                        else:
                            flash("Permissions were not changed", "Error")
                            return redirect(url_for('listpwd'))
                    elif perms1 and perms1 != "o":
                        resp = upd_appperms(perms1, form.uid.data, appid, 1)
                        if resp:
                            flash("Permissions changed", "Success")
                            return redirect(url_for('listpwd'))
                        else:
                            flash("Permissions were not changed", "Error")
                            return redirect(url_for('listpwd'))
                    else:
                        flash("Permissions were not changed", "Error")
                        return redirect(url_for('listpwd'))
                else:
                    return redirect(url_for('dashboard'))
            elif ref == "listuser":
                if r[1] == "admin":
                    ID = request.form['id']
                    if form.role.data == "admin":
                        resp = update_accrole(ID, "admin")
                        if resp:
                            flash("Admin privilege granted", "Success")
                            return redirect(url_for('listuser'))
                        else:
                            flash("Admin privilege not granted", "Error")
                            return redirect(url_for('listuser'))
                    elif form.role.data == "user":
                        resp = update_accrole(ID, "user")
                        if resp:
                            flash("User privilege granted", "Success")
                            return redirect(url_for('listuser'))
                        else:
                            flash("User privilege granted", "Error")
                            return redirect(url_for('listuser'))
                    else:
                        return redirect(url_for('listuser'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard'))


@app.route('/delpwd', methods=["GET", "POST"])
def delpwd():
    if not session.get("id") or request.environ.get('HTTP_X_REAL_IP', request.remote_addr) != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        if request.method == "POST":
            ID = session.get("id")
            r = lookup_role(ID, 1)
            if r[1] == "admin" or r[1] == "user":
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
    if not session.get("id") or request.environ.get('HTTP_X_REAL_IP', request.remote_addr) != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        form = PolicyForm(request.form)
        form1 = UploadForm(request.form)
        ID = session.get("id")
        rows = lookup_acc(None, ID, 2)
        r = lookup_role(ID, 1)
        poli = read_pol()
        form.length.data = poli['Length']
        form.upper.data = poli['Upper']
        form.lower.data = poli['Lower']
        form.digits.data = poli['Digits']
        form.special.data = poli['Special']
        form.age.data = poli['Age']
        if r[1] == "admin":
            return render_template("pass-pol.html", form=form, form1=form1, template="admin.html", fname=rows[1],
                                   lname=rows[2], mimetypes="UTF-8")
        elif r[1] == "user":
            return redirect(url_for('dashboard'))
        else:
            session.clear()
            return render_template("index.html", mimetypes="UTF-8")


@app.route('/updpol', methods=["GET", "POST"])
def updpol():
    if not session.get("id") or request.environ.get('HTTP_X_REAL_IP', request.remote_addr) != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        ID = session.get("id")
        r = lookup_role(ID, 1)
        if request.method == 'POST' and r[1] == "admin":
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
                        return redirect(url_for('passpol'))
                    else:
                        flash('Invalid/Empty policy information provided',
                              'Error')
                        return redirect(url_for('passpol'))
                else:
                    flash('Invalid/Empty policy information provided', 'Error')
                    return redirect(url_for('passpol'))
            elif "upload_pol" in request.form:
                form = UploadForm()
                if form.validate_on_submit():
                    filedata = form.file.data
                    if filedata:
                        filedata.save(os.path.join(app.config['UPLOAD_FOLDER'], "temp_policy.json"))
                    else:
                        flash('File is empty', 'Error')
                        root.info("File is empty")
                        return redirect(url_for('passpol'))
                    resp = add_pol()
                    if resp:
                        flash('Policy updated!!', 'Success')
                        root.info("New Password Policy added")
                        return redirect(url_for('passpol'))
                    else:
                        root.info("Password Policy update failed")
                        flash('Invalid JSON file uploaded', "Error")
                        return redirect(url_for('passpol'))
                else:
                    root.info("Password Policy update failed")
                    flash('Invalid JSON file uploaded', "Error")
                    return redirect(url_for('passpol'))
        elif r[1] == "user":
            return redirect(url_for('dashboard'))
        else:
            session.clear()
            return render_template("index.html", mimetypes="UTF-8")


@app.route("/listuser", methods=["GET", "POST"])
def listuser():
    if not session.get("id") or request.environ.get('HTTP_X_REAL_IP', request.remote_addr) != session.get("IP"):
        return redirect(url_for('login'))
    else:
        form = ShareForm(request.form)
        ID = session.get("id")
        rows = lookup_acc(None, ID, 2)
        users = query_acc(ID, 2)
        r = lookup_role(ID, 1)
        rdata = lookup_role(ID, 2)
        if r[1] == "admin":
            return render_template("list-user.html", form=form, all_data=users, rdata=rdata, template="admin.html",
                                   fname=rows[1],
                                   lname=rows[2], mimetypes="UTF-8")
        elif r[1] == "user":
            return redirect(url_for('dashboard'))
        else:
            session.clear()
            return render_template("index.html", mimetypes="UTF-8")


@app.route('/deluser', methods=["GET", "POST"])
def deluser():
    if not session.get("id") or request.environ.get('HTTP_X_REAL_IP', request.remote_addr) != session.get("IP"):
        return render_template("index.html", mimetypes="UTF-8")
    else:
        ID = session.get("id")
        r = lookup_role(ID, 1)
        if request.method == 'POST' and r[1] == "admin":
            ID = request.form['id']
            resp = del_user(ID)
            if resp:
                flash("User removed successfully", "Success")
                return redirect(url_for('listuser'))
            else:
                flash("User removal failed", "Success")
                return redirect(url_for('listuser'))
        elif r[1] == "user":
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
