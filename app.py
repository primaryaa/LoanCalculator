import streamlit as pd_st
import pandas as pd
import io
from datetime import datetime
from fpdf import FPDF

# Konfigurasi Halaman Streamlit
pd_st.set_page_config(
    page_title="Kalkulator Kredit",
    page_icon="🏦",
    layout="wide"
)

# Custom CSS untuk styling ala perbankan profesional
pd_st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #003366;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 0.6rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #002244;
        color: white;
    }
    .info-box {
        background-color: #e6f0fa;
        padding: 18px;
        border-left: 6px solid #003366;
        border-radius: 6px;
        margin-top: 10px;
        margin-bottom: 20px;
        font-size: 14px;
        color: #002244;
        line-height: 1.5;
    }
    .disclaimer {
        font-size: 12px;
        color: #666666;
        font-style: italic;
        margin-top: 15px;
        text-align: center;
    }
    .section-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #003366;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Mapping nama bulan Indonesia
nama_bulan_indo = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

def format_rupiah(angka):
    """Format angka menjadi Rupiah Indonesia (Rp X.XXX.XXX)"""
    try:
        return f"Rp {int(round(angka)):,}".replace(",", ".")
    except:
        return "Rp 0"

def hitung_anuitas(plafon, rate_thn, tenor, tanggal_mulai):
    r = (rate_thn / 100) / 12
    n = tenor
    if r == 0:
        angsuran = plafon / n
    else:
        angsuran = plafon * (r * (1 + r)**n) / ((1 + r)**n - 1)
    
    data = []
    outstanding = plafon
    total_pokok = 0
    total_bunga = 0
    
    curr_date = tanggal_mulai
    for bulan in range(1, tenor + 1):
        if curr_date.month == 12:
            curr_date = curr_date.replace(year=curr_date.year + 1, month=1)
        else:
            try:
                curr_date = curr_date.replace(month=curr_date.month + 1)
            except ValueError:
                next_month = curr_date.month + 1 if curr_date.month < 12 else 1
                next_year = curr_date.year if curr_date.month < 12 else curr_date.year + 1
                if next_month == 2:
                    day = 29 if next_year % 4 == 0 and (next_year % 100 != 0 or next_year % 400 == 0) else 28
                elif next_month in [4, 6, 9, 11]:
                    day = 30
                else:
                    day = 31
                curr_date = curr_date.replace(year=next_year, month=next_month, day=day)

        if r == 0:
            bunga = 0
            pokok = angsuran
        else:
            bunga = outstanding * r
            pokok = angsuran - bunga
        
        if bulan == tenor:
            pokok = outstanding
            angsuran = pokok + bunga
            
        outstanding_akhir = outstanding - pokok
        if outstanding_akhir < 0:
            outstanding_akhir = 0
            
        total_pokok += pokok
        total_bunga += bunga
        
        label_bulan = f"{nama_bulan_indo[curr_date.month]} {curr_date.year}"
        
        data.append({
            "Bulan Ke": bulan,
            "Bulan": label_bulan,
            "Jatuh Tempo": curr_date.strftime("%d-%m-%Y"),
            "Angsuran": round(angsuran, 2),
            "Pokok": round(pokok, 2),
            "Bunga": round(bunga, 2),
            "Outstanding": round(outstanding_akhir, 2)
        })
        outstanding = outstanding_akhir
        
    df = pd.DataFrame(data)
    return df, total_pokok, total_bunga, df.iloc[0]['Angsuran'], df.iloc[-1]['Angsuran']

