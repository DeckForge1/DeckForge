import sys,os,subprocess,math,time,threading
sys.path.insert(0,"/home/deck/.local/lib/python3.13/site-packages")
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
ST="QMainWindow,QWidget{background:#111;color:#eee;font-family:'Segoe UI',sans-serif;}QPushButton#start{background:#00c853;color:#000;border:none;border-radius:24px;padding:16px;font-size:15px;font-weight:bold;min-height:48px;}QPushButton#start:hover{background:#00e676;}QPushButton#stop{background:#c62828;color:#fff;border:none;border-radius:24px;padding:16px;font-size:15px;font-weight:bold;min-height:48px;}QPushButton#stop:hover{background:#e53935;}QPushButton#sm{background:#1e1e1e;color:#aaa;border:1px solid #2a2a2a;border-radius:8px;padding:8px 14px;font-size:12px;}QPushButton#sm:hover{background:#2a2a2a;color:#fff;}QSlider::groove:horizontal{height:4px;background:#2a2a2a;border-radius:2px;}QSlider::sub-page:horizontal{background:#00c853;border-radius:2px;}QSlider::handle:horizontal{background:#fff;border:2px solid #00c853;width:16px;height:16px;border-radius:8px;margin:-7px 0;}QLabel#val{color:#555;font-size:11px;}"
def capture(zone=None):
    tmp="/tmp/cs.png"
    try:
        if os.path.exists(tmp):os.remove(tmp)
        r=subprocess.run(["scrot","--silent",tmp],timeout=4,capture_output=True)
        if r.returncode!=0 or not os.path.exists(tmp) or os.path.getsize(tmp)<1000:return None
        import numpy as np
        from PIL import Image
        img=Image.open(tmp).convert("RGB");w,h=img.size
        if zone:
            x1,y1,x2,y2=zone
            img=img.crop((int(x1*w),int(y1*h),int(x2*w),int(y2*h)))
        else:
            cx,cy=w//2,h//2;hw,hh=int(w*0.3/2),int(h*0.3/2)
            img=img.crop((cx-hw,cy-hh,cx+hw,cy+hh))
        arr=np.array(img)
        return int(arr[:,:,0].mean()),int(arr[:,:,1].mean()),int(arr[:,:,2].mean())
    except:return None
