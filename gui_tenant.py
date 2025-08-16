import os
import sys
import threading
import subprocess
import queue
import re
import time
import signal
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json

# Konsol unicode güvenliği
for _s in (sys.stdout, sys.stderr):
    try:
        _.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ---- Doğrulama fonksiyonları ----
ALIAS_RE = re.compile(r"^[a-z0-9_]+$")  # küçük harf, rakam, altçizgi

def validate_inputs(alias, domain, name, admin_user, admin_email, admin_pass):
    """Kullanıcı girişlerini doğrular"""
    if not alias or not ALIAS_RE.match(alias):
        return False, "❌ Alias sadece küçük harf, rakam ve altçizgi içermelidir\n(örn: firma1, demir_ltd)"
    if not domain or "." not in domain:
        return False, "❌ Geçerli bir domain girin\n(örn: firma1.localhost)"
    if not name:
        return False, "❌ Firma adı boş olamaz"
    if not admin_user:
        return False, "❌ Admin kullanıcı adı boş olamaz"
    if not admin_email or "@" not in admin_email:
        return False, "❌ Geçerli bir admin e-posta girin"
    if not admin_pass:
        return False, "❌ Admin şifresi boş olamaz"
    return True, ""

class ModernStyle:
    """Modern UI stilleri"""
    # Renkler
    PRIMARY = "#2563eb"      # Mavi
    SUCCESS = "#059669"      # Yeşil
    WARNING = "#d97706"      # Turuncu
    ERROR = "#dc2626"        # Kırmızı
    SECONDARY = "#6b7280"    # Gri
    BACKGROUND = "#f8fafc"   # Açık gri
    SURFACE = "#ffffff"      # Beyaz
    TEXT = "#1f2937"         # Koyu gri
    TEXT_LIGHT = "#6b7280"   # Açık gri

    @staticmethod
    def configure_styles():
        """TTK stillerini yapılandır"""
        style = ttk.Style()
        
        # Modern buton stilleri
        style.configure("Primary.TButton",
                       background=ModernStyle.PRIMARY,
                       foreground="black",
                       borderwidth=0,
                       focuscolor="none",
                       padding=(20, 10))
        
        style.configure("Success.TButton",
                       background=ModernStyle.SUCCESS,
                       foreground="black",
                       borderwidth=0,
                       focuscolor="none",
                       padding=(15, 8))
        
        style.configure("Warning.TButton",
                       background=ModernStyle.WARNING,
                       foreground="black",
                       borderwidth=0,
                       focuscolor="none",
                       padding=(15, 8))
        
        style.configure("Error.TButton",
                       background=ModernStyle.ERROR,
                       foreground="black",
                       borderwidth=0,
                       focuscolor="none",
                       padding=(15, 8))
        
        # Modern entry stilleri
        style.configure("Modern.TEntry",
                       fieldbackground="white",
                       borderwidth=1,
                       relief="solid",
                       padding=(10, 8))
        
        # Modern label stilleri
        style.configure("Title.TLabel",
                       font=("Segoe UI", 12, "bold"),
                       foreground=ModernStyle.TEXT)
        
        style.configure("Subtitle.TLabel",
                       font=("Segoe UI", 10),
                       foreground=ModernStyle.TEXT_LIGHT)
        
        style.configure("Status.TLabel",
                       font=("Segoe UI", 9, "bold"),
                       padding=(8, 4))

