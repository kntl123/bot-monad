from dotenv import load_dotenv
import os
from web3 import Web3
import json
import time

# --- Konfigurasi Awal & Load Variabel Lingkungan ---
load_dotenv() # Memuat variabel dari file .env
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL")

# Pastikan variabel lingkungan dimuat
if not PRIVATE_KEY or not RPC_URL:
    print("Error: Kunci privat atau URL RPC tidak ditemukan di file .env")
    print("Pastikan file .env ada dan berisi PRIVATE_KEY dan RPC_URL.")
    exit()

# --- Konfigurasi Monad Testnet & Ambient Finance (Dibaca dari .env) ---
MONAD_RPC_URL = RPC_URL 
AMBIENT_FINANCE_ROUTER_ADDRESS = os.getenv("AMBIENT_FINANCE_ROUTER_ADDRESS")
MONAD_WETH_ADDRESS = os.getenv("MONAD_WETH_ADDRESS") # Token input Anda
MONAD_USDC_ADDRESS = os.getenv("MONAD_USDC_ADDRESS") # Token output Anda

# --- ABI STANDAR ERC-20 (Umumnya universal untuk token) ---
ERC20_ABI = json.loads('''
[
    {"constant": true, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "payable": false, "stateMutability": "view", "type": "function"},
    {"constant": false, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "payable": false, "stateMutability": "nonpayable", "type": "function"},
    {"constant": true, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "payable": false, "stateMutability": "view", "type": "function"},
    {"constant": false, "inputs": [{"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transferFrom", "outputs": [{"name": "", "type": "bool"}], "payable": false, "stateMutability": "nonpayable", "type": "function"},
    {"constant": true, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "payable": false, "stateMutability": "view", "type": "function"},
    {"constant": true, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "payable": false, "stateMutability": "view", "type": "function"},
    {"constant": true, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "payable": false, "stateMutability": "view", "type": "function"},
    {"constant": false, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "payable": false, "stateMutability": "nonpayable", "type": "function"},
    {"constant": true, "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "remaining", "type": "uint256"}], "payable": false, "stateMutability": "view", "type": "function"},
    {"anonymous": false, "inputs": [{"indexed": true, "name": "owner", "type": "address"}, {"indexed": true, "name": "spender", "type": "address"}, {"indexed": false, "name": "value", "type": "uint256"}], "name": "Approval", "type": "event"},
    {"anonymous": false, "inputs": [{"indexed": true, "name": "from", "type": "address"}, {"indexed": true, "name": "to", "type": "address"}, {"indexed": false, "name": "value", "type": "uint256"}], "name": "Transfer", "type": "event"}
]
''')

