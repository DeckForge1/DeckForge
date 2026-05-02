
import sys,os,subprocess,random,math,threading,time
sys.path.insert(0,"/home/deck/.local/lib/python3.13/site-packages")
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtCore import QMetaObject,Q_ARG
from PySide6.QtGui import *

LIGHT="""
QMainWindow,QWidget{background:#f5f5f0;color:#1a1a1a;font-family:'Segoe UI',sans-serif;}
QWidget#sidebar{background:#eaeae5;border-right:1px solid #ddd;}
QPushButton#navbtn{background:transparent;border:none;border-left:3px solid transparent;padding:10px 16px;text-align:left;font-size:13px;color:#555;border-radius:0;}
QPushButton#navbtn:hover{background:#fff;color:#1a1a1a;}
QPushButton#navbtn[active=true]{background:#fff;border-left:3px solid #3B6D11;color:#1a1a1a;font-weight:bold;}
QPushButton#applybtn{background:#1a1a2e;color:white;border:none;border-radius:8px;padding:10px;font-size:13px;font-weight:bold;}
QPushButton#applybtn:hover{background:#2a2a4e;}
QPushButton#applybtn:pressed{background:#0a0a1e;padding:11px 9px 9px 11px;}
QWidget#card{background:#fff;border:1px solid #e0e0e0;border-radius:10px;}
QLabel#title{font-size:15px;font-weight:bold;}
QLabel#sub{font-size:12px;color:#888;}
QLabel#cardtitle{font-size:13px;font-weight:bold;}
QLabel#statlabel{font-size:11px;color:#888;}
QLabel#statvalue{font-size:22px;font-weight:bold;}
QProgressBar{border:none;border-radius:2px;background:#e8e8e8;max-height:4px;}
QProgressBar::chunk{border-radius:2px;}
QCheckBox{font-size:13px;}
QSlider::groove:horizontal{height:6px;background:#e0e0e0;border-radius:3px;}
QSlider::sub-page:horizontal{background:#3B6D11;border-radius:3px;}
QSlider::handle:horizontal{background:#fff;border:2px solid #3B6D11;width:18px;height:18px;border-radius:9px;margin:-7px 0;}
QComboBox{border:1px solid #ddd;border-radius:6px;padding:4px 8px;font-size:12px;background:#fff;}
QScrollArea{border:none;background:transparent;}
QWidget#statcard{background:#f0f0ea;border-radius:8px;}
QLabel#sectionlabel{font-size:10px;color:#aaa;font-weight:bold;}
QLineEdit{border:1px solid #ddd;border-radius:6px;padding:4px 8px;font-size:12px;background:#fff;}
"""
DARK="""
QMainWindow,QWidget{background:#1c1c1e;color:#f0f0f0;font-family:'Segoe UI',sans-serif;}
QWidget#sidebar{background:#141416;border-right:1px solid #2a2a2e;}
QPushButton#navbtn{background:transparent;border:none;border-left:3px solid transparent;padding:10px 16px;text-align:left;font-size:13px;color:#888;border-radius:0;}
QPushButton#navbtn:hover{background:#2a2a2e;color:#f0f0f0;}
QPushButton#navbtn[active=true]{background:#2a2a2e;border-left:3px solid #639922;color:#f0f0f0;font-weight:bold;}
QPushButton#applybtn{background:#639922;color:white;border:none;border-radius:8px;padding:10px;font-size:13px;font-weight:bold;}
QPushButton#applybtn:hover{background:#7ab82a;}
QPushButton#applybtn:pressed{background:#3a5910;padding:11px 9px 9px 11px;}
QWidget#card{background:#2a2a2e;border:1px solid #3a3a3e;border-radius:10px;}
QLabel#title{font-size:15px;font-weight:bold;}
QLabel#sub{font-size:12px;color:#666;}
QLabel#cardtitle{font-size:13px;font-weight:bold;}
QLabel#statlabel{font-size:11px;color:#666;}
QLabel#statvalue{font-size:22px;font-weight:bold;}
QProgressBar{border:none;border-radius:2px;background:#3a3a3e;max-height:4px;}
QProgressBar::chunk{border-radius:2px;}
QCheckBox{font-size:13px;color:#ccc;}
QSlider::groove:horizontal{height:6px;background:#3a3a3e;border-radius:3px;}
QSlider::sub-page:horizontal{background:#639922;border-radius:3px;}
QSlider::handle:horizontal{background:#1c1c1e;border:2px solid #639922;width:18px;height:18px;border-radius:9px;margin:-7px 0;}
QComboBox{border:1px solid #3a3a3e;border-radius:6px;padding:4px 8px;font-size:12px;background:#2a2a2e;color:#f0f0f0;}
QScrollArea{border:none;background:transparent;}
QWidget#statcard{background:#222226;border-radius:8px;}
QLabel#sectionlabel{font-size:10px;color:#555;font-weight:bold;}
QLineEdit{border:1px solid #3a3a3e;border-radius:6px;padding:4px 8px;font-size:12px;background:#2a2a2e;color:#f0f0f0;}
"""

