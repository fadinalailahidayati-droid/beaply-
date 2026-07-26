import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = Config.SECRET_KEY

# Folder upload
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

mysql = MySQL(app)

# ==================================================
# HALAMAN UTAMA
# ==================================================

@app.route("/", methods=["GET"])
def home():

    keyword = request.args.get("keyword")

    cur = mysql.connection.cursor()

    if keyword:

        cur.execute("""
            SELECT * FROM beasiswa
            WHERE NAMA_BEASISWA LIKE %s
        """, ("%" + keyword + "%",))

    else:

        cur.execute("SELECT * FROM beasiswa")

    data = cur.fetchall()

    cur.close()

    return render_template(
        "index.html",
        beasiswa=data,
        keyword=keyword
    )

# ==================================================
# DETAIL BEASISWA
# ==================================================

@app.route("/detail/<int:id>")
def detail(id):

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM beasiswa WHERE ID=%s",
        (id,)
    )

    data = cur.fetchone()

    cur.close()

    return render_template(
        "detail.html",
        data=data
    )

# ==================================================
# LOGIN
# ==================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT * FROM users
            WHERE EMAIL=%s AND PASSWORD=%s
        """, (email, password))

        user = cur.fetchone()

        cur.close()

        if user:

            session["login"] = True
            session["id"] = user["ID"]
            session["nama"] = user["NAMA"]
            session["email"] = user["EMAIL"]

            return redirect(url_for("dashboard"))

        else:

            return render_template(
                "login.html",
                error="Email atau Password Salah!"
            )

    return render_template("login.html")


# ==================================================
# REGISTER
# ==================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        nama = request.form["nama"]
        nim = request.form["nim"]
        prodi = request.form["prodi"]
        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()

        # ==========================
        # CEK EMAIL SUDAH ADA ATAU BELUM
        # ==========================
        cur.execute(
            "SELECT * FROM users WHERE EMAIL=%s",
            (email,)
        )

        cek = cur.fetchone()

        if cek:

            cur.close()

            return render_template(
                "register.html",
                error="Email sudah digunakan!"
            )

        cur.execute("""
            INSERT INTO users
            (NAMA, NIM, PRODI, EMAIL, PASSWORD)
            VALUES (%s,%s,%s,%s,%s)
        """, (nama, nim, prodi, email, password))

        mysql.connection.commit()

        cur.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ==================================================
# DASHBOARD
# ==================================================

@app.route("/dashboard")
def dashboard():

    if "login" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    # Total Beasiswa
    cur.execute("SELECT COUNT(*) AS total FROM beasiswa")
    total_beasiswa = cur.fetchone()["total"]

    # Total User
    cur.execute("SELECT COUNT(*) AS total FROM users")
    total_user = cur.fetchone()["total"]

    # Total Pendaftaran
    cur.execute("SELECT COUNT(*) AS total FROM pendaftaran")
    total_daftar = cur.fetchone()["total"]

    cur.close()

    return render_template(
        "dashboard.html",
        nama=session["nama"],
        total_beasiswa=total_beasiswa,
        total_user=total_user,
        total_daftar=total_daftar
    )

# ==================================================
# READ DATA BEASISWA
# ==================================================

@app.route("/beasiswa")
def beasiswa():

    if "login" not in session:
        return redirect(url_for("login"))

    keyword = request.args.get("keyword", "")
    page = request.args.get("page", 1, type=int)
    per_page = 5

    cur = mysql.connection.cursor()

    if keyword:

        cur.execute("""
            SELECT COUNT(*) AS total
            FROM beasiswa
            WHERE NAMA_BEASISWA LIKE %s
        """, ("%" + keyword + "%",))

        total = cur.fetchone()["total"]

        offset = (page - 1) * per_page

        cur.execute("""
            SELECT *
            FROM beasiswa
            WHERE NAMA_BEASISWA LIKE %s
            LIMIT %s OFFSET %s
        """, ("%" + keyword + "%", per_page, offset))

    else:

        cur.execute("SELECT COUNT(*) AS total FROM beasiswa")

        total = cur.fetchone()["total"]

        offset = (page - 1) * per_page

        cur.execute("""
            SELECT *
            FROM beasiswa
            LIMIT %s OFFSET %s
        """, (per_page, offset))

    data = cur.fetchall()

    cur.close()

    return render_template(
        "beasiswa.html",
        beasiswa=data,
        nama=session["nama"],
        page=page,
        keyword=keyword,
        total_page=(total + per_page - 1) // per_page
    )

# ==================================================
# CREATE BEASISWA
# ==================================================

@app.route("/beasiswa/tambah", methods=["GET", "POST"])
def tambah_beasiswa():

    if "login" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        nama = request.form["nama_beasiswa"]
        penyelenggara = request.form["penyelenggara"]
        kuota = request.form["kuota"]
        deadline = request.form["deadline"]
        deskripsi = request.form["deskripsi"]

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO beasiswa
            (NAMA_BEASISWA, PENYELENGGARA, KUOTA, DEADLINE, DESKRIPSI)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            nama,
            penyelenggara,
            kuota,
            deadline,
            deskripsi
        ))

        mysql.connection.commit()
        cur.close()

        return redirect(url_for("beasiswa"))

    return render_template("tambah_beasiswa.html")

# ==================================================
# DAFTAR BEASISWA
# ==================================================

@app.route("/pendaftaran/tambah/<int:id>")
def daftar_beasiswa(id):

    if "login" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    # cek apakah sudah pernah daftar
    cur.execute("""
    SELECT *
    FROM pendaftaran
    WHERE ID_USER=%s
    AND ID_BEASISWA=%s
    """, (session["id"], id))

    cek = cur.fetchone()

    if cek:
        cur.close()
        return redirect(url_for("pendaftaran"))

    # simpan pendaftaran
    cur.execute("""
    INSERT INTO pendaftaran
    (ID_USER, ID_BEASISWA, TANGGAL_DAFTAR, STATUS)
    VALUES (%s, %s, CURDATE(), 'Menunggu')
    """, (session["id"], id))

    mysql.connection.commit()

    cur.close()

    return redirect(url_for("pendaftaran"))

# ==================================================
# TAMBAH PENDAFTARAN MANUAL
# ==================================================

@app.route("/pendaftaran/tambah", methods=["GET", "POST"])
def tambah_pendaftaran():

    if "login" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    if request.method == "POST":

        id_beasiswa = request.form["id_beasiswa"]
        tanggal = request.form["tanggal"]
        status = request.form["status"]

        cur.execute("""
            INSERT INTO pendaftaran
            (ID_USER, ID_BEASISWA, TANGGAL_DAFTAR, STATUS)
            VALUES (%s,%s,%s,%s)
        """, (
            session["id"],
            id_beasiswa,
            tanggal,
            status
        ))

        mysql.connection.commit()

        cur.close()

        return redirect(url_for("pendaftaran"))

    cur.execute("SELECT ID, NAMA_BEASISWA FROM beasiswa")
    data = cur.fetchall()

    cur.close()

    return render_template(
        "tambah_pendaftaran.html",
        beasiswa=data
    )

# ==================================================
# UPDATE BEASISWA
# ==================================================

@app.route("/beasiswa/edit/<int:id>", methods=["GET","POST"])
def edit_beasiswa(id):

    if "login" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    if request.method == "POST":

        nama = request.form["nama_beasiswa"]
        penyelenggara = request.form["penyelenggara"]
        kuota = request.form["kuota"]
        deadline = request.form["deadline"]
        deskripsi = request.form["deskripsi"]

        cur.execute("""
            UPDATE beasiswa
            SET
                NAMA_BEASISWA=%s,
                PENYELENGGARA=%s,
                KUOTA=%s,
                DEADLINE=%s,
                DESKRIPSI=%s
            WHERE ID=%s
        """,(nama,penyelenggara,kuota,deadline,deskripsi,id))

        mysql.connection.commit()

        cur.close()

        return redirect(url_for("beasiswa"))

    cur.execute("SELECT * FROM beasiswa WHERE ID=%s",(id,))
    data = cur.fetchone()

    cur.close()

    return render_template(
        "edit_beasiswa.html",
        data=data
    )


# ==================================================
# DELETE BEASISWA
# ==================================================

@app.route("/beasiswa/hapus/<int:id>")
def hapus_beasiswa(id):

    if "login" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM beasiswa WHERE ID=%s",(id,))

    mysql.connection.commit()

    cur.close()

    return redirect(url_for("beasiswa"))


# ==================================================
# MENU LAIN
# ==================================================

# ==================================================
# DATA PENDAFTARAN
# ==================================================

@app.route("/pendaftaran")
def pendaftaran():

    if "login" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
            p.ID,
            b.NAMA_BEASISWA,
            p.TANGGAL_DAFTAR,
            p.STATUS
        FROM pendaftaran p
        JOIN beasiswa b
        ON p.ID_BEASISWA = b.ID
        WHERE p.ID_USER = %s
        ORDER BY p.ID DESC
    """, (session["id"],))

    data = cur.fetchall()

    cur.close()

    return render_template(
        "pendaftaran.html",
        pendaftaran=data,
        nama=session["nama"]
    )

