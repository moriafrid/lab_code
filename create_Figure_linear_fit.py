from matplotlib import pyplot as plt
from sklearn.metrics import r2_score

from add_figure import add_figure, adgust_subplot
from create_folder import create_folder_dirr
from open_pickle import read_from_pickle
from function_Figures import find_RA, legend_size, get_MOO_result_parameters, get_std_halloffame
import numpy as np
import sys
from read_spine_properties import get_n_spinese
from scipy.optimize import curve_fit
from scipy.stats import linregress

if len(sys.argv)!=2:
    save_folder='final_data/total_moo/'
    print("sys.argv not running" ,len(sys.argv))
else:
    save_folder=sys.argv[1]
save_dir=save_folder+'Figure6_AMPA_NMDA_linear_fit/'
create_folder_dirr(save_dir)
scatter_size=8
passive_parameter_names=['RA_min_error','RA_best_fit','RA=100','RA=120']
def linear_fit1(x, a, c):
    return a*x+c
def linear_fit0(x, a):
    return a*x

def add_curve_fit(ax,x,y,m_name='m',units=1,name_units='',x_m=0.3,start_in_zero=True,plot_curve=True):
    if start_in_zero:
        linear_fit=linear_fit0
    else:
        slope, intercept, r, p, se = linregress(x, y)
        r_score=r**2
        popt=[intercept,slope]
        # linear_fit=linear_fit1
    # ax0_1.errorbar(all_PSD, all_AMPA, all_std_AMPA, linestyle='None')
    x_data=np.arange(0,max(x)+0.01,0.0005)
    popt, pcov = curve_fit(linear_fit, x, y)
    x_m=10/(len(m_name)+len(name_units))*2
    if plot_curve:
        ax.plot(x_data, linear_fit(x_data, *popt), '-')
        ax.text(x_m,0.03,m_name+'='+str(round(popt[0]*units,2))+name_units,transform=ax.transAxes,size='16')
    else:
        ax.text(0.05,0.94,'p='+str(round(p,2)),transform=ax.transAxes,size='16',fontweight='bold')

    y_pred = linear_fit(x, *popt)
    r_score=r2_score(y, y_pred)
    ax.text(0.05,0.94,'r='+str(round(r_score,2)),transform=ax.transAxes,size='16',fontweight='bold')

colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf','#1f77b4']


# adgust_subplot(ax8,'','Rneck [Mohm]','',latter='H')
all_W_AMPA,all_W_NMDA,all_V_NMDA,all_PSD,all_color,all_RA=[],[],[],[],[],[]
all_I_spine_head,all_I_spine_base,all_V_spine_head,all_V_spine_base,all_Rin_spine_head,all_Rin_spine_base,all_V_soma_NMDA=[],[],[],[],[],[],[]
all_Rin_soma,all_Rtrans_spine_head,all_Rtrans_spine_base,all_Rneck=[],[],[],[]

