from matplotlib import pyplot as plt
from add_figure import add_figure, adgust_subplot
from open_pickle import read_from_pickle
from read_spine_properties import get_sec_and_seg, get_parameter, get_n_spinese, calculate_Rneck
from function_Figures import find_RA,legend_size
from glob import glob
import numpy as np
import string

colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf','#1f77b4']
scatter_size=8
fig1 = plt.figure(figsize=(20, 5))  # , sharex="row", sharey="row"
shapes = (1, 3)
ax0_1 = plt.subplot2grid(shape=shapes, loc=(0, 0), rowspan=1, colspan=1)
ax0_2 = plt.subplot2grid(shape=shapes, loc=(0, 1), colspan=1, rowspan=1)
ax0_3 = plt.subplot2grid(shape=shapes, loc=(0, 2), colspan=1, rowspan=1)

for i,cell_name in enumerate(read_from_pickle('cells_name2.p')):
    color=colors[i]
    base_dir='final_data/'+cell_name+'/'
    decided_passive_params=find_RA(base_dir)
    dicty=read_from_pickle(glob(base_dir+'Rins_pickles*'+decided_passive_params+'.p')[0])
    PSD=dicty['parameters']['PSD']

    adgust_subplot(ax0_1,'Distance from Soma','PSD','micron')
    ax0_1.scatter(PSD,dicty['parameters']['distance'],lw=scatter_size)

    adgust_subplot(ax0_2,'PSD against AMPA','PSD','AMPA [nS]')
    W_AMPA=np.array(dicty['parameters']['reletive_strengths']*dicty['parameters']['W_AMPA'])*1000 #nS
    ax0_2.scatter(PSD,W_AMPA,color=color,label=cell_name,lw=scatter_size)
    #ax0_1.legend()

    adgust_subplot(ax0_3,'PSD against NMDA','PSD','NMDA [nS]')
    W_NMDA=np.array(dicty['parameters']['reletive_strengths']*dicty['parameters']['W_NMDA'])*1000 #nS
    ax0_3.scatter(PSD,W_NMDA,marker='*',color=color,label=cell_name,lw=scatter_size)
    ax0_3.legend(loc="center right", bbox_to_anchor=(1.4, 0.4),prop={'size': legend_size+2})
