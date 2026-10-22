from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math
OUT=Path(r"D:\软件\健康管理工具")
W,H,S=390,844,3
bg="#ffffff"; ink="#111315"; muted="#6b6b72"; line="#ece9ed"; mint="#f7d9e8"; accent="#ef92bb"; good="#f7e6ef"; warn="#ffe4d8"; bad="#f4ccd9"
font_path=r"C:\Windows\Fonts\NotoSansSC-VF.ttf"
def F(n): return ImageFont.truetype(font_path, n*S)
def sc(v): return int(v*S)
def rr(d,box,r,fill,outline=None,w=1): d.rounded_rectangle(tuple(sc(x) for x in box), radius=sc(r), fill=fill, outline=outline, width=sc(w))
def t(d,xy,s,size=12,fill=ink,anchor=None,bold=False):
    d.text((sc(xy[0]),sc(xy[1])),s,font=F(size+(1 if bold else 0)),fill=fill,anchor=anchor)
def line(d,pts,fill=line,w=1): d.line([(sc(x),sc(y)) for x,y in pts],fill=fill,width=sc(w),joint="curve")
def icon(d,kind,x,y,color,scale=1):
    x0,y0=sc(x),sc(y); c=color; w=max(1,sc(1.7*scale))
    if kind=="back":
        d.line([(x0+sc(6),y0-sc(8)),(x0-sc(2),y0),(x0+sc(6),y0+sc(8))],fill=c,width=w,joint="curve")
    elif kind=="moon":
        d.arc((x0-sc(8),y0-sc(8),x0+sc(8),y0+sc(8)),55,305,fill=c,width=w)
        d.arc((x0-sc(3),y0-sc(8),x0+sc(10),y0+sc(5)),55,240,fill="#ffffff",width=sc(3))
    elif kind=="utensils":
        d.line([(x0-sc(5),y0-sc(8)),(x0-sc(5),y0+sc(8))],fill=c,width=w)
        for dx in [-7,-4,-1]: d.line([(x0+sc(dx),y0-sc(8)),(x0+sc(dx),y0-sc(2))],fill=c,width=w)
        d.line([(x0+sc(5),y0-sc(8)),(x0+sc(5),y0+sc(8))],fill=c,width=w)
        d.arc((x0+sc(1),y0-sc(8),x0+sc(9),y0+sc(2)),270,90,fill=c,width=w)
    elif kind=="sparkles":
        d.line([(x0,y0-sc(8)),(x0,y0+sc(8))],fill=c,width=w); d.line([(x0-sc(8),y0),(x0+sc(8),y0)],fill=c,width=w)
        d.line([(x0+sc(7),y0-sc(7)),(x0+sc(7),y0+sc(1))],fill=c,width=w); d.line([(x0+sc(3),y0-sc(3)),(x0+sc(11),y0-sc(3))],fill=c,width=w)
    elif kind=="sun":
        d.ellipse((x0-sc(4),y0-sc(4),x0+sc(4),y0+sc(4)),outline=c,width=w)
        for dx,dy in [(0,-9),(0,9),(-9,0),(9,0),(-6,-6),(6,6),(-6,6),(6,-6)]: d.line([(x0+sc(dx*.75),y0+sc(dy*.75)),(x0+sc(dx),y0+sc(dy))],fill=c,width=w)
    elif kind=="insight":
        d.line([(x0,y0-sc(9)),(x0,y0+sc(9))],fill=c,width=w); d.line([(x0-sc(9),y0),(x0+sc(9),y0)],fill=c,width=w)
        d.line([(x0-sc(6),y0-sc(6)),(x0+sc(6),y0+sc(6))],fill=c,width=w); d.line([(x0-sc(6),y0+sc(6)),(x0+sc(6),y0-sc(6))],fill=c,width=w)
    elif kind=="calendar":
        d.rounded_rectangle((x0-sc(8),y0-sc(7),x0+sc(8),y0+sc(8)),radius=sc(2),outline=c,width=w)
        d.line([(x0-sc(8),y0-sc(2)),(x0+sc(8),y0-sc(2))],fill=c,width=w)
        d.line([(x0-sc(4),y0-sc(10)),(x0-sc(4),y0-sc(5))],fill=c,width=w); d.line([(x0+sc(4),y0-sc(10)),(x0+sc(4),y0-sc(5))],fill=c,width=w)
def screen():
    im=Image.new("RGB",(sc(W),sc(H)),bg); d=ImageDraw.Draw(im)
    rr(d,(0,0,W,H),34,"#f7f7f7"); rr(d,(7,7,W-7,H-7),28,bg); rr(d,(151,10,239,34),14,"#111315")
    return im,d