W_AMPA=[]
for i,cell_name in enumerate(read_from_pickle('cells_name2.p')):
    if cell_name=='2017_04_03_B':continue
    j=0
    W_AMPA=[]
    while len(W_AMPA)==0:
        dictMOO={'passive_parameter':passive_parameter_names[j],'syn_num':None,'from_picture':cell_name in read_from_pickle('cells_sec_from_picture.p'),'double_spine_area':False}
        RA=get_MOO_result_parameters(cell_name,'RA',**dictMOO)
        W_AMPA=get_MOO_result_parameters(cell_name,'W_AMPA',**dictMOO)
        W_NMDA=get_MOO_result_parameters(cell_name,'W_NMDA',**dictMOO)
        V_NMDA=get_MOO_result_parameters(cell_name,'V_syn_NMDA',**dictMOO)
        V_soma_NMDA=get_MOO_result_parameters(cell_name,'V_soma_NMDA',**dictMOO)
        V_spine_head=get_MOO_result_parameters(cell_name,'spine_head_V_high',**dictMOO)
        V_spine_base=get_MOO_result_parameters(cell_name,'neck_base_V_high',**dictMOO)
        Rin_spine_head=get_MOO_result_parameters(cell_name,'spine_head_Rin',**dictMOO)
        Rin_spine_base=get_MOO_result_parameters(cell_name,'neck_base_Rin',**dictMOO)
        PSD=get_MOO_result_parameters(cell_name,'PSD',**dictMOO)
        Rneck=get_MOO_result_parameters(cell_name,'Rneck',**dictMOO)
        Rin_spine_head=get_MOO_result_parameters(cell_name,'spine_head_Rin',**dictMOO)
        Rin_spine_base=get_MOO_result_parameters(cell_name,'neck_base_Rin',**dictMOO)
        Rin_soma=get_MOO_result_parameters(cell_name,'soma_Rin',**dictMOO)
        Rtrans_spine_head=get_MOO_result_parameters(cell_name,'spine_head_Rin',**dictMOO)
        Rtrans_spine_base=get_MOO_result_parameters(cell_name,'neck_base_Rin',**dictMOO)
        j+=1
        print(cell_name,sum(W_NMDA))

    if sum(W_NMDA)<=0.005*sum(PSD/max(PSD)):
        W_NMDA,V_NMDA,V_soma_NMDA=[None]*len(PSD),[None]*len(PSD),[None]*len(PSD)
    all_PSD=np.append(all_PSD, PSD)
    all_color=np.append(all_color,[colors[i]]*get_n_spinese(cell_name))
    all_RA=np.append(all_RA, RA)
    all_W_AMPA=np.append(all_W_AMPA,W_AMPA)
    all_W_NMDA=np.append(all_W_NMDA, W_NMDA)
    all_V_NMDA=np.append(all_V_NMDA,V_NMDA)
    all_V_soma_NMDA=np.append(all_V_soma_NMDA,V_soma_NMDA)
    all_V_spine_head=np.append(all_V_spine_head, V_spine_head)
    all_V_spine_base=np.append(all_V_spine_base,V_spine_base)
    all_Rin_spine_head=np.append(all_Rin_spine_head, Rin_spine_head)
    all_Rin_spine_base=np.append(all_Rin_spine_base,Rin_spine_base)
    all_I_spine_head=np.append(all_I_spine_head,list(V_spine_head/Rin_spine_head))
    all_I_spine_base=np.append(all_I_spine_base,list(V_spine_base/Rin_spine_base))

    all_Rin_soma=np.append(all_Rin_soma, Rin_soma)
    all_Rtrans_spine_head=np.append(all_Rtrans_spine_head,Rtrans_spine_head)
    all_Rtrans_spine_base=np.append(all_Rtrans_spine_base, Rtrans_spine_base)
    all_Rneck=np.append(all_Rneck,Rneck)
all_V_spine_base_NMDA,all_PSD_NMDA,all_V_spine_head_NMDA,all_V_NMDA_NMDA,color_NMDA,all_W_AMPA_NMDA,all_W_NMDA_NMDA,all_V_soma_NMDA_NMDA=[],[],[],[],[],[],[],[]
for i,val in enumerate(all_V_NMDA):
    if val != None :
        all_V_spine_head_NMDA=np.append(all_V_spine_head_NMDA,all_V_spine_head[i])
        all_V_spine_base_NMDA=np.append(all_V_spine_base_NMDA,all_V_spine_base[i])
        all_V_NMDA_NMDA=np.append(all_V_NMDA_NMDA,val)
        all_V_soma_NMDA_NMDA=np.append(all_V_soma_NMDA_NMDA,all_V_soma_NMDA[i])
        color_NMDA=np.append(color_NMDA,all_color[i])
        all_W_AMPA_NMDA=np.append(all_W_AMPA_NMDA,all_W_AMPA[i])
        all_W_NMDA_NMDA=np.append(all_W_NMDA_NMDA,all_W_NMDA[i])
        all_PSD_NMDA=np.append(all_PSD_NMDA,all_PSD[i])
