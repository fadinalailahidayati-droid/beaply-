// ===============================
// Beaply - Main JavaScript
// ===============================

// Cek apakah JavaScript berhasil berjalan
console.log("Beaply berhasil dijalankan!");

// ===============================
// Konfirmasi Hapus
// ===============================
function konfirmasiHapus() {
    return confirm("Apakah Anda yakin ingin menghapus data ini?");
}

// ===============================
// Show / Hide Password
// ===============================
function showPassword() {

    const password = document.getElementById("password");

    if (!password) return;

    if (password.type === "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }

}

// ===============================
// Cari Beasiswa
// ===============================
function cariBeasiswa() {

    const input = document.getElementById("searchInput");

    if (!input) return;

    const keyword = input.value.trim();

    if (keyword === "") {
        alert("Silakan masukkan kata kunci.");
        return;
    }

    alert("Mencari beasiswa: " + keyword);

    // Nanti diganti mengambil data dari database

}

// ===============================
// Daftar Sekarang
// ===============================
function daftarSekarang() {

    alert("Silakan login terlebih dahulu.");

}

// ===============================
// Detail Beasiswa
// ===============================
function lihatDetail(nama) {

    alert("Membuka detail " + nama);

}