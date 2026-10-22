from pathlib import Path
from html import escape

OUT = Path(r"D:\软件\健康管理工具\figma-source")
OUT.mkdir(exist_ok=True)
W, H = 390, 844
INK, MUTED, LINE = "#111315", "#6B6B72", "#ECE9ED"
PINK, PINK_SOFT, LILAC, PEACH, ROSE = "#EF92BB", "#F7D9E8", "#F6E5F0", "#FFE4D8", "#F4CCD9"
FONT = "Noto Sans SC, Microsoft YaHei, PingFang SC, sans-serif"

def esc(s): return escape(str(s))
def rect(x,y,w,h,fill="#fff",r=0,stroke=None,sw=1,extra=""):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"{st} {extra}/>'
def text(x,y,s,size=12,fill=INK,weight=400,anchor="start"):
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}px" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>'
def line(x1,y1,x2,y2,stroke=LINE,sw=1): return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"/>'
def circle(cx,cy,r,fill="none",stroke=None,sw=1):
    st=f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{st}/>'
def icon(kind,x,y,color=INK,scale=1):
    sw=1.7*scale
    if kind=="back": return f'<path d="M{x+6*scale},{y-8*scale} L{x-2*scale},{y} L{x+6*scale},{y+8*scale}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
    if kind=="plus": return line(x-7*scale,y,x+7*scale,y,color,sw)+line(x,y-7*scale,x,y+7*scale,color,sw)
    if kind=="home": return f'<path d="M{x-8*scale},{y} L{x},{y-8*scale} L{x+8*scale},{y} M{x-6*scale},{y} V{y+8*scale} H{x+6*scale} V{y}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
    if kind=="report": return circle(x,y,7*scale,"none",color,sw)+circle(x,y,2*scale,color)
    if kind=="moon": return f'<path d="M{x+6*scale},{y-7*scale} A{8*scale},{8*scale} 0 1 0 {x+6*scale},{y+7*scale} A{6*scale},{6*scale} 0 0 1 {x+6*scale},{y-7*scale}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>'
    if kind=="sparkles": return line(x,y-8*scale,x,y+8*scale,color,sw)+line(x-8*scale,y,x+8*scale,y,color,sw)+line(x+7*scale,y-7*scale,x+7*scale,y+1*scale,color,sw)+line(x+3*scale,y-3*scale,x+11*scale,y-3*scale,color,sw)
    if kind=="sun":
        out=circle(x,y,4*scale,"none",color,sw)
        for dx,dy in [(0,-9),(0,9),(-9,0),(9,0),(-6,-6),(6,6),(-6,6),(6,-6)]: out+=line(x+dx*.75*scale,y+dy*.75*scale,x+dx*scale,y+dy*scale,color,sw)
        return out
    if kind=="utensils": return line(x-5*scale,y-8*scale,x-5*scale,y+8*scale,color,sw)+line(x-8*scale,y-8*scale,x-8*scale,y-2*scale,color,sw)+line(x-5*scale,y-8*scale,x-5*scale,y-2*scale,color,sw)+line(x-2*scale,y-8*scale,x-2*scale,y-2*scale,color,sw)+line(x+5*scale,y-8*scale,x+5*scale,y+8*scale,color,sw)
    return ""
def tag(x,y,s,selected=False,orange=False):
    w=12+len(s)*12; fill=PEACH if orange else (PINK_SOFT if selected else "#F7F7F8"); stroke="#F1C7D9" if orange else ("#EFB6CF" if selected else LINE)
    return rect(x,y,w,26,fill,10,stroke)+text(x+w/2,y+18,s,11,"#9F5776" if orange or selected else MUTED,700 if orange or selected else 400,"middle")
def header_back(title=None):
    out=rect(20,48,36,36,"#fff",13,LINE)+icon("back",38,66,INK)
    if title: out+=text(195,71,title,12,MUTED,400,"middle")
    return out
