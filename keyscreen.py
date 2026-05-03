import sys,os,subprocess,threading,time,re
sys.path.insert(0,"/home/deck/.local/lib/python3.13/site-packages")
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtCore import QMetaObject,Q_ARG
from PySide6.QtGui import *
import numpy as np

LED_MAP={
    (0,0):1,(0,1):3,(0,2):4,(0,3):5,(0,4):6,(0,5):7,(0,6):8,(0,7):9,
    (0,8):10,(0,9):11,(0,10):12,(0,11):13,(0,12):14,(0,13):15,(0,14):16,(0,15):17,
    (1,0):23,(1,1):24,(1,2):25,(1,3):26,(1,4):27,(1,5):28,(1,6):29,(1,7):30,
    (1,8):31,(1,9):32,(1,10):33,(1,11):34,(1,12):35,(1,13):36,(1,14):37,(1,15):38,(1,16):39,
    (2,0):45,(2,1):46,(2,2):47,(2,3):48,(2,4):49,(2,5):50,(2,6):51,(2,7):52,
    (2,8):53,(2,9):54,(2,10):55,(2,11):56,(2,12):57,(2,13):58,(2,14):59,(2,15):60,(2,16):61,
    (3,0):67,(3,1):68,(3,2):69,(3,3):70,(3,4):71,(3,5):72,(3,6):73,(3,7):74,
    (3,8):75,(3,9):76,(3,10):77,(3,11):78,(3,13):80,
    (4,0):89,(4,2):91,(4,3):92,(4,4):93,(4,5):94,(4,6):95,(4,7):96,(4,8):97,
    (4,9):98,(4,10):100,(4,12):102,(4,14):104,
    (5,0):111,(5,1):112,(5,2):113,(5,4):117,(5,7):121,(5,8):124,
    (5,12):125,(5,13):126,(5,14):127,
}
ROWS=6;COLS=17
KEY_GRID=[
    ["Escape","F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12","Print Screen","Scroll Lock","Pause Break",""],
    ["`","1","2","3","4","5","6","7","8","9","0","-","=","Backspace","Insert","Home","Page Up"],
    ["Tab","Q","W","E","R","T","Y","U","I","O","P","[","]","\\","Delete","End","Page Down"],
    ["Caps Lock","A","S","D","F","G","H","J","K","L",";","'","","Enter","","",""],
    ["Left Shift","","Z","X","C","V","B","N","M",",",".","Right Shift","","","Up Arrow","",""],
    ["Left Control","Left Windows","Left Alt","","Space","","","Right Alt","Right Control","","","","Left Arrow","Down Arrow","Right Arrow","",""],
]

DARK="""
QMainWindow,QWidget{background:#1c1c1e;color:#f0f0f0;font-family:'Segoe UI',sans-serif;}
QPushButton#applybtn{background:#7c3aed;color:white;border:none;border-radius:8px;padding:10px;font-size:13px;font-weight:bold;}
QPushButton#applybtn:hover{background:#9d5ef5;}
QWidget#card{background:#2a2a2e;border:1px solid #3a3a3e;border-radius:10px;}
QLabel#title{font-size:15px;font-weight:bold;}
QLabel#sub{font-size:12px;color:#666;}
QLabel#cardtitle{font-size:13px;font-weight:bold;}
QSlider::groove:horizontal{height:6px;background:#3a3a3e;border-radius:3px;}
QSlider::sub-page:horizontal{background:#7c3aed;border-radius:3px;}
QSlider::handle:horizontal{background:#1c1c1e;border:2px solid #7c3aed;width:18px;height:18px;border-radius:9px;margin:-7px 0;}
"""

def _monitors():
    out=[]
    try:
        r=subprocess.run(["xrandr","--listmonitors"],capture_output=True,text=True)
        for line in r.stdout.splitlines():
            m=re.search(r"(\d+)/\d+x(\d+)/\d+\+(\d+)\+(\d+)",line)
            if m:out.append((int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4))))
    except:pass
    return out or [(2560,1440,0,0)]

