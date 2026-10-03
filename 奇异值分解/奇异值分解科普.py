# -*- coding: utf-8 -*-
"""SVD cinematic explainer. All geometric transformations and image reconstructions are numerical.
Render: python -m manim -qh 奇异值分解科普.py SVDExplainer --media_dir media
"""
from pathlib import Path
import json
import numpy as np
from manim import *

# Let the CLI choose resolution / fps: -ql is a genuine fast preview, -qh is 1080p60.
config.frame_width = 16
config.frame_height = 9
config.max_files_cached = 600
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / '素材'
ZH_FONT = 'Kaiti SC'
BG='#0F1720'; INK='#F6F2EA'; MUTED='#A9B4C2'; BLUE='#5DADEC'
GREEN='#66D19E'; GOLD='#FFD166'; ORANGE='#F59E62'; RED='#FF6B6B'; PURPLE='#B79CFF'; CYAN='#58D6D6'
WRITE=1.48

def rot(t):
    return np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]])

U2=rot(30*DEGREES)
V2=rot(25*DEGREES)
S2=np.diag([1.75,.65])
A2=U2@S2@V2.T

class SVDExplainer(Scene):
    def t(self,s,size=34,color=INK):
        return Text(s,font=ZH_FONT,font_size=size,color=color)
    def m(self,s,size=49,color=INK):
        return MathTex(s,font_size=size,color=color,stroke_width=.7)
    def fit(self,o,w):
        if o.width>w:o.scale_to_fit_width(w)
        return o
    def mix(self,*parts,size=33):
        return VGroup(*[self.m(s,size+8,c) if k=='m' else self.t(s,size,c) for k,s,c in parts]).arrange(RIGHT,buff=.10)
    def begin(self,title,chapter,section):
        self.start=float(self.time)
        self.section_name=title
        self.section_id=section
        h=self.fit(self.t(title,47,INK),14.2).move_to([0,3.64,0])
        tag=self.t(chapter,22,GOLD).move_to([-6.6,4.22,0],aligned_edge=LEFT)
        num=self.t(f'{section:02d} / 20',21,MUTED).move_to([7.05,4.22,0],aligned_edge=RIGHT)
        self.play(FadeIn(h,shift=UP*.12),FadeIn(tag),FadeIn(num),run_time=.65)
    def foot(self,text,color=MUTED):
        f=self.fit(self.t(text,29,color),14.5).move_to([0,-3.82,0])
        self.play(FadeIn(f,shift=UP*.08),run_time=.45)
        return f
    def write(self,o,pause=1.0):
        self.play(Write(o),run_time=WRITE)
        self.wait(pause)
    def end(self,duration):
        remaining=duration-(float(self.time)-self.start)
        self.wait(max(1.8,remaining))
        self.timeline.append(dict(index=self.section_id,title=self.section_name,start=self.start,end=float(self.time),sample=float(self.time)-.65))
        for o in self.mobjects:
            for m in o.get_family():
                if isinstance(m,(Text,MathTex)) and m.width:
                    if m.get_left()[0]<-7.85 or m.get_right()[0]>7.85 or m.get_bottom()[1]<-4.4 or m.get_top()[1]>4.48:
                        self.layout_warnings.append(dict(section=self.section_id,type=type(m).__name__,bounds=[float(m.get_left()[0]),float(m.get_right()[0]),float(m.get_bottom()[1]),float(m.get_top()[1])]))
        self.play(*[FadeOut(o) for o in self.mobjects],run_time=.5)
        self.clear()
    def panel(self,x=3.9,y=-.15,w=6.65,h=5.6):
        return RoundedRectangle(width=w,height=h,corner_radius=.2,stroke_color='#304355',stroke_width=1.1,fill_color='#14212E',fill_opacity=.65).move_to([x,y,0])
    def left(self,o,y,w=7):
        self.fit(o,w)
        return o.move_to([-7.05,y,0],aligned_edge=LEFT)
    def plane(self,center=(3.85,-.05),scale=1.13):
        p=NumberPlane(x_range=[-2.6,2.6,1],y_range=[-2.3,2.3,1],x_length=5.2*scale,y_length=4.6*scale,
            background_line_style={'stroke_color':'#2B4052','stroke_width':1,'stroke_opacity':.65},
            axis_config={'stroke_color':'#637787','stroke_width':1.5,'include_ticks':False})
        p.move_to([*center,0]);return p
    def curve(self,p,matrix=np.eye(2),color=GOLD):
        return ParametricFunction(lambda t:p.c2p(*(matrix@np.array([np.cos(t),np.sin(t)]))),t_range=[0,TAU,.035],color=color,stroke_width=3.5)
    def rays(self,p,matrix=np.eye(2)):
        colors=[GOLD,CYAN,PURPLE,ORANGE]
        return VGroup(*[Arrow(p.c2p(0,0),p.c2p(*(matrix@v)),buff=0,color=c,stroke_width=4,max_tip_length_to_length_ratio=.16) for v,c in zip([np.array([1.,0]),np.array([0.,1]),np.array([-.7,-.7]),np.array([.6,-.8])],colors)])
    def photo(self,k=256,width=4.5):
        im=ImageMobject(str(ASSETS/f'rank_{k:03d}.png'))
        im.width=width
        return im
    def image_frame(self,pos,width=4.5):
        return RoundedRectangle(width=width+.13,height=width+.13,corner_radius=.09,color=GOLD,stroke_width=1.5).move_to(pos)
    def spectrum(self,x=3.8,y=-.1,width=5.2,height=3.2,count=24):
        values=self.data['s'][:count]
        bars=VGroup()
        # sqrt height deliberately labelled to reveal the spectral tail.
        for i,s in enumerate(values):
            h=max(.035,height*np.sqrt(s/values[0]))
            r=Rectangle(width=width/count*.73,height=h,stroke_width=0,fill_color=GOLD if i<4 else BLUE,fill_opacity=.95)
            r.move_to([x-width/2+(i+.5)*width/count,y-height/2+h/2,0]);bars.add(r)
        return bars
    def vector_pair(self,p):
        vs=VGroup(*[Arrow(p.c2p(0,0),p.c2p(*V2[:,i]),buff=0,color=c,stroke_width=5) for i,c in enumerate([GOLD,CYAN])])
        out=VGroup(*[Arrow(p.c2p(0,0),p.c2p(*(A2@V2[:,i])),buff=0,color=c,stroke_width=5) for i,c in enumerate([GOLD,CYAN])])
        return vs,out
    def construct(self):
        self.camera.background_color=BG
        self.timeline=[];self.layout_warnings=[]
        self.data=np.load(ASSETS/'image_svd.npz')
        for method in [self.hook,self.pixels,self.geometry,self.definition,self.roadmap,
                       self.two_grams,self.positive,self.spectral,self.square_roots,self.orthogonal,
                       self.left_eigen,self.assembly,self.zero_rank,self.eigen_contrast,
                       self.layers,self.optimal,self.compression,self.pca,self.inverse,self.finale]:
            method()
        (ROOT/'验收').mkdir(exist_ok=True)
        (ROOT/'验收'/'时间轴.json').write_text(json.dumps(self.timeline,ensure_ascii=False,indent=2),encoding='utf-8')
        (ROOT/'验收'/'排版检查.json').write_text(json.dumps(self.layout_warnings,ensure_ascii=False,indent=2),encoding='utf-8')

    def hook(self):
        self.begin('一张照片，能只用几层信息还原吗？','从应用出发',1)
        pos=np.array([-3.65,-.1,0])
        im=self.photo(1,4.8).move_to(pos)
        frame=self.image_frame(pos,4.8)
        self.play(FadeIn(im),Create(frame),run_time=.8)
        title=self.t('奇异值分解',54,GOLD).move_to([3.55,2.05,0])
        en=self.t('SINGULAR VALUE DECOMPOSITION',20,MUTED).next_to(title,DOWN,buff=.16)
        self.play(Write(title),FadeIn(en),run_time=1.3)
        count=self.m('k=1',54,GOLD).move_to([3.55,.25,0])
        desc=self.t('保留最重要的层',33,INK).move_to([3.55,-.7,0])
        self.play(Write(count),FadeIn(desc),run_time=.8)
        bars=self.spectrum(x=3.55,y=-2.1,width=4.7,height=1.5,count=16)
        self.play(LaggedStart(*[GrowFromEdge(b,DOWN) for b in bars],lag_ratio=.025),run_time=.9)
        for k in [4,16,64]:
            target=self.photo(k,4.8).move_to(pos)
            label=self.m(f'k={k}',54,GOLD).move_to(count)
            self.play(FadeOut(im),FadeIn(target),Transform(count,label),run_time=1.25)
            im=target;self.wait(.55)
        self.foot('保留一层、四层、十六层……照片的结构正在逐层浮现')
        self.end(16)

    def pixels(self):
        self.begin('照片背后，就是一个数字矩阵','01  看懂分解',2)
        im=self.photo(256,4.3).move_to([-4.05,0,0])
        self.play(FadeIn(im),run_time=.7)
        a=self.data['image'][70:76,130:136]
        grid=VGroup()
        for i in range(6):
            for j in range(6):
                sq=Square(.58,stroke_color=BG,stroke_width=1,fill_color=interpolate_color(ManimColor(BG),ManimColor(GOLD),float(a[i,j])),fill_opacity=1).move_to([1.9+j*.6,1.5-i*.6,0])
                val=self.t(str(int(a[i,j]*255)),20,BG if a[i,j]>.55 else INK).move_to(sq)
                grid.add(VGroup(sq,val))
        crop=Square(6/256*4.3,color=GOLD,stroke_width=2).move_to([-4.05+(133/256-.5)*4.3,(.5-73/256)*4.3,0])
        arrow=Arrow([-1.65,0,0],[1.3,0,0],buff=.1,color=ORANGE)
        self.play(Create(crop),GrowArrow(arrow),LaggedStart(*[FadeIn(x) for x in grid],lag_ratio=.014),run_time=1.8)
        label=self.m(r'A\in\mathbb{R}^{256\times256}',49,GOLD).move_to([3.35,-2.6,0])
        self.write(label)
        self.foot('每个数代表一个像素的亮度；SVD 寻找它最重要的结构')
        self.end(11)

    def geometry(self):
        self.begin('把一次复杂形变，拆成三个简单动作','01  看懂分解',3)
        self.add(self.panel())
        p=self.plane();self.play(Create(p),run_time=.7)
        circle=self.curve(p,np.eye(2),BLUE); rays=self.rays(p)
        lattice=VGroup(*[self.curve(p,np.eye(2)*r,BLUE).set_stroke(width=1,opacity=.35) for r in [.25,.5,.75]])
        for angle in np.linspace(0,TAU,16,endpoint=False):
            lattice.add(Line(p.c2p(0,0),p.c2p(np.cos(angle),np.sin(angle)),color=BLUE,stroke_width=.8,stroke_opacity=.32))
        mesh=VGroup()
        for c in [-1.5,-1,-.5,.5,1,1.5]:
            mesh.add(Line(p.c2p(c,-1.5),p.c2p(c,1.5),color=BLUE,stroke_width=1,stroke_opacity=.34))
            mesh.add(Line(p.c2p(-1.5,c),p.c2p(1.5,c),color=BLUE,stroke_width=1,stroke_opacity=.34))
        body=VGroup(mesh,lattice,circle,rays)
        self.play(Create(body),run_time=.8)
        base=body.copy();origin=p.c2p(0,0)
        f=self.left(self.m(r'A=U\Sigma V^{\mathsf T}',61,GOLD),2.05)
        self.write(f,pause=.45)
        stages=[(lambda a:rot(-25*DEGREES*a),r'V^{\mathsf T}','先转动输入坐标',PURPLE),
                (lambda a:((1-a)*np.eye(2)+a*S2)@V2.T,r'\Sigma','再沿坐标轴拉伸',GOLD),
                (lambda a:rot(30*DEGREES*a)@S2@V2.T,r'U','最后转到输出方向',GREEN)]
        sc=p.x_length/5.2
        tip_vecs=[np.array([1.,0]),np.array([0.,1]),np.array([-.7,-.7]),np.array([.6,-.8])]
        N=32;traces=[]
        for v in tip_vecs:
            pts=[]
            for fn,_,_,_ in stages:
                seg=[]
                for s in np.linspace(0,1,N+1):
                    w=fn(s)@v
                    seg.append(origin+sc*np.array([w[0],w[1],0.]))
                pts.extend(seg if not pts else seg[1:])
            traces.append(pts)
        trails=VGroup(*[VMobject(stroke_color=c,stroke_width=1.8,stroke_opacity=.5) for c in [GOLD,CYAN,PURPLE,ORANGE]])
        self.add(trails)
        text=None;symbol=None
        for k,(fn,ss,caption,color) in enumerate(stages):
            nt=self.left(self.t(caption,34,color),-.05)
            ns=self.left(self.m(ss,66,color),.95)
            def update(o,alpha,fn=fn,color=color,k=k):
                transformed=base.copy().apply_matrix(fn(alpha),about_point=origin)
                for g in transformed[:3]:g.set_color(color)
                o.become(transformed)
                for tr,pts in zip(trails,traces):
                    n=k*N+1+int(round(alpha*N))
                    tr.set_points_as_corners(pts[:max(2,n)])
            anim=[UpdateFromAlphaFunc(body,update)]
            if text is not None:anim.extend([FadeOut(text),FadeOut(symbol)])
            self.play(*anim,FadeIn(nt),FadeIn(ns),run_time=2.0)
            text=nt;symbol=ns;self.wait(.55)
        self.foot('正交变换保持长度和角度；一般还可能包含镜像翻转')
        path=self.curve(p,A2,GREEN)
        dot=Dot(path.get_start(),radius=.075,color=GOLD)
        glow=Dot(path.get_start(),radius=.17,color=GOLD,fill_opacity=.13)
        self.play(trails.animate.set_opacity(.16),MoveAlongPath(dot,path),MoveAlongPath(glow,path),run_time=1.7,rate_func=linear)
        self.end(17)

    def definition(self):
        self.begin('准确的定义：任何实矩阵都能这样分解','01  看懂分解',4)
        eq=self.m(r'A_{m\times n}=U_{m\times m}\,\Sigma_{m\times n}\,V_{n\times n}^{\mathsf T}',57,GOLD).move_to([0,2.15,0])
        self.fit(eq,14.5);self.write(eq)
        cards=VGroup()
        for x,title,form,caption,c in [(-4.9,'输出方向',r'U^{\mathsf T}U=I_m','左奇异向量',GREEN),(0,'非负拉伸',r'\sigma_1\ge\cdots\ge\sigma_p\ge0','奇异值',GOLD),(4.9,'输入方向',r'V^{\mathsf T}V=I_n','右奇异向量',PURPLE)]:
            box=RoundedRectangle(width=4.45,height=3.25,corner_radius=.16,color=c,fill_color=c,fill_opacity=.04).move_to([x,-.3,0])
            t=self.t(title,34,c).move_to([x,.77,0]);f=self.fit(self.m(form,42,c),4.0).move_to([x,-.3,0]);d=self.t(caption,30,MUTED).move_to([x,-1.36,0])
            cards.add(VGroup(box,t,f,d))
        self.play(LaggedStart(*[FadeIn(c,shift=UP*.15) for c in cards],lag_ratio=.2),run_time=1.6)
        p=self.m(r'p=\min(m,n),\qquad \Sigma_{ij}=0\ (i\ne j)',44,INK).move_to([0,-2.75,0]);self.write(p)
        self.end(13)

    def roadmap(self):
        self.begin('证明路线：先找方向，再测长度，最后拼装','02  一步一步证明',5)
        labels=[('构造对称矩阵',r'A^{\mathsf T}A',BLUE),('得到正交方向',r'v_1,\ldots,v_n',PURPLE),('确定拉伸倍率',r'\sigma_i=\sqrt{\lambda_i}',GOLD),('构造输出方向',r'u_i=Av_i/\sigma_i',GREEN)]
        nodes=VGroup()
        for i,(t,f,c) in enumerate(labels):
            x=-5.7+i*3.8
            ring=Circle(.41,color=c,stroke_width=2).move_to([x,1.15,0])
            num=self.m(str(i+1),32,c).move_to(ring)
            label=self.t(t,29,c).move_to([x,.15,0]);formula=self.fit(self.m(f,38,INK),3.35).move_to([x,-.8,0])
            nodes.add(VGroup(ring,num,label,formula))
        self.play(LaggedStart(*[FadeIn(n,shift=UP*.2) for n in nodes],lag_ratio=.23),run_time=2.0)
        for i in range(3):self.play(GrowArrow(Arrow(nodes[i][0].get_right(),nodes[i+1][0].get_left(),buff=.18,color=MUTED)),run_time=.4)
        self.foot('关键问题：为什么这些方向一定存在，而且两边都能彼此正交？')
        self.end(9)

    def two_grams(self):
        self.begin('两个对称矩阵，分别观察输入空间与输出空间','02  一步一步证明',6)
        left=self.m(r'A^{\mathsf T}A\in\mathbb{R}^{n\times n}',50,PURPLE).move_to([-3.7,2,0])
        right=self.m(r'AA^{\mathsf T}\in\mathbb{R}^{m\times m}',50,GREEN).move_to([3.7,2,0])
        self.write(VGroup(left,right),pause=.6)
        circles=VGroup(Circle(1.0,color=PURPLE),Circle(1.0,color=GREEN)).arrange(RIGHT,buff=6).move_to([0,-.2,0])
        ns=self.m(r'\mathbb{R}^n',54,PURPLE).move_to(circles[0]);ms=self.m(r'\mathbb{R}^m',54,GREEN).move_to(circles[1])
        top=ArcBetweenPoints(circles[0].get_top(),circles[1].get_top(),angle=-.48,color=GOLD).add_tip()
        bottom=ArcBetweenPoints(circles[1].get_bottom(),circles[0].get_bottom(),angle=-.48,color=BLUE).add_tip()
        a=self.m('A',44,GOLD).move_to([0,1.33,0]);at=self.m(r'A^{\mathsf T}',44,BLUE).move_to([0,-1.73,0])
        self.play(Create(circles),Write(ns),Write(ms),Create(top),Create(bottom),FadeIn(a),FadeIn(at),run_time=1.5)
        dot=Dot(circles[0].get_top(),color=GOLD,radius=.095)
        self.play(MoveAlongPath(dot,top),run_time=1.25)
        self.play(dot.animate.move_to(circles[1].get_bottom()),run_time=.35)
        self.play(MoveAlongPath(dot,bottom),run_time=1.25)
        eq=self.m(r'(A^{\mathsf T}A)^{\mathsf T}=A^{\mathsf T}A,\qquad(AA^{\mathsf T})^{\mathsf T}=AA^{\mathsf T}',43,INK).move_to([0,-2.7,0]);self.write(eq,pause=.65)
        self.foot('两者都对称；非零特征值相同，零特征值的个数可以不同')
        self.end(15)

    def positive(self):
        self.begin('第一步：为什么它的特征值不会是负数？','02  一步一步证明',7)
        self.add(self.panel())
        p=self.plane();self.add(p)
        v=np.array([.65,.8]);w=A2@v
        arrow=Arrow(p.c2p(0,0),p.c2p(*w),buff=0,color=GOLD,stroke_width=5)
        norm=np.linalg.norm(w)
        square=Square(norm*1.13,fill_color=GOLD,fill_opacity=.13,stroke_color=GOLD).move_to([3.85,-.3,0])
        l1=self.left(self.m(r'x^{\mathsf T}A^{\mathsf T}Ax',51,INK),2.05)
        l2=self.left(self.m(r'=(Ax)^{\mathsf T}(Ax)=\|Ax\|^2',47,GOLD),.9)
        l3=self.left(self.m(r'\ge0',57,GREEN),-.3)
        self.write(l1,pause=.45);self.play(GrowArrow(arrow),run_time=.8)
        self.write(l2,pause=.45);self.play(FadeIn(square),run_time=.75);self.write(l3,pause=.45)
        eig=self.left(self.m(r'\lambda_i\|v_i\|^2=\|Av_i\|^2\ge0',42,BLUE),-1.65)
        self.write(eig)
        self.foot('长度的平方不能为负，所以所有特征值都非负')
        self.end(15)

    def spectral(self):
        self.begin('第二步：谱定理给出一整组正交方向','02  一步一步证明',8)
        self.add(self.panel());p=self.plane();self.add(p)
        vs,out=self.vector_pair(p)
        circle=self.curve(p,np.eye(2),MUTED);self.play(Create(circle),GrowArrow(vs[0]),GrowArrow(vs[1]),run_time=1.3)
        l1=self.left(self.m(r'A^{\mathsf T}A=V\Lambda V^{\mathsf T}',46,PURPLE),2.12)
        l2=self.left(self.m(r'V=[v_1\ \cdots\ v_n],\quad V^{\mathsf T}V=I',42,INK),.75)
        l3=self.left(self.m(r'A^{\mathsf T}Av_i=\lambda_i v_i',48,GOLD),-.7)
        for x in [l1,l2,l3]:self.write(x,pause=.8)
        labs=VGroup(self.m('v_1',34,GOLD).next_to(vs[0].get_end(),RIGHT,buff=.08),self.m('v_2',34,CYAN).next_to(vs[1].get_end(),LEFT,buff=.08))
        self.play(FadeIn(labs),run_time=.5)
        self.foot('实对称矩阵总有一组标准正交特征向量；把它们作为输入坐标轴')
        self.end(15)

    def square_roots(self):
        self.begin('第三步：特征值是倍率的平方，开根号才是奇异值','02  一步一步证明',9)
        self.add(self.panel());p=self.plane();self.add(p)
        vs,out=self.vector_pair(p)
        self.add(self.curve(p,np.eye(2),MUTED),vs)
        l1=self.left(self.m(r'\|Av_i\|^2=v_i^{\mathsf T}(A^{\mathsf T}Av_i)',43,INK),2.0)
        l2=self.left(self.m(r'=\lambda_i\,v_i^{\mathsf T}v_i=\lambda_i',49,BLUE),.7)
        l3=self.left(self.m(r'\boxed{\sigma_i:=\|Av_i\|=\sqrt{\lambda_i}}',49,GOLD),-.8)
        self.write(l1,pause=.65);self.write(l2,pause=.65)
        self.play(Transform(vs,out),Create(self.curve(p,A2,GOLD)),run_time=1.8)
        self.write(l3,pause=.9)
        self.foot('这里特征向量已单位化；非负平方根保证奇异值非负')
        self.end(16)

    def orthogonal(self):
        self.begin('第四步：不同输入方向，为什么输出仍然正交？','02  一步一步证明',10)
        self.add(self.panel());p=self.plane();self.add(p)
        vs,out=self.vector_pair(p);self.add(out,self.curve(p,A2,MUTED))
        l1=self.left(self.m(r'(Av_i)^{\mathsf T}(Av_j)',50,INK),2.15)
        l2=self.left(self.m(r'=v_i^{\mathsf T}A^{\mathsf T}Av_j',49,BLUE),1.0)
        l3=self.left(self.m(r'=\lambda_j v_i^{\mathsf T}v_j=0\quad(i\ne j)',44,GREEN),-.2)
        for x in [l1,l2,l3]:self.write(x,pause=.7)
        right=VMobject(color=INK,stroke_width=2).set_points_as_corners([p.c2p(*(U2@np.array([.24,0]))),p.c2p(*(U2@np.array([.24,.24]))),p.c2p(*(U2@np.array([0,.24])))])
        self.play(Create(right),run_time=.6)
        f=self.left(self.m(r'u_i=\frac{Av_i}{\sigma_i},\quad u_i^{\mathsf T}u_j=\delta_{ij}',45,GOLD),-1.65)
        self.write(f,pause=.8)
        unit=VGroup(*[Arrow(p.c2p(0,0),p.c2p(*U2[:,i]),buff=0,color=c,stroke_width=5) for i,c in enumerate([GOLD,CYAN])])
        self.play(Transform(out,unit),run_time=1.4)
        self.foot('对非零奇异值，把正交的输出向量除以各自长度，就得到标准正交向量')
        self.end(18)

    def left_eigen(self):
        self.begin('现在回到另一侧：左奇异向量也是特征向量','02  一步一步证明',11)
        rows=[self.m(r'AA^{\mathsf T}u_i=AA^{\mathsf T}\frac{Av_i}{\sigma_i}',52,INK),
              self.m(r'=\frac{A(A^{\mathsf T}Av_i)}{\sigma_i}=\frac{A(\lambda_i v_i)}{\sigma_i}',51,BLUE),
              self.m(r'=\lambda_i u_i=\sigma_i^2u_i',58,GREEN)]
        for r,y in zip(rows,[2.05,.65,-.85]):
            self.fit(r,13.4);r.move_to([0,y,0]);self.write(r,pause=1.0)
        strip=self.mix(('m',r'A^{\mathsf T}A\longleftrightarrow v_i',PURPLE),('t','     同一个非零特征值     ',MUTED),('m',r'AA^{\mathsf T}\longleftrightarrow u_i',GREEN),size=30)
        self.fit(strip,14.0);strip.move_to([0,-2.65,0]);self.play(FadeIn(strip),run_time=.7)
        self.foot('左右奇异向量分别来自两侧；奇异值都是相应非零特征值的平方根')
        self.end(16)

    def assembly(self):
        self.begin('第五步：把每一列拼回去，分解就完成了','02  一步一步证明',12)
        f=self.m(r'Av_i=\sigma_i u_i',62,GOLD).move_to([0,2.18,0]);self.write(f,pause=.75)
        cols=VGroup()
        for i,c in enumerate([GOLD,CYAN,PURPLE]):
            box=RoundedRectangle(width=2.6,height=1.35,corner_radius=.12,color=c,fill_color=c,fill_opacity=.07)
            expr=self.m(fr'Av_{i+1}=\sigma_{i+1}u_{i+1}',36,c).move_to(box)
            cols.add(VGroup(box,expr))
        cols.arrange(RIGHT,buff=.65).move_to([0,.48,0])
        self.play(LaggedStart(*[FadeIn(c,shift=UP*.25) for c in cols],lag_ratio=.18),run_time=1.3)
        nextf=self.m(r'AV=U\Sigma',58,BLUE).move_to([0,-1.08,0]);self.write(nextf,pause=.65)
        final=self.m(r'AVV^{\mathsf T}=U\Sigma V^{\mathsf T}\quad\Rightarrow\quad\boxed{A=U\Sigma V^{\mathsf T}}',48,GREEN).move_to([0,-2.57,0]);self.fit(final,14.2)
        self.write(final,pause=1.0)
        self.end(15)

    def zero_rank(self):
        self.begin('补上最后的细节：零奇异值与长方形矩阵','02  一步一步证明',13)
        self.add(self.panel());p=self.plane();self.add(p)
        circ=self.curve(p,np.eye(2),BLUE)
        self.play(Create(circ),run_time=.6)
        l1=self.left(self.m(r'\sigma_i=0\Rightarrow\|Av_i\|=0\Rightarrow Av_i=0',42,RED),2.05)
        self.write(l1,pause=.6)
        self.play(Transform(circ,self.curve(p,np.diag([1.8,0]),GOLD)),run_time=1.8)
        l2=self.left(self.mix(('m',r'r=\operatorname{rank}(A)',GREEN),('t',' 个非零奇异值',INK),size=27),.55)
        self.play(FadeIn(l2),run_time=.5)
        l3=self.left(self.m(r'A=U_r\Sigma_r V_r^{\mathsf T}',54,GREEN),-.65)
        l4=self.left(self.m(r'U_r\in\mathbb{R}^{m\times r},\ V_r\in\mathbb{R}^{n\times r}',41,MUTED),-1.83)
        self.write(l3,pause=.6);self.write(l4,pause=.6)
        self.foot('只留非零部分是紧致 SVD；补齐正交基并给 Σ 补零，即得到完整 SVD')
        self.end(14)

    def eigen_contrast(self):
        self.begin('奇异值，不等于原矩阵的特征值','03  回到真实应用',14)
        self.add(self.panel());p=self.plane();self.add(p)
        circle=self.curve(p,np.eye(2),MUTED);rays=self.rays(p);self.add(circle,rays)
        f=self.left(self.m(r'A=\begin{bmatrix}0&-1\\1&0\end{bmatrix}',51,INK),1.85);self.write(f,pause=.6)
        def spin(o,alpha):
            o.become(self.rays(p,rot(PI/2*alpha)))
        self.play(UpdateFromAlphaFunc(rays,spin),run_time=1.4)
        g=self.left(self.m(r'\lambda(A)=\pm i',51,PURPLE),-.0);self.write(g,pause=.6)
        h=self.left(self.m(r'A^{\mathsf T}A=I\Rightarrow\sigma_1=\sigma_2=1',43,GOLD),-1.5);self.write(h,pause=.6)
        self.foot('旋转没有实特征方向，但长度不变，所以两个奇异值都等于一')
        self.end(12)

    def layers(self):
        self.begin('把矩阵拆成一层层可见的信息','03  回到真实应用',15)
        eq=self.m(r'A=\sum_{i=1}^{r}\sigma_i u_i v_i^{\mathsf T}',57,GOLD).move_to([0,2.1,0]);self.write(eq,pause=.65)
        u=self.data['u'];s=self.data['s'];vt=self.data['vt']
        imgs=[];labels=[]
        for j in range(4):
            component=s[j]*np.outer(u[:,j],vt[j])
            # Signed visualization: negative blue, positive gold; scale per component.
            v=component/max(abs(component.min()),abs(component.max()))
            b=np.array([15,23,32]);pos=np.array([255,209,102]);neg=np.array([93,173,236])
            rgb=b[None,None,:]+np.maximum(v,0)[:,:,None]*(pos-b)+np.maximum(-v,0)[:,:,None]*(neg-b)
            im=ImageMobject(np.uint8(np.clip(rgb,0,255)));im.width=2.75;im.move_to([-5.25+j*3.5,-.6,0]);imgs.append(im)
            labels.append(self.m(fr'\sigma_{j+1}u_{j+1}v_{j+1}^{{\mathsf T}}',34,[GOLD,BLUE,PURPLE,GREEN][j]).move_to([-5.25+j*3.5,-2.36,0]))
        self.play(LaggedStart(*[FadeIn(im,shift=UP*.12) for im in imgs],lag_ratio=.22),run_time=1.6)
        self.play(*[Write(l) for l in labels],run_time=WRITE)
        self.foot('每层都是秩一矩阵；金色为正、蓝色为负，分层图各自归一化显示')
        self.end(13)

    def optimal(self):
        self.begin('为什么保留前几层？因为它是最佳低秩近似','03  回到真实应用',16)
        self.add(self.panel())
        bars=self.spectrum();self.play(LaggedStart(*[GrowFromEdge(b,DOWN) for b in bars],lag_ratio=.035),run_time=1.5)
        xlabel=self.t('奇异值序号',26,MUTED).move_to([3.9,-2.22,0]);self.add(xlabel)
        scale=self.t('柱高按平方根缩放，便于看清尾部',22,MUTED).move_to([3.9,2.17,0]);self.add(scale)
        f=self.left(self.m(r'A_k=\sum_{i=1}^k\sigma_i u_i v_i^{\mathsf T}',50,GOLD),1.88);self.write(f,pause=.7)
        g=self.left(self.m(r'\min_{\operatorname{rank}(B)\le k}\|A-B\|_F',45,INK),.27);self.write(g,pause=.65)
        h=self.left(self.m(r'=\|A-A_k\|_F=\sqrt{\sum_{i>k}\sigma_i^2}',43,GREEN),-1.22);self.write(h,pause=.7)
        self.play(*[b.animate.set_color(RED).set_opacity(.45) for b in bars[4:]],run_time=.8)
        self.foot('Eckart–Young 定理：在相同秩预算下，截断 SVD 的总平方误差最小')
        self.end(14)

    def compression(self):
        self.begin('应用一：图像压缩，把预算花在重要结构上','03  回到真实应用',17)
        orig=self.photo(256,4.25).move_to([-3.85,.05,0]);rec=self.photo(4,4.25).move_to([3.85,.05,0])
        self.add(orig,rec)
        left=self.t('原图',31,MUTED).move_to([-3.85,2.55,0]);lab=self.m('k=4',39,GOLD).move_to([3.85,2.55,0]);self.add(left,lab)
        raw=self.m(r'256\times256=65\,536',37,MUTED).move_to([-3.85,-2.68,0]);self.add(raw)
        stats=None
        for k in [4,16,32,64]:
            energy=100*np.sum(self.data['s'][:k]**2)/np.sum(self.data['s']**2)
            nl=self.m(f'k={k}',39,GOLD).move_to(lab)
            st=self.mix(('m',fr'{k*(256+256+1):,}'.replace(',',r'\,'),GREEN),('t',f' 个数 · 能量 {energy:.1f}%',MUTED),size=27).move_to([3.85,-2.68,0])
            new=self.photo(k,4.25).move_to(rec)
            anim=[FadeOut(rec),FadeIn(new),Transform(lab,nl),FadeIn(st)]
            if stats is not None:anim.append(FadeOut(stats))
            self.play(*anim,run_time=1.1);rec=new;stats=st;self.wait(.65)
        self.foot('存储量约为 k(m+n+1) 个标量；能量是平方奇异值占比，不等于视觉准确率')
        self.end(15)

    def pca(self):
        self.begin('应用二：降维与识别，留下最有信息的方向','03  回到真实应用',18)
        self.add(self.panel());p=self.plane();self.add(p)
        rng=np.random.default_rng(8)
        points=(rng.normal(size=(65,2))*[.86,.27])@rot(30*DEGREES).T
        points-=points.mean(axis=0)
        _,_,vt=np.linalg.svd(points,full_matrices=False);v=vt[0]
        if v[0]<0:v=-v
        dots=VGroup(*[Dot(p.c2p(*xy),radius=.046,color=CYAN) for xy in points])
        axis=Line(p.c2p(*(-2.25*v)),p.c2p(*(2.25*v)),color=GOLD,stroke_width=3)
        self.play(FadeIn(dots),Create(axis),run_time=1.0)
        f=self.left(self.m(r'X=U\Sigma V^{\mathsf T}',52,GOLD),2.0);self.write(f,pause=.55)
        t=self.left(self.t('每行是一张图的特征，先减去均值',29,INK),.77);self.play(FadeIn(t),run_time=.5)
        g=self.left(self.m(r'Z=XV_k=U_k\Sigma_k',49,GREEN),-.5);self.write(g,pause=.7)
        projections=points@v[:,None]@v[None,:]
        tracks=VGroup(*[Line(p.c2p(*a),p.c2p(*b),color=BLUE,stroke_opacity=.28,stroke_width=1) for a,b in zip(points,projections)])
        self.play(Create(tracks),run_time=.6)
        self.play(*[d.animate.move_to(p.c2p(*q)) for d,q in zip(dots,projections)],run_time=1.65)
        self.foot('PCA 保留最大方差方向；这些低维特征可交给后续分类器，SVD 本身不负责认人')
        self.end(14)

    def inverse(self):
        self.begin('应用三：解方程与去噪，别让微小误差被放大','03  回到真实应用',19)
        self.add(self.panel())
        problem=self.left(self.m(r'Ax\approx b',39,BLUE),2.67);self.add(problem)
        vals=[2,.9,.35,.12,.025]
        bars=VGroup()
        for j,v in enumerate(vals):
            x=1.8+j*1.03
            r=Rectangle(width=.55,height=v*1.1,fill_color=BLUE,fill_opacity=.85,stroke_width=0).move_to([x,-1.8+v*.55,0])
            bars.add(r)
        self.play(LaggedStart(*[GrowFromEdge(b,DOWN) for b in bars],lag_ratio=.1),run_time=.9)
        f=self.left(self.m(r'x^{\dagger}=\sum_{i=1}^{r}\frac{u_i^{\mathsf T}b}{\sigma_i}\,v_i',50,GOLD),1.65);self.write(f,pause=.7)
        g=self.left(self.m(r'\sigma_i\approx0\ \Rightarrow\ 1/\sigma_i\gg1',45,RED),-.0);self.write(g,pause=.7)
        warning=self.t('小奇异值 → 大噪声放大',29,RED).move_to([3.9,2.1,0]);self.play(FadeIn(warning),run_time=.5)
        spikes=VGroup()
        for j,v in enumerate(vals):
            h=min(3.8,.17/v)
            spikes.add(Rectangle(width=.55,height=h,fill_color=RED if j>2 else GOLD,fill_opacity=.85,stroke_width=0).move_to([1.8+j*1.03,-1.8+h/2,0]))
        self.play(Transform(bars,spikes),run_time=1.25)
        text=self.left(self.t('截断或正则化，让解更稳定',32,GREEN),-1.5);self.play(FadeIn(text),run_time=.5)
        self.play(bars[-1].animate.set_opacity(.12),bars[-2].animate.set_opacity(.2),run_time=.6)
        self.foot('用于最小二乘、信号去噪和逆问题；图中的倒数高度作了封顶示意')
        self.end(14)

    def finale(self):
        self.begin('现在，这个分解已经不再神秘','从像素，回到数学',20)
        eq=self.m(r'A=U\Sigma V^{\mathsf T}',76,GOLD).move_to([0,1.82,0]);self.write(eq,pause=.8)
        cols=VGroup()
        for x,s,caption,c in [(-4.8,r'AA^{\mathsf T}u_i=\sigma_i^2u_i','输出方向',GREEN),(0,r'\sigma_i=\sqrt{\lambda_i}','拉伸倍率',GOLD),(4.8,r'A^{\mathsf T}Av_i=\sigma_i^2v_i','输入方向',PURPLE)]:
            f=self.fit(self.m(s,39,c),4.45).move_to([x,-.08,0]);t=self.t(caption,32,c).move_to([x,-1.03,0]);cols.add(VGroup(f,t))
        self.play(LaggedStart(*[FadeIn(c,shift=UP*.12) for c in cols],lag_ratio=.2),run_time=1.5)
        tagline=self.t('用最重要的方向，保留世界最重要的结构',42,INK).move_to([0,-2.5,0]);self.play(Write(tagline),run_time=1.6)
        self.end(12)