def nav(active):
    out=rect(20,776,350,56,INK,28)
    xs=[65,195,325]; kinds=["home","plus","report"]; labels=["首页","记录","报告"]
    for i,(x,k,l) in enumerate(zip(xs,kinds,labels)):
        if i==active: out+=rect(x-22,782,44,31,PINK_SOFT,16)
        out+=icon(k,x,797,INK if i==active else "#fff",1)
        out+=text(x,827,l,10,INK if i==active else "#fff",700 if i==active else 400,"middle")
    return out
def frame(title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><title>{esc(title)}</title>', rect(0,0,W,H,"#fff",34), rect(7,7,W-14,H-14,"#fff",28,stroke="#F7F7F7",sw=6), rect(151,10,88,24,INK,14)]
def end(parts): return "".join(parts)+"</svg>"
def home():
    p=frame("首页")
    p += [rect(20,46,350,133,PINK_SOFT,26), text(38,70,"早上好，Lin · 皮肤基线",12,"#8A6075"), text(38,108,"你的皮肤，只和",25,INK,500), text(38,139,"过去的自己对比",25,INK,500), text(38,170,"记录生活，理解波动。今天也给自己 30 秒。",12,MUTED), rect(304,122,46,46,"#fff",16), icon("sparkles",327,145,PINK,.8), rect(20,194,350,56,INK,18), text(195,228,"＋  新增今日记录",15,"#fff",700,"middle"), text(20,279,"皮肤生活联动日历",17,INK,500), text(370,279,"2026 年 10 月 v",11,"#8C7B88",400,"end"), rect(20,295,350,176,"#fff",22,LINE), text(36,326,"十月 · 第 3 周",13,INK,700), text(354,326,"点击日期查看诱因",11,"#8A7A86",400,"end")]
    for i,s in enumerate("一二三四五六日"): p.append(text(44+i*49,352,s,10,"#A5A0A7",400,"middle"))
    nums=["28","29","30","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18"]
    for i,n in enumerate(nums):
        row,col=divmod(i,7); x=44+col*49; y=376+row*34; fill=None
        if i in [4,5,7,8,10,12,13,17,18]: fill=PINK_SOFT
        if i in [6,9,15]: fill=PEACH
        if i in [11,16]: fill=ROSE
        if fill: p.append(rect(x-16,y-14,32,28,fill,10))
        if i==16: p.append(rect(x-18,y-16,36,32,"none",10,INK,2))
        p.append(text(x,y+5,n,11,"#A44F78" if fill==PINK_SOFT else ("#B06B4B" if fill==PEACH else ("#A44F66" if fill==ROSE else "#7E8589")),400 if i!=16 else 700,"middle"))
        if i>=4: p.append(circle(x,y+10,2,"#E899BE"))
    p += [rect(20,487,350,70,"#fff",22,LINE), circle(62,522,26,"none", "#F1EDF1",6), f'<path d="M62 496 A26 26 0 0 1 86 536" fill="none" stroke="{PINK}" stroke-width="6"/>', text(62,527,"5/7",12,INK,400,"middle"), text(106,512,"皮肤实验收集",13,INK,700), text(106,534,"再记录 2 条，解锁你的专属诱因报告",11,MUTED), text(350,529,"›",24,"#AAA2AA",400,"middle"), text(20,585,"最近一条日志",17,INK,500), text(370,585,"查看全部 ›",11,"#8C7B88",400,"end"), rect(20,602,350,96,"#fff",22,LINE), text(36,631,"10 月 14 日 · 星期三",11,MUTED), text(36,653,"皮肤评分 3 / 5",14,INK,700), tag(275,620,"轻微波动",False,True), tag(36,665,"熬夜",True), tag(95,665,"甜食",True), tag(154,665,"压力大"), nav(0)]
    return end(p)
def record():
    p=frame("每日皮肤记录")
    p += [header_back(), rect(250,48,120,36,PINK_SOFT,13), text(310,71,"2026 / 10 / 20v",12,INK,700,"middle"), text(20,110,"•  低负担 · 30 秒完成",11,"#7C6C77"), text(20,141,"今日皮肤日志",26,INK,500), text(20,176,"只记录今天的真实感受，不需要和别人比较。",12,MUTED), rect(20,193,350,240,"#fff",22,LINE), text(36,224,"今天的皮肤状态",19,INK,500), text(354,224,"必填",11,MUTED,400,"end"), text(36,250,"自评分数",12,"#7C6C77")]
    for i,n in enumerate("12345"):
        x=58+i*63; p.append(rect(x-22,264,44,45,INK if i==2 else "#F6F3F6",14,INK if i==2 else LINE)); p.append(text(x,293,n,14,"#fff" if i==2 else "#817881",700,"middle"))
    p += [text(36,329,"状态标签 · 可多选",12,"#7C6C77"),tag(36,340,"泛红",True),tag(101,340,"干痒"),tag(166,340,"闭口",True),tag(231,340,"爆痘"),tag(296,340,"无异常"),text(36,390,"局部照片 · 可选",12,"#7C6C77"),rect(36,405,318,50,"#FFFAFE",14,"#E8DFE5"),text(195,435,"＋ 添加照片（仅自己可见）",12,"#8A6075",400,"middle"),rect(20,447,350,285,"#fff",22,LINE),text(36,478,"今天可能的诱因",19,INK,500),text(354,478,"可多选",11,MUTED,400,"end")]
    groups=[("moon","作息",[("熬夜",1),("早睡",0)]),("utensils","饮食",[("甜食",1),("奶制品",0),("辛辣",0)]),("sparkles","护肤品",[("新增护肤品",0),("更换面霜",0)]),("sun","环境 / 情绪",[("暴晒",0),("换季",0),("压力大",0)])]
    yy=500
    for k,lab,tags in groups:
        p += [icon(k,36,yy+1,"#7B6B77",.7), text(64,yy,lab,12,"#7B6B77",700,"middle")]; xx=36
        for s,sel in tags: p.append(tag(xx,yy+12,s,bool(sel))); xx+=12+len(s)*12+8
        yy+=50
    p += [rect(36,708,318,56,"#FFFAFE",14,"#E8DFE5"),text(48,733,"写下今天想补充的细节（可选）",12,"#9AABA4"),text(195,785,"仅作个人健康追踪，不替代医生诊断",11,"#8D8790",400,"middle"),rect(20,796,350,54,INK,18),text(195,829,"保存今日日志  →",15,"#fff",700,"middle")]
    return end(p)
def report():
    p=frame("诱因分析报告")
    p += [header_back(),rect(260,48,110,36,PINK_SOFT,13),text(315,71,"已记录 12 天",12,INK,700,"middle"),text(20,110,"•  基于你的个人记录",11,"#7C6C77"),text(20,141,"皮肤诱因分析报告",26,INK,500),text(20,176,"只和你过去的自己比较，结论仅供参考。",12,MUTED),rect(20,193,350,190,"#fff",22,LINE),text(36,222,"趋势概览",12,"#7C6C77"),text(36,247,"最近 14 天皮肤评分",19,INK,500),tag(294,218,"↗ 稳定",True)]
    for y in [281,317,353]: p.append(line(36,y,354,y,"#F0EDF0"))
    pts=[(36,327),(68,319),(100,323),(132,301),(164,311),(196,292),(228,306),(260,282),(292,293),(324,273),(354,278)]
    p.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in pts+[(354,367),(36,367)])}" fill="{LILAC}"/>'); p.append("<polyline points=\""+" ".join(f"{x},{y}" for x,y in pts)+f'" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    for x,y in pts[::3]: p.append(circle(x,y,3,"#fff",INK,2))
    for x,lab in zip([36,116,196,276,354],["10/07","10/10","10/13","10/16","10/20"]): p.append(text(x,380,lab,10,"#9AA9A3",400,"middle"))
    p += [rect(20,394,350,67,LILAC,17),icon("sparkles",38,418,"#B05F88",.7),text(62,416,"观察到一个可能的关联",12,"#5E4756",700),text(62,439,"熬夜后皮肤评分更容易下降约 0.8 分。",11,"#5E4756"),rect(20,474,350,184,"#fff",22,LINE),text(36,502,"把猜想变成小实验",12,"#7C6C77"),text(36,527,"验证你的诱因假设",19,INK,500),icon("plus",350,518,INK,.9),rect(36,540,318,44,"#FFFAFE",13,"#E8DFE5"),text(48,567,"例如：我怀疑奶制品会让我长痘…",12,"#8DA098"),rect(36,594,318,42,PINK,13),text(195,621,"开始验证",12,"#5F3D22",700,"middle"),rect(36,646,318,48,"#FFF0F6",14),text(48,665,"有奶制品日平均 3.1 分，无奶制品日平均 3.8 分。",11,"#87506A"),text(48,685,"目前支持这个猜想，继续记录会更准确。",11,"#87506A",700),rect(20,706,350,56,"#fff",22,LINE),text(36,730,"给生活的小提示",13,INK,700),tag(262,716,"温和建议",False,True),text(36,751,"连续 3 天在 23:30 前入睡，再看看变化。",11,MUTED),nav(2)]
    return end(p)