@app.route("/dokumen", methods=["GET","POST"])
def dokumen():

    if "login" not in session:
        return redirect("/login")

    if request.method == "POST":

        file = request.files["file"]

        if file.filename != "":

            nama_file = secure_filename(file.filename)

            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    nama_file
                )
            )

            return render_template(
                "dokumen.html",
                sukses=True
            )

    return render_template("dokumen.html")

@app.route("/laporan")
def laporan():

    if "login" not in session:
        return redirect("/login")

    cur=mysql.connection.cursor()

    cur.execute("""
    SELECT
    STATUS,
    COUNT(*) jumlah
    FROM pendaftaran
    GROUP BY STATUS
    """)

    data=cur.fetchall()

    cur.close()

    return render_template(
        "laporan.html",
        laporan=data
    )

@app.route("/profil")
def profil():

    if "login" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM users WHERE ID=%s",
        (session["id"],)
    )

    user = cur.fetchone()

    cur.close()

    return render_template(
        "profil.html",
        user=user
    )

# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ==================================================
# TEST DATABASE
# ==================================================

@app.route("/testdb")
def testdb():

    try:

        cur = mysql.connection.cursor()

        cur.execute("SELECT 1")

        cur.close()

        return "✅ Koneksi Database Berhasil"

    except Exception as e:

        return f"❌ Error : {e}"


# ==================================================
# RUN APP
# ==================================================

if __name__ == "__main__":
    app.run(debug=True)