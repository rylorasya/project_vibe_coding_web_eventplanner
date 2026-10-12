"""Kalilla Event Planner: website Flask sekaligus contoh materi dasar Python."""
from urllib.parse import quote

from flask import Flask, render_template, request

app = Flask(__name__)

# Variabel dan tipe data: str, int, float, dan bool.
NAMA_BRAND = "Kalilla Event Planner"
SLOGAN = "Create Unforgetable Moment"
NOMOR_WA = "6282137048586"
NOMOR_TAMPIL = "082137048586"
INSTAGRAM = "kalillaeventplanner"
EMAIL = "officekalilla@gmail.com"
MIN_TAMU = 50
MAX_TAMU = 1000
BUKA_PEMESANAN = True

# Pilihan layanan.
SERVICES = [
    {
        "nama": "Biro Tour & Gathering",
        "ikon": "✦",
        "deskripsi": "Paket tour dan gathering yang dirancang seru, nyaman, dan berkesan untuk rombongan.",
    },
    {
        "nama": "Consultan trip",
        "ikon": "♡",
        "deskripsi": "Konsultasi perjalanan untuk membantu menyusun rencana trip sesuai kebutuhan dan tujuanmu.",
    },
    {
        "nama": "Event Organizer",
        "ikon": "✳",
        "deskripsi": "Perencanaan dan koordinasi acara dari persiapan hingga hari pelaksanaan.",
    },
]

# Harga per orang sesuai foto Harga 1 dan Harga 2.
PACKAGES = [
    {
        "nama": "Outbound / Tubing Kemuning + Lawu Park",
        "harga_per_pax": 370_000,
    },
    {
        "nama": "Adventure Jeep Kemuning + Lawu Park",
        "harga_per_pax": 440_000,
    },
    {
        "nama": "Malioboro + Picnic",
        "harga_per_pax": 310_000,
    },
    {
        "nama": "On The Rock + Picnic",
        "harga_per_pax": 350_000,
    },
]

PORTFOLIO = [
    {
        "file": "/static/images/biro-tour.jpeg",
        "judul": "Perjalanan dengan Biro Tour",
        "kategori": "Biro Tour & Gathering",
    },
    {
        "file": "/static/images/gathering.jpeg",
        "judul": "Gathering Bersama",
        "kategori": "Biro Tour & Gathering",
    },
    {
        "file": "/static/images/trip-2.jpeg",
        "judul": "Serunya Arung Jeram",
        "kategori": "Consultan trip",
    },
    {
        "file": "/static/images/trip-1.jpeg",
        "judul": "Petualangan Jeep",
        "kategori": "Consultan trip",
    },
    {
        "file": "/static/images/event-organizer-2.png",
        "judul": "Kebersamaan dalam Acara",
        "kategori": "Event Organizer",
    },
    {
        "file": "/static/images/event-organizer-4.png",
        "judul": "Gathering Penuh Kehangatan",
        "kategori": "Event Organizer",
    },
]


def format_rupiah(angka):
    """Ubah angka menjadi format mata uang Indonesia."""
    return "Rp " + f"{int(angka):,}".replace(",", ".")


def cari_layanan(nama_layanan):
    """Looping untuk mencari layanan di dalam list."""
    for layanan in SERVICES:
        if layanan["nama"] == nama_layanan:
            return layanan
    return None


def cari_paket(nama_paket):
    """Looping untuk mencari paket perjalanan berdasarkan nama."""
    for paket in PACKAGES:
        if paket["nama"] == nama_paket:
            return paket
    return None


