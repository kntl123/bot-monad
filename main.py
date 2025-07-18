import requests
import json
import os
from dotenv import load_dotenv
import time # Untuk jeda waktu

load_dotenv() # Muat variabel lingkungan

# --- Konfigurasi Penting (Harus Anda Isi di file .env) ---
# Alamat dompet Anda yang akan digunakan untuk swap
MY_ADDRESS = os.getenv("WALLET_ADDRESS")

# Kunci privat dompet Anda. SANGAT PENTING: JANGAN PERNAH EXPOSE KUNCI INI KE PUBLIK!
# Hanya diperlukan jika API Euclid Protocol membutuhkan penandatanganan off-chain
# Cek dokumentasi API mereka untuk detail ini.
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Endpoint API Euclid Swap
API_URL = "https://testnet.api.euclidprotocol.com/api/v1/execute/swap"

# Token Identifier yang digunakan oleh API Euclid Protocol
# Anda perlu MENGONFIRMASI ini dari dokumentasi Euclid atau contoh transaksi swap mereka
# Contoh:
OG_TOKEN_API_ID = "og"   # Asumsi: OG diidentifikasi sebagai "og" oleh API Euclid
EUCLID_TOKEN_API_ID = "euclid" # Asumsi: EUCLID diidentifikasi sebagai "euclid" oleh API Euclid

# Chain Identifier untuk Chain OG Anda
# Anda perlu MENGONFIRMASI ini dari dokumentasi Euclid atau blockchain explorer mereka
# Contoh:
OG_CHAIN_UID = "og_testnet" # Ganti dengan Chain ID yang benar untuk chain OG Anda