def detail():
    p=frame("历史日志详情")
    p += [header_back("日志详情"),text(20,110,"•  个人健康存档",11,"#7C6C77"),text(20,141,"10 月 14 日 · 星期三",26,INK,500),text(20,176,"记录于 2026 年 10 月 14 日 22:18",12,MUTED),rect(20,193,350,235,"#fff",22,LINE),text(36,224,"当日皮肤状态",19,INK,500),tag(286,213,"轻微波动",False,True),text(36,272,"3.0",44,INK,500),text(112,278,"皮肤自评",12,MUTED),text(112,297,"比前一天低 0.5 分",12,MUTED),tag(36,320,"泛红",True),tag(101,320,"闭口",True),rect(36,360,318,150,PINK_SOFT,18),rect(158,381,92,125,"#DCA2BE",46),text(338,485,"局部照片",11,"#fff",400,"end"),rect(20,535,350,205,"#fff",22,LINE),text(36,566,"当日诱因记录",19,INK,500),text(354,566,"3 项",11,MUTED,400,"end"),icon("moon",36,597,"#7B6B77",.7),text(64,600,"作息",12,"#7B6B77",700,"middle"),tag(36,607,"熬夜",True),icon("utensils",36,648,"#7B6B77",.7),text(64,651,"饮食",12,"#7B6B77",700,"middle"),tag(36,658,"甜食",True),icon("sparkles",36,705,"#7B6B77",.7),text(64,708,"备注",12,"#7B6B77",700,"middle"),text(36,729,"昨晚加班到 1 点，下午喝了奶茶。早上有一点泛红。",11,MUTED),rect(20,756,170,44,"#fff",14,"#E8DFE5"),text(105,783,"编辑日志",12,INK,700,"middle"),rect(200,756,170,44,"#FFF6F3",14,"#F1D0C7"),text(285,783,"删除日志",12,"#A75C52",700,"middle"),text(195,824,"本条记录仅为个人健康存档，结论仅作参考，不代表医疗诊断",10,"#8D8790",400,"middle")]
    return end(p)

files={"01-首页.svg":home(),"02-每日皮肤记录.svg":record(),"03-诱因分析报告.svg":report(),"04-历史日志详情.svg":detail()}
for name,content in files.items(): (OUT/name).write_text(content,encoding="utf-8")
(OUT/"README.md").write_text("# 皮肤诱因追踪 · Figma 源文件\n\n将四个 SVG 文件直接拖入 Figma，即可作为可编辑的矢量图层继续拆分和修改。\n\n- 画布：390 × 844\n- 字体：Noto Sans SC / Microsoft YaHei\n- 颜色与间距：参见上级目录 assets/design-tokens.json\n",encoding="utf-8")
print("exported", len(files), "SVG files")