class StatusIndicator(ttk.Frame):
    """Modern durum göstergesi"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.status_var = tk.StringVar(value="●")
        self.text_var = tk.StringVar(value="Kapalı")
        
        self.status_label = ttk.Label(self, textvariable=self.status_var, 
                                     font=("Segoe UI", 16), foreground="red")
        self.text_label = ttk.Label(self, textvariable=self.text_var, 
                                   style="Status.TLabel")
        
        self.status_label.pack(side="left", padx=(0, 8))
        self.text_label.pack(side="left")
    
    def set_status(self, running: bool, text: str = ""):
        if running:
            self.status_var.set("●")
            self.status_label.config(foreground=ModernStyle.SUCCESS)
            self.text_var.set(f"Çalışıyor - {text}" if text else "Çalışıyor")
        else:
            self.status_var.set("●")
            self.status_label.config(foreground=ModernStyle.ERROR)
            self.text_var.set("Kapalı")

class LogViewer(ttk.Frame):
    """Gelişmiş log görüntüleyici"""
    def __init__(self, parent, title="Log", **kwargs):
        super().__init__(parent, **kwargs)
        
        # Başlık ve kontroller
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 8))
        
        ttk.Label(header, text=title, style="Title.TLabel").pack(side="left")
        
        controls = ttk.Frame(header)
        controls.pack(side="right")
        
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(controls, text="Otomatik Kaydır", 
                       variable=self.auto_scroll_var).pack(side="left", padx=(0, 8))
        
        ttk.Button(controls, text="📋 Kopyala", 
                  command=self.copy_log).pack(side="left", padx=(0, 4))
        ttk.Button(controls, text="🗑️ Temizle", 
                  command=self.clear_log).pack(side="left")
        
        # Log metni
        log_frame = ttk.Frame(self)
        log_frame.pack(fill="both", expand=True)
        
        self.text = tk.Text(log_frame, wrap="word", height=12,
                           font=("Consolas", 9),
                           bg="#1e1e1e", fg="#ffffff",
                           insertbackground="white")
        self.text.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.text.yview)
        scrollbar.pack(side="right", fill="y")
        self.text.configure(yscrollcommand=scrollbar.set)
        
        # Renk etiketleri
        self.text.tag_configure("success", foreground="#4ade80")
        self.text.tag_configure("error", foreground="#f87171")
        self.text.tag_configure("warning", foreground="#fbbf24")
        self.text.tag_configure("info", foreground="#60a5fa")
        self.text.tag_configure("timestamp", foreground="#9ca3af")
    
    def append(self, text: str, tag: str = None):
        """Log'a metin ekle"""
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        
        self.text.insert("end", timestamp, "timestamp")
        self.text.insert("end", text)
        
        if tag:
            start_idx = self.text.index("end-1c linestart +1c")
            end_idx = self.text.index("end-1c")
            self.text.tag_add(tag, start_idx, end_idx)
        
        if self.auto_scroll_var.get():
            self.text.see("end")
    
    def clear_log(self):
        """Log'u temizle"""
        self.text.delete("1.0", "end")
    
    def copy_log(self):
        """Log içeriğini panoya kopyala"""
        content = self.text.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo("Bilgi", "Log içeriği panoya kopyalandı!")