def hitung_principal_equal(plafon, rate_thn, tenor, tanggal_mulai):
    r = (rate_thn / 100) / 12
    pokok_bulanan = plafon / tenor if tenor > 0 else 0
    
    data = []
    outstanding = plafon
    total_pokok = 0
    total_bunga = 0
    
    curr_date = tanggal_mulai
    for bulan in range(1, tenor + 1):
        if curr_date.month == 12:
            curr_date = curr_date.replace(year=curr_date.year + 1, month=1)
        else:
            try:
                curr_date = curr_date.replace(month=curr_date.month + 1)
            except ValueError:
                next_month = curr_date.month + 1 if curr_date.month < 12 else 1
                next_year = curr_date.year if curr_date.month < 12 else curr_date.year + 1
                if next_month == 2:
                    day = 29 if next_year % 4 == 0 and (next_year % 100 != 0 or next_year % 400 == 0) else 28
                elif next_month in [4, 6, 9, 11]:
                    day = 30
                else:
                    day = 31
                curr_date = curr_date.replace(year=next_year, month=next_month, day=day)

        bunga = outstanding * r
        pokok = pokok_bulanan
        
        if bulan == tenor:
            pokok = outstanding
            
        angsuran = pokok + bunga
        outstanding_akhir = outstanding - pokok
        if outstanding_akhir < 0:
            outstanding_akhir = 0
            
        total_pokok += pokok
        total_bunga += bunga
        
        label_bulan = f"{nama_bulan_indo[curr_date.month]} {curr_date.year}"
        
        data.append({
            "Bulan Ke": bulan,
            "Bulan": label_bulan,
            "Jatuh Tempo": curr_date.strftime("%d-%m-%Y"),
            "Angsuran": round(angsuran, 2),
            "Pokok": round(pokok, 2),
            "Bunga": round(bunga, 2),
            "Outstanding": round(outstanding_akhir, 2)
        })
        outstanding = outstanding_akhir
        
    df = pd.DataFrame(data)
    return df, total_pokok, total_bunga, df.iloc[0]['Angsuran'], df.iloc[-1]['Angsuran']

def hitung_principal_bullet(plafon, rate_thn, tenor, tanggal_mulai):
    r = (rate_thn / 100) / 12
    bunga_bulanan = plafon * r
    
    data = []
    total_pokok = plafon
    total_bunga = bunga_bulanan * tenor
    
    curr_date = tanggal_mulai
    for bulan in range(1, tenor + 1):
        if curr_date.month == 12:
            curr_date = curr_date.replace(year=curr_date.year + 1, month=1)
        else:
            try:
                curr_date = curr_date.replace(month=curr_date.month + 1)
            except ValueError:
                next_month = curr_date.month + 1 if curr_date.month < 12 else 1
                next_year = curr_date.year if curr_date.month < 12 else curr_date.year + 1
                if next_month == 2:
                    day = 29 if next_year % 4 == 0 and (next_year % 100 != 0 or next_year % 400 == 0) else 28
                elif next_month in [4, 6, 9, 11]:
                    day = 30
                else:
                    day = 31
                curr_date = curr_date.replace(year=next_year, month=next_month, day=day)

        if bulan < tenor:
            pokok = 0
            angsuran = bunga_bulanan
            outstanding = plafon
        else:
            pokok = plafon
            angsuran = pokok + bunga_bulanan
            outstanding = 0
            
        label_bulan = f"{nama_bulan_indo[curr_date.month]} {curr_date.year}"
        
        data.append({
            "Bulan Ke": bulan,
            "Bulan": label_bulan,
            "Jatuh Tempo": curr_date.strftime("%d-%m-%Y"),
            "Pembayaran Pokok": round(pokok, 2),
            "Bunga": round(bunga_bulanan, 2),
            "Total Pembayaran": round(angsuran, 2),
            "Outstanding": round(outstanding, 2)
        })
        
    df = pd.DataFrame(data)
    return df, total_pokok, total_bunga, df.iloc[0]['Total Pembayaran'], df.iloc[-1]['Total Pembayaran']

