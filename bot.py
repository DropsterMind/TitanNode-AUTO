from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    BasicAuth
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, uuid, time, json, re, os, pytz

# Inisialisasi Colorama
init(autoreset=True)

# Atur zona waktu
wib = pytz.timezone('Asia/Jakarta')

class Titan:
    """
    Kelas utama untuk bot Titan Node.
    Mengelola akun, proksi, dan interaksi dengan API Titan.
    """
    def __init__(self) -> None:
        self.BASE_API = "https://task.titannet.info/api"
        self.WS_API = "wss://task.titannet.info/api/public/webnodes/ws"
        self.VERSION = "0.0.5"
        self.LANGUAGE = "en"
        
        # Kamus untuk menyimpan data per akun
        self.BASE_HEADERS = {}
        self.WS_HEADERS = {}
        self.password = {}
        self.device_ids = {}
        self.access_tokens = {}
        self.refresh_tokens = {}
        self.expires_times = {}
        self.account_proxies = {}

        # Manajemen proksi
        self.proxies = []
        self.proxy_index = 0

        # Konfigurasi logging modern
        self.LOG_LEVELS = {
            "INFO": {"color": Fore.CYAN, "symbol": "ℹ️"},
            "SUCCESS": {"color": Fore.GREEN, "symbol": "✅"},
            "WARNING": {"color": Fore.YELLOW, "symbol": "⚠️"},
            "ERROR": {"color": Fore.RED, "symbol": "❌"},
            "JOB": {"color": Fore.BLUE, "symbol": "💼"},
            "DEBUG": {"color": Fore.MAGENTA, "symbol": "🐞"}
        }

    def clear_terminal(self):
        """Membersihkan layar terminal."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, level, message, account_info=None):
        """
        Fungsi logging modern yang terpusat.
        Mencetak pesan dengan format, warna, dan simbol berdasarkan level.
        """
        level_config = self.LOG_LEVELS.get(level.upper(), {"color": Fore.WHITE, "symbol": "•"})
        color = level_config["color"]
        symbol = level_config["symbol"]
        
        timestamp = f"{Fore.YELLOW}{datetime.now().astimezone(wib).strftime('%H:%M:%S')}{Style.RESET_ALL}"
        log_header = f"{color}{Style.BRIGHT}[{symbol} {level.upper()}]{Style.RESET_ALL}"
        
        print(f"[{timestamp}] {log_header} {message}", flush=True)

        if account_info:
            email = account_info.get("email", "N/A")
            proxy = account_info.get("proxy", "N/A")
            device_id = account_info.get("device_id", "N/A")
            
            details = [
                f"{Fore.CYAN}Account  : {Style.BRIGHT}{self.mask_account(email)}",
                f"{Fore.CYAN}Proxy    : {Style.BRIGHT}{proxy}",
                f"{Fore.CYAN}Device ID: {Style.BRIGHT}{device_id}"
            ]
            
            for i, detail in enumerate(details):
                prefix = " └─" if i == len(details) - 1 else " ├─"
                print(f"  {prefix} {detail}{Style.RESET_ALL}", flush=True)

    def welcome(self):
        """Menampilkan pesan selamat datang yang lebih bersih."""
        self.clear_terminal()
        banner = f"""
{Fore.CYAN}
 ________   __  __   _________  ______    _______   ______   _________  
/_______/\\ /_/\\/_/\\ /________/\\/_____/\\ /_______/\\ /_____/\\ /________/\\ 
\\::: _  \\ \\\\:\\ \\:\\ \\\\__.::.__\\/\\:::_ \\ \\\\::: _  \\ \\\\:::_ \\ \\\\__.::.__\\/ 
 \\::(_)  \\ \\\\:\\ \\:\\ \\  \\::\\ \\   \\:\\ \\ \\ \\\\::(_)  \\/_\\:\\ \\ \\ \\  \\::\\ \\   
  \\:: __  \\ \\\\:\\ \\:\\ \\  \\::\\ \\   \\:\\ \\ \\ \\\\::  _  \\ \\\\:\\ \\ \\ \\  \\::\\ \\  
   \\:.\\ \\  \\ \\\\:\\_\\:\\ \\  \\::\\ \\   \\:\\_\\ \\ \\\\::(_)  \\ \\\\:\\_\\ \\ \\  \\::\\ \\ 
    \\__\\/\\__\\/ \\_____\\/   \\__\\/    \\_____\\/ \\______\\/ \\_____\\/   \\__\\/ 
                                                                        