class TenantCreatorTab(ttk.Frame):
    """Tenant oluşturma sekmesi"""
    def __init__(self, parent, log_callback):
        super().__init__(parent)
        self.log_callback = log_callback
        self.setup_ui()
        
    def setup_ui(self):
        # Ana form
        form_frame = ttk.LabelFrame(self, text="🏢 Tenant Bilgileri", padding=20)
        form_frame.pack(fill="x", padx=20, pady=20)
        
        # Form alanları
        self.var_alias = tk.StringVar()
        self.var_domain = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_admin_user = tk.StringVar(value="admin")
        self.var_admin_email = tk.StringVar(value="admin@example.com")
        self.var_admin_pass = tk.StringVar(value="")
        self.var_persist = tk.BooleanVar(value=True)
        
        self.create_form_field(form_frame, "Firma Kısaltması:", self.var_alias, 
                              "Sadece küçük harf, rakam ve _ kullanın (örn: firma1)", 0)
        self.create_form_field(form_frame, "Domain Adresi:", self.var_domain, 
                              "Firma'nın erişim adresi (örn: firma1.localhost)", 1)
        self.create_form_field(form_frame, "Firma Adı:", self.var_name, 
                              'Tam firma adı (örn: "Firma 1 Ltd. Şti.")', 2)
        self.create_form_field(form_frame, "Admin Kullanıcı:", self.var_admin_user, 
                              "Sistem yöneticisi kullanıcı adı", 3)
        self.create_form_field(form_frame, "Admin E-posta:", self.var_admin_email, 
                              "Sistem yöneticisi e-posta adresi", 4)
        self.create_form_field(form_frame, "Admin Şifre:", self.var_admin_pass, 
                              "Sistem yöneticisi şifresi", 5, show="*")
        
        # Persist seçeneği
        ttk.Checkbutton(form_frame, text="📁 Veritabanı ayarlarını kalıcı olarak kaydet", 
                       variable=self.var_persist).grid(row=6, column=0, columnspan=3, 
                                                      sticky="w", pady=(15, 0))
        
        # Hızlı erişim bağlantıları
        links_frame = ttk.LabelFrame(self, text="🔗 Hızlı Erişim", padding=15)
        links_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ttk.Button(links_frame, text="🌐 Frontend'i Aç (Port 3000)", 
                  command=self.open_frontend, style="Primary.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(links_frame, text="⚙️ Admin Paneli (Port 8000)", 
                  command=self.open_admin, style="Primary.TButton").pack(side="left")
        
        # Kontrol butonları
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.btn_create = ttk.Button(control_frame, text="✨ Tenant Oluştur", 
                                    command=self.create_tenant, style="Success.TButton")
        self.btn_create.pack(side="right", padx=(10, 0))
        
        ttk.Button(control_frame, text="🗑️ Formu Temizle", 
                  command=self.clear_form).pack(side="right")
        
        # Alias değiştikçe domain'i otomatik güncelle
        self.var_alias.trace_add("write", self.on_alias_change)
        
        # İlk odağı alias alanına ver
        self.focus_first_entry(form_frame)
    
    def create_form_field(self, parent, label, variable, hint, row, show=None):
        """Modern form alanı oluştur"""
        ttk.Label(parent, text=label, style="Title.TLabel").grid(
            row=row, column=0, sticky="w", pady=(8, 4))
        
        entry = ttk.Entry(parent, textvariable=variable, width=50, 
                         style="Modern.TEntry", show=show)
        entry.grid(row=row, column=1, sticky="ew", pady=(8, 4), padx=(10, 0))
        
        ttk.Label(parent, text=hint, style="Subtitle.TLabel").grid(
            row=row, column=2, sticky="w", pady=(8, 4), padx=(10, 0))
        
        parent.columnconfigure(1, weight=1)
    
    def focus_first_entry(self, frame):
        """İlk entry alanına odak ver"""
        for child in frame.winfo_children():
            if isinstance(child, ttk.Entry):
                child.focus_set()
                break
    
    def on_alias_change(self, *_):
        """Alias değiştiğinde domain'i otomatik güncelle"""
        alias = self.var_alias.get().strip()
        current_domain = self.var_domain.get().strip()
        
        if alias and (not current_domain or current_domain.endswith(".localhost")):
            self.var_domain.set(f"{alias}.localhost")
    
    def clear_form(self):
        """Formu temizle"""
        self.var_alias.set("")
        self.var_domain.set("")
        self.var_name.set("")
        self.var_admin_user.set("admin")
        self.var_admin_email.set("admin@example.com")
        self.var_admin_pass.set("")
        self.var_persist.set(True)
    
    def open_frontend(self):
        """Frontend'i tarayıcıda aç"""
        domain = self.var_domain.get().strip()
        if not domain:
            messagebox.showwarning("Uyarı", "Önce domain adresini girin!")
            return
        
        url = f"http://{domain}:3000/login"
        webbrowser.open(url)
        self.log_callback(f"🌐 Frontend açıldı: {url}\n", "info")
    
    def open_admin(self):
        """Admin panelini tarayıcıda aç"""
        domain = self.var_domain.get().strip()
        if not domain:
            messagebox.showwarning("Uyarı", "Önce domain adresini girin!")
            return
        
        url = f"http://{domain}:8000/admin"
        webbrowser.open(url)
        self.log_callback(f"⚙️ Admin paneli açıldı: {url}\n", "info")
    
    def create_tenant(self):
        """Tenant oluştur"""
        # Değerleri al ve doğrula
        alias = self.var_alias.get().strip()
        domain = self.var_domain.get().strip()
        name = self.var_name.get().strip()
        admin_user = self.var_admin_user.get().strip()
        admin_email = self.var_admin_email.get().strip()
        admin_pass = self.var_admin_pass.get().strip()
        persist = self.var_persist.get()
        
        # Doğrulama
        is_valid, error_msg = validate_inputs(alias, domain, name, admin_user, admin_email, admin_pass)
        if not is_valid:
            messagebox.showerror("Hata", error_msg)
            return
        
        # Komutu hazırla
        cmd = [
            sys.executable, "create_tenant.py",
            "--alias", alias,
            "--domain", domain,
            "--name", name,
            "--admin-username", admin_user,
            "--admin-email", admin_email,
            "--admin-password", admin_pass,
        ]
        
        if persist:
            cmd.append("--persist")
        
        # Formu devre dışı bırak
        self.set_form_state("disabled")
        
        self.log_callback(f"🚀 Tenant oluşturma başlatıldı...\n", "info")
        self.log_callback(f"📋 Komut: {' '.join(cmd)}\n", "info")
        
        # Arka planda çalıştır
        threading.Thread(target=self.run_create_tenant, args=(cmd,), daemon=True).start()
    
    def run_create_tenant(self, cmd):
        """Tenant oluşturma komutunu çalıştır"""
        try:
            env = os.environ.copy()
            env["PYTHONUTF8"] = "1"
            
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                cwd=os.getcwd(),
                env=env,
            )
            
            # Çıktıyı oku
            for line in proc.stdout:
                self.log_callback(line)
            
            # Sonucu kontrol et
            return_code = proc.wait()
            
            if return_code == 0:
                self.log_callback("✅ Tenant başarıyla oluşturuldu!\n", "success")
                messagebox.showinfo("Başarılı", "🎉 Tenant başarıyla oluşturuldu!\n\nArtık hızlı erişim bağlantılarını kullanabilirsiniz.")
            else:
                self.log_callback(f"❌ İşlem başarısız oldu (Çıkış kodu: {return_code})\n", "error")
                messagebox.showerror("Hata", f"Tenant oluşturma başarısız!\nÇıkış kodu: {return_code}\n\nDetaylar için log'u kontrol edin.")
                
        except Exception as e:
            self.log_callback(f"💥 Kritik hata: {e}\n", "error")
            messagebox.showerror("Kritik Hata", f"Beklenmeyen bir hata oluştu:\n{e}")
        
        finally:
            # Formu yeniden etkinleştir
            self.after(100, lambda: self.set_form_state("normal"))
    
    def set_form_state(self, state):
        """Form öğelerinin durumunu değiştir"""
        self.btn_create.config(state=state)
        
        def update_widgets(widget):
            for child in widget.winfo_children():
                if isinstance(child, (ttk.Entry, ttk.Checkbutton, ttk.Button)):
                    try:
                        if hasattr(child, 'cget') and child.cget('text') != '🗑️ Formu Temizle':
                            child.config(state=state)
                    except:
                        pass
                else:
                    update_widgets(child)
        
        update_widgets(self)