# --- Fungsi untuk Melakukan Swap Melalui API ---
def perform_single_chain_swap_via_api(
    amount_in_str: str,
    min_receive_str: str,
    asset_in_token_id: str,
    asset_out_token_id: str, # Tambahkan parameter untuk token output
    chain_uid: str,
    sender_address: str
):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    # Payload untuk swap satu chain
    payload = {
        "amount_in": amount_in_str,
        "slippage": "0.01", # Toleransi slippage, 1%
        "asset_in": {
            "token": asset_in_token_id,
            # Sesuaikan token_type jika OG bukan native token
            # Contoh untuk ERC-20: "token_type": {"erc20": {"contract_address": "0x..."}}
            "token_type": {
                "native": { "denom": asset_in_token_id }
            }
        },
        "minimum_receive": min_receive_str,
        # Untuk swap satu chain, bagian cross_chain_addresses kemungkinan tidak diperlukan
        # atau bisa disederhanakan/dihapus, tergantung API Euclid.
        # Saya akan menghapusnya untuk penyederhanaan maksimal.
        # Jika API Euclid tetap membutuhkannya untuk target chain yang sama,
        # gunakan sender_address dan chain_uid yang sama.

        # "partnerFee": { # Sesuaikan atau hapus jika tidak ada partner fee
        #     "partner_fee_bps": 10,
        #     "recipient": "0x72bbb..." # Ganti dengan alamat penerima fee
        # },
        "sender": {
            "address": sender_address,
            "chain_uid": chain_uid # Chain OG Anda
        },
        "swap_path": {
            "path": [
                {
                    "route": [asset_in_token_id, asset_out_token_id], # Dari OG ke EUCLID
                    "dex": "euclid", # Nama DEX yang digunakan
                    "amount_in": amount_in_str,
                    "amount_out": min_receive_str, # Ini harus disesuaikan dengan perkiraan jumlah output
                    "chain_uid": chain_uid # Chain OG Anda
                }
            ]
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Akan memunculkan error untuk status kode 4xx/5xx

        print("Swap request sent successfully!")
        print("Response:", response.json())
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error sending swap request: {e}")
        if response is not None:
            print("Error Response:", response.text)
        return None

# --- Logika Utama Bot ---
if __name__ == "__main__":
    if not MY_ADDRESS:
        print("Error: WALLET_ADDRESS tidak ditemukan di file .env. Mohon konfigurasikan.")
        exit()

    # --- Ini adalah bagian yang perlu Anda sesuaikan ---
    # 1. Jumlah Token OG yang ingin Anda swap (dalam satuan terkecil token)
    # Misalnya, jika 1 OG = 10^18 (1 dengan 18 nol di belakangnya)
    # Untuk swap 0.1 OG: "100000000000000000"
    AMOUNT_TO_SWAP_OG = "100000000000000000"

    # 2. Jumlah Minimum EUCLID yang diharapkan (dalam satuan terkecil token)
    # Ini HARUS dihitung secara DINAMIS berdasarkan harga pasar saat ini dan slippage!
    # Angka statis ini hanya untuk contoh dan sangat berisiko di dunia nyata.
    # Anda perlu mencari cara untuk mendapatkan quote harga dari Euclid API.
    EXPECTED_EUCLID_MIN = "900000" # Contoh: 0.0000000000009 EUCLID (jika 18 desimal)

    # 3. Interval pengecekan/swap (dalam detik)
    SWAP_INTERVAL_SECONDS = 300 # Swap setiap 5 menit (300 detik)

    print(f"Bot dimulai. Akan mencoba swap {AMOUNT_TO_SWAP_OG} {OG_TOKEN_API_ID} ke {EUCLID_TOKEN_API_ID} setiap {SWAP_INTERVAL_SECONDS} detik di chain {OG_CHAIN_UID}.")
    print(f"Menggunakan alamat dompet: {MY_ADDRESS}")

    while True:
        try:
            # --- Langkah 1: Dapatkan Harga Terkini (PENTING!) ---
            # Anda perlu mencari endpoint API Euclid Protocol untuk mendapatkan QUOTE harga.
            # Contoh (ini BUKAN kode nyata dari Euclid):
            # quote_response = requests.get(f"https://testnet.api.euclidprotocol.com/api/v1/quote?from={OG_TOKEN_API_ID}&to={EUCLID_TOKEN_API_ID}&amount={AMOUNT_TO_SWAP_OG}")
            # if quote_response.status_code == 200:
            #     quote_data = quote_response.json()
            #     # Misal, ambil estimated_amount_out dari quote_data
            #     estimated_amount_out = quote_data.get("estimated_amount_out")
            #     # Hitung minimum_receive_str dengan slippage
            #     # Pastikan untuk mengonversi ke format string yang benar (tanpa desimal)
            #     EXPECTED_EUCLID_MIN = str(int(estimated_amount_out * (1 - 0.01))) # Contoh slippage 1%
            # else:
            #     print(f"Gagal mendapatkan quote harga: {quote_response.status_code}")
            #     # Lanjutkan dengan minimum_receive statis atau skip iterasi ini
            #     pass

            # --- Langkah 2: Lakukan Swap ---
            print(f"\nMencoba melakukan swap pada {time.ctime()}...")
            swap_result = perform_single_chain_swap_via_api(
                amount_in_str=AMOUNT_TO_SWAP_OG,
                min_receive_str=EXPECTED_EUCLID_MIN,
                asset_in_token_id=OG_TOKEN_API_ID,
                asset_out_token_id=EUCLID_TOKEN_API_ID,
                chain_uid=OG_CHAIN_UID,
                sender_address=MY_ADDRESS
            )

            if swap_result:
                print("Swap request berhasil dikirim ke API Euclid.")
                # Lakukan pengecekan status transaksi lebih lanjut jika API mengembalikan hash transaksi
            else:
                print("Swap request gagal atau ada masalah dengan respons API.")

        except Exception as e:
            print(f"Terjadi kesalahan tak terduga dalam loop bot: {e}")

        print(f"Menunggu {SWAP_INTERVAL_SECONDS} detik sebelum iterasi berikutnya...")
        time.sleep(SWAP_INTERVAL_SECONDS)