# --- ABI Ambient Finance (SANGAT PENTING: GANTI DENGAN ABI ASLI DARI SUMBER RESMI!) ---
# Ini hanya contoh fungsi yang mungkin ada. Ambient Finance adalah concentrated liquidity AMM.
# Fungsi swap dan query price akan sangat spesifik.
AMBIENT_FINANCE_ROUTER_ABI = json.loads('''
[
  {
    "inputs": [],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "authority",
        "type": "address"
      }
    ],
    "name": "AuthorityTransfer",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "input",
        "type": "bytes"
      }
    ],
    "name": "CrocColdCmd",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "input",
        "type": "bytes"
      }
    ],
    "name": "CrocColdProtocolCmd",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "input",
        "type": "bytes"
      },
      {
        "indexed": false,
        "internalType": "int128",
        "name": "baseFlow",
        "type": "int128"
      },
      {
        "indexed": false,
        "internalType": "int128",
        "name": "quoteFlow",
        "type": "int128"
      }
    ],
    "name": "CrocHotCmd",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "input",
        "type": "bytes"
      },
      {
        "indexed": false,
        "internalType": "int128",
        "name": "baseFlow",
        "type": "int128"
      },
      {
        "indexed": false,
        "internalType": "int128",
        "name": "quoteFlow",
        "type": "int128"
      }
    ],
    "name": "CrocKnockoutCmd",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "bytes32",
        "name": "pool",
        "type": "bytes32"
      },
      {
        "indexed": true,
        "internalType": "int24",
        "name": "tick",
        "type": "int24"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isBid",
        "type": "bool"
      },
      {
        "indexed": false,
        "internalType": "uint32",
        "name": "pivotTime",
        "type": "uint32"
      },
      {
        "indexed": false,
        "internalType": "uint64",
        "name": "feeMileage",
        "type": "uint64"
      },
      {
        "indexed": false,
        "internalType": "uint160",
        "name": "commitEntropy",
        "type": "uint160"
      }
    ],
    "name": "CrocKnockoutCross",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "input",
        "type": "bytes"
      },
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "output",
        "type": "bytes"
      }
    ],
    "name": "CrocMicroBurnAmbient",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "input",
        "type": "bytes"
      },
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "output",
        "type": "bytes"
      }
    ],
    "name": "CrocMicroBurnRange",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "input",
        "type": "bytes"
      },
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "output",
        "type": "bytes"
      }
    ],
    "name": "CrocMicroMintAmbient",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "input",
        "type": "bytes"
      },
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "output",
        "type": "bytes"
      }
    ],
    "name": "CrocMicroMintRange",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "input",
        "type": "bytes"
      },
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "output",
        "type": "bytes"
      }
    ],
    "name": "CrocMicroSwap",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "base",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "quote",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "poolIdx",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "isBuy",
        "type": "bool"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "inBaseQty",
        "type": "bool"
      },
      {
        "indexed": false,
        "internalType": "uint128",
        "name": "qty",
        "type": "uint128"
      },
      {
        "indexed": false,
        "internalType": "uint16",
        "name": "tip",
        "type": "uint16"
      },
      {
        "indexed": false,
        "internalType": "uint128",
        "name": "limitPrice",
        "type": "uint128"
      },
      {
        "indexed": false,
        "internalType": "uint128",
        "name": "minOut",
        "type": "uint128"
      },
      {
        "indexed": false,
        "internalType": "uint8",
        "name": "reserveFlags",
        "type": "uint8"
      },
      {
        "indexed": false,
        "internalType": "int128",
        "name": "baseFlow",
        "type": "int128"
      },
      {
        "indexed": false,
        "internalType": "int128",
        "name": "quoteFlow",
        "type": "int128"
      }
    ],
    "name": "CrocSwap",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "input",
        "type": "bytes"
      },
      {
        "indexed": false,
        "internalType": "int128",
        "name": "baseFlow",
        "type": "int128"
      },
      {
        "indexed": false,
        "internalType": "int128",
        "name": "quoteFlow",
        "type": "int128"
      }
    ],
    "name": "CrocWarmCmd",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "uint256",
        "name": "poolIdx",
        "type": "uint256"
      }
    ],
    "name": "DisablePoolTemplate",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "name": "HotPathOpen",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "token",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint128",
        "name": "unitTickCollateral",
        "type": "uint128"
      },
      {
        "indexed": false,
        "internalType": "uint16",
        "name": "awayTickTol",
        "type": "uint16"
      }
    ],
    "name": "PriceImproveThresh",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "token",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "recv",
        "type": "address"
      }
    ],
    "name": "ProtocolDividend",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "base",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "quote",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "uint256",
        "name": "poolIdx",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint8",
        "name": "takeRate",
        "type": "uint8"
      }
    ],
    "name": "ResyncTakeRate",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "name": "SafeMode",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "uint128",
        "name": "liq",
        "type": "uint128"
      }
    ],
    "name": "SetNewPoolLiq",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "uint256",
        "name": "poolIdx",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint16",
        "name": "feeRate",
        "type": "uint16"
      },
      {
        "indexed": false,
        "internalType": "uint16",
        "name": "tickSize",
        "type": "uint16"
      },
      {
        "indexed": false,
        "internalType": "uint8",
        "name": "jitThresh",
        "type": "uint8"
      },
      {
        "indexed": false,
        "internalType": "uint8",
        "name": "knockout",
        "type": "uint8"
      },
      {
        "indexed": false,
        "internalType": "uint8",
        "name": "oracleFlags",
        "type": "uint8"
      }
    ],
    "name": "SetPoolTemplate",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "uint8",
        "name": "takeRate",
        "type": "uint8"
      }
    ],
    "name": "SetRelayerTakeRate",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "uint8",
        "name": "takeRate",
        "type": "uint8"
      }
    ],
    "name": "SetTakeRate",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "treasury",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "uint64",
        "name": "startTime",
        "type": "uint64"
      }
    ],
    "name": "TreasurySet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "proxy",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint16",
        "name": "proxyIdx",
        "type": "uint16"
      }
    ],
    "name": "UpgradeProxy",
    "type": "event"
  },
  {
    "inputs": [],
    "name": "acceptCrocDex",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "pure",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint16",
        "name": "callpath",
        "type": "uint16"
      },
      {
        "internalType": "bytes",
        "name": "cmd",
        "type": "bytes"
      },
      {
        "internalType": "bool",
        "name": "sudo",
        "type": "bool"
      }
    ],
    "name": "protocolCmd",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "slot",
        "type": "uint256"
      }
    ],
    "name": "readSlot",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "data",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "base",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "quote",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "poolIdx",
        "type": "uint256"
      },
      {
        "internalType": "bool",
        "name": "isBuy",
        "type": "bool"
      },
      {
        "internalType": "bool",
        "name": "inBaseQty",
        "type": "bool"
      },
      {
        "internalType": "uint128",
        "name": "qty",
        "type": "uint128"
      },
      {
        "internalType": "uint16",
        "name": "tip",
        "type": "uint16"
      },
      {
        "internalType": "uint128",
        "name": "limitPrice",
        "type": "uint128"
      },
      {
        "internalType": "uint128",
        "name": "minOut",
        "type": "uint128"
      },
      {
        "internalType": "uint8",
        "name": "reserveFlags",
        "type": "uint8"
      }
    ],
    "name": "swap",
    "outputs": [
      {
        "internalType": "int128",
        "name": "baseFlow",
        "type": "int128"
      },
      {
        "internalType": "int128",
        "name": "quoteFlow",
        "type": "int128"
      }
    ],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint16",
        "name": "callpath",
        "type": "uint16"
      },
      {
        "internalType": "bytes",
        "name": "cmd",
        "type": "bytes"
      }
    ],
    "name": "userCmd",
    "outputs": [
      {
        "internalType": "bytes",
        "name": "",
        "type": "bytes"
      }
    ],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint16",
        "name": "callpath",
        "type": "uint16"
      },
      {
        "internalType": "bytes",
        "name": "cmd",
        "type": "bytes"
      },
      {
        "internalType": "bytes",
        "name": "conds",
        "type": "bytes"
      },
      {
        "internalType": "bytes",
        "name": "relayerTip",
        "type": "bytes"
      },
      {
        "internalType": "bytes",
        "name": "signature",
        "type": "bytes"
      }
    ],
    "name": "userCmdRelayer",
    "outputs": [
      {
        "internalType": "bytes",
        "name": "output",
        "type": "bytes"
      }
    ],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "

    // LENGKAPI DENGAN ABI ASLI DARI AMBIENT FINANCE DI MONAD TESTNET!
    // ABI ini mungkin akan jauh lebih panjang dan kompleks.
]
''') 