def card(d,y,h):
    rr(d,(20,y,370,y+h),22,"#ffffff","#e6eee9")
def nav(d,active):
    rr(d,(20,776,370,832),28,"#111315")
    items=["首页","记录","报告"]
    for i,lab in enumerate(items):
        x=65+130*i
        if i==active: rr(d,(x-22,782,x+22,813),16,mint)
        icon_color="#111315" if i==active else "#ffffff"
        if i==0:
            d.line([(sc(x-8),sc(797)),(sc(x),sc(789)),(sc(x+8),sc(797))],fill=icon_color,width=sc(2),joint="curve")
            d.rectangle((sc(x-6),sc(797),sc(x+6),sc(805)),outline=icon_color,width=sc(2))
            d.line([(sc(x),sc(805)),(sc(x),sc(799))],fill=icon_color,width=sc(2))
        elif i==1:
            d.line([(sc(x-7),sc(797)),(sc(x+7),sc(797))],fill=icon_color,width=sc(2))
            d.line([(sc(x),sc(790)),(sc(x),sc(804))],fill=icon_color,width=sc(2))
        else:
            d.ellipse((sc(x-7),sc(790),sc(x+7),sc(804)),outline=icon_color,width=sc(2))
            d.ellipse((sc(x-2),sc(795),sc(x+2),sc(799)),fill=icon_color)
        t(d,(x,823),lab,10,"#111315" if i==active else "#ffffff",anchor="mm",bold=i==active)
def tag(d,x,y,s,sel=False,orange=False):
    w=12+len(s)*12
    rr(d,(x,y,x+w,y+26),10,"#fff1de" if orange else (mint if sel else "#f4f7f5"),"#f1c7d9" if orange else ("#efb6cf" if sel else "#e6eee9"))
    t(d,(x+w/2,y+13),s,11,"#9f5776" if orange else ("#285b4d" if sel else "#6e6770"),anchor="mm",bold=sel or orange)
def home():
    im,d=screen()
    rr(d,(20,46,370,179),26,"#f4d9e8"); t(d,(38,70),"早上好，Lin · 皮肤基线",12,"#8a6075")
    t(d,(38,93),"你的皮肤，只和",25,ink,bold=True); t(d,(38,124),"过去的自己对比",25,ink,bold=True); t(d,(38,157),"记录生活，理解波动。今天也给自己 30 秒。",12,muted)
    rr(d,(304,122,350,168),16,"#ffffff"); icon(d,"sparkles",327,145,"#ef92bb",.8)
    rr(d,(20,194,370,250),18,ink); t(d,(195,222),"+  新增今日记录",15,"#ffffff",anchor="mm",bold=True)
    t(d,(20,279),"皮肤生活联动日历",17,ink,bold=True); t(d,(370,279),"2026 年 10 月v",11,"#8c7b88",anchor="ra")
    card(d,295,176); t(d,(36,320),"十月 · 第 3 周",13,ink,bold=True); t(d,(354,320),"点击日期查看诱因",11,"#8a7a86",anchor="ra")
    for i,lab in enumerate("一二三四五六日"): t(d,(44+i*49,346),lab,10,"#9aa9a3",anchor="mm")
    nums=["28","29","30","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18"]
    for i,n in enumerate(nums):
        row,col=divmod(i,7); x=44+col*49; y=370+row*34; fill=None
        if i in [4,5,7,8,10,12,13,17,18]: fill=good
        if i in [6,9,15]: fill=warn
        if i in [11,16]: fill=bad
        if fill: rr(d,(x-16,y-14,x+16,y+14),10,fill)
        if i==16: d.rounded_rectangle((sc(x-18),sc(y-16),sc(x+18),sc(y+16)),radius=sc(10),outline=ink,width=sc(2))
        t(d,(x,y),n,11,"#a44f78" if fill==good else ("#b06b4b" if fill==warn else ("#a44f66" if fill==bad else "#667b73")),anchor="mm",bold=i==16)
        if i>=4: d.ellipse((sc(x-2),sc(y+8),sc(x+2),sc(y+12)),fill="#e899be")
    card(d,487,70); rr(d,(36,496,88,548),26,"#f7edf4"); d.arc((sc(36),sc(496),sc(88),sc(548)),0,257,fill=accent,width=sc(6)); t(d,(62,522),"5/7",12,ink,anchor="mm",bold=True)
    t(d,(106,507),"皮肤实验收集",13,ink,bold=True); t(d,(106,529),"再记录 2 条，解锁你的专属诱因报告",11,muted); t(d,(350,522),">",24,"#aaa2aa",anchor="mm")
    t(d,(20,585),"最近一条日志",17,ink,bold=True); t(d,(370,585),"查看全部 >",11,"#8c7b88",anchor="ra")
    card(d,602,96); t(d,(36,628),"10 月 14 日 · 星期三",11,muted); t(d,(36,649),"皮肤评分 3 / 5",14,ink,bold=True); tag(d,275,620,"轻微波动",orange=True); tag(d,36,665,"熬夜",sel=True); tag(d,95,665,"甜食",sel=True); tag(d,154,665,"压力大")
    nav(d,0); return im