all_color=list(all_color)
fig2 = plt.figure(figsize=(15, 10))  # , sharex="row", sharey="row"
fig2.subplots_adjust(left=0.1,right=0.95,top=0.9,bottom=0.1,hspace=0.2, wspace=0.25)
shapes = (2, 3)
plt.title('max EPSP  against resistance')
ax1 = plt.subplot2grid(shape=shapes, loc=(0, 0), rowspan=1, colspan=1)
ax2 = plt.subplot2grid(shape=shapes, loc=(1, 0), colspan=1, rowspan=1)
ax3 = plt.subplot2grid(shape=shapes, loc=(0, 1), colspan=1, rowspan=1)
ax4 = plt.subplot2grid(shape=shapes, loc=(1, 1), colspan=1, rowspan=1)
ax5 = plt.subplot2grid(shape=shapes, loc=(0, 2), rowspan=1, colspan=1)
ax6 = plt.subplot2grid(shape=shapes, loc=(1, 2), colspan=1, rowspan=1)

adgust_subplot(ax1,'','Rin spine head [MOum]','EPSP  spine head [mV]',latter='A')
adgust_subplot(ax2,'','Rin spine base [MOum]','EPSP  spine base [mV]',latter='B')
adgust_subplot(ax3,'','Rtrans spine head [Oum]','EPSP  spine head [mV]',latter='C')
adgust_subplot(ax4,'','Rtrans spine base [Oum]','EPSP  spine base [mV]',latter='D')
adgust_subplot(ax5,'','Rneck [MOum*1e-2]','EPSP  spine head [mV]',latter='E')
adgust_subplot(ax6,'','Rneck [MOum*1e-2]','EPSP  spine base [mV]',latter='F')

dict4plot={'ax1':[all_Rin_spine_head,all_V_spine_head],'ax2':[all_Rin_spine_base,all_V_spine_base],'ax3':[all_Rtrans_spine_head,all_V_spine_head],
 'ax4':[all_Rtrans_spine_base,all_V_spine_base],'ax5':[all_Rneck,all_V_spine_head],'ax6':[all_Rneck,all_V_spine_base]}
plot_dict={'color':all_color,'lw':scatter_size-2}
# plot_dict={'color':all_color,'label':cell_name,'lw':scatter_size-2}
for key,item in dict4plot.items():
    ax=eval(key)
    ax.scatter(item[0],item[1],**plot_dict)
    add_curve_fit(ax,item[0],item[1],start_in_zero=False,plot_curve=False)
plt.savefig(save_dir+'/V againg resistance.png')
plt.savefig(save_dir+'/V against resistance.svg')
# plt.show()

fig2 = plt.figure(figsize=(15, 10))  # , sharex="row", sharey="row"
# fig2.subplots_adjust(left=0.05,right=0.99,top=0.95,bottom=0.05,hspace=0.2, wspace=0.25)
fig2.subplots_adjust(left=0.1,right=0.95,top=0.9,bottom=0.1,hspace=0.2, wspace=0.25)
shapes = (2, 3)
plt.title('RA min error EPSP on spine and base')
ax1 = plt.subplot2grid(shape=shapes, loc=(0, 0), rowspan=1, colspan=1)
ax2 = plt.subplot2grid(shape=shapes, loc=(1, 0), colspan=1, rowspan=1)
ax3 = plt.subplot2grid(shape=shapes, loc=(0, 1), colspan=1, rowspan=1)
ax4 = plt.subplot2grid(shape=shapes, loc=(1, 1), colspan=1, rowspan=1)
ax5 = plt.subplot2grid(shape=shapes, loc=(0, 2), rowspan=1, colspan=1)
ax6 = plt.subplot2grid(shape=shapes, loc=(1, 2), colspan=1, rowspan=1)

adgust_subplot(ax1,'','','EPSP  spine head [mV]',latter='A')
adgust_subplot(ax2,'','PSD [um^2]','EPSP spine base [mV]',latter='B')
adgust_subplot(ax3,'','','',latter='C')
adgust_subplot(ax4,'','AMPA [nS]','',latter='D')
adgust_subplot(ax5,'','','',latter='E')
adgust_subplot(ax6,'','NMDA [nS]','',latter='F')


dict4plot={'ax1':[all_PSD,all_V_spine_head],'ax2':[all_PSD,all_V_spine_base],'ax3':[all_W_AMPA,all_V_spine_head],
 'ax4':[all_W_AMPA,all_V_spine_base],'ax5':[all_V_NMDA_NMDA,all_V_spine_head_NMDA],'ax6':[all_V_NMDA_NMDA,all_V_spine_base_NMDA]}
