import sys, os, secrets, smtplib, sqlite3, dotenv
sys.dont_write_bytecode = True

from email.message import EmailMessage
from functools import wraps
from security import uuid1_now, check_password_hash, generate_password_hash
from flask import Flask, flash, g, redirect, render_template, request, session, url_for

dotenv.load_dotenv()


class Settings:
    DB_PATH = "./db/lite.db"
    FLAG: str = os.getenv("FLAG", "flag-not-configured")
    HTTP_PORT: int = int(os.getenv("HTTP_PORT", "8000"))
    HTTP_HOST: str = os.getenv("HTTP_HOST", "0.0.0.0")

    VICTIM_EMAIL: str = os.getenv("VICTIM_EMAIL", "blackhole@dragonsec.si").strip().lower()
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "noreply@dragonsec.si")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "mail.dragonsec.si")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PWD: str = os.getenv("SMTP_PWD")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "1") == "1"


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(Settings.DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(_error: Exception | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def current_user() -> sqlite3.Row | None:
    user_id = session.get("user_id")
    if not user_id:
        return None

    return get_db().execute("SELECT id, email FROM users WHERE id = ?", (user_id,)).fetchone()

def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if current_user() is None:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view

def send_reset_email(receiver_email: str, token: str) -> bool:
    reset_url: str = url_for("reset_password", token=token, email=receiver_email, _external=True)

    msg = EmailMessage()
    msg["Subject"] = "Nom Nom Lab Password Reset"
    msg["From"] = Settings.SENDER_EMAIL
    msg["To"] = receiver_email
    msg.set_content(
        "\n".join(
            [
                "Hey there,",
                "",
                "Your reset sandwich link is ready:",
                reset_url,
                "",
                "If this wasn't you, ignore this message.",
                "Nom Nom Lab",
            ]
        )
    )

    try:
        with smtplib.SMTP(Settings.SMTP_HOST, Settings.SMTP_PORT, timeout=10) as smtp:
            if Settings.SMTP_USE_TLS:
                smtp.starttls()

            if Settings.SMTP_USER and Settings.SMTP_PWD:
                smtp.login(Settings.SMTP_USER, Settings.SMTP_PWD)

            smtp.send_message(msg)
    
    except Exception as exc:
        app.logger.exception("Failed to send reset email: %s", exc)
        return False

    return True


@app.route("/")
def index() -> str:
    user = current_user()
    if user:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register() -> str:
    if current_user() is not None:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or "@" not in email:
            flash("Please enter a valid email address.", "error")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must have at least 8 characters.", "error")
            return render_template("register.html")

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users(email, password_hash) VALUES (?, ?)",
                (email, generate_password_hash(password)),
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash("An account with this email already exists.", "error")
            return render_template("register.html")

        flash("Account created. You can log in now.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    if current_user() is not None:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = get_db().execute(
            "SELECT id, email, password_hash FROM users WHERE email = ?", (email,),
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        flash("Welcome back to Nom Nom Lab.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/logout")
def logout() -> str:
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard() -> str:
    user = current_user()
    show_flag = user["email"].lower() == Settings.VICTIM_EMAIL
    return render_template(
        "dashboard.html",
        user=user,
        show_flag=show_flag,
        flag=Settings.FLAG if show_flag else None,
    )

@app.route("/request-reset", methods=["GET", "POST"])
def request_reset() -> str:
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = get_db().execute(
            "SELECT id, email FROM users WHERE email = ?", (email,),
        ).fetchone()

        if user is not None:
            token = uuid1_now()
            db = get_db()
            db.execute(
                "INSERT INTO reset_tokens(user_id, token) VALUES (?, ?)",
                (user["id"], token),
            )
            db.commit()
            send_reset_email(user["email"], token)

        flash(
            "If this email exists, a reset sandwich link has been delivered.",
            "success",
        )
        return redirect(url_for("login"))

    return render_template("request_reset.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password() -> str:
    if request.method == "GET":
        return render_template(
            "reset_password.html",
            token=request.args.get("token", ""),
            email=request.args.get("email", ""),
        )

    email = request.form.get("email", "").strip().lower()
    token = request.form.get("token", "").strip().lower()
    new_password = request.form.get("new_password", "")

    if not email or not token:
        flash("Email and token are required.", "error")
        return render_template("reset_password.html", token=token, email=email)

    if len(new_password) < 8:
        flash("New password must have at least 8 characters.", "error")
        return render_template("reset_password.html", token=token, email=email)

    token_row = get_db().execute(
        """
        SELECT rt.id, rt.user_id
        FROM reset_tokens rt
        JOIN users u ON u.id = rt.user_id
        WHERE u.email = ? AND rt.token = ? AND rt.used_at IS NULL
        ORDER BY rt.id DESC
        LIMIT 1
        """,
        (email, token),
    ).fetchone()

    if token_row is None:
        flash("Invalid reset token or email.", "error")
        return render_template("reset_password.html", token=token, email=email)

    db = get_db()
    db.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (generate_password_hash(new_password), token_row["user_id"]),
    )
    db.execute(
        "UPDATE reset_tokens SET used_at = CURRENT_TIMESTAMP WHERE id = ?",
        (token_row["id"],),
    )
    db.commit()

    flash("Password updated. You can now log in.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=Settings.HTTP_HOST, port=Settings.HTTP_PORT, debug=False)