def record():
    im,d=screen(); rr(d,(20,48,56,84),13,"#ffffff","#e6eee9"); icon(d,"back",38,66,ink); rr(d,(250,48,370,84),13,mint); t(d,(310,66),"2026 / 10 / 20v",12,ink,anchor="mm",bold=True)
    t(d,(20,110),"•  低负担 · 30 秒完成",11,"#7c6c77"); t(d,(20,133),"今日皮肤日志",26,ink,bold=True); t(d,(20,168),"只记录今天的真实感受，不需要和别人比较。",12,muted)
    card(d,193,240); t(d,(36,224),"今天的皮肤状态",19,ink,bold=True); t(d,(354,224),"必填",11,muted,anchor="ra"); t(d,(36,250),"自评分数",12,"#7c6c77")
    for i,n in enumerate("12345"):
        x=58+i*63; rr(d,(x-22,264,x+22,309),14,ink if i==2 else "#f6f3f6",ink if i==2 else "#ece9ed"); t(d,(x,286),n,14,"#ffffff" if i==2 else "#817881",anchor="mm",bold=True)
    t(d,(36,329),"状态标签 · 可多选",12,"#7c6c77"); tag(d,36,340,"泛红",sel=True); tag(d,101,340,"干痒"); tag(d,166,340,"闭口",sel=True); tag(d,231,340,"爆痘"); tag(d,296,340,"无异常")
    t(d,(36,390),"局部照片 · 可选",12,"#7c6c77"); rr(d,(36,405,354,455),14,"#fffafe","#e8dfe5",1); t(d,(195,430),"+ 添加照片（仅自己可见）",12,"#8a6075",anchor="mm")
    card(d,447,285); t(d,(36,478),"今天可能的诱因",19,ink,bold=True); t(d,(354,478),"可多选",11,muted,anchor="ra")
    groups=[("moon","作息",[("熬夜",1),("早睡",0)]),("utensils","饮食",[("甜食",1),("奶制品",0),("辛辣",0)]),("sparkles","护肤品",[("新增护肤品",0),("更换面霜",0)]),("sun","环境 / 情绪",[("暴晒",0),("换季",0),("压力大",0)])]
    yy=500
    for ic,lab,tags in groups:
        icon(d,ic,36,yy+1,"#7b6b77",.7); t(d,(64,yy),lab,12,"#7b6b77",anchor="lm",bold=True); xx=36
        for s,sel in tags: tag(d,xx,yy+12,s,sel=sel); xx+=12+len(s)*12+8
        yy+=50
    rr(d,(36,708,354,764),14,"#fffafe","#e8dfe5",1); t(d,(48,727),"写下今天想补充的细节（可选）",12,"#9aaba4")
    t(d,(195,785),"仅作个人健康追踪，不替代医生诊断",11,"#8d8790",anchor="mm"); rr(d,(20,796,370,850),18,ink); t(d,(195,823),"保存今日日志  →",15,"#ffffff",anchor="mm",bold=True)
    return im