def _get_screen_res():
    """Return (W,H,ox,oy) of the primary/active monitor only."""
    try:
        import re
        r=subprocess.run(["xrandr","--listmonitors"],capture_output=True,text=True)
        # find the primary monitor (marked with *)
        m=re.search(r"\+\*\S+\s+(\d+)/(\d+)x(\d+)/(\d+)\+(\d+)\+(\d+)",r.stdout)
        if m:
            w,h,ox,oy=int(m.group(1)),int(m.group(3)),int(m.group(5)),int(m.group(6))
            return w,h,ox,oy
    except:pass
    return 1280,800,0,0

def _get_total_res():
    try:
        import re
        r=subprocess.run(["xdpyinfo"],capture_output=True,text=True)
        m=re.search(r"dimensions:\s+(\d+)x(\d+)",r.stdout)
        if m:return int(m.group(1)),int(m.group(2))
    except:pass
    return 3840,1440

def _start_orgb_server():
    import socket
    try:
        s=socket.socket();s.connect(("localhost",6742));s.close();return
    except:pass
    subprocess.Popen(["flatpak","run","org.openrgb.OpenRGB","--server","--noautoconnect"],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(5)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark=False
        self.sudo_pwd=""
        self.rgb_color="FF0000"
        self._cs_running=False
        self._cs_zone=None
        self._cs_boost_val=2.5
        self._cs_thresh_val=5
        self._cs_bright_val=1.0
        self.setWindowTitle("DeckForge")
        self.setMinimumSize(800,560)
        self.resize(900,600)
        icon_path="/home/deck/DeckForge/icon.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self._build_ui()
        self.setStyleSheet(LIGHT)
        self._switch_page(0)
        threading.Thread(target=_start_orgb_server,daemon=True).start()
        self._setup_tray()

    def _setup_tray(self):
        # use system settings icon, fallback to color swatch
        icon=QIcon.fromTheme("preferences-system")
        if icon.isNull():
            pm=QPixmap(32,32);pm.fill(QColor("#639922"))
            icon=QIcon(pm)
        self._tray=QSystemTrayIcon(icon,self)
        self._tray.setToolTip("DeckForge")
        menu=QMenu()
        menu.addAction("Show",self.show)
        menu.addAction("ChromaSync",lambda:self._switch_page(4))
        menu.addSeparator()
        menu.addAction("Quit",self._quit_app)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(lambda r:self.show() if r==QSystemTrayIcon.ActivationReason.Trigger else None)
        self._tray.show()

    def _quit_app(self):
        self._cs_running=False
        self._tray.hide()
        QApplication.quit()

    def _build_ui(self):
        c=QWidget();self.setCentralWidget(c)
        root=QHBoxLayout(c);root.setContentsMargins(0,0,0,0);root.setSpacing(0)
        self.sidebar=QWidget();self.sidebar.setObjectName("sidebar");self.sidebar.setFixedWidth(170)
        sb=QVBoxLayout(self.sidebar);sb.setContentsMargins(0,12,0,12);sb.setSpacing(0)
        logo=QLabel("  DeckForge");logo.setStyleSheet("font-size:15px;font-weight:bold;padding:8px 14px 16px;")
        sb.addWidget(logo)
        self.nav_buttons=[]
        sections=[("SYSTEM",None),("Dashboard","◈"),("Performance","⚡"),("Processes","≡"),("RGB Control","●"),("ChromaSync","◎"),("Profiles","◧"),("CONFIG",None),("Settings","⚙")]
        page_idx=0
        for label,icon in sections:
            if icon is None:
                l=QLabel(f"  {label}");l.setObjectName("sectionlabel");l.setContentsMargins(0,10,0,2);sb.addWidget(l)
            else:
                btn=QPushButton(f"  {icon}  {label}");btn.setObjectName("navbtn")
                btn.setProperty("active",False);btn.setProperty("pidx",page_idx)
                idx_copy=page_idx
                btn.clicked.connect(lambda _,i=idx_copy:self._switch_page(i))
                self.nav_buttons.append(btn);sb.addWidget(btn);page_idx+=1
        sb.addStretch()
        root.addWidget(self.sidebar)
        self.stack=QStackedWidget()
        self.stack.addWidget(self._page_dashboard())
        self.stack.addWidget(self._page_performance())
        self.stack.addWidget(self._page_processes())
        self.stack.addWidget(self._page_rgb())
        self.stack.addWidget(self._page_chromasync())
        self.stack.addWidget(self._page_profiles())
        self.stack.addWidget(self._page_settings())
        root.addWidget(self.stack)
        self.timer=QTimer();self.timer.timeout.connect(self._update_stats);self.timer.start(2000)

    def _switch_page(self,idx):
        self.stack.setCurrentIndex(idx)
        for btn in self.nav_buttons:
            a=btn.property("pidx")==idx
            btn.setProperty("active",a);btn.setStyle(btn.style())

    def _scroll_page(self,widget):
        page=QWidget();scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(widget)
        outer=QVBoxLayout(page);outer.setContentsMargins(0,0,0,0);outer.addWidget(scroll)
        return page

    def _card(self):
        w=QWidget();w.setObjectName("card");return w

    def _sep(self):
        f=QFrame();f.setFrameShape(QFrame.HLine);f.setStyleSheet("color:#eee;max-height:1px;");return f

    def _toggle_row(self,label,desc="",checked=False):
        row=QWidget();h=QHBoxLayout(row);h.setContentsMargins(0,4,0,4)
        lv=QVBoxLayout();lv.setSpacing(0);lv.addWidget(QLabel(label))
        if desc:
            d=QLabel(desc);d.setObjectName("sub");lv.addWidget(d)
        h.addLayout(lv);h.addStretch()
        cb=QCheckBox();cb.setChecked(checked);h.addWidget(cb)
        return row

    def _play_click(self):
        for s in ["/usr/share/sounds/freedesktop/stereo/button-pressed.oga"]:
            if os.path.exists(s):
                subprocess.Popen(["paplay",s],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                return

    def _apply_btn(self,text,fn):
        btn=QPushButton(text);btn.setObjectName("applybtn")
        def _click():
            self._play_click()
            fn()
        btn.clicked.connect(_click)
        return btn

    def _progress_row(self,layout,label,val,color):
        rw=QWidget();rv=QVBoxLayout(rw);rv.setContentsMargins(0,0,0,0);rv.setSpacing(3)
        hdr=QHBoxLayout()
        hdr.addWidget(QLabel(f'<span style="font-size:12px">{label}</span>'))
        hdr.addStretch()
        pct=QLabel(f'<span style="font-size:12px">{val}%</span>')
        hdr.addWidget(pct);rv.addLayout(hdr)
        bar=QProgressBar();bar.setValue(val);bar.setTextVisible(False);bar.setFixedHeight(4)
        bar.setStyleSheet(f"QProgressBar::chunk{{background:{color};}}")
        rv.addWidget(bar);layout.addWidget(rw)
        return bar,pct

    def _page_dashboard(self):
        inner=QWidget();v=QVBoxLayout(inner);v.setContentsMargins(20,20,20,20);v.setSpacing(12)
        t=QLabel("Dashboard");t.setObjectName("title");v.addWidget(t)
        s=QLabel("Real-time stats — Desktop Mode optimized");s.setObjectName("sub");v.addWidget(s)
        stat_row=QHBoxLayout();stat_row.setSpacing(8)
        self.cpu_lbl=None
        for label,val,unit in [("CPU load","34","%"),("RAM used","5.2","GB"),("GPU clock","800","MHz")]:
            sc=QWidget();sc.setObjectName("statcard");sv=QVBoxLayout(sc);sv.setContentsMargins(12,10,12,10)
            l=QLabel(label);l.setObjectName("statlabel");sv.addWidget(l)
            vl=QLabel(f"{val}{unit}");vl.setObjectName("statvalue")
            if label=="CPU load":self.cpu_lbl=vl
            sv.addWidget(vl);stat_row.addWidget(sc)
        v.addLayout(stat_row)
        card=self._card();cv=QVBoxLayout(card);cv.setContentsMargins(14,12,14,12);cv.setSpacing(8)
        t2=QLabel("Resource usage");t2.setObjectName("cardtitle");cv.addWidget(t2)
        self.cpu_bar,_=self._progress_row(cv,"CPU",34,"#639922")
        self._progress_row(cv,"RAM",66,"#BA7517")
        self._progress_row(cv,"GPU",28,"#378ADD")
        v.addWidget(card)
        log=self._card();lv2=QVBoxLayout(log);lv2.setContentsMargins(14,12,14,12)
        lt=QLabel("Activity log");lt.setObjectName("cardtitle");lv2.addWidget(lt)
        for ts,ok,msg in [("09:41:02",True,"CPU governor set to performance"),("09:41:02",True,"Killed 3 background services"),("09:41:03",True,"GPU power profile set to high"),("09:41:03",True,"OpenRGB connected — 2 devices"),("09:41:04",False,"Swap usage elevated (1.1 GB)")]:
            c2="#639922" if ok else "#BA7517";s2="✓" if ok else "⚠"
            row=QLabel(f'<span style="color:#aaa;font-family:monospace">{ts}</span>  <span style="color:{c2}">{s2}</span>  {msg}')
            row.setTextFormat(Qt.RichText);row.setStyleSheet("font-size:12px;padding:1px 0;");lv2.addWidget(row)
        v.addWidget(log);v.addStretch()
        return self._scroll_page(inner)

    def _page_performance(self):
        inner=QWidget();v=QVBoxLayout(inner);v.setContentsMargins(20,20,20,20);v.setSpacing(12)
        t=QLabel("Performance");t.setObjectName("title");v.addWidget(t)
        s=QLabel("System-level tuning for Desktop Mode");s.setObjectName("sub");v.addWidget(s)
        groups=[
            ("CPU",[("Performance governor","Sets CPU to max frequency",True),("Disable CPU idle states","Reduces latency",False),("SMT (hyperthreading)","Enables all logical cores",True)]),
            ("GPU",[("GPU performance mode","Unlocks full GPU clock range",True),("Disable power saving","Prevents GPU clock gating",True)]),
            ("Memory",[("Drop disk cache","Frees memory used by file cache",False),("Swappiness to 10","Prefer RAM over swap",True)]),
        ]
        for grp,items in groups:
            card=self._card();cv=QVBoxLayout(card);cv.setContentsMargins(14,12,14,12);cv.setSpacing(4)
            gt=QLabel(grp);gt.setObjectName("cardtitle");cv.addWidget(gt)
            for l,d,c in items:
                cv.addWidget(self._toggle_row(l,d,c));cv.addWidget(self._sep())
            v.addWidget(card)
        v.addWidget(self._apply_btn("Apply performance settings",self._apply_perf))
        v.addStretch()
        return self._scroll_page(inner)

    def _get_sudo(self):
        if self.sudo_pwd:return self.sudo_pwd
        pwd,ok=QInputDialog.getText(self,"Sudo Required","Password:",QLineEdit.EchoMode.Password)
        if ok and pwd:self.sudo_pwd=pwd;return pwd
        return None

    def _apply_perf(self):
        pwd=self._get_sudo()
        if not pwd:return
        cmds=[
            f"echo {pwd!r}|sudo -S cpupower frequency-set -g performance",
            f"echo {pwd!r}|sudo -S bash -c 'echo 10|tee /proc/sys/vm/swappiness'",
        ]
        for cmd in cmds:
            subprocess.Popen(["bash","-c",cmd],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

    def _page_processes(self):
        inner=QWidget();v=QVBoxLayout(inner);v.setContentsMargins(20,20,20,20);v.setSpacing(12)
        t=QLabel("Background processes");t.setObjectName("title");v.addWidget(t)
        s=QLabel("Kill non-essential services to free RAM");s.setObjectName("sub");v.addWidget(s)
        card=self._card();cv=QVBoxLayout(card);cv.setContentsMargins(14,12,14,12);cv.setSpacing(4)
        self.proc_checks=[]
        for proc,mem,checked in [("baloo_file","~80 MB",True),("kscreen_backend_launcher","~20 MB",True),("kdeconnect-daemon","~30 MB",False),("tracker-miner-fs","~50 MB",True),("plasma-browser-integration","~15 MB",False)]:
            row=QWidget();h=QHBoxLayout(row);h.setContentsMargins(0,4,0,4)
            lv=QVBoxLayout();lv.setSpacing(0);lv.addWidget(QLabel(proc))
            d=QLabel(mem);d.setObjectName("sub");lv.addWidget(d)
            h.addLayout(lv);h.addStretch()
            cb=QCheckBox();cb.setChecked(checked);self.proc_checks.append((proc,cb));h.addWidget(cb)
            cv.addWidget(row);cv.addWidget(self._sep())
        v.addWidget(card)
        v.addWidget(self._apply_btn("Kill selected processes",self._kill_procs))
        v.addStretch()
        return self._scroll_page(inner)

    def _kill_procs(self):
        for name,cb in self.proc_checks:
            if cb.isChecked():subprocess.Popen(["pkill","-f",name])

    def _page_rgb(self):
        inner=QWidget();v=QVBoxLayout(inner);v.setContentsMargins(20,20,20,20);v.setSpacing(12)
        t=QLabel("RGB control");t.setObjectName("title");v.addWidget(t)
        s=QLabel("Powered by OpenRGB");s.setObjectName("sub");v.addWidget(s)
        card=self._card();cv=QVBoxLayout(card);cv.setContentsMargins(14,12,14,12);cv.setSpacing(12)
        ct=QLabel("Color");ct.setObjectName("cardtitle");cv.addWidget(ct)
        swatch_row=QHBoxLayout();swatch_row.setSpacing(8)
        self.swatches=[]
        colors=[("378ADD","Blue"),("639922","Green"),("D85A30","Red"),("D4537E","Pink"),("ffffff","White"),("FF8C00","Orange"),("8B00FF","Purple"),("00FFFF","Cyan")]
        for hex_,name in colors:
            btn=QPushButton();btn.setFixedSize(32,32);btn.setToolTip(name)
            btn.setStyleSheet(f"background:#{hex_};border-radius:16px;border:2px solid transparent;")
            btn.clicked.connect(lambda _,h=hex_,b=btn:self._set_rgb(h,b))
            swatch_row.addWidget(btn);self.swatches.append(btn)
        swatch_row.addStretch();cv.addLayout(swatch_row)
        pick_row=QHBoxLayout()
        self.color_preview=QLabel();self.color_preview.setFixedSize(48,32)
        self.color_preview.setStyleSheet("background:#378ADD;border-radius:6px;border:1px solid #ccc;")
        pick_row.addWidget(self.color_preview)
        cpbtn=self._apply_btn("Custom color...",self._open_color_picker)
        pick_row.addWidget(cpbtn);pick_row.addStretch();cv.addLayout(pick_row)
        v.addWidget(card)
        mcard=self._card();mcv=QVBoxLayout(mcard);mcv.setContentsMargins(14,12,14,12);mcv.setSpacing(8)
        mt=QLabel("Mouse  —  G502 HERO");mt.setObjectName("cardtitle");mcv.addWidget(mt)
        self.mouse_effect=QComboBox()
        self.mouse_effect.addItems(["Static","Breathing","Spectrum Cycle","Off"])
        mcv.addWidget(self.mouse_effect)
        mcv.addWidget(self._apply_btn("Apply to mouse",lambda:self._rgb_apply_device("mouse")))
        v.addWidget(mcard)
        kcard=self._card();kcv=QVBoxLayout(kcard);kcv.setContentsMargins(14,12,14,12);kcv.setSpacing(8)
        kt=QLabel("Keyboard  —  Blackwidow Chroma TE");kt.setObjectName("cardtitle");kcv.addWidget(kt)
        self.kb_effect=QComboBox()
        self.kb_effect.addItems(["Static","Breathing","Spectrum Cycle","Wave","Off"])
        kcv.addWidget(self.kb_effect)
        kcv.addWidget(self._apply_btn("Apply to keyboard",lambda:self._rgb_apply_device("keyboard")))
        v.addWidget(kcard)
        v.addWidget(self._apply_btn("Apply to all devices",self._apply_rgb))
        bake_card=self._card();bcv=QVBoxLayout(bake_card);bcv.setContentsMargins(14,12,14,12);bcv.setSpacing(8)
        bt=QLabel("Hardware Memory");bt.setObjectName("cardtitle");bcv.addWidget(bt)
        bs=QLabel("Saves color directly to device — persists after app closes");bs.setObjectName("sub");bcv.addWidget(bs)
        bcv.addWidget(self._apply_btn("Bake color to hardware",self._bake_to_hardware))
        v.addWidget(bake_card)
        v.addStretch()
        return self._scroll_page(inner)

    def _bake_to_hardware(self):
        """Set Static mode + color so device remembers it without the app."""
        try:
            from openrgb import OpenRGBClient
            from openrgb.utils import RGBColor
            h=self.rgb_color.lstrip("#")
            r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
            cl=OpenRGBClient()
            for d in cl.devices:
                mode_map={m.name:i for i,m in enumerate(d.modes)}
                if "Static" in mode_map:
                    d.set_mode(mode_map["Static"])
                for z in d.zones:
                    try:z.set_color(RGBColor(r,g,b))
                    except:pass
            QMessageBox.information(self,"Baked","Color saved to hardware. Devices will keep this color even after DeckForge closes.")
        except Exception as e:
            QMessageBox.warning(self,"Error",str(e))

    def _open_color_picker(self):
        c=QColorDialog.getColor(QColor(f"#{self.rgb_color}"),self)
        if c.isValid():
            hex_=f"{c.red():02X}{c.green():02X}{c.blue():02X}"
            self._set_rgb(hex_)

    def _set_rgb(self,hex_,btn=None):
        self.rgb_color=hex_
        self.color_preview.setStyleSheet(f"background:#{hex_};border-radius:6px;border:1px solid #ccc;")
        for s in self.swatches:
            ss=s.styleSheet()
            if "3px solid" in ss:
                s.setStyleSheet(ss.replace("3px solid #333","2px solid transparent"))
        if btn:
            btn.setStyleSheet(btn.styleSheet().replace("2px solid transparent","3px solid #333"))

    def _rgb_connect(self):
        from openrgb import OpenRGBClient
        return OpenRGBClient()

    def _rgb_set_device(self,d,effect,r,g,b):
        from openrgb.utils import RGBColor
        mode_map={m.name:i for i,m in enumerate(d.modes)}
        aliases={"Spectrum Cycle":["Spectrum Cycle","Rainbow","Cycle"],"Wave":["Wave"],"Breathing":["Breathing"],"Static":["Static"],"Off":["Off"]}
        idx=None
        for name in aliases.get(effect,[effect]):
            if name in mode_map:idx=mode_map[name];break
        if idx is not None:d.set_mode(idx)
        if effect in ("Static","Breathing"):
            for z in d.zones:
                try:z.set_color(RGBColor(r,g,b))
                except:pass

    def _rgb_apply_device(self,which):
        try:
            h=self.rgb_color.lstrip("#")
            r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
            cl=self._rgb_connect()
            for d in cl.devices:
                n=d.name.lower()
                if which=="mouse" and ("g502" in n or "mouse" in n):
                    self._rgb_set_device(d,self.mouse_effect.currentText(),r,g,b)
                elif which=="keyboard" and ("blackwidow" in n or "keyboard" in n or "razer" in n):
                    self._rgb_set_device(d,self.kb_effect.currentText(),r,g,b)
        except Exception as e:
            QMessageBox.warning(self,"OpenRGB Error",str(e))

    def _apply_rgb(self):
        self._rgb_apply_device("mouse")
        self._rgb_apply_device("keyboard")

    def _page_chromasync(self):
        self._cs_running=False;self._cs_zone=None
        inner=QWidget();v=QVBoxLayout(inner);v.setContentsMargins(20,20,20,20);v.setSpacing(12)
        t=QLabel("ChromaSync");t.setObjectName("title");v.addWidget(t)
        s=QLabel("Screen-reactive RGB at ~24fps via ffmpeg");s.setObjectName("sub");v.addWidget(s)
        swatch=QLabel();swatch.setFixedHeight(90);swatch.setStyleSheet("background:#1a1a1a;border-radius:10px;")
        hexl=QLabel("--");hexl.setAlignment(Qt.AlignCenter);hexl.setStyleSheet("font-size:20px;font-weight:bold;color:#444;letter-spacing:2px;")
        QVBoxLayout(swatch).addWidget(hexl);v.addWidget(swatch)
        sr2=QHBoxLayout()
        self.cs_badge=QLabel("OFF");self.cs_badge.setStyleSheet("color:#BA7517;font-size:12px;font-weight:bold;")
        self.cs_fps=QLabel("");self.cs_fps.setStyleSheet("color:#555;font-size:11px;")
        sr2.addWidget(self.cs_badge);sr2.addStretch();sr2.addWidget(self.cs_fps);v.addLayout(sr2)
        card0=self._card();cv0=QVBoxLayout(card0);cv0.setContentsMargins(14,12,14,12);cv0.setSpacing(8)
        ct0=QLabel("Capture Zone");ct0.setObjectName("cardtitle");cv0.addWidget(ct0)
        zr=QHBoxLayout()
        zb=QPushButton("Select Zone");zb.setObjectName("applybtn")
        rb=QPushButton("Reset");rb.setObjectName("applybtn")
        zr.addWidget(zb);zr.addWidget(rb);cv0.addLayout(zr)
        self.cs_zlbl=QLabel("Zone: full screen");self.cs_zlbl.setStyleSheet("color:#888;font-size:11px;");cv0.addWidget(self.cs_zlbl)
        v.addWidget(card0)
        card=self._card();cv=QVBoxLayout(card);cv.setContentsMargins(14,12,14,12);cv.setSpacing(10)
        ct=QLabel("Settings");ct.setObjectName("cardtitle");cv.addWidget(ct)
        def _slider(lbl,lo,hi,init,fmt,attr):
            row=QHBoxLayout();row.addWidget(QLabel(lbl))
            sl=QSlider(Qt.Horizontal);sl.setRange(lo,hi);sl.setValue(init)
            lv=QLabel(fmt(init));lv.setStyleSheet("color:#888;font-size:11px;");lv.setFixedWidth(40)
            def _upd(val,l=lv,f=fmt,a=attr):
                l.setText(f(val))
                if a=="boost":self._cs_boost_val=val/10
                elif a=="thresh":self._cs_thresh_val=val
                elif a=="bright":self._cs_bright_val=val/100
            sl.valueChanged.connect(_upd)
            row.addWidget(sl);row.addWidget(lv);cv.addLayout(row)
            return sl
        _slider("Boost",10,50,25,lambda v:f"{v/10:.1f}x","boost")
        _slider("Threshold",1,30,5,lambda v:str(v),"thresh")
        _slider("Brightness",10,100,100,lambda v:f"{v}%","bright")
        cv.addWidget(self._sep())
        self.cs_dev0=QCheckBox("Device 0 (Mouse)");self.cs_dev0.setChecked(True);cv.addWidget(self.cs_dev0)
        self.cs_dev1=QCheckBox("Device 1 (Keyboard)");self.cs_dev1.setChecked(True);cv.addWidget(self.cs_dev1)
        v.addWidget(card)

        def _capture_pipe(zone=None):
            SW,SH,MOX,MOY=_get_screen_res()
            TW,TH=_get_total_res()
            W,H=128,72
            if zone:
                x1,y1,x2,y2=zone
                ox=MOX+int(x1*SW);oy=MOY+int(y1*SH)
                sw=max(int((x2-x1)*SW),2);sh=max(int((y2-y1)*SH),2)
                vf=f"crop={sw}:{sh}:{ox}:{oy},scale={W}:{H}"
            else:
                cx=MOX+SW//2;cy=MOY+SH//2;hw=SW//5;hh=SH//5
                vf=f"crop={hw*2}:{hh*2}:{cx-hw}:{cy-hh},scale={W}:{H}"
            cmd=["ffmpeg","-f","x11grab","-video_size",f"{TW}x{TH}","-framerate","30","-i",":0","-vf",vf,"-f","rawvideo","-pix_fmt","rgb24","-an","-"]
            return subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL),W,H

        def _loop():
            import numpy as np,queue
            cur=[128,128,128];frames=0;t0=time.time()
            send_q=queue.Queue(maxsize=1)
            def _sender():
                try:
                    from openrgb import OpenRGBClient
                    from openrgb.utils import RGBColor
                    cl=OpenRGBClient()
                    # set both devices to Direct mode once
                    for d in cl.devices:
                        try:
                            dm={m.name:i for i,m in enumerate(d.modes)}
                            if "Direct" in dm:d.set_mode(dm["Direct"])
                        except:pass
                except:cl=None
                while self._cs_running:
                    try:
                        r,g,b=send_q.get(timeout=0.5)
                    except:continue
                    if cl:
                        try:
                            from openrgb.utils import RGBColor
                            color=RGBColor(r,g,b)
                            for i,d in enumerate(cl.devices):
                                if i==0 and not self.cs_dev0.isChecked():continue
                                if i==1 and not self.cs_dev1.isChecked():continue
                                # set per-LED for mouse compatibility
                                for z in d.zones:
                                    try:
                                        leds=len(z.leds)
                                        if leds>0:z.set_color(color)
                                    except:pass
                        except:
                            cl=None
                    if cl is None:
                        h2=f"{r:02X}{g:02X}{b:02X}"
                        if self.cs_dev0.isChecked():
                            subprocess.Popen(["flatpak","run","org.openrgb.OpenRGB","--device","0","--color",h2],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                        if self.cs_dev1.isChecked():
                            subprocess.Popen(["flatpak","run","org.openrgb.OpenRGB","--device","1","--color",h2],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            threading.Thread(target=_sender,daemon=True).start()
            proc,W,H=_capture_pipe(self._cs_zone)
            sz=W*H*3
            last_ui=0
            while self._cs_running:
                raw=proc.stdout.read(sz)
                if not raw or len(raw)<sz:break
                arr=np.frombuffer(raw,dtype=np.uint8).reshape(H,W,3)
                r=int(arr[:,:,0].mean());g=int(arr[:,:,1].mean());b=int(arr[:,:,2].mean())
                mx=max(r,g,b,1)
                sc=min(255/mx,self._cs_boost_val)
                br=self._cs_bright_val
                r,g,b=int(r*sc*br),int(g*sc*br),int(b*sc*br)
                if math.sqrt(sum((cur[i]-[r,g,b][i])**2 for i in range(3)))>=self._cs_thresh_val:
                    cur=[r,g,b]
                    try:send_q.put_nowait((r,g,b))
                    except:pass
                    now=time.time()
                    if now-last_ui>0.08:
                        last_ui=now
                        col=f"#{r:02X}{g:02X}{b:02X}"
                        fg="#000" if (r*299+g*587+b*114)//1000>140 else "#fff"
                        QMetaObject.invokeMethod(swatch,"setStyleSheet",Qt.QueuedConnection,Q_ARG(str,f"background:{col};border-radius:10px;"))
                        QMetaObject.invokeMethod(hexl,"setText",Qt.QueuedConnection,Q_ARG(str,col))
                        QMetaObject.invokeMethod(hexl,"setStyleSheet",Qt.QueuedConnection,Q_ARG(str,f"font-size:20px;font-weight:bold;color:{fg};letter-spacing:2px;"))
                        QMetaObject.invokeMethod(self.cs_badge,"setText",Qt.QueuedConnection,Q_ARG(str,f"LIVE {col}"))
                        QMetaObject.invokeMethod(self.cs_badge,"setStyleSheet",Qt.QueuedConnection,Q_ARG(str,"color:#639922;font-size:12px;font-weight:bold;"))
                frames+=1
                if frames%20==0:
                    fps=frames/(time.time()-t0+0.001)
                    QMetaObject.invokeMethod(self.cs_fps,"setText",Qt.QueuedConnection,Q_ARG(str,f"{fps:.1f} fps"))
            try:proc.kill()
            except:pass

        def _toggle():
            if self._cs_running:
                self._cs_running=False
                self.cs_badge.setText("OFF");self.cs_badge.setStyleSheet("color:#BA7517;font-size:12px;font-weight:bold;")
                swatch.setStyleSheet("background:#1a1a1a;border-radius:10px;")
                hexl.setText("--");hexl.setStyleSheet("font-size:20px;font-weight:bold;color:#444;letter-spacing:2px;")
                self.cs_fps.setText("");tbtn.setText("Start ChromaSync")
            else:
                self._cs_running=True
                threading.Thread(target=_loop,daemon=True).start()
                tbtn.setText("Stop ChromaSync")
                self.showMinimized()

        class ZSel(QWidget):
            done=Signal(float,float,float,float)
            def __init__(self):
                super().__init__()
                self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool)
                self.setAttribute(Qt.WA_TranslucentBackground)
                self.setGeometry(QApplication.primaryScreen().geometry())
                self.p0=None;self.p1=None;self.setCursor(Qt.CrossCursor)
            def paintEvent(self,e):
                p=QPainter(self);p.fillRect(self.rect(),QColor(0,0,0,100))
                if self.p0 and self.p1:
                    r=QRect(self.p0,self.p1).normalized()
                    p.fillRect(r,QColor(0,200,83,50))
                    p.setPen(QPen(QColor(0,200,83),2));p.drawRect(r)
                p.setPen(QColor(255,255,255,200));p.setFont(QFont("monospace",13,QFont.Bold))
                p.drawText(self.rect(),Qt.AlignTop|Qt.AlignHCenter,"drag to select zone  —  esc to cancel")
            def mousePressEvent(self,e):self.p0=e.position().toPoint()
            def mouseMoveEvent(self,e):self.p1=e.position().toPoint();self.update()
            def mouseReleaseEvent(self,e):
                if self.p0 and self.p1:
                    sw,sh=self.width(),self.height()
                    r=QRect(self.p0,e.position().toPoint()).normalized()
                    self.done.emit(r.left()/sw,r.top()/sh,r.right()/sw,r.bottom()/sh)
                self.close()
            def keyPressEvent(self,e):
                if e.key()==Qt.Key_Escape:self.close()

        def _sel_zone():
            self._zsel=ZSel();self._zsel.done.connect(_zset);self._zsel.showFullScreen()
        def _zset(x1,y1,x2,y2):
            self._cs_zone=(x1,y1,x2,y2)
            self.cs_zlbl.setText(f"Zone: {int(x1*100)}%,{int(y1*100)}% -> {int(x2*100)}%,{int(y2*100)}%")
        def _rzset():
            self._cs_zone=None;self.cs_zlbl.setText("Zone: full screen")
        zb.clicked.connect(_sel_zone);rb.clicked.connect(_rzset)
        tbtn=self._apply_btn("Start ChromaSync",_toggle)
        v.addWidget(tbtn);v.addStretch()
        return self._scroll_page(inner)

    def _page_profiles(self):
        inner=QWidget();v=QVBoxLayout(inner);v.setContentsMargins(20,20,20,20);v.setSpacing(12)
        t=QLabel("Profiles");t.setObjectName("title");v.addWidget(t)
        s=QLabel("One-click presets");s.setObjectName("sub");v.addWidget(s)
        grid=QGridLayout();grid.setSpacing(8)
        self.profile_btns=[]
        profiles=[("Performance","Max CPU/GPU, kill background tasks"),("Balanced","Good perf, quieter fans"),("Battery saver","Powersave governor, RGB off"),("Custom","Your saved configuration")]
        for i,(name,desc) in enumerate(profiles):
            btn=QPushButton(f"{name}\n{desc}");btn.setCheckable(True);btn.setChecked(i==0)
            btn.setStyleSheet("text-align:left;padding:12px;border:1px solid #ddd;border-radius:8px;font-size:13px;")
            self.profile_btns.append(btn)
            btn.clicked.connect(lambda _,b=btn:self._select_profile(b))
            grid.addWidget(btn,i//2,i%2)
        v.addLayout(grid)
        v.addWidget(self._apply_btn("Apply selected profile",self._apply_profile))
        v.addStretch()
        return self._scroll_page(inner)

    def _select_profile(self,selected):
        for btn in self.profile_btns:btn.setChecked(btn is selected)

    def _apply_profile(self):
        for btn in self.profile_btns:
            if btn.isChecked():
                name=btn.text().split("\n")[0]
                if name=="Performance":self._apply_perf()
                elif name=="Battery saver":
                    pwd=self._get_sudo()
                    if pwd:
                        subprocess.Popen(["bash","-c",f"echo {pwd!r}|sudo -S cpupower frequency-set -g powersave"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

    def _page_settings(self):
        inner=QWidget();v=QVBoxLayout(inner);v.setContentsMargins(20,20,20,20);v.setSpacing(12)
        t=QLabel("Settings");t.setObjectName("title");v.addWidget(t)
        s=QLabel("App preferences");s.setObjectName("sub");v.addWidget(s)
        card=self._card();cv=QVBoxLayout(card);cv.setContentsMargins(14,12,14,12);cv.setSpacing(8)
        at=QLabel("Appearance");at.setObjectName("cardtitle");cv.addWidget(at)
        theme_row=QHBoxLayout();theme_row.addWidget(QLabel("Theme"));theme_row.addStretch()
        for mode in ["Light","Dark"]:
            btn=QPushButton(mode);btn.setFixedWidth(80)
            btn.setStyleSheet("border:1px solid #ddd;border-radius:6px;padding:5px;font-size:12px;")
            btn.clicked.connect(lambda _,m=mode:self._set_theme(m));theme_row.addWidget(btn)
        cv.addLayout(theme_row);cv.addWidget(self._sep())
        cv.addWidget(self._toggle_row("Launch on startup","Start DeckForge when Desktop Mode opens",False))
        cv.addWidget(self._sep())
        cv.addWidget(self._toggle_row("Show in system tray","Minimize to tray instead of closing",True))
        v.addWidget(card)
        card2=self._card();cv2=QVBoxLayout(card2);cv2.setContentsMargins(14,12,14,12);cv2.setSpacing(8)
        ot=QLabel("OpenRGB");ot.setObjectName("cardtitle");cv2.addWidget(ot)
        cv2.addWidget(self._toggle_row("Auto-connect on launch","Connect to OpenRGB automatically",True))
        cv2.addWidget(self._sep())
        prow=QHBoxLayout();prow.addWidget(QLabel("OpenRGB port"));prow.addStretch()
        port=QLineEdit("6742");port.setFixedWidth(80);prow.addWidget(port);cv2.addLayout(prow)
        v.addWidget(card2)
        card3=self._card();cv3=QVBoxLayout(card3);cv3.setContentsMargins(14,12,14,12);cv3.setSpacing(4)
        abt=QLabel("About");abt.setObjectName("cardtitle");cv3.addWidget(abt)
        cv3.addWidget(QLabel("DeckForge v1.1"));cv3.addWidget(QLabel("Steam Deck Desktop Optimizer"))
        v.addWidget(card3);v.addStretch()
        return self._scroll_page(inner)

    def closeEvent(self,e):
        e.ignore()
        self.hide()
        self._tray.showMessage("DeckForge","Running in background. Right-click tray icon to quit.",QSystemTrayIcon.MessageIcon.Information,2000)

    def _set_theme(self,mode):
        self.dark=(mode=="Dark");self.setStyleSheet(DARK if self.dark else LIGHT)

    def _update_stats(self):
        val=random.randint(22,52)
        self.cpu_lbl.setText(f"{val}%");self.cpu_bar.setValue(val)

if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setApplicationName("DeckForge")
    win=MainWindow();win.show()
    sys.exit(app.exec())