for n, ax in enumerate([ax0_1,ax0_2,ax0_3]):
    ax.text(-0.1, 1.1, string.ascii_uppercase[n], transform=ax.transAxes, size=20, weight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
plt.savefig('final_data/Figure3/AMPA_NMDA_dis_relation.png')
plt.savefig('final_data/Figure3/AMPA_NMDA_dis_relation.svg')
plt.show()
plt.close()
print('AMPA-NMDA figure is ready')

fig1 = plt.figure(figsize=(20, 10))  # , sharex="row", sharey="row"
shapes = (1, 2)
ax0_1 = plt.subplot2grid(shape=shapes, loc=(0, 0), rowspan=1, colspan=1)
ax0_2 = plt.subplot2grid(shape=shapes, loc=(0, 1), colspan=1, rowspan=1)
for i,cell_name in enumerate(read_from_pickle('cells_name2.p')):
    color=colors[i]
    base_dir='final_data/'+cell_name+'/'
    decided_passive_params=find_RA(base_dir)
    dicty=read_from_pickle(glob(base_dir+'Rins_pickles*'+decided_passive_params+'.p')[0])
    PSD=dicty['parameters']['PSD']
    adgust_subplot(ax0_1,'PSD against AMPA','PSD','AMPA [nS]')
    W_AMPA=np.array(dicty['parameters']['reletive_strengths']*dicty['parameters']['W_AMPA'])*1000 #nS
    ax0_1.scatter(PSD,W_AMPA,color=color,label=cell_name,lw=scatter_size)
    #ax0_1.legend()
    
    adgust_subplot(ax0_2,'PSD against NMDA','PSD','NMDA [nS]')
    W_NMDA=np.array(dicty['parameters']['reletive_strengths']*dicty['parameters']['W_NMDA'])*1000 #nS
    ax0_2.scatter(PSD,W_NMDA,marker='*',color=color,label=cell_name,lw=scatter_size)
    ax0_2.legend(loc="center right", bbox_to_anchor=(1.25, 0.6),prop={'size': legend_size+5})
for n, ax in enumerate([ax0_1,ax0_2]):
    ax.text(-0.1, 1.1, string.ascii_uppercase[n], transform=ax.transAxes, size=20, weight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)    
plt.savefig('final_data/Figure3/AMPA_NMDA_relation.png')
plt.savefig('final_data/Figure3/AMPA_NMDA_relation.svg')
plt.show()
print('AMPA-NMDA figure is ready')
   
fig = plt.figure(figsize=(20, 20))  # , sharex="row", sharey="row"
shapes = (2, 3)
ax1 = plt.subplot2grid(shape=shapes, loc=(0, 0), rowspan=1, colspan=1)
ax2 = plt.subplot2grid(shape=shapes, loc=(0, 1), colspan=1, rowspan=1)
ax3 = plt.subplot2grid(shape=shapes, loc=(0, 2), colspan=1, rowspan=1)
ax4 = plt.subplot2grid(shape=shapes, loc=(1, 0), colspan=1, rowspan=1)
ax5 = plt.subplot2grid(shape=shapes, loc=(1, 1), colspan=1, rowspan=1)
ax6 = plt.subplot2grid(shape=shapes, loc=(1, 2), colspan=1, rowspan=1)   
for i,cell_name in enumerate(read_from_pickle('cells_name2.p')):
    color=colors[i]
    base_dir='final_data/'+cell_name+'/'
    decided_passive_params=find_RA(base_dir)
    dicty=read_from_pickle(glob(base_dir+'Rins_pickles*'+decided_passive_params+'.p')[0])
    PSD=dicty['parameters']['PSD']

    adgust_subplot(ax1,'R transfer syn','PSD','MOum')
    ax1.scatter(PSD,dicty['spine_head']['Rtrans'],color=color,lw=scatter_size)
    ax1.scatter(PSD,dicty['neck_base']['Rtrans'],marker='*',color=colors[i+1],lw=scatter_size)

    adgust_subplot(ax2,'Rins','PSD','MOum')
    ax2.scatter(PSD,dicty['spine_head']['Rin'],color=color)
    ax2.scatter(PSD,dicty['neck_base']['Rin'],marker='*',color=colors[i+1],lw=scatter_size)
    ax2.scatter(sum(PSD),dicty['soma']['Rin'],marker='o',color=color,lw=scatter_size)

    
    adgust_subplot(ax3,'PSD against AMPA','PSD','AMPA [nS]')
    W_AMPA=np.array(dicty['parameters']['reletive_strengths']*dicty['parameters']['W_AMPA'])*1000 #nS
    ax3.scatter(PSD,W_AMPA,color=color,label=cell_name,lw=scatter_size)
    ax3.legend(loc="center right", bbox_to_anchor=(1.3, 0.7),prop={'size': legend_size+4})

    adgust_subplot(ax4,'PSD against NMDA','PSD','NMDA [nS]')
    W_NMDA=np.array(dicty['parameters']['reletive_strengths']*dicty['parameters']['W_NMDA'])*1000 #nS
    ax4.scatter(PSD,W_NMDA,color=color,label=cell_name,lw=scatter_size)
    #ax4.legend()
    
    adgust_subplot(ax5,'Rneck','PSD','micron')
    ax5.scatter(PSD,calculate_Rneck(cell_name,dicty['parameters']['RA']),lw=scatter_size)

    adgust_subplot(ax6,'Distance from Soma','PSD','micron')
    ax6.scatter(PSD,dicty['parameters']['distance'],lw=scatter_size)
for n, ax in enumerate([ax1,ax2,ax3,ax4,ax5,ax6]):
    ax.text(-0.1, 1.1, string.ascii_uppercase[n], transform=ax.transAxes,size=20, weight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False) 
plt.savefig('final_data/Figure3/PSD relation.png')
plt.savefig('final_data/Figure3/PSD relation.svg')


add_figure('all cells psd against distance from soma','soma distance [um]','PSD [um^2]')

for i,cell_name in enumerate(read_from_pickle('cells_name2.p')):
    diss,psd=[],[]
    for i in range(get_n_spinese(cell_name)):
        sec,seg,dis=get_sec_and_seg(cell_name,with_distance=True,spine_num=i)
        # secs.append(sec)
        # segs.append(seg)
        diss.append(dis)
        psd.append(get_parameter(cell_name,'PSD',i))
    plt.scatter(diss,psd,lw=scatter_size,color=colors[i])
plt.savefig('final_data/Figure3/PSD_distance.png')
plt.close()
plt.show()