def report():
    im,d=screen(); rr(d,(20,48,56,84),13,"#ffffff","#e6eee9"); t(d,(38,66),"‹",22,ink,anchor="mm"); rr(d,(260,48,370,84),13,mint); t(d,(315,66),"已记录 12 天",12,ink,anchor="mm",bold=True)
    t(d,(20,110),"•  基于你的个人记录",11,"#7c6c77"); t(d,(20,133),"皮肤诱因分析报告",26,ink,bold=True); t(d,(20,168),"只和你过去的自己比较，结论仅供参考。",12,muted)
    card(d,193,190); t(d,(36,222),"趋势概览",12,"#7c6c77"); t(d,(36,243),"最近 14 天皮肤评分",19,ink,bold=True); tag(d,294,218,"↗ 稳定",sel=True)
    for y in [281,317,353]: line(d,[(36,y),(354,y)],"#f0edf0",1)
    pts=[(36,327),(68,319),(100,323),(132,301),(164,311),(196,292),(228,306),(260,282),(292,293),(324,273),(354,278)]
    d.polygon([(sc(x),sc(y)) for x,y in pts+[(354,367),(36,367)]],fill="#f6e5f0"); line(d,pts,ink,3)
    for x,y in pts[::3]: d.ellipse((sc(x-3),sc(y-3),sc(x+3),sc(y+3)),fill="#ffffff",outline=ink,width=sc(2))
    for x,lab in zip([36,116,196,276,354],["10/07","10/10","10/13","10/16","10/20"]): t(d,(x,380),lab,10,"#9aa9a3",anchor="mm")
    rr(d,(20,394,370,461),17,"#f6e5f0"); icon(d,"insight",38,418,"#b05f88",.7); t(d,(62,411),"观察到一个可能的关联",12,"#5e4756",bold=True); t(d,(62,434),"熬夜后皮肤评分更容易下降约 0.8 分。",11,"#5e4756")
    card(d,474,184); t(d,(36,502),"把猜想变成小实验",12,"#7c6c77"); t(d,(36,523),"验证你的诱因假设",19,ink,bold=True); t(d,(350,518),"+",20,ink,anchor="mm")
    rr(d,(36,540,354,584),13,"#fffafe","#e8dfe5"); t(d,(48,562),"例如：我怀疑奶制品会让我长痘…",12,"#8da098",anchor="lm"); rr(d,(36,594,354,636),13,accent); t(d,(195,615),"开始验证",12,"#5f3d22",anchor="mm",bold=True)
    rr(d,(36,646,354,694),14,"#fff0f6"); t(d,(48,662),"有奶制品日平均 3.1 分，无奶制品日平均 3.8 分。",11,"#87506a"); t(d,(48,682),"目前支持这个猜想，继续记录会更准确。",11,"#87506a",bold=True)
    card(d,706,56); t(d,(36,728),"给生活的小提示",13,ink,bold=True); tag(d,262,716,"温和建议",orange=True); t(d,(36,750),"连续 3 天在 23:30 前入睡，再看看变化。",11,muted)
    nav(d,2); return im
def detail():
    im,d=screen(); rr(d,(20,48,56,84),13,"#ffffff","#e6eee9"); icon(d,"back",38,66,ink); t(d,(195,66),"日志详情",12,muted,anchor="mm")
    t(d,(20,110),"•  个人健康存档",11,"#7c6c77"); t(d,(20,133),"10 月 14 日 · 星期三",26,ink,bold=True); t(d,(20,168),"记录于 2026 年 10 月 14 日 22:18",12,muted)
    card(d,193,235); t(d,(36,224),"当日皮肤状态",19,ink,bold=True); tag(d,286,213,"轻微波动",orange=True); t(d,(36,272),"3.0",44,ink,bold=True); t(d,(112,278),"皮肤自评\n比前一天低 0.5 分",12,muted)
    tag(d,36,320,"泛红",sel=True); tag(d,101,320,"闭口",sel=True); rr(d,(36,360,354,510),18,"#f5d7e6"); rr(d,(158,381,250,506),46,"#dca2be"); t(d,(338,485),"局部照片",11,"#ffffff",anchor="ra")
    card(d,535,205); t(d,(36,566),"当日诱因记录",19,ink,bold=True); t(d,(354,566),"3 项",11,muted,anchor="ra")
    icon(d,"moon",36,597,"#7b6b77",.7); t(d,(64,596),"作息",12,"#7b6b77",anchor="lm",bold=True); tag(d,36,607,"熬夜",sel=True)
    icon(d,"utensils",36,648,"#7b6b77",.7); t(d,(64,647),"饮食",12,"#7b6b77",anchor="lm",bold=True); tag(d,36,658,"甜食",sel=True)
    icon(d,"sparkles",36,705,"#7b6b77",.7); t(d,(64,704),"备注",12,"#7b6b77",anchor="lm",bold=True); t(d,(36,725),"昨晚加班到 1 点，下午喝了奶茶。早上有一点泛红。",11,muted)
    rr(d,(20,756,190,800),14,"#ffffff","#e8dfe5"); t(d,(105,778),"编辑日志",12,ink,anchor="mm",bold=True); rr(d,(200,756,370,800),14,"#fff6f3","#f1d0c7"); t(d,(285,778),"删除日志",12,"#a75c52",anchor="mm",bold=True); t(d,(195,824),"本条记录仅为个人健康存档，结论仅作参考，不代表医疗诊断",10,"#8d8790",anchor="mm")
    return im
imgs=[home(),record(),report(),detail()]
names=["01-首页.png","02-每日皮肤记录.png","03-诱因分析报告.png","04-历史日志详情.png"]
for im,n in zip(imgs,names): im.save(OUT/n)
ov=Image.new("RGB",(sc(390*2+28),sc(844*2+28)),"#ffffff")
for i,im in enumerate(imgs): ov.paste(im,((0 if i%2==0 else sc(390+28)),(0 if i<2 else sc(844+28))))
ov.save(OUT/"ui-mockups-overview.png")
print("done")