class ServerControlTab(ttk.Frame):
    """Sunucu kontrol sekmesi"""
    def __init__(self, parent, log_callback):
        super().__init__(parent)
        self.log_callback = log_callback
        self.proc_django = None
        self.proc_frontend = None
        self.setup_ui()
    
    def setup_ui(self):
        # Django sunucu kontrolleri
        django_frame = ttk.LabelFrame(self, text="🐍 Django Sunucu Kontrolü", padding=20)
        django_frame.pack(fill="x", padx=20, pady=20)
        
        # Django ayarları
        self.var_dj_host = tk.StringVar(value="0.0.0.0")
        self.var_dj_port = tk.StringVar(value="8000")
        self.var_dj_settings = tk.StringVar(value="avukatlik_portali.settings.rowlevel")
        
        self.create_server_field(django_frame, "Host Adresi:", self.var_dj_host, 
                                "Sunucu IP adresi (0.0.0.0 = tüm arayüzler)", 0)
        self.create_server_field(django_frame, "Port:", self.var_dj_port, 
                                "Sunucu port numarası", 1)
        self.create_server_field(django_frame, "Settings Modülü:", self.var_dj_settings, 
                                "Django ayarlar modülü", 2)
        
        # Django kontrolleri
        django_controls = ttk.Frame(django_frame)
        django_controls.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(15, 10))
        
        self.django_status = StatusIndicator(django_controls)
        self.django_status.pack(side="left")
        
        controls_right = ttk.Frame(django_controls)
        controls_right.pack(side="right")
        
        self.btn_django_start = ttk.Button(controls_right, text="▶️ Başlat", 
                                          command=self.start_django, style="Success.TButton")
        self.btn_django_stop = ttk.Button(controls_right, text="⏹️ Durdur", 
                                         command=self.stop_django, style="Error.TButton", state="disabled")
        
        self.btn_django_start.pack(side="left", padx=(0, 8))
        self.btn_django_stop.pack(side="left")
        
        # Frontend kontrolleri
        frontend_frame = ttk.LabelFrame(self, text="⚛️ Frontend Kontrolü (npm)", padding=20)
        frontend_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Frontend ayarları
        self.var_fe_dir = tk.StringVar(value=os.path.join(os.getcwd(), "frontend"))
        
        fe_dir_frame = ttk.Frame(frontend_frame)
        fe_dir_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        
        ttk.Label(fe_dir_frame, text="Frontend Klasörü:", style="Title.TLabel").pack(side="left")
        
        fe_entry = ttk.Entry(fe_dir_frame, textvariable=self.var_fe_dir, 
                            style="Modern.TEntry", width=60)
        fe_entry.pack(side="left", fill="x", expand=True, padx=(10, 8))
        
        ttk.Button(fe_dir_frame, text="📁 Seç", 
                  command=self.browse_frontend).pack(side="right")
        
        # Frontend kontrolleri
        frontend_controls = ttk.Frame(frontend_frame)
        frontend_controls.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        self.frontend_status = StatusIndicator(frontend_controls)
        self.frontend_status.pack(side="left")
        
        fe_controls_right = ttk.Frame(frontend_controls)
        fe_controls_right.pack(side="right")
        
        self.btn_frontend_start = ttk.Button(fe_controls_right, text="▶️ Başlat", 
                                           command=self.start_frontend, style="Success.TButton")
        self.btn_frontend_stop = ttk.Button(fe_controls_right, text="⏹️ Durdur", 
                                          command=self.stop_frontend, style="Error.TButton", state="disabled")
        
        self.btn_frontend_start.pack(side="left", padx=(0, 8))
        self.btn_frontend_stop.pack(side="left")
        
        frontend_frame.columnconfigure(0, weight=1)
        
        # Hızlı işlemler
        quick_frame = ttk.LabelFrame(self, text="⚡ Hızlı İşlemler", padding=15)
        quick_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ttk.Button(quick_frame, text="🚀 Her İkisini Birden Başlat", 
                  command=self.start_both, style="Primary.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(quick_frame, text="🛑 Her İkisini Birden Durdur", 
                  command=self.stop_both, style="Warning.TButton").pack(side="left")
    
    def create_server_field(self, parent, label, variable, hint, row):
        """Sunucu ayar alanı oluştur"""
        ttk.Label(parent, text=label, style="Title.TLabel").grid(
            row=row, column=0, sticky="w", pady=(5, 5))
        
        entry = ttk.Entry(parent, textvariable=variable, width=40, style="Modern.TEntry")
        entry.grid(row=row, column=1, sticky="ew", pady=(5, 5), padx=(10, 10))
        
        ttk.Label(parent, text=hint, style="Subtitle.TLabel").grid(
            row=row, column=2, sticky="w", pady=(5, 5))
        
        parent.columnconfigure(1, weight=1)
    
    def browse_frontend(self):
        """Frontend klasörü seç"""
        directory = filedialog.askdirectory(
            initialdir=self.var_fe_dir.get() or os.getcwd(),
            title="Frontend klasörü seçin"
        )
        if directory:
            self.var_fe_dir.set(directory)
    
    def start_django(self):
        """Django sunucuyu başlat"""
        if self.proc_django and self.proc_django.poll() is None:
            messagebox.showinfo("Bilgi", "Django sunucu zaten çalışıyor!")
            return
        
        host = self.var_dj_host.get().strip() or "0.0.0.0"
        port = self.var_dj_port.get().strip() or "8000"
        settings = self.var_dj_settings.get().strip() or "avukatlik_portali.settings.rowlevel"
        
        cmd = [sys.executable, "manage.py", "runserver", f"{host}:{port}"]
        
        env = os.environ.copy()
        env["DJANGO_SETTINGS_MODULE"] = settings
        env["PYTHONUTF8"] = "1"
        
        try:
            self.proc_django = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                cwd=os.getcwd(),
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
            )
            
            # UI güncellemeleri
            self.django_status.set_status(True, f"{host}:{port}")
            self.btn_django_start.config(state="disabled")
            self.btn_django_stop.config(state="normal")
            
            # Log okuma thread'i
            threading.Thread(target=self.pipe_output, 
                           args=(self.proc_django, "🐍 [Django] "), daemon=True).start()
            
            self.log_callback(f"✅ Django sunucu başlatıldı: http://{host}:{port}\n", "success")
            
        except Exception as e:
            self.log_callback(f"❌ Django başlatılamadı: {e}\n", "error")
            messagebox.showerror("Hata", f"Django sunucu başlatılamadı!\n\nHata: {e}")
    
    def stop_django(self):
        """Django sunucuyu durdur"""
        self.stop_process(self.proc_django, "Django")
        self.proc_django = None
        self.django_status.set_status(False)
        self.btn_django_start.config(state="normal")
        self.btn_django_stop.config(state="disabled")
    
    def start_frontend(self):
        """Frontend'i başlat"""
        if self.proc_frontend and self.proc_frontend.poll() is None:
            messagebox.showinfo("Bilgi", "Frontend zaten çalışıyor!")
            return
        
        fe_dir = self.var_fe_dir.get().strip()
        if not fe_dir or not os.path.isdir(fe_dir):
            messagebox.showerror("Hata", "Geçerli bir frontend klasörü seçin!")
            return
        
        # package.json kontrolü
        if not os.path.exists(os.path.join(fe_dir, "package.json")):
            messagebox.showerror("Hata", "Seçilen klasörde package.json bulunamadı!\n\nBu bir Node.js projesi değil gibi görünüyor.")
            return
        
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        cmd = [npm_cmd, "run", "dev"]
        
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        
        try:
            self.proc_frontend = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                cwd=fe_dir,
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
            )
            
            # UI güncellemeleri
            self.frontend_status.set_status(True, "npm run dev")
            self.btn_frontend_start.config(state="disabled")
            self.btn_frontend_stop.config(state="normal")
            
            # Log okuma thread'i
            threading.Thread(target=self.pipe_output, 
                           args=(self.proc_frontend, "⚛️ [Frontend] "), daemon=True).start()
            
            self.log_callback(f"✅ Frontend başlatıldı: {fe_dir}\n", "success")
            
        except FileNotFoundError:
            self.log_callback("❌ npm bulunamadı! Node.js kurulu ve PATH'te mi?\n", "error")
            messagebox.showerror("Hata", "npm komutu bulunamadı!\n\nNode.js kurulu mu ve PATH'te tanımlı mı?")
        except Exception as e:
            self.log_callback(f"❌ Frontend başlatılamadı: {e}\n", "error")
            messagebox.showerror("Hata", f"Frontend başlatılamadı!\n\nHata: {e}")
    
    def stop_frontend(self):
        """Frontend'i durdur"""
        self.stop_process(self.proc_frontend, "Frontend")
        self.proc_frontend = None
        self.frontend_status.set_status(False)
        self.btn_frontend_start.config(state="normal")
        self.btn_frontend_stop.config(state="disabled")
    
    def start_both(self):
        """Her iki servisi de başlat"""
        self.start_django()
        time.sleep(1)  # Kısa bir bekleme
        self.start_frontend()
    
    def stop_both(self):
        """Her iki servisi de durdur"""
        if self.proc_django and self.proc_django.poll() is None:
            self.stop_django()
        if self.proc_frontend and self.proc_frontend.poll() is None:
            self.stop_frontend()
    
    def pipe_output(self, process, prefix):
        """Process çıktısını log'a aktar"""
        try:
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                
                # Hata mesajlarını renklendir
                if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
                    self.log_callback(f"{prefix}{line}", "error")
                elif any(keyword in line.lower() for keyword in ['warning', 'warn']):
                    self.log_callback(f"{prefix}{line}", "warning")
                elif any(keyword in line.lower() for keyword in ['success', 'started', 'running']):
                    self.log_callback(f"{prefix}{line}", "success")
                else:
                    self.log_callback(f"{prefix}{line}")
                    
        except Exception as e:
            self.log_callback(f"{prefix}[Log okuma hatası: {e}]\n", "error")
    
    def stop_process(self, process, name):
        """Process'i güvenli şekilde durdur"""
        if not process or process.poll() is not None:
            self.log_callback(f"ℹ️ {name} zaten kapalı\n", "info")
            return
        
        self.log_callback(f"🛑 {name} durduruluyor...\n", "warning")
        
        try:
            if os.name == "nt":
                # Windows için önce Ctrl-Break dene
                try:
                    os.kill(process.pid, signal.CTRL_BREAK_EVENT)
                    time.sleep(1.5)
                except Exception:
                    pass
            
            # Terminate
            process.terminate()
            
            try:
                process.wait(timeout=5)
                self.log_callback(f"✅ {name} başarıyla durduruldu\n", "success")
            except subprocess.TimeoutExpired:
                self.log_callback(f"⚠️ {name} zaman aşımı, zorla kapatılıyor...\n", "warning")
                process.kill()
                process.wait(timeout=5)
                self.log_callback(f"🔥 {name} zorla kapatıldı\n", "warning")
                
        except Exception as e:
            self.log_callback(f"❌ {name} durdurulamadı: {e}\n", "error")