{Style.RESET_ALL}
        """
        print(banner)
        print(f"{Fore.GREEN}{Style.BRIGHT}{'By: DropsterMind'.center(80)}{Style.RESET_ALL}")
        print("\n")

    def format_seconds(self, seconds):
        """Mengonversi detik menjadi format HH:MM:SS."""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        """Memuat data akun dari file accounts.json."""
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log('ERROR', f"File '{filename}' tidak ditemukan.")
                return []
            with open(filename, 'r') as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            self.log('ERROR', f"Gagal mem-parsing '{filename}'. Pastikan format JSON valid.")
            return []
    
    async def load_proxies(self, use_proxy_choice: int):
        """Memuat proksi dari file atau sumber online."""
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                self.log('INFO', "Mengunduh daftar proksi gratis...")
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/refs/heads/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log('ERROR', f"File proksi '{filename}' tidak ditemukan.")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log('WARNING', "Tidak ada proksi yang dimuat.")
                return

            self.log('INFO', f"Total proksi yang dimuat: {Fore.GREEN}{len(self.proxies)}")
        
        except Exception as e:
            self.log('ERROR', f"Gagal memuat proksi: {e}")
            self.proxies = []

    def check_proxy_schemes(self, proxy_str):
        """Memastikan proksi memiliki skema (http, socks)."""
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxy_str.startswith(scheme) for scheme in schemes):
            return proxy_str
        return f"http://{proxy_str}"

    def get_next_proxy_for_account(self, account):
        """Mendapatkan proksi berikutnya untuk sebuah akun."""
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        """Mengganti proksi yang tidak valid untuk sebuah akun."""
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        """Membangun konfigurasi proksi untuk aiohttp."""
        if not proxy:
            return None, None, None
        if proxy.startswith("socks"):
            return ProxyConnector.from_url(proxy), None, None
        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            return None, proxy, None
        raise ValueError("Tipe proksi tidak didukung.")
    
    def generate_device_id(self):
        """Menghasilkan ID perangkat unik."""
        return str(uuid.uuid4())
    
    def mask_account(self, account):
        """Menyamarkan alamat email untuk privasi."""
        if "@" in account:
            local, domain = account.split('@', 1)
            if len(local) > 6:
                return f"{local[:3]}***{local[-3:]}@{domain}"
            return f"{local[:1]}***@{domain}"
        if len(account) > 6:
            return f"{account[:3]}***{account[-3:]}"
        return f"{account[:1]}***"

    def print_question(self):
        """Menampilkan pertanyaan pilihan proksi kepada pengguna."""
        while True:
            try:
                print(f"{Fore.CYAN}{Style.BRIGHT}Pilih mode proksi:{Style.RESET_ALL}")
                print("1. Gunakan proksi gratis (dari proxyscrape)")
                print("2. Gunakan proksi pribadi (dari proxy.txt)")
                print("3. Jalankan tanpa proksi")
                choose = int(input(f"{Fore.YELLOW}Pilihan [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = "proksi gratis" if choose == 1 else "proksi pribadi" if choose == 2 else "tanpa proksi"
                    self.log('INFO', f"Mode '{proxy_type}' dipilih.")
                    break
                else:
                    print(f"{Fore.RED}Masukkan 1, 2, atau 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Input tidak valid. Masukkan angka.{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate_input = input(f"{Fore.YELLOW}Ganti proksi jika tidak valid? [y/n] -> {Style.RESET_ALL}").strip().lower()
                if rotate_input in ["y", "n"]:
                    rotate = rotate_input == "y"
                    break
                else:
                    print(f"{Fore.RED}Input tidak valid. Masukkan 'y' atau 'n'.{Style.RESET_ALL}")
        return choose, rotate
    
    async def check_connection(self, email: str, proxy_url=None):
        """Memeriksa konektivitas proksi."""
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get("https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except Exception as e:
            self.log('ERROR', f"Koneksi gagal: {e}", {"email": email, "proxy": proxy_url, "device_id": self.device_ids[email]})
            return False
    
    async def auth_login(self, email: str, proxy_url=None, retries=5):
        """Melakukan login ke API Titan."""
        url = f"{self.BASE_API}/auth/login"
        data = json.dumps({"password": self.password[email], "user_id": email})
        headers = {**self.BASE_HEADERS[email], "Content-Type": "application/json"}
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log('ERROR', f"Login gagal setelah {retries} percobaan: {e}", {"email": email, "proxy": proxy_url, "device_id": self.device_ids[email]})
                return None
    
    async def auth_refresh(self, email: str, proxy_url=None, retries=5):
        """Memperbarui token otentikasi."""
        url = f"{self.BASE_API}/auth/refresh-token"
        data = json.dumps({"refresh_token": self.refresh_tokens[email]})
        headers = {**self.BASE_HEADERS[email], "Content-Type": "application/json"}

        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log('ERROR', f"Gagal memperbarui token: {e}", {"email": email, "proxy": proxy_url, "device_id": self.device_ids[email]})
                return None

    async def register_webnodes(self, email: str, proxy_url=None, retries=5):
        """Mendaftarkan node ke server Titan."""
        url = f"{self.BASE_API}/webnodes/register"
        data = json.dumps({
            "ext_version": self.VERSION,
            "language": self.LANGUAGE,
            "user_script_enabled": True,
            "device_id": self.device_ids[email],
            "install_time": datetime.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        })
        headers = {
            **self.BASE_HEADERS[email],
            "Authorization": f"Bearer {self.access_tokens[email]}",
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log('ERROR', f"Gagal mendaftarkan webnode: {e}", {"email": email, "proxy": proxy_url, "device_id": self.device_ids[email]})
                return None

    async def connect_websocket(self, email: str, use_proxy: bool, rotate_proxy: bool):
        """Menghubungkan ke WebSocket untuk menerima dan mengirim pekerjaan."""
        wss_url = f"{self.WS_API}?token={self.access_tokens[email]}&device_id={self.device_ids[email]}"
        
        while True:
            proxy_url = self.get_next_proxy_for_account(email) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            session = None
            send_ping_task = None

            try:
                session = ClientSession(connector=connector, timeout=ClientTimeout(total=300))
                async with session.ws_connect(wss_url, headers=self.WS_HEADERS[email], proxy=proxy, proxy_auth=proxy_auth) as wss:
                    
                    self.log('SUCCESS', "WebSocket terhubung.", {"email": email, "proxy": proxy_url, "device_id": self.device_ids[email]})

                    async def send_heartbeat():
                        while True:
                            await wss.send_json({"cmd": 1, "echo": "echo me", "jobReport": {"cfgcnt": 2, "jobcnt": 0}})
                            self.log('JOB', "Laporan pekerjaan terkirim.", {"email": email, "proxy": proxy_url, "device_id": self.device_ids[email]})
                            await asyncio.sleep(30)

                    send_ping_task = asyncio.create_task(send_heartbeat())

                    async for msg in wss:
                        response = json.loads(msg.data)
                        if response.get("cmd") == 1:
                            update = response.get("userDataUpdate", {})
                            today_point = update.get("today_points", 0)
                            total_point = update.get("total_points", 0)
                            message = (f"Update data: {Fore.WHITE}Hari ini {today_point} PTS "
                                       f"{Fore.MAGENTA}- {Fore.WHITE}Total {total_point} PTS")
                            self.log('SUCCESS', message, {"email": email, "proxy": proxy_url, "device_id": self.device_ids[email]})
                        
                        elif response.get("cmd") == 2:
                            await wss.send_json(response)
                            self.log('DEBUG', "Pesan 'echo' dibalas.", {"email": email, "proxy": proxy_url, "device_id": self.device_ids[email]})

            except Exception as e:
                self.log('WARNING', f"Koneksi WebSocket terputus: {e}", {"email": email, "proxy": proxy_url, "device_id": self.device_ids[email]})
                if rotate_proxy and use_proxy:
                    self.rotate_proxy_for_account(email)
                    self.log('INFO', "Mencoba proksi baru...", {"email": email, "proxy": self.account_proxies.get(email), "device_id": self.device_ids[email]})
                await asyncio.sleep(10) # Tunggu sebelum mencoba lagi
            
            finally:
                if send_ping_task and not send_ping_task.done():
                    send_ping_task.cancel()
                if session:
                    await session.close()

    async def process_check_connection(self, email: str, use_proxy: bool, rotate_proxy: bool):
        """Memproses pemeriksaan koneksi dengan rotasi proksi jika perlu."""
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            if await self.check_connection(email, proxy):
                return True
            if not rotate_proxy:
                return False # Gagal jika tidak ada rotasi
            self.rotate_proxy_for_account(email)
            self.log('INFO', "Mencoba proksi baru...", {"email": email, "proxy": self.account_proxies.get(email), "device_id": self.device_ids[email]})
            await asyncio.sleep(1)

    async def process_auth_login(self, email: str, use_proxy: bool, rotate_proxy: bool):
        """Memproses alur login lengkap."""
        if not await self.process_check_connection(email, use_proxy, rotate_proxy):
            self.log('ERROR', "Tidak dapat membuat koneksi, membatalkan login.", {"email": email, "proxy": "N/A", "device_id": self.device_ids[email]})
            return False
            
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None
        login = await self.auth_login(email, proxy)
        if login and login.get("code") == 0:
            self.access_tokens[email] = login["data"]["access_token"]
            self.refresh_tokens[email] = login["data"]["refresh_token"]
            self.expires_times[email] = login["data"]["expires_at"]
            self.log('SUCCESS', "Login berhasil.", {"email": email, "proxy": proxy, "device_id": self.device_ids[email]})
            return True
        elif login:
            self.log('ERROR', f"Login gagal: {login.get('msg')}", {"email": email, "proxy": proxy, "device_id": self.device_ids[email]})
        return False

    async def process_auth_refresh(self, email: str, use_proxy: bool):
        """Tugas latar belakang untuk memperbarui token secara berkala."""
        while True:
            now_time = int(time.time())
            # Refresh 5 menit sebelum token kedaluwarsa
            refresh_delay = self.expires_times.get(email, now_time) - now_time - 300
            if refresh_delay > 0:
                await asyncio.sleep(refresh_delay)
            
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            refresh = await self.auth_refresh(email, proxy)
            if refresh and refresh.get("code") == 0:
                self.access_tokens[email] = refresh["data"]["access_token"]
                self.refresh_tokens[email] = refresh["data"]["refresh_token"]
                self.expires_times[email] = refresh["data"]["expires_at"]
                self.log('SUCCESS', "Token berhasil diperbarui.", {"email": email, "proxy": proxy, "device_id": self.device_ids[email]})
            elif refresh:
                self.log('ERROR', f"Gagal memperbarui token: {refresh.get('msg')}", {"email": email, "proxy": proxy, "device_id": self.device_ids[email]})
                await asyncio.sleep(60) # Coba lagi setelah 1 menit jika gagal
            else:
                await asyncio.sleep(60)

    async def process_register_webnodes(self, email: str, use_proxy: bool):
        """Memproses pendaftaran webnode."""
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None
        register = await self.register_webnodes(email, proxy)
        if register and register.get("code") == 0:
            self.log('SUCCESS', "Registrasi webnode berhasil.", {"email": email, "proxy": proxy, "device_id": self.device_ids[email]})
            return True
        elif register:
            self.log('ERROR', f"Registrasi webnode gagal: {register.get('msg')}", {"email": email, "proxy": proxy, "device_id": self.device_ids[email]})
        return False
        
    async def process_accounts(self, email: str, use_proxy: bool, rotate_proxy: bool):
        """Alur kerja utama untuk setiap akun."""
        if not await self.process_auth_login(email, use_proxy, rotate_proxy):
            return
        if not await self.process_register_webnodes(email, use_proxy):
            return

        await asyncio.gather(
            self.process_auth_refresh(email, use_proxy),
            self.connect_websocket(email, use_proxy, rotate_proxy)
        )

    async def main(self):
        """Fungsi utama untuk menjalankan bot."""
        self.welcome()
        accounts = self.load_accounts()
        if not accounts:
            self.log('ERROR', "Tidak ada akun yang dimuat. Bot berhenti.")
            return
        
        use_proxy_choice, rotate_proxy = self.print_question()
        use_proxy = use_proxy_choice in [1, 2]

        self.welcome() # Clear screen again and show banner
        self.log('INFO', f"Total akun yang akan diproses: {Fore.GREEN}{len(accounts)}")

        if use_proxy:
            await self.load_proxies(use_proxy_choice)
            if not self.proxies:
                self.log('ERROR', "Tidak ada proksi yang tersedia. Bot berhenti.")
                return

        print(f"\n{Fore.CYAN}{'='*75}{Style.RESET_ALL}\n")

        tasks = []
        for account in accounts:
            email = account.get("Email")
            password = account.get("Password")

            if not email or not password or "@" not in email:
                self.log('WARNING', f"Data akun tidak valid dilewati: {account}")
                continue

            user_agent = FakeUserAgent().random
            
            self.BASE_HEADERS[email] = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Lang": self.LANGUAGE,
                "Origin": "https://edge.titannet.info",
                "Referer": "https://edge.titannet.info/",
                "User-Agent": user_agent
            }
            
            self.WS_HEADERS[email] = {
                "User-Agent": user_agent
            }

            self.password[email] = password
            self.device_ids[email] = self.generate_device_id()

            tasks.append(self.process_accounts(email, use_proxy, rotate_proxy))

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        bot = Titan()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Bot dihentikan oleh pengguna.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}{Style.BRIGHT}Terjadi kesalahan fatal: {e}{Style.RESET_ALL}")