# plot_dict={'color':all_color,'label':cell_name,'lw':scatter_size-2}
for key,item in dict4plot.items():
    print(key)
    if key in ['ax5','ax6']:
        plot_dict={'color':color_NMDA,'lw':scatter_size-2}
    else:
        plot_dict={'color':all_color,'lw':scatter_size-2}
    ax=eval(key)
    ax.scatter(item[0],item[1],**plot_dict)
    add_curve_fit(ax,item[0],item[1],start_in_zero=False,plot_curve=False)

plt.savefig(save_dir+'/V_high.png')
plt.savefig(save_dir+'/V_high.svg')
# plt.show()
fig1 = plt.figure(figsize=(15, 6))  # , sharex="row", sharey="row"
fig1.subplots_adjust(left=0.1,right=0.95,top=0.85,bottom=0.15,hspace=0.01, wspace=0.3)
shapes = (1, 3)
plt.title('gmax AMPA against NMDA')
ax1 = plt.subplot2grid(shape=shapes, loc=(0, 0), rowspan=1, colspan=1)
ax2 = plt.subplot2grid(shape=shapes, loc=(0, 1), colspan=1, rowspan=1)
ax3 = plt.subplot2grid(shape=shapes, loc=(0, 2), colspan=1, rowspan=1)

adgust_subplot(ax1,'' ,'gmax AMPA [nS]','g NMDA AMPA [nS]',latter='A')
adgust_subplot(ax2,'','gmax AMPA [nS]','Vmax NMDA spine head [mV]',latter='B')
adgust_subplot(ax3,'','gmax AMPA [nS]','Vmax NMDA soma[mV]',latter='C')
dict4plot={'ax1':[all_W_AMPA_NMDA,all_W_NMDA_NMDA],'ax2':[all_W_AMPA_NMDA,all_V_NMDA_NMDA],'ax3':[all_W_AMPA_NMDA,all_V_soma_NMDA_NMDA]}
# plot_dict={'color':all_color,'label':cell_name,'lw':scatter_size-2}
for key,item in dict4plot.items():
    print(key)
    plot_dict={'color':color_NMDA,'lw':scatter_size-2}
    ax=eval(key)
    ax.scatter(item[0],item[1],**plot_dict)
    add_curve_fit(ax,item[0],item[1],start_in_zero=False,plot_curve=False)
plt.savefig(save_dir+'/NMDA against AMPA.png')
plt.savefig(save_dir+'/NMDA against AMPA.svg')

fig2 = plt.figure(figsize=(6, 6))  # , sharex="row", sharey="row"
fig2.subplots_adjust(left=0.2,right=0.95,top=0.95,bottom=0.15,hspace=0.2, wspace=0.25)
shapes = (1, 1)
plt.title('Synaptic current against PSD')
ax1 = plt.subplot2grid(shape=shapes, loc=(0, 0), rowspan=1, colspan=1)
# ax2 = plt.subplot2grid(shape=shapes, loc=(0, 1), colspan=1, rowspan=1)
adgust_subplot(ax1,'','PSD [um^2]','Isyn [nA]',latter='',xylabelsize=1,xytitlesize=100)
# adgust_subplot(ax2,'','PSD [um^2]','I spine base [nA]',latter='B')
plot_dict={'label':cell_name,'lw':scatter_size-1,'color':all_color}
ax1.scatter(all_PSD,all_I_spine_head,color=all_color,**plot_dict)
#ax2.scatter(all_PSD,I_spine_base,**plot_dict)
add_curve_fit(ax1,all_PSD,all_I_spine_head,name_units='um^2/pA')
plt.savefig(save_dir+'/gregor-current_PSD1.png')
plt.savefig(save_dir+'/gregor-current_PSD1.svg')
# plt.show()

fig1 = plt.figure(figsize=(15, 6))  # , sharex="row", sharey="row"
fig1.subplots_adjust(left=0.1,right=0.95,top=0.85,bottom=0.15,hspace=0.01, wspace=0.2)
shapes = (1, 3)
plt.title('RA_min_error')
ax1 = plt.subplot2grid(shape=shapes, loc=(0, 0), rowspan=1, colspan=1)
ax2 = plt.subplot2grid(shape=shapes, loc=(0, 1), colspan=1, rowspan=1)
ax3 = plt.subplot2grid(shape=shapes, loc=(0, 2), colspan=1, rowspan=1)