def _start_orgb():
    import socket
    try:s=socket.socket();s.connect(("localhost",6742));s.close();return
    except:pass
    subprocess.Popen(["flatpak","run","org.openrgb.OpenRGB","--server","--noautoconnect"],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(6)

class Preview(QWidget):
    def __init__(self):
        super().__init__()
        self.grid=[[(0,0,0)]*COLS for _ in range(ROWS)]
        self.setMinimumHeight(120)
    def set_grid(self,g):self.grid=g;self.update()
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
        W,H=self.width(),self.height();cw=W/COLS;ch=H/ROWS
        for r in range(ROWS):
            for c in range(COLS):
                name=KEY_GRID[r][c];rc,gc,bc=self.grid[r][c]
                p.setBrush(QColor(rc,gc,bc) if name else QColor(20,20,22))
                p.setPen(QPen(QColor(40,40,44),1))
                p.drawRoundedRect(int(c*cw+1),int(r*ch+1),int(cw-2),int(ch-2),3,3)

class ZonePicker(QWidget):
    picked=Signal(float,float,float,float,int)
    def __init__(self,mons):
        super().__init__()
        self.mons=mons
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        tw=max(m[0]+m[2] for m in mons);th=max(m[1]+m[3] for m in mons)
        self.setGeometry(0,0,tw,th);self.p0=None;self.p1=None;self.setCursor(Qt.CrossCursor)
    def paintEvent(self,e):
        p=QPainter(self);p.fillRect(self.rect(),QColor(0,0,0,100))
        if self.p0 and self.p1:
            r=QRect(self.p0,self.p1).normalized()
            p.fillRect(r,QColor(124,58,237,60));p.setPen(QPen(QColor(124,58,237),2));p.drawRect(r)
        p.setPen(QColor(255,255,255,200));p.setFont(QFont("monospace",13,QFont.Bold))
        p.drawText(self.rect(),Qt.AlignTop|Qt.AlignHCenter,"drag zone — esc cancel")
    def mousePressEvent(self,e):self.p0=e.position().toPoint()
    def mouseMoveEvent(self,e):self.p1=e.position().toPoint();self.update()
    def mouseReleaseEvent(self,e):
        if self.p0 and self.p1:
            r=QRect(self.p0,e.position().toPoint()).normalized()
            bi=0;ba=0
            for i,m in enumerate(self.mons):
                ov=r.intersected(QRect(m[2],m[3],m[0],m[1]))
                a=ov.width()*ov.height()
                if a>ba:ba=a;bi=i
            mw,mh,mox,moy=self.mons[bi]
            self.picked.emit(max(0.0,(r.left()-mox)/mw),max(0.0,(r.top()-moy)/mh),
                min(1.0,(r.right()-mox)/mw),min(1.0,(r.bottom()-moy)/mh),bi)
        self.close()
    def keyPressEvent(self,e):
        if e.key()==Qt.Key_Escape:self.close()

class KeyScreen(QMainWindow):
    _sig=Signal(list)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KeyScreen");self.resize(820,500)
        self._running=False;self._zone=None
        self._mons=_monitors();self._bright=1.0;self._sat=1.5
        self._sig.connect(lambda g:self.prev.set_grid(g))
        self._build();self.setStyleSheet(DARK)
        threading.Thread(target=_start_orgb,daemon=True).start()
        self._tray_setup()

    def _tray_setup(self):
        pm=QPixmap(32,32);pm.fill(QColor("#7c3aed"))
        self._tray=QSystemTrayIcon(QIcon(pm),self)
        self._tray.setToolTip("KeyScreen")
        m=QMenu();m.addAction("Show",self.show);m.addAction("Quit",self._quit)
        self._tray.setContextMenu(m)
        self._tray.activated.connect(lambda r:self.show() if r==QSystemTrayIcon.ActivationReason.Trigger else None)
        self._tray.show()

    def closeEvent(self,e):e.ignore();self.hide()
    def _quit(self):self._running=False;self._tray.hide();QApplication.quit()
    def _btn(self,t,f):b=QPushButton(t);b.setObjectName("applybtn");b.clicked.connect(f);return b
    def _card(self):w=QWidget();w.setObjectName("card");return w

    def _build(self):
        root=QWidget();self.setCentralWidget(root)
        v=QVBoxLayout(root);v.setContentsMargins(20,20,20,20);v.setSpacing(10)
        h=QHBoxLayout();tl=QLabel("KeyScreen");tl.setObjectName("title");h.addWidget(tl);h.addStretch()
        self.fps_lbl=QLabel("");self.fps_lbl.setStyleSheet("color:#7c3aed;font-weight:bold;font-size:12px;")
        self.stat_lbl=QLabel("STOPPED");self.stat_lbl.setStyleSheet("color:#888;font-weight:bold;font-size:12px;")
        h.addWidget(self.fps_lbl);h.addWidget(self.stat_lbl);v.addLayout(h)
        sub=QLabel("Screen → keyboard pixel display");sub.setObjectName("sub");v.addWidget(sub)
        pc=self._card();pv=QVBoxLayout(pc);pv.setContentsMargins(10,8,10,8)
        pl=QLabel("Preview");pl.setObjectName("cardtitle");pv.addWidget(pl)
        self.prev=Preview();pv.addWidget(self.prev);v.addWidget(pc)
        zc=self._card();zv=QVBoxLayout(zc);zv.setContentsMargins(14,10,14,10);zv.setSpacing(6)
        zl=QLabel("Zone");zl.setObjectName("cardtitle");zv.addWidget(zl)
        zr=QHBoxLayout();zr.addWidget(self._btn("Select Zone",self._pick_zone))
        zr.addWidget(self._btn("Reset",self._reset_zone));zv.addLayout(zr)
        self.zlbl=QLabel("full primary monitor");self.zlbl.setStyleSheet("color:#888;font-size:11px;")
        zv.addWidget(self.zlbl);v.addWidget(zc)
        sc=self._card();sv=QVBoxLayout(sc);sv.setContentsMargins(14,10,14,10);sv.setSpacing(8)
        sv.addWidget(QLabel("Settings").__class__.__new__(QLabel.__class__) if False else (lambda:( (l:=QLabel("Settings")).__setattr__('objectName','cardtitle') or l)  )())
        def _sl(lbl,lo,hi,init,fmt,cb):
            row=QHBoxLayout();row.addWidget(QLabel(lbl))
            s=QSlider(Qt.Horizontal);s.setRange(lo,hi);s.setValue(init)
            lv=QLabel(fmt(init));lv.setStyleSheet("color:#888;font-size:11px;");lv.setFixedWidth(44)
            s.valueChanged.connect(lambda val,l=lv,f=fmt:(l.setText(f(val)),cb(val)))
            row.addWidget(s);row.addWidget(lv);sv.addLayout(row)
        _sl("Brightness",10,200,100,lambda v:f"{v}%",lambda v:setattr(self,"_bright",v/100))
        _sl("Saturation",10,30,15,lambda v:f"{v/10:.1f}x",lambda v:setattr(self,"_sat",v/10))
        v.addWidget(sc)
        self.tbtn=self._btn("▶  Start",self._toggle);v.addWidget(self.tbtn)

    def _pick_zone(self):
        self._zp=ZonePicker(self._mons);self._zp.picked.connect(self._set_zone);self._zp.showFullScreen()
    def _set_zone(self,x1,y1,x2,y2,mi):
        self._zone=(x1,y1,x2,y2,mi);m=self._mons[mi]
        self.zlbl.setText(f"Mon{mi} {int(x1*100)},{int(y1*100)}→{int(x2*100)},{int(y2*100)}%")
    def _reset_zone(self):self._zone=None;self.zlbl.setText("full primary monitor")

    def _toggle(self):
        if self._running:
            self._running=False;self.tbtn.setText("▶  Start")
            self.stat_lbl.setText("STOPPED");self.stat_lbl.setStyleSheet("color:#888;font-weight:bold;font-size:12px;")
            self.fps_lbl.setText("")
        else:
            self._running=True;self.tbtn.setText("■  Stop")
            self.stat_lbl.setText("LIVE");self.stat_lbl.setStyleSheet("color:#7c3aed;font-weight:bold;font-size:12px;")
            threading.Thread(target=self._loop,daemon=True).start()
            self.showMinimized()

    def _loop(self):
        from openrgb import OpenRGBClient
        from openrgb.utils import RGBColor
        import mss

        kb=None
        for _ in range(10):
            try:
                cl=OpenRGBClient()
                for d in cl.devices:
                    if any(x in d.name.lower() for x in ["blackwidow","razer","keyboard"]):
                        kb=d;break
                if kb:break
            except:time.sleep(1)

        if not kb:print("no keyboard");return

        mode_map={m.name:i for i,m in enumerate(kb.modes)}
        kb.set_mode(mode_map["Direct"])
        time.sleep(0.2)

        num=len(kb.leds)
        black=[RGBColor(0,0,0)]*num
        send=list(black)

        mons=self._mons;pi=0
        for i,m in enumerate(mons):
            if m[2]==0 and m[3]==0:pi=i;break
        z=self._zone
        if z:x1,y1,x2,y2,mi=z;mw,mh,mox,moy=mons[mi]
        else:mw,mh,mox,moy=mons[pi];x1,y1,x2,y2=0.0,0.0,1.0,1.0
        ox=int(mox+x1*mw);oy=int(moy+y1*mh)
        sw=max(int((x2-x1)*mw),COLS);sh=max(int((y2-y1)*mh),ROWS)

        frames=0;t0=time.time()
        with mss.mss() as sct:
            mon={"left":ox,"top":oy,"width":sw,"height":sh}
            # precompute sample indices
            yi=np.linspace(0,sh-1,ROWS,dtype=int)
            xi=np.linspace(0,sw-1,COLS,dtype=int)
            while self._running:
                img=sct.grab(mon)
                # BGRA → sample grid directly
                arr=np.frombuffer(img.raw,dtype=np.uint8).reshape(sh,sw,4)
                samp=arr[np.ix_(yi,xi)]  # ROWS x COLS x 4 BGRA
                br=self._bright;sat=self._sat
                r=samp[:,:,2].astype(np.float32)
                g=samp[:,:,1].astype(np.float32)
                b=samp[:,:,0].astype(np.float32)
                mn=np.minimum(np.minimum(r,g),b)
                r=np.clip((mn+(r-mn)*sat)*br,0,255).astype(np.uint8)
                g=np.clip((mn+(g-mn)*sat)*br,0,255).astype(np.uint8)
                b=np.clip((mn+(b-mn)*sat)*br,0,255).astype(np.uint8)
                grid=[[(int(r[row,col]),int(g[row,col]),int(b[row,col])) for col in range(COLS)] for row in range(ROWS)]
                for (row,col),idx in LED_MAP.items():
                    send[idx]=RGBColor(int(r[row,col]),int(g[row,col]),int(b[row,col]))
                try:kb.set_colors(send)
                except:pass
                self._sig.emit(grid)
                frames+=1
                if frames%30==0:
                    fps=frames/(time.time()-t0+0.001)
                    QMetaObject.invokeMethod(self.fps_lbl,"setText",Qt.QueuedConnection,Q_ARG(str,f"{fps:.1f}fps"))

        try:kb.set_colors(black)
        except:pass

if __name__=="__main__":
    app=QApplication(sys.argv);app.setApplicationName("KeyScreen")
    app.setQuitOnLastWindowClosed(False)
    win=KeyScreen();win.show();sys.exit(app.exec())