# --- Inisialisasi Web3 ---
w3 = Web3(Web3.HTTPProvider(MONAD_RPC_URL))

# --- Cek Koneksi ---
if w3.is_connected():
    print(f"Berhasil terhubung ke jaringan Monad testnet: {MONAD_RPC_URL}")
else:
    print("Gagal terhubung ke jaringan Monad testnet. Mohon periksa URL RPC Anda di .env.")
    exit()

# --- Informasi Akun ---
try:
    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"Alamat wallet Anda: {account.address}")
    monad_balance_wei = w3.eth.get_balance(account.address)
    monad_balance_formatted = w3.from_wei(monad_balance_wei, 'ether')
    print(f"Saldo MONAD Anda di testnet: {monad_balance_formatted} MONAD")
    latest_block = w3.eth.block_number
    print(f"Nomor blok terakhir di testnet Monad: {latest_block}")
except Exception as e:
    print(f"Terjadi error saat mendapatkan informasi akun atau saldo: {e}")
    print("Pastikan kunci privat Anda benar dan memiliki format yang valid, serta Anda punya MONAD test token untuk gas fee.")
    exit()

# --- Fungsi Bantu ERC-20 (Umum) ---
def get_token_contract(token_address):
    return w3.eth.contract(address=token_address, abi=ERC20_ABI)

def get_token_balance(token_address, wallet_address):
    token_contract = get_token_contract(token_address)
    try:
        balance_wei = token_contract.functions.balanceOf(wallet_address).call()
        decimals = token_contract.functions.decimals().call()
        return balance_wei, decimals
    except Exception as e:
        print(f"Error getting balance for {token_address}: {e}")
        return 0, 18 # Default to 0 balance, 18 decimals if error