adgust_subplot(ax1,'' ,'PSD [um^2]','g_max AMPA [nS]',latter='A')
adgust_subplot(ax2,'','PSD [um^2]','g NMDA [nS]',latter='B')
adgust_subplot(ax3,'','gmax AMPA [nS]','Vmax NMDA [mV]',latter='C')
dict4plot={'ax1':[all_PSD,all_W_AMPA],'ax2':[all_PSD_NMDA,all_W_NMDA],'ax3':[all_W_AMPA_NMDA,all_V_soma_NMDA]}
plot_dict={'label':cell_name,'lw':scatter_size-1,'color':all_color}
for key,item in dict4plot.items():
    ax=eval(key)
    ax.scatter(item[0],item[1],**plot_dict)
    # add_curve_fit(ax,item[0],item[1],start_in_zero=False,plot_curve=False)

ax3.legend(loc='upper right',bbox_to_anchor=(1.2, 0.55),prop={'size': legend_size-1})

add_curve_fit(ax1,all_PSD, all_W_AMPA,'g_density',name_units='pS/um^2')
add_curve_fit(ax2,all_PSD_NMDA, all_W_NMDA_NMDA,'g_density',name_units='pS/um^2')
add_curve_fit(ax3,all_W_AMPA_NMDA, all_V_NMDA_NMDA,'AMPA/NMDA',name_units='AU',x_m=0.62)

plt.savefig(save_dir+'/AMPA_NMDA_PSD_RA_min_error.png')
plt.savefig(save_dir+'/AMPA_NMDA_PSD_RA_min_error.svg')
# plt.show()

fig1 = plt.figure(figsize=(16, 6))  # , sharex="row", sharey="row"
shapes = (1, 3)
fig1.subplots_adjust(left=0.1,right=0.95,top=0.80,bottom=0.15,hspace=0.11, wspace=0.2)
plt.title('RA min error')
ax0_1 = plt.subplot2grid(shape=shapes, loc=(0, 0), rowspan=1, colspan=1)
ax0_2 = plt.subplot2grid(shape=shapes, loc=(0, 1), colspan=1, rowspan=1)
ax0_3 = plt.subplot2grid(shape=shapes, loc=(0, 2), colspan=1, rowspan=1)

adgust_subplot(ax0_1,'','distance [um]','PSD [um^2]','A')
adgust_subplot(ax0_2,'' ,'distance [um]','gmax AMPA [nS]','B')
adgust_subplot(ax0_3,'','distance [um]','Vmax NMDA [mV]','C')
adgust_subplot(ax0_3,'','PSD/spine_head_area','gmax [mV]','C')

all_AMPA,all_NMDA,all_PSD,all_dis,all_dis_NMDA=[],[],[],[],[]
for i,cell_name in enumerate(read_from_pickle('cells_name2.p')):
    plot_dict={'color':colors[i],'label':cell_name,'lw':scatter_size-2}
    j=0
    W_AMPA=[]
    while len(W_AMPA)==0:
        dictMOO={'passive_parameter':passive_parameter_names[j],'syn_num':None,'from_picture':cell_name in read_from_pickle('cells_sec_from_picture.p'),'double_spine_area':False}
        RA=get_MOO_result_parameters(cell_name,'RA',**dictMOO)
        W_AMPA=get_MOO_result_parameters(cell_name,'W_AMPA',**dictMOO)
        W_NMDA=get_MOO_result_parameters(cell_name,'W_NMDA',**dictMOO)
        V_NMDA=get_MOO_result_parameters(cell_name,'V_syn_NMDA',**dictMOO)
        PSD=get_MOO_result_parameters(cell_name,'PSD',**dictMOO)
        distance=get_MOO_result_parameters(cell_name,'distance',**dictMOO)
        j+=1
        print(W_AMPA)

    all_AMPA=np.append(all_AMPA, W_AMPA)
    all_PSD=np.append(all_PSD, PSD)
    all_dis=np.append(all_dis, distance)


    ax0_1.scatter(distance,PSD,**plot_dict)
    if cell_name=='2017_04_03_B':continue

    if sum(W_NMDA)<=0.005*sum(PSD/max(PSD)):
        W_NMDA,V_NMDA=[None]*len(PSD),[None]*len(PSD)
    else:
        all_NMDA=np.append(all_NMDA, V_NMDA)
        all_dis_NMDA=np.append(all_dis_NMDA, distance)
    ax0_2.scatter(distance,W_AMPA,**plot_dict)
    ax0_3.scatter(distance,V_NMDA,**plot_dict)