def send(r,g,b):
    h=f"{r:02X}{g:02X}{b:02X}"
    for d in ["0","1"]:
        subprocess.Popen(["flatpak","run","org.openrgb.OpenRGB","--device",d,"--color",h],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
        p.drawText(self.rect(),Qt.AlignTop|Qt.AlignHCenter,"  drag to select zone   esc=cancel  ")
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
class Worker(QThread):
    sig=Signal(int,int,int)
    def __init__(self):super().__init__();self.on=False;self.zone=None;self.boost=2.5;self.smooth=0.4
    def run(self):
        cur=[128,128,128]
        while self.on:
            c=capture(self.zone)
            if c:
                r,g,b=c;mx=max(r,g,b,1);sc=min(255/mx,self.boost)
                r,g,b=int(r*sc),int(g*sc),int(b*sc)
                if math.sqrt(sum((cur[i]-[r,g,b][i])**2 for i in range(3)))>=3:
                    cur=[r,g,b]
                    threading.Thread(target=send,args=(*cur,),daemon=True).start()
                    self.sig.emit(*cur)
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChromaSync");self.setFixedSize(340,500)
        self.zone=None;self.w=Worker();self.w.sig.connect(self._color)
        self._ui();self.setStyleSheet(ST)
    def _ui(self):
        root=QWidget();self.setCentralWidget(root)
        v=QVBoxLayout(root);v.setContentsMargins(24,24,24,24);v.setSpacing(16)
        # logo row
        hr=QHBoxLayout()
        logo=QLabel();logo.setFixedSize(36,36)
        pm=QPixmap(36,36);pm.fill(Qt.transparent)
        pp=QPainter(pm);pp.setRenderHint(QPainter.Antialiasing)
        pp.setBrush(QColor("#00c853"));pp.setPen(Qt.NoPen);pp.drawEllipse(0,0,36,36)
        pp.setBrush(QColor("#111"));pp.drawEllipse(8,8,20,20);pp.end()
        logo.setPixmap(pm)
        hr.addWidget(logo)
        tl=QLabel("Chroma<span style='color:#00c853'>Sync</span>");tl.setTextFormat(Qt.RichText)
        tl.setStyleSheet("font-size:18px;font-weight:bold;")
        hr.addWidget(tl);hr.addStretch()
        self.badge=QLabel("OFF");self.badge.setStyleSheet("background:#1e1e1e;color:#555;border-radius:8px;padding:3px 10px;font-size:11px;font-weight:bold;")
        hr.addWidget(self.badge);v.addLayout(hr)
        # color block
        self.swatch=QLabel();self.swatch.setFixedHeight(100)
        self.swatch.setStyleSheet("background:#1a1a1a;border-radius:12px;")
        self.hex=QLabel("--");self.hex.setAlignment(Qt.AlignCenter)
        self.hex.setStyleSheet("font-size:22px;font-weight:bold;color:#333;letter-spacing:2px;")
        sl=QVBoxLayout(self.swatch);sl.addWidget(self.hex);v.addWidget(self.swatch)
        # zone buttons
        zr=QHBoxLayout();zr.setSpacing(8)
        zb=QPushButton("Select Zone");zb.setObjectName("sm");zb.clicked.connect(self._zone)
        rb=QPushButton("Reset");rb.setObjectName("sm");rb.clicked.connect(self._rzone)
        zr.addWidget(zb);zr.addWidget(rb);v.addLayout(zr)
        self.zlbl=QLabel("Zone: full screen");self.zlbl.setObjectName("val");v.addWidget(self.zlbl)
        # sliders
        for lbl,attr,lo,hi,init,fmt in [("Smooth","smooth",1,9,4,lambda v:f"{v/10:.1f}"),("Boost","boost",10,40,25,lambda v:f"{v/10:.1f}x")]:
            row=QHBoxLayout();row.addWidget(QLabel(lbl))
            sl2=QSlider(Qt.Horizontal);sl2.setRange(lo,hi);sl2.setValue(init)
            lv=QLabel(fmt(init));lv.setObjectName("val");lv.setFixedWidth(36)
            sl2.valueChanged.connect(lambda val,a=attr,l=lv,f=fmt:(l.setText(f(val)),setattr(self.w,a,val/10)))
            row.addWidget(sl2);row.addWidget(lv);v.addLayout(row)
        v.addStretch()
        self.btn=QPushButton("START");self.btn.setObjectName("start")
        self.btn.clicked.connect(self._tog);v.addWidget(self.btn)
    def _tog(self):
        if self.w.on:
            self.w.on=False;self.w.wait()
            self.btn.setText("START");self.btn.setObjectName("start");self.btn.setStyle(self.btn.style())
            self.badge.setText("OFF");self.badge.setStyleSheet("background:#1e1e1e;color:#555;border-radius:8px;padding:3px 10px;font-size:11px;font-weight:bold;")
            self.swatch.setStyleSheet("background:#1a1a1a;border-radius:12px;")
            self.hex.setText("--");self.hex.setStyleSheet("font-size:22px;font-weight:bold;color:#333;letter-spacing:2px;")
        else:
            self.w.zone=self.zone;self.w.on=True
            if not self.w.isRunning():self.w.start()
            self.btn.setText("STOP");self.btn.setObjectName("stop");self.btn.setStyle(self.btn.style())
            self.badge.setText("LIVE");self.badge.setStyleSheet("background:#00c853;color:#000;border-radius:8px;padding:3px 10px;font-size:11px;font-weight:bold;")
    def _color(self,r,g,b):
        col=f"#{r:02X}{g:02X}{b:02X}"
        self.swatch.setStyleSheet(f"background:{col};border-radius:12px;")
        fg="#000" if (r*299+g*587+b*114)//1000>140 else "#fff"
        self.hex.setText(col);self.hex.setStyleSheet(f"font-size:22px;font-weight:bold;color:{fg};letter-spacing:2px;")
    def _zone(self):
        self.sel=ZSel();self.sel.done.connect(self._zset);self.sel.showFullScreen()
    def _zset(self,x1,y1,x2,y2):
        self.zone=(x1,y1,x2,y2);self.w.zone=self.zone
        self.zlbl.setText(f"Zone: {int(x1*100)}%,{int(y1*100)}% -> {int(x2*100)}%,{int(y2*100)}%")
    def _rzone(self):self.zone=None;self.w.zone=None;self.zlbl.setText("Zone: full screen")
    def closeEvent(self,e):
        self.w.on=False
        if self.w.isRunning():self.w.quit();self.w.wait(3000)
        super().closeEvent(e)
if __name__=="__main__":
    app=QApplication(sys.argv);win=App();win.show();sys.exit(app.exec())