class ModernTenantGUI(tk.Tk):
    """Triencode yönetim arayüzü"""
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_styles()
        self.setup_ui()
        
        # Uygulama kapanırken çalışan process'leri temizle
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_window(self):
        """Pencere ayarları"""
        self.title("🏢 Triencode Yönetimi")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # İkon ayarla (eğer varsa)
        try:
            self.iconbitmap('icon.ico')
        except:
            pass
        
        # Pencereyi ortala
        self.center_window()
    
    def center_window(self):
        """Pencereyi ekranın ortasına yerleştir"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        """Modern stiller"""
        ModernStyle.configure_styles()
        self.configure(bg=ModernStyle.BACKGROUND)
    
    def setup_ui(self):
        """Ana arayüz"""
        # Ana başlık
        header = ttk.Frame(self)
        header.pack(fill="x", padx=20, pady=20)
        
        title_label = ttk.Label(header, text="🏢 Triencode Yönetim Sistemi", 
                               font=("Segoe UI", 16, "bold"), foreground=ModernStyle.PRIMARY)
        title_label.pack(side="left")
        
        subtitle_label = ttk.Label(header, text="", 
                                  font=("Segoe UI", 10), foreground=ModernStyle.TEXT_LIGHT)
        subtitle_label.pack(side="left", padx=(10, 0))
        
        # Notebook (sekmeler)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Log viewer (alt kısım)
        self.log_viewer = LogViewer(self, title="📋 İşlem Geçmişi")
        self.log_viewer.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Sekmeleri oluştur
        self.tenant_tab = TenantCreatorTab(self.notebook, self.log_callback)
        self.server_tab = ServerControlTab(self.notebook, self.log_callback)
        
        self.notebook.add(self.tenant_tab, text="🏢  Tenant Oluştur")
        self.notebook.add(self.server_tab, text="🔧  Sunucu Kontrol")
        
        # Durum çubuğu
        self.status_frame = ttk.Frame(self, relief="sunken", padding=5)
        self.status_frame.pack(fill="x", side="bottom")
        
        self.status_var = tk.StringVar(value="✅ Hazır")
        ttk.Label(self.status_frame, textvariable=self.status_var, 
                 font=("Segoe UI", 9)).pack(side="left")
        
        # Sağ tarafta sistem bilgileri
        info_text = f"Python {sys.version.split()[0]} | " \
                   f"Platform: {sys.platform} | " \
                   f"CWD: {os.path.basename(os.getcwd())}"
        ttk.Label(self.status_frame, text=info_text, 
                 font=("Segoe UI", 8), foreground=ModernStyle.TEXT_LIGHT).pack(side="right")
        
        # Başlangıç mesajı
        self.log_callback("🚀 Modern Tenant Yönetim Sistemi başlatıldı!\n", "success")
        self.log_callback("💡 İpucu: Önce bir tenant oluşturun, ardından sunucuları başlatın.\n", "info")
    
    def log_callback(self, text, tag=None):
        """Log mesajı ekle"""
        # Ana thread'de çalıştırmak için
        if threading.current_thread() != threading.main_thread():
            self.after(0, lambda: self.log_viewer.append(text, tag))
        else:
            self.log_viewer.append(text, tag)
        
        # Durum çubuğunu güncelle
        if tag == "success":
            self.status_var.set("✅ İşlem tamamlandı")
        elif tag == "error":
            self.status_var.set("❌ Hata oluştu")
        elif tag == "warning":
            self.status_var.set("⚠️ Uyarı")
        elif tag == "info":
            self.status_var.set("ℹ️ Bilgi")
    
    def on_closing(self):
        """Uygulama kapanırken temizlik yap"""
        try:
            # Çalışan process'leri durdur
            if hasattr(self.server_tab, 'proc_django') and self.server_tab.proc_django:
                self.server_tab.stop_django()
            if hasattr(self.server_tab, 'proc_frontend') and self.server_tab.proc_frontend:
                self.server_tab.stop_frontend()
            
            # Kısa bekleme
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Temizlik sırasında hata: {e}")
        
        finally:
            self.destroy()


def main():
    """Ana fonksiyon"""
    try:
        # Yüksek DPI desteği (Windows)
        if os.name == "nt":
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass
        
        # Uygulamayı başlat
        app = ModernTenantGUI()
        app.mainloop()
        
    except KeyboardInterrupt:
        print("\n🛑 Uygulama kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"💥 Kritik hata: {e}")
        messagebox.showerror("Kritik Hata", f"Uygulama başlatılamadı!\n\nHata: {e}")


if __name__ == "__main__":
    main()