# ax0_3.legend()

add_curve_fit(ax0_1,all_dis, all_PSD,units=10000,name_units='um')
add_curve_fit(ax0_2,all_dis, all_AMPA,units=1000,name_units='pS/um')
add_curve_fit(ax0_3,all_dis_NMDA, all_NMDA,units=1000,name_units='pS/um')
plt.savefig(save_dir+'/distance_against_PSD_AMPA_NMDA_RA_min_error.png')
plt.savefig(save_dir+'/distance_against_PSD_AMPA_NMDA_RA_min_error.svg')
# plt.show()


fig2 = plt.figure(figsize=(20, 10))  # , sharex="row", sharey="row"
fig2.subplots_adjust(left=0.05,right=0.95,top=0.95,bottom=0.1,hspace=0.2, wspace=0.25)
shapes = (2, 4)
plt.title('RA min error Rneck against AMPA and NMDA')
ax1 = plt.subplot2grid(shape=shapes, loc=(0, 0), rowspan=1, colspan=1)
ax2 = plt.subplot2grid(shape=shapes, loc=(1, 0), colspan=1, rowspan=1)
ax3 = plt.subplot2grid(shape=shapes, loc=(0, 1), colspan=1, rowspan=1)
ax4 = plt.subplot2grid(shape=shapes, loc=(1, 1), rowspan=1, colspan=1)
ax5 = plt.subplot2grid(shape=shapes, loc=(0, 2), colspan=1, rowspan=1)
ax6 = plt.subplot2grid(shape=shapes, loc=(1, 2), colspan=1, rowspan=1)
ax7 = plt.subplot2grid(shape=shapes, loc=(0, 3), colspan=1, rowspan=1)
ax8 = plt.subplot2grid(shape=shapes, loc=(1, 3), colspan=1, rowspan=1)

adgust_subplot(ax1,'','','gmax AMPA [nS]',latter='A')
adgust_subplot(ax2,'','Rin spine head [Mohm]','Vmax NMDA [nS]',latter='B')
adgust_subplot(ax3,'','','',latter='C')
adgust_subplot(ax4,'','Rin spine base [Mohm]','',latter='D')
adgust_subplot(ax5,'','','',latter='E')
adgust_subplot(ax6,'','Rtranfer [Mohm]','',latter='F')
adgust_subplot(ax7,'','','',latter='G')
adgust_subplot(ax8,'','Rneck [Mohm]','',latter='H')
all_AMPA,all_NMDA,all_PSD=[],[],[]
W_AMPA=[]
for i,cell_name in enumerate(read_from_pickle('cells_name2.p')):
    if cell_name=='2017_04_03_B':continue
    plot_dict={'color':colors[i],'label':cell_name,'lw':scatter_size-2}
    j=0
    W_AMPA=[]
    while len(W_AMPA)==0:
        dictMOO={'passive_parameter':passive_parameter_names[j],'syn_num':None,'from_picture':cell_name in read_from_pickle('cells_sec_from_picture.p'),'double_spine_area':False}
        RA=get_MOO_result_parameters(cell_name,'RA',**dictMOO)
        W_AMPA=get_MOO_result_parameters(cell_name,'W_AMPA',**dictMOO)
        W_NMDA=get_MOO_result_parameters(cell_name,'W_NMDA',**dictMOO)
        V_NMDA=get_MOO_result_parameters(cell_name,'V_syn_NMDA',**dictMOO)

        Rneck=get_MOO_result_parameters(cell_name,'Rneck',**dictMOO)
        Rin_spine_head=get_MOO_result_parameters(cell_name,'spine_head_Rin',**dictMOO)
        Rin_spine_base=get_MOO_result_parameters(cell_name,'neck_base_Rin',**dictMOO)
        Rin_soma=get_MOO_result_parameters(cell_name,'soma_Rin',**dictMOO)
        Rtrans_spine_head=get_MOO_result_parameters(cell_name,'spine_head_Rin',**dictMOO)
        Rtrans_spine_base=get_MOO_result_parameters(cell_name,'neck_base_Rin',**dictMOO)
        j+=1
        print(W_AMPA)
    if sum(W_NMDA)<=0.005*sum(PSD/max(PSD)):
        W_NMDA,V_NMDA=[None]*len(PSD),[None]*len(PSD)
    ax1.scatter(Rin_spine_head,W_AMPA,**plot_dict)
    ax3.scatter(Rin_spine_base,W_AMPA,**plot_dict)
    ax5.scatter(Rtrans_spine_base,W_AMPA,**plot_dict)
    ax7.scatter(Rneck,W_AMPA,**plot_dict)
    ax2.scatter(Rin_spine_head,V_NMDA,**plot_dict)
    ax4.scatter(Rin_spine_base,V_NMDA,**plot_dict)
    ax6.scatter(Rtrans_spine_base,V_NMDA,**plot_dict)
    ax8.scatter(Rneck,V_NMDA,**plot_dict)