def bandingkan_paket(nama_paket_a, nama_paket_b, jumlah_tamu):
    """Bandingkan total dua paket untuk jumlah peserta yang sama."""
    paket_a = cari_paket(nama_paket_a)
    paket_b = cari_paket(nama_paket_b)
    if paket_a is None or paket_b is None:
        return None
    if paket_a["nama"] == paket_b["nama"]:
        return None

    total_a = paket_a["harga_per_pax"] * jumlah_tamu
    total_b = paket_b["harga_per_pax"] * jumlah_tamu
    selisih = abs(total_a - total_b)

    if total_a < total_b:
        lebih_hemat = paket_a["nama"]
    elif total_b < total_a:
        lebih_hemat = paket_b["nama"]
    else:
        lebih_hemat = "Kedua paket memiliki total yang sama"

    return {
        "paket_a": paket_a["nama"],
        "harga_per_pax_a": format_rupiah(paket_a["harga_per_pax"]),
        "total_a": format_rupiah(total_a),
        "paket_b": paket_b["nama"],
        "harga_per_pax_b": format_rupiah(paket_b["harga_per_pax"]),
        "total_b": format_rupiah(total_b),
        "tamu": jumlah_tamu,
        "selisih": format_rupiah(selisih),
        "lebih_hemat": lebih_hemat,
    }


def validasi_input(nama, layanan, paket_a, paket_b, tamu_teks):
    """Periksa nama, layanan, dua paket berbeda, dan jumlah peserta."""
    errors = []

    if not nama.strip():
        errors.append("Nama wajib diisi.")
    if cari_layanan(layanan) is None:
        errors.append("Pilih salah satu layanan.")
    if cari_paket(paket_a) is None:
        errors.append("Pilih paket pertama.")
    if cari_paket(paket_b) is None:
        errors.append("Pilih paket kedua.")
    if paket_a and paket_a == paket_b:
        errors.append("Pilih dua paket yang berbeda untuk dibandingkan.")

    if not tamu_teks.isdigit():
        errors.append("Jumlah peserta harus berupa angka.")
        jumlah_tamu = 0
    else:
        jumlah_tamu = int(tamu_teks)
        if jumlah_tamu < MIN_TAMU or jumlah_tamu > MAX_TAMU:
            errors.append(
                f"Jumlah peserta harus antara {MIN_TAMU} dan {MAX_TAMU}."
            )

    return errors, jumlah_tamu


def buat_link_wa(pesan):
    """Encode pesan lalu tambahkan ke link WhatsApp."""
    return f"https://wa.me/{NOMOR_WA}?text={quote(pesan)}"


@app.route("/", methods=["GET", "POST"])
def index():
    errors = []
    hasil = None
    link_wa = None
    form = {
        "nama": "",
        "layanan": "",
        "paket_a": "",
        "paket_b": "",
        "tamu": "",
    }

    if request.method == "POST" and BUKA_PEMESANAN:
        form["nama"] = request.form.get("nama", "")
        form["layanan"] = request.form.get("layanan", "")
        form["paket_a"] = request.form.get("paket_a", "")
        form["paket_b"] = request.form.get("paket_b", "")
        form["tamu"] = request.form.get("tamu", "")

        errors, jumlah_tamu = validasi_input(
            form["nama"],
            form["layanan"],
            form["paket_a"],
            form["paket_b"],
            form["tamu"],
        )
        if not errors:
            hasil = bandingkan_paket(
                form["paket_a"], form["paket_b"], jumlah_tamu
            )
            link_wa = buat_link_wa(
                f"Halo {NAMA_BRAND}, saya {form['nama']}. "
                f"Saya ingin konsultasi layanan {form['layanan']} untuk "
                f"{jumlah_tamu} pax. Mohon informasi tentang paket "
                f"{hasil['paket_a']} (estimasi {hasil['total_a']}) dan "
                f"{hasil['paket_b']} (estimasi {hasil['total_b']})."
            )

    return render_template(
        "index.html",
        nama=NAMA_BRAND,
        slogan=SLOGAN,
        services=SERVICES,
        packages=PACKAGES,
        portfolio=PORTFOLIO,
        nomor=NOMOR_TAMPIL,
        wa_number=NOMOR_WA,
        instagram=INSTAGRAM,
        email=EMAIL,
        wa_contact=buat_link_wa(
            f"Halo {NAMA_BRAND}, saya ingin bertanya tentang layanan event."
        ),
        min_tamu=MIN_TAMU,
        max_tamu=MAX_TAMU,
        format_rupiah=format_rupiah,
        errors=errors,
        hasil=hasil,
        link_wa=link_wa,
        form=form,
    )


if __name__ == "__main__":
    app.run(debug=True)