def hitung_rekening_koran(plafon, rate_thn, periode_hari, pemakaian_rata, tanggal_mulai):
    data = []
    total_bunga = 0
    
    jumlah_bulan = max(1, periode_hari // 30)
    hari_per_bulan = periode_hari // jumlah_bulan
    
    saldo_berjalan = pemakaian_rata
    curr_date = tanggal_mulai
    for bulan in range(1, jumlah_bulan + 1):
        if curr_date.month == 12:
            curr_date = curr_date.replace(year=curr_date.year + 1, month=1)
        else:
            try:
                curr_date = curr_date.replace(month=curr_date.month + 1)
            except ValueError:
                next_month = curr_date.month + 1 if curr_date.month < 12 else 1
                next_year = curr_date.year if curr_date.month < 12 else curr_date.year + 1
                if next_month == 2:
                    day = 29 if next_year % 4 == 0 and (next_year % 100 != 0 or next_year % 400 == 0) else 28
                elif next_month in [4, 6, 9, 11]:
                    day = 30
                else:
                    day = 31
                curr_date = curr_date.replace(year=next_year, month=next_month, day=day)

        saldo_awal = saldo_berjalan
        penarikan = 0
        setoran = 0
        saldo_akhir = saldo_awal
        
        bunga = saldo_akhir * (rate_thn / 100) * (hari_per_bulan / 360)
        total_bunga += bunga
        
        label_bulan = f"{nama_bulan_indo[curr_date.month]} {curr_date.year}"
        
        data.append({
            "Bulan Ke": bulan,
            "Bulan": label_bulan,
            "Saldo Awal": round(saldo_awal, 2),
            "Penarikan": round(penarikan, 2),
            "Pembayaran": round(setoran, 2),
            "Saldo Akhir": round(saldo_akhir, 2),
            "Hari": hari_per_bulan,
            "Bunga": round(bunga, 2)
        })
        
    df = pd.DataFrame(data)
    return df, pemakaian_rata, total_bunga

def create_excel_fully_linked(df, jenis_kredit, info_dict):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        summary_data = {
            "Parameter": [
                "Jenis Kredit", "Plafon Kredit", "Tenor (Bulan)", "Suku Bunga (% p.a)",
                "Tanggal Mulai", "Total Pokok", "Total Bunga", "Total Pembayaran"
            ],
            "Nilai": [
                jenis_kredit, 
                info_dict['plafon'], 
                info_dict['tenor'], 
                info_dict['rate'], 
                info_dict['tanggal_mulai'].strftime("%d-%m-%Y"),
                info_dict['total_pokok'], 
                info_dict['total_bunga'], 
                info_dict['total_pembayaran']
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Ringkasan', index=False)
        df.to_excel(writer, sheet_name='Tabel Angsuran', index=False)
            
    return output.getvalue()

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 12)
        self.cell(0, 6, "SIMULASI ANGSURAN", 0, 1, 'C')
        self.set_font("Arial", '', 9)
        self.cell(0, 5, "Nominal yang ditampilkan hanya untuk keperluan simulasi dan bukan merupakan nominal kredit sebenarnya", 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f"Halaman {self.page_no()} | Dokumen Simulasi Internal RM SME BRI", 0, 0, 'C')

def create_pdf(df, jenis_kredit, info_dict):
    pdf = PDF()
    pdf.add_page(orientation='P', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, "RINGKASAN SIMULASI KREDIT", 0, 1, 'L')
    pdf.set_font("Arial", '', 9)
    
    summary_items = [
        ("Jenis Kredit:", str(jenis_kredit)),
        ("Plafon Kredit:", format_rupiah(info_dict['plafon'])),
        ("Tenor:", f"{info_dict['tenor']} Bulan"),
        ("Suku Bunga:", f"{info_dict['rate']}% p.a"),
        ("Tanggal Mulai:", info_dict['tanggal_mulai'].strftime("%d-%m-%Y")),
        ("Total Pokok:", format_rupiah(info_dict['total_pokok'])),
        ("Total Bunga:", format_rupiah(info_dict['total_bunga'])),
        ("Total Pembayaran:", format_rupiah(info_dict['total_pembayaran']))
    ]
    
    for label, val in summary_items:
        pdf.cell(45, 5, label, 0, 0)
        pdf.cell(0, 5, val, 0, 1)
    
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, "TABEL ANGSURAN LENGKAP", 0, 1, 'L')
    pdf.set_font("Arial", 'B', 8)
    
    cols = list(df.columns)
    if len(cols) == 7:
        col_widths = [18, 28, 26, 32, 29, 27, 30]
    else:
        col_widths = [18] + [172 / (len(cols) - 1)] * (len(cols) - 1)
    
    for i, col in enumerate(cols):
        pdf.cell(col_widths[i], 6, str(col), 1, 0, 'C')
    pdf.ln()
    
    pdf.set_font("Arial", '', 8)
    for index, row in df.iterrows():
        for i, col in enumerate(cols):
            val = row[col]
            if isinstance(val, (int, float)) and col not in ["Bulan Ke", "Bulan", "Hari"]:
                val_str = f"{val:,.0f}"
            else:
                val_str = str(val)
            pdf.cell(col_widths[i], 5, val_str, 1, 0, 'C')
        pdf.ln()
        
    return bytes(pdf.output())

# --- HEADER APLIKASI UTAMA ---
pd_st.title("KALKULATOR KREDIT")
pd_st.markdown("**Simulasi Kredit & Tabel Angsuran**")
pd_st.markdown("---")

# --- TOMBOL BANTUAN (HELP) ---
with pd_st.expander("❓ Bantuan & Panduan Penggunaan Aplikasi", expanded=False):
    pd_st.markdown("""
    ### 📖 Panduan Singkat Penggunaan Loan Calculator RM SME:
    1. **Pilih Jenis Fasilitas Kredit**: Tentukan skema pembiayaan yang diinginkan (*Principal & Interest Equal*, *Principal Equal*, *Principal Bullet*, atau *KMK Rekening Koran*).
    2. **Tentukan Tanggal Mulai**: Masuk tanggal awal dimulainya fasilitas pinjaman agar jadwal jatuh tempo bulanan terhitung secara otomatis.
    3. **Masukkan Data Finansial**: 
       - Masukkan nominal **Plafon Kredit** (Rp).
       - Masukkan **Tenor** (dalam Bulan) atau **Periode Hari** (untuk Rekening Koran).
       - Masukkan besar **Suku Bunga** (% per tahun).
    4. **Hitung Simulasi**: Klik tombol **"HITUNG SIMULASI"** untuk memproses tabel angsuran dan ringkasan pembiayaan.
    5. **Unduh Laporan**: Gunakan tombol unduh yang tersedia di bagian bawah untuk mendownload file laporan dalam format **Excel (.xlsx)** atau **PDF Summary**.
    """)

# --- PARAMETER INPUT DI ATAS ---
pd_st.markdown("<div class='section-header'>📋 1. PILIH FASILITAS & PARAMETER KREDIT</div>", unsafe_allow_html=True)

col_input_1, col_input_2 = pd_st.columns([1, 1])

with col_input_1:
    jenis_fasilitas = pd_st.selectbox(
        "Jenis Fasilitas Kredit",
        [
            "Principal & Interest Equal",
            "Principal Equal",
            "Principal Bullet",
            "KMK Rekening Koran (RC)"
        ]
    )

with col_input_2:
    tanggal_mulai = pd_st.date_input("Tanggal Mulai Pinjaman", value=datetime.today())

explanations_detail = {
    "Principal & Interest Equal": """
    <b>Principal & Interest Equal (Anuitas / Angsuran Tetap)</b><br>
    • <b>Penjelasan:</b> Total angsuran per bulan yang dibayarkan debitur bernilai <b>tetap/konstan</b> dari bulan pertama hingga akhir tenor.<br>
    • <b>Komposisi:</b> Porsi bunga pada awal periode bernilai besar dan berangsur mengecil, sebaliknya porsi pokok pinjaman pada awal periode kecil dan berangsur semakin besar di akhir.<br>
    • <b>Penggunaan:</b> Cocok untuk nasabah SME yang memerlukan kepastian cash flow bulanan yang stabil dan terencana.
    """,
    "Principal Equal": """
    <b>Principal Equal (Pokok Tetap / Angsuran Menurun)</b><br>
    • <b>Penjelasan:</b> Pembayaran pokok pinjaman setiap bulan ditetapkan dalam jumlah yang <b>sama besar</b>.<br>
    • <b>Komposisi:</b> Karena pokok berkurang secara konstan, beban bunga dihitung dari sisa *outstanding* sehingga nilai bunga bulanan semakin menurun. Akibatnya, total angsuran bulanan akan <b>semakin menurun</b> dari bulan ke bulan.<br>
    • <b>Penggunaan:</b> Sangat ideal untuk struktur kredit investasi atau modal kerja dengan pendekatan penurunan risiko pembiayaan secara cepat (*sliding rate*).
    """,
    "Principal Bullet": """
    <b>Principal Bullet (Pokok Dibayar Sekaligus di Akhir)</b><br>
    • <b>Penjelasan:</b> Pokok pinjaman <b>tidak dicicil setiap bulan</b> (nilai pokok = Rp 0 selama periode berjalan), melainkan dilunasi sekaligus secara penuh pada saat jatuh tempo akhir tenor.<br>
    • <b>Komposisi:</b> Selama masa tenor, kewajiban pembayaran debitur setiap bulan hanya berupa beban <b>bunga pinjaman saja</b>.<br>
    • <b>Penggunaan:</b> Digunakan untuk fasilitas pembiayaan dengan skema project-based, trade finance, atau siklus bisnis tertentu di mana pelunasan bersumber dari hasil penjualan/termin proyek akhir.
    """,
    "KMK Rekening Koran (RC)": """
    <b>KMK Rekening Koran (RC) — Fasilitas Revolving</b><br>
    • <b>Penjelasan:</b> Fasilitas kredit modal kerja berputar di mana penarikan dan pelunasan dapat dilakukan fleksibel sewaktu-waktu oleh debitur selama tidak melebihi plafon.<br>
    • <b>Komposisi:</b> Perhitungan bunga tidak menggunakan skema cicilan pokok bulanan, melainkan dihitung berdasarkan saldo *outstanding* / pemakaian aktual harian dikali suku bunga dibagi basis 360 hari.<br>
    • <b>Penggunaan:</b> Cocok untuk pembiayaan modal kerja musiman atau perputaran stok barang dagang/piutang usaha.
    """
}

pd_st.markdown(f"<div class='info-box'>{explanations_detail[jenis_fasilitas]}</div>", unsafe_allow_html=True)

pd_st.markdown("<div class='section-header'>⚙️ 2. MASUKAN DATA FINANSIAL</div>", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = pd_st.columns(3)

if jenis_fasilitas != "KMK Rekening Koran (RC)":
    with col_f1:
        plafon = pd_st.number_input("Plafon Kredit (Rp)", min_value=0.0, value=0.0, step=10000000.0, format="%.0f")
    with col_f2:
        tenor = pd_st.number_input("Tenor (Bulan)", min_value=0, value=0, step=1)
    with col_f3:
        rate = pd_st.number_input("Suku Bunga (% per tahun)", min_value=0.0, value=0.0, step=0.25, format="%.2f")
    pemakaian_rata = 0.0
else:
    with col_f1:
        plafon = pd_st.number_input("Plafon KMK (Rp)", min_value=0.0, value=0.0, step=10000000.0, format="%.0f")
    with col_f2:
        tenor = pd_st.number_input("Periode Simulasi (Hari)", min_value=0, value=0, step=30)
    with col_f3:
        rate = pd_st.number_input("Suku Bunga (% per tahun)", min_value=0.0, value=0.0, step=0.25, format="%.2f")
    
    pemakaian_rata = pd_st.number_input("Rata-rata Pemakaian/Outstanding (Rp)", min_value=0.0, value=0.0, step=10000000.0, format="%.0f")

pd_st.markdown("<br>", unsafe_allow_html=True)

col_btn1, col_btn2, col_col3 = pd_st.columns([1, 1, 2])
with col_btn1:
    hitung_clicked = pd_st.button("HITUNG SIMULASI")

input_valid = True
if plafon <= 0 or rate <= 0 or (tenor <= 0):
    input_valid = False

if hitung_clicked and not input_valid:
    pd_st.error("⚠️ Validasi Gagal: Plafon, Suku Bunga, dan Tenor/Periode harus bernilai lebih besar dari 0 (tidak boleh kosong atau 0).")

if input_valid:
    pd_st.markdown("---")
    pd_st.markdown("<div class='section-header'>📊 3. RINGKASAN & TABEL SIMULASI KREDIT</div>", unsafe_allow_html=True)
    
    if jenis_fasilitas == "Principal & Interest Equal":
        df, total_pokok, total_bunga, angsuran_pertama, angsuran_terakhir = hitung_anuitas(plafon, rate, tenor, tanggal_mulai)
        total_pembayaran = total_pokok + total_bunga
        
        col1, col2, col3, col4 = pd_st.columns(4)
        col1.metric("Plafon Kredit", format_rupiah(plafon))
        col2.metric("Tenor", f"{tenor} Bulan")
        col3.metric("Suku Bunga", f"{rate}% p.a")
        col4.metric("Angsuran Pertama", format_rupiah(angsuran_pertama))
        
        col5, col6, col7, col8 = pd_st.columns(4)
        col5.metric("Angsuran Terakhir", format_rupiah(angsuran_terakhir))
        col6.metric("Total Pokok", format_rupiah(total_pokok))
        col7.metric("Total Bunga", format_rupiah(total_bunga))
        col8.metric("Total Pembayaran", format_rupiah(total_pembayaran))

    elif jenis_fasilitas == "Principal Equal":
        df, total_pokok, total_bunga, angsuran_pertama, angsuran_terakhir = hitung_principal_equal(plafon, rate, tenor, tanggal_mulai)
        total_pembayaran = total_pokok + total_bunga
        
        col1, col2, col3, col4 = pd_st.columns(4)
        col1.metric("Plafon Kredit", format_rupiah(plafon))
        col2.metric("Tenor", f"{tenor} Bulan")
        col3.metric("Suku Bunga", f"{rate}% p.a")
        col4.metric("Angsuran Pertama", format_rupiah(angsuran_pertama))
        
        col5, col6, col7, col8 = pd_st.columns(4)
        col5.metric("Angsuran Terakhir", format_rupiah(angsuran_terakhir))
        col6.metric("Total Pokok", format_rupiah(total_pokok))
        col7.metric("Total Bunga", format_rupiah(total_bunga))
        col8.metric("Total Pembayaran", format_rupiah(total_pembayaran))

    elif jenis_fasilitas == "Principal Bullet":
        df, total_pokok, total_bunga, angsuran_pertama, angsuran_terakhir = hitung_principal_bullet(plafon, rate, tenor, tanggal_mulai)
        total_pembayaran = total_pokok + total_bunga
        
        col1, col2, col3, col4 = pd_st.columns(4)
        col1.metric("Plafon Kredit", format_rupiah(plafon))
        col2.metric("Tenor", f"{tenor} Bulan")
        col3.metric("Suku Bunga", f"{rate}% p.a")
        col4.metric("Pembayaran Bulan 1", format_rupiah(angsuran_pertama))
        
        col5, col6, col7, col8 = pd_st.columns(4)
        col5.metric("Pembayaran Bulan Terakhir", format_rupiah(angsuran_terakhir))
        col6.metric("Total Pokok", format_rupiah(total_pokok))
        col7.metric("Total Bunga", format_rupiah(total_bunga))
        col8.metric("Total Pembayaran", format_rupiah(total_pembayaran))

    else:
        df, rata_pakai, total_bunga = hitung_rekening_koran(plafon, rate, tenor, pemakaian_rata, tanggal_mulai)
        total_pembayaran = total_bunga
        total_pokok = pemakaian_rata
        
        col1, col2, col3, col4 = pd_st.columns(4)
        col1.metric("Plafon KMK", format_rupiah(plafon))
        col2.metric("Rata-rata Pemakaian", format_rupiah(pemakaian_rata))
        col3.metric("Suku Bunga", f"{rate}% p.a (Basis 360)")
        col4.metric("Total Bunga RC", format_rupiah(total_bunga))

    pd_st.markdown("<br>", unsafe_allow_html=True)
    pd_st.subheader(f"Tabel Angsuran / Simulasi: {jenis_fasilitas}")

    df_display = df.copy()
    for col in df_display.columns:
        if col not in ["Bulan Ke", "Bulan", "Jatuh Tempo", "Hari"]:
            df_display[col] = df_display[col].apply(lambda x: format_rupiah(x))

    pd_st.dataframe(df_display, use_container_width=True)

    pd_st.markdown("---")
    col_d1, col_d2 = pd_st.columns(2)

    info_dict = {
        'plafon': plafon,
        'tenor': tenor if jenis_fasilitas != "KMK Rekening Koran (RC)" else tenor // 30,
        'rate': rate,
        'tanggal_mulai': tanggal_mulai,
        'total_pokok': total_pokok,
        'total_bunga': total_bunga,
        'total_pembayaran': total_pembayaran
    }

    excel_data = create_excel_fully_linked(df, jenis_fasilitas, info_dict)
    with col_d1:
        pd_st.download_button(
            label="📥 Download Excel (.xlsx)",
            data=excel_data,
            file_name=f"Simulasi_Kredit_{jenis_fasilitas.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    pdf_data = create_pdf(df, jenis_fasilitas, info_dict)
    with col_d2:
        pd_st.download_button(
            label="📥 Download PDF Summary",
            data=pdf_data,
            file_name=f"Simulasi_Kredit_{jenis_fasilitas.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )

pd_st.markdown(
    "<div class='disclaimer'>Catatan: Simulasi ini merupakan kalkulator perhitungan awal dan bukan penetapan final struktur kredit BRI.<br><b>Made by: Primarya</b></div>",
    unsafe_allow_html=True
)