plt.savefig(save_dir+'/Resistance-Conductance.png')
plt.savefig(save_dir+'/Resistance-Conductance.svg')
# plt.show()


fig1 = plt.figure(figsize=(15, 6))  # , sharex="row", sharey="row"
colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf','#1f77b4']
shapes = (1, 2)
fig1.subplots_adjust(left=0.1,right=0.95,top=0.85,bottom=0.15,hspace=0.01, wspace=0.2)
plt.title('RA=70')
ax0_1 = plt.subplot2grid(shape=shapes, loc=(0, 0), rowspan=1, colspan=1)
ax0_2 = plt.subplot2grid(shape=shapes, loc=(0, 1), colspan=1, rowspan=1)
adgust_subplot(ax0_1,'AMPA g_max [pS]' ,'PSD [um^2]','gmax AMPA [nS]',latter='A')
adgust_subplot(ax0_2,'NMDA g [pS]','PSD [um^2]','Vmax NMDA [mV]',latter='B')
all_AMPA,all_NMDA,all_PSD,all_PSD_NMDA=[],[],[],[]
W_AMPA=[]
for i,cell_name in enumerate(read_from_pickle('cells_name2.p')):
    if cell_name=='2017_04_03_B':continue
    plot_dict={'color':colors[i],'label':cell_name,'lw':scatter_size-2}
    W_AMPA=[]
    dictMOO={'passive_parameter':'RA=70','syn_num':None,'from_picture':cell_name in read_from_pickle('cells_sec_from_picture.p'),'double_spine_area':False}

    PSD=get_MOO_result_parameters(cell_name,'PSD',**dictMOO)
    RA=get_MOO_result_parameters(cell_name,'RA',**dictMOO)
    W_AMPA=get_MOO_result_parameters(cell_name,'W_AMPA',**dictMOO)
    W_NMDA=get_MOO_result_parameters(cell_name,'W_NMDA',**dictMOO)
    V_NMDA=get_MOO_result_parameters(cell_name,'V_syn_NMDA',**dictMOO)

    if sum(W_NMDA)<=0.005*sum(PSD/max(PSD)):
        W_NMDA,V_NMDA=[None]*len(PSD),[None]*len(PSD)
    else:
        all_NMDA=np.append(all_NMDA, V_NMDA)
        all_PSD_NMDA=np.append(all_PSD_NMDA, PSD)

    all_AMPA=np.append(all_AMPA, W_AMPA)
    all_PSD=np.append(all_PSD, PSD)
    ax0_1.scatter(PSD,W_AMPA,**plot_dict)
    ax0_2.scatter(PSD,V_NMDA,**plot_dict)
ax0_2.legend()
add_curve_fit(ax0_1,all_PSD,all_AMPA,name_units='g_density')
add_curve_fit(ax0_2,all_PSD_NMDA,all_NMDA,name_units='g_density')

plt.savefig(save_dir+'/AMPA_NMDA_PSD_RA=70.png')
plt.savefig(save_dir+'/AMPA_NMDA_PSD_RA=70.svg')
# plt.show()