def get_token_symbol(token_address):
    token_contract = get_token_contract(token_address)
    try:
        return token_contract.functions.symbol().call()
    except Exception:
        return "UNKNOWN"

def check_allowance(token_address, owner_address, spender_address):
    token_contract = get_token_contract(token_address)
    allowance = token_contract.functions.allowance(owner_address, spender_address).call()
    return allowance

def approve_token(token_address, spender_address, amount_to_approve):
    token_contract = get_token_contract(token_address)
    
    current_allowance = check_allowance(token_address, account.address, spender_address)
    if current_allowance >= amount_to_approve:
        print(f"Token {get_token_symbol(token_address)} sudah diapprove sejumlah yang cukup ({w3.from_wei(current_allowance, 'ether')} atau lebih) untuk {spender_address}.")
        return True

    nonce = w3.eth.get_transaction_count(account.address)
    
    print(f"Melakukan approval {w3.from_wei(amount_to_approve, 'ether')} {get_token_symbol(token_address)} ke {spender_address}...")

    try:
        approve_txn = token_contract.functions.approve(
            spender_address,
            amount_to_approve
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gasPrice': w3.eth.gas_price,
            'chainId': w3.eth.chain_id
        })

        approve_txn['gas'] = int(w3.eth.estimate_gas(approve_txn) * 1.2) # Tambah buffer 20%

        signed_txn = w3.eth.account.sign_transaction(approve_txn, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"Transaksi approval dikirim: {tx_hash.hex()}")

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print(f"Approval berhasil! Block: {receipt.blockNumber}")
            return True
        else:
            print(f"Approval gagal! Receipt: {receipt}")
            return False
    except Exception as e:
        print(f"Error saat melakukan approval: {e}")
        return False

# --- Fungsi Kuotasi Harga & Swap Ambient Finance (PERLU VERIFIKASI ABI & FUNGSI ASLI) ---
def get_ambient_quote(token_in_address, token_out_address, amount_in_wei):
    ambient_contract = w3.eth.contract(address=AMBIENT_FINANCE_ROUTER_ADDRESS, abi=AMBIENT_FINANCE_ROUTER_ABI)
    try:
        # PENTING: Anda harus merujuk pada ABI Ambient Finance yang ASLI.
        # Fungsi query_price di ABI placeholder di atas mungkin tidak mengembalikan "amount out".
        # Ambient Finance adalah concentrated liquidity, mungkin ada fungsi seperti 'swapDryRun'
        # atau 'quoteAmountOut' atau Anda perlu query pool langsung.
        # Untuk demo, saya akan buat asumsi yang sangat sederhana atau placeholder return.

        # --- CONTOH ASUMSI DUMMY (GANTI DENGAN LOGIKA ASLI AMBIENT) ---
        # Ini adalah placeholder yang sangat sederhana. Anda HARUS mengganti ini
        # dengan cara Ambient Finance memberikan kuotasi harga.
        # Cek dokumentasi Ambient Finance untuk fungsi seperti `simulateSwap` atau `getAmountOut`.
        token_out_decimals = get_token_balance(token_out_address, account.address)[1]
        token_in_decimals = get_token_balance(token_in_address, account.address)[1]
        
        # ASUMSI DUMMY: 1 WETH = 2000 USDC. USDC 6 desimal, WETH 18 desimal
        if token_in_address == MONAD_WETH_ADDRESS and token_out_address == MONAD_USDC_ADDRESS:
            # Mengubah jumlah WETH (18 desimal) menjadi USDC (6 desimal) dengan rasio 1:2000
            estimated_out_wei = int(amount_in_wei * (2000 * (10**token_out_decimals)) / (10**token_in_decimals))
            print(f"DEBUG: Dummy quote: {w3.from_wei(amount_in_wei, 'ether')} WETH -> {estimated_out_wei / (10**token_out_decimals)} USDC")
            return estimated_out_wei
        
        print("Warning: `get_ambient_quote` menggunakan asumsi dummy. Perlu ABI & fungsi asli Ambient!")
        return 0 # Return 0 jika tidak bisa mengkuotasi

    except Exception as e:
        print(f"Gagal mendapatkan kuotasi harga dari Ambient Finance: {e}")
        return None

def perform_ambient_swap(token_in_address, token_out_address, amount_in_wei, amount_out_min_wei):
    ambient_contract = w3.eth.contract(address=AMBIENT_FINANCE_ROUTER_ADDRESS, abi=AMBIENT_FINANCE_ROUTER_ABI)
    
    nonce = w3.eth.get_transaction_count(account.address)
    deadline = int(time.time()) + (60 * 5) # Deadline 5 menit

    print(f"\n--- Memulai transaksi swap di Ambient Finance ---")
    print(f"Swap {w3.from_wei(amount_in_wei, 'ether')} {get_token_symbol(token_in_address)}")
    token_out_decimals = get_token_balance(token_out_address, account.address)[1]
    print(f"Mengharapkan minimal {amount_out_min_wei / (10**token_out_decimals)} {get_token_symbol(token_out_address)}")

    try:
        # PENTING: Anda harus merujuk pada ABI Ambient Finance yang ASLI
        # Nama fungsi swap di Ambient mungkin 'swap' atau lainnya, dengan parameter yang spesifik.
        # Contoh di sini menggunakan fungsi 'swap' dengan parameter yang diasumsikan dari ABI placeholder.
        # Parameter 'is_token_in_base' adalah penting dan perlu disesuaikan dengan pool.

        swap_txn_builder = ambient_contract.functions.swap(
            token_in_address,
            token_out_address,
            amount_in_wei,
            True, # Ini placeholder untuk `is_token_in_base`. Anda HARUS cari tahu nilai yang benar.
            amount_out_min_wei,
            account.address
        )

        txn_params = {
            'from': account.address,
            'nonce': nonce,
            'gasPrice': w3.eth.gas_price,
            'chainId': w3.eth.chain_id
        }
        
        swap_txn = swap_txn_builder.build_transaction(txn_params)
        swap_txn['gas'] = int(w3.eth.estimate_gas(swap_txn) * 1.2) # Tambah buffer gas

        print(f"Estimasi Gas: {swap_txn['gas']} units")
        print(f"Gas Price: {w3.from_wei(swap_txn['gasPrice'], 'gwei')} Gwei")
        print(f"Biaya Gas Maksimal (estimasi): {w3.from_wei(swap_txn['gas'] * swap_txn['gasPrice'], 'ether')} MONAD")

        signed_txn = w3.eth.account.sign_transaction(swap_txn, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"Transaksi swap dikirim! Hash: {tx_hash.hex()}")

        print("Menunggu konfirmasi transaksi...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            print(f"Swap berhasil di Monad testnet! Transaksi dikonfirmasi di blok: {receipt.blockNumber}")
            return True
        else:
            print(f"Swap GAGAL di Monad testnet! Status receipt: {receipt.status}")
            print(f"Lihat detailnya di Block Explorer Monad (cari berdasarkan hash): {tx_hash.hex()}")
            return False

    except Exception as e:
        print(f"Error saat melakukan swap di Ambient Finance: {e}")
        return False

# --- Bagian Utama Skrip (Logika Bot Otomatis) ---
def main_bot_loop():
    print("\n--- Memulai Bot Auto Swap di Monad Testnet ---")
    
    # --- Konfigurasi Strategi Swap Anda ---
    AMOUNT_TO_SWAP_WETH = w3.to_wei(0.01, 'ether') # Contoh: Jumlah WETH yang ingin di-swap setiap kali
    SLIPPAGE_TOLERANCE = 0.99 # Toleransi slippage 1% (misal, 99% dari harga kuotasi minimum yang diterima)
    
    # --- Strategi Harga (Contoh Sederhana, Anda bisa kembangkan!) ---
    # Misalnya, Anda ingin swap WETH ke USDC jika 1 WETH bisa mendapatkan minimal 2000 USDC.
    # Ingat, USDC umumnya memiliki 6 desimal.
    TARGET_USDC_PER_WETH = 2000.0 # Target harga: 1 WETH = 2000 USDC
    
    # Ini adalah jumlah USDC dalam WEI/unit terkecil yang Anda harap dapatkan per 1 WETH
    # Kita perlu mendapatkan desimal USDC terlebih dahulu
    _, usdc_decimals_for_target = get_token_balance(MONAD_USDC_ADDRESS, account.address)
    TARGET_USDC_PER_WETH_WEI = int(TARGET_USDC_PER_WETH * (10**usdc_decimals_for_target))


    # --- Loop Utama Bot ---
    while True:
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Pengecekan kondisi swap...")

        try:
            # 1. Cek Saldo Token Input (WETH)
            weth_balance_wei, weth_decimals = get_token_balance(MONAD_WETH_ADDRESS, account.address)
            weth_balance_formatted = w3.from_wei(weth_balance_wei, 'ether')
            print(f"Saldo WETH Anda: {weth_balance_formatted} WETH")

            if weth_balance_wei < AMOUNT_TO_SWAP_WETH:
                print(f"Saldo WETH tidak cukup ({weth_balance_formatted}) untuk swap {w3.from_wei(AMOUNT_TO_SWAP_WETH, 'ether')}. Menunggu saldo.")
                time.sleep(30)
                continue # Lanjutkan ke iterasi berikutnya

            # 2. Lakukan Approval untuk WETH (jika diperlukan)
            #    Approval hanya perlu dilakukan sekali atau ketika jumlah approval kurang.
            if not approve_token(MONAD_WETH_ADDRESS, AMBIENT_FINANCE_ROUTER_ADDRESS, AMOUNT_TO_SWAP_WETH):
                print("Approval WETH gagal atau tidak cukup. Coba lagi di iterasi berikutnya.")
                time.sleep(30)
                continue

            # 3. Dapatkan Kuotasi Harga dari Ambient Finance
            print(f"Simulasi swap {w3.from_wei(AMOUNT_TO_SWAP_WETH, 'ether')} WETH ke USDC...")
            # PENTING: Fungsi get_ambient_quote harus sudah DIKOREKSI dan mengembalikan nilai valid.
            quoted_amount_out_usdc_wei = get_ambient_quote(MONAD_WETH_ADDRESS, MONAD_USDC_ADDRESS, AMOUNT_TO_SWAP_WETH)

            if quoted_amount_out_usdc_wei and quoted_amount_out_usdc_wei > 0:
                usdc_decimals = get_token_balance(MONAD_USDC_ADDRESS, account.address)[1]
                quoted_amount_out_usdc_formatted = quoted_amount_out_usdc_wei / (10**usdc_decimals)
                print(f"Perkiraan mendapatkan: {quoted_amount_out_usdc_formatted} USDC.")

                # Tentukan amount_out_min untuk proteksi slippage
                amount_out_min_usdc_wei = int(quoted_amount_out_usdc_wei * SLIPPAGE_TOLERANCE)
                
                # --- Logika Keputusan Swap ---
                # Anda bisa kembangkan ini. Contoh: swap jika harga saat ini lebih baik dari target.
                # Perhitungan target untuk jumlah swap spesifik
                expected_usdc_from_swap = (AMOUNT_TO_SWAP_WETH / (10**weth_decimals)) * TARGET_USDC_PER_WETH
                
                if quoted_amount_out_usdc_formatted >= expected_usdc_from_swap:
                    print(f"Kondisi swap terpenuhi! Perkiraan {quoted_amount_out_usdc_formatted} USDC, target minimal {expected_usdc_from_swap} USDC.")
                    
                    # 4. Lakukan Swap Sebenarnya
                    swap_successful = perform_ambient_swap(
                        MONAD_WETH_ADDRESS,
                        MONAD_USDC_ADDRESS,
                        AMOUNT_TO_SWAP_WETH,
                        amount_out_min_usdc_wei
                    )

                    if swap_successful:
                        print("Transaksi swap berhasil dilakukan!")
                        # Setelah swap berhasil, mungkin Anda ingin menunggu lebih lama atau melakukan sesuatu yang lain.
                        time.sleep(120) # Tunggu lebih lama setelah swap berhasil
                    else:
                        print("Transaksi swap gagal. Mencoba lagi di iterasi berikutnya.")
                else:
                    print(f"Kondisi swap belum terpenuhi. Perkiraan {quoted_amount_out_usdc_formatted} USDC, target minimal {expected_usdc_from_swap} USDC.")
            else:
                print("Gagal mendapatkan kuotasi harga atau kuotasi 0. Swap tidak dilakukan.")

        except Exception as e:
            print(f"Terjadi kesalahan fatal di loop utama: {e}")
            # Anda bisa menambahkan logika notifikasi di sini (misal: kirim email/notif Discord)

        time.sleep(30) # Cek setiap 30 detik (sesuaikan sesuai kebutuhan dan batas RPC rate limit)

if __name__ == "__main__":
    main_bot_loop()