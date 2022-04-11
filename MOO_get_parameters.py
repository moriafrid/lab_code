#!/ems/elsc-labs/segev-i/moria.fridman/anaconda3/envs/project/bin/python
# from __future__ import print_function
import binstar_client.utils
import bluepyopt as bpopt
import bluepyopt.ephys as ephys
import pprint
import matplotlib.pyplot as plt
import matplotlib
import pickle
from add_figure import add_figure
from open_pickle import read_from_pickle
from calculate_F_factor import calculate_F_factor
import sys
from read_spine_properties import *
from bluepyopt.ephys.parameters import NrnParameter, NrnRangeParameter
from bluepyopt.ephys.parameterscalers import *
import logging
import signal
from extra_function import SIGSEGV_signal_arises, load_hoc,load_ASC,load_swc,create_folder_dirr
from glob import glob
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['svg.fonttype'] = 'none'

signal.signal(signal.SIGSEGV, SIGSEGV_signal_arises)
logger = logging.getLogger(__name__)
matplotlib.use('agg')


do_calculate_F_factor=True
do_resize_dend=True
do_run_another_morphology=False
another_morphology_resize_dend_by=1
do_compare2result = False
frozen_NMDA_weigth=False
runnum2compare = '13'
# spine_type="mouse_spine" #"groger_spine"

print(sys.argv,flush=True)
if len(sys.argv) != 15:
    print("the function doesn't run with sys.argv",len(sys.argv),flush=True)
    cpu_node = 1
    cell_name= '2017_05_08_A_4-5'
    file_type='z_correct.swc'  #file type is just used to calculate F_factor
    passive_val={'RA':float(100),'CM':1,'RM':10000}
    passive_fit_condition='const_param'
    passive_val_name='test'
    resize_dend_by=1.0
    shrinkage_by=1.0
    SPINE_START=20
    profile = '_'
    RA=float(100)
    generation_size = 5
    num_of_genarations = 2
    double_spine_area=True
    same_strengh=True

else:
    print("the sys.argv len is correct",flush=True)
    cpu_node = int(sys.argv[1])
    cell_name = sys.argv[2]
    file_type=sys.argv[3] #hoc ar ASC
    passive_val={"RA":float(sys.argv[4]),"CM":float(sys.argv[5]),'RM':float(sys.argv[6])}
    passive_fit_condition=sys.argv[7]
    passive_val_name=sys.argv[8]
    resize_dend_by = float(sys.argv[9]) #how much the cell sweel during the electrophisiology records
    shrinkage_by =float(sys.argv[10]) #how much srinkage the cell get between electrophysiology record and LM
    SPINE_START=int(sys.argv[11])
    double_spine_area=eval(sys.argv[12])
    same_strengh=eval(sys.argv[13])
    profile = sys.argv[14]
    RA=float(sys.argv[4])
    generation_size = 100
    num_of_genarations = 1000
# same_strengh=False

if same_strengh:
    reletive_strengths=np.ones(get_n_spinese(cell_name))
else:
    psd_sizes=get_parameter(cell_name,'PSD')
    argmax=np.argmax(psd_sizes)
    reletive_strengths=psd_sizes/psd_sizes[argmax]

folder_=''
data_dir= "cells_initial_information/"
save_dir = "cells_outputs_data_short/"
if same_strengh:
    base2 = folder_+save_dir+cell_name+'/MOO_results_same_strange/'+file_type+'_SPINE_START='+str(SPINE_START)+'/'  # folder name  _RA_free
else:
    base2 = folder_+save_dir+cell_name+'/MOO_results_relative_strange/'+file_type+'_SPINE_START='+str(SPINE_START)+'/'  # folder name  _RA_free

base2+='F_shrinkage='+str(round(shrinkage_by,2))+'_dend*'+str(round(resize_dend_by,2))
if double_spine_area:
    base2+='_double_spine_area'
base_save_folder=base2 + '/'+passive_fit_condition+'/'+passive_val_name+'/'

print('base_save_folder:',base_save_folder)
create_folder_dirr(base_save_folder)
RDSM_objective_file = folder_+save_dir+cell_name+"/data/electrophysio_records/syn/mean_syn.p"
short_pulse_parameters_file=folder_+save_dir+cell_name+'/data/electrophysio_records/short_pulse_parameters.p'
morphology_dirr =glob(folder_+data_dir+cell_name+'/*'+file_type)[0]
# morphology_dirr =glob( folder_+data_dir+cell_name+'/*z_correct.swc')[0]

print('profile=',profile)

model_description='the file to fit is '+RDSM_objective_file+\
            '\ngeneration size is '+str(generation_size)+' and num of generation is '+str(num_of_genarations)
model_description=model_description+' the profile to run is '+profile

model_description=model_description+'\nRunning with  cell:'+passive_fit_condition+ ' that had the paremeters:\n'+str(passive_val)+'\nThe shrinking factor is '+str(round(shrinkage_by,2))
# passive_val = {'05_08_A_01062017':{'RM':RM*1.0/shrinkage_by,'RA':RA,'CM':CM*shrinkage_by}}

if resize_dend_by!=1.0:
    model_description=model_description+'\nthe dendrite resize by '+str(resize_dend_by)
else:
    model_description = model_description+ "\nthe dendrite isn't resize"
if do_compare2result:
    model_description=model_description+'\nwe compare to another running:'+runnum2compare

if frozen_NMDA_weigth:
    model_description=model_description+'\nthere is no NMDA in the experiment '
model_description=model_description+'\n'

model_description+="the model is run with relative strenght of "+str(reletive_strengths)
print(model_description,flush=True)
# import ast
#from utiles import *
pp = pprint.PrettyPrinter(indent=2)
#############################################################
#
# maker: YONI LEIBNER
#
# parameter that compansate for spine area in CM or g_pas
#
#############################################################

##########################################################
#
def create_spine(sim, icell, sec, seg, number=0, neck_diam=0.25, neck_length=1.35,
                 head_diam=0.944):  # np.sqrt(2.8/(4*np.pi))
    neck = sim.neuron.h.Section(name="spineNeck" + str(number))
    head = sim.neuron.h.Section(name="spineHead" + str(number))
    # icell.add_sec(neck)#?# moria why add twice??
    # icell.add_sec(head)
    neck.L = neck_length
    neck.diam = neck_diam
    head.L = head.diam = head_diam
    head.connect(neck(1))
    neck.connect(sec(seg))
    sim.neuron.h("access " + str(neck.hoc_internal_name()))
    try: icell.add_sec(neck)
    except: icell.all.append(neck)
    # if sec.name().find('dend') > -1: #?# moria- need to be sure it is ok to remove the neck and head from the dend list
    #     icell.dend.append(neck)
    # else:
    #     icell.apical.append(neck)
    sim.neuron.h.pop_section()
    sim.neuron.h("access " + str(head.hoc_internal_name()))
    try:icell.add_sec(head) #if using in hoc or ASC file (load_hoc,load_ASC
    except:icell.all.append(head) #if using in swc
    # if sec.name().find('dend') > -1: #?# moria- need to be sure it is ok to remove the neck and head from the dend list
    #     icell.dend.append(head)
    # else:
    #     icell.apical.append(head)
    sim.neuron.h.pop_section()
    for sec in [neck, head]:
        sec.insert("pas")
    neck.g_pas = 1.0 / passive_val["RM"]
    neck.cm= passive_val["CM"]
    neck.Ra=passive_val["RA"]#int(Rneck)
    return [neck, head]


def add_morph(sim, icell, syns, spine_properties):#,spine_property=self.spine_propertie
    all = []
    # sim.neuron.h.execute('create spineNeck['+str(len(syns))+']', icell)
    # sim.neuron.h.execute('create spineHead['+str(len(syns))+']', icell)
    for i, syn in enumerate(syns):
        num = syn[0]
        num = int(num[num.find("[") + 1:num.find("]")])
        if syn[0].find("dend") > -1:
            sec = icell.dend[num]
        elif syn[0].find("apic") > -1 :
            sec = icell.apic[num]
        else:
            sec = list(icell.soma)[0]
        all.append(create_spine(sim, icell, sec, syn[1], i, neck_diam=spine_properties[i]['NECK_DIAM'], neck_length=spine_properties[i]['NECK_LENGHT'],
                            head_diam=spine_properties[i]['HEAD_DIAM']))
    return all


##################################################################################################
##################################################################################################
##################################################################################################


##########################################################
#
# set this befor start
#
##########################################################



def run(cell, seed=0):
    from extraClasses import NrnSegmentSomaDistanceScaler_, NrnSectionParameterPas, neuron_start_time, \
        EFeatureImpadance, EFeaturePeak, EFeaturePeakTime, EFeatureRDSM, NrnNetstimWeightParameter, SweepProtocolRin2
    #cell_folder = base + cell + "/"  # the folder where the data is
    # cell_folder="/ems/elsc-labs/segev-i/moria.fridman/project/data_analysis_git/data_analysis/test_moo/"
    #############################################################################################################

    syn_pickle = read_from_pickle(RDSM_objective_file)
    M=syn_pickle#['mean']

    T_with_units=M[0]
    T_with_units=T_with_units-T_with_units[0]
    T_with_units=T_with_units.rescale('ms')
    V_with_units=M[1]
    T_base = np.array(T_with_units)
    V_base = np.array(V_with_units)
    # syn_place=np.argmax(np.array(V_base))

    dt =T_with_units.units

    spike_timeing=T_base[np.argmax(np.array(V_base))-65]
    # syn_place=np.argmax(np.array(V_base))
    E_PAS=read_from_pickle(short_pulse_parameters_file)['E_pas']
    V_base=V_base+E_PAS
    # E_PAS=syn_pickle['E_pas']
    # E_PAS=np.mean(V_base[:syn_place-10])

    ###################################################################################
    # make morphology png fig and load morphology to opt
    ###################################################################################

    synapses_dict=pd.read_excel(folder_+save_dir+"synaptic_location_seperate.xlsx",index_col=0)
    synapses_locations=[]
    spine_properties={}
    for i in range(get_n_spinese(cell_name)):
        sec=synapses_dict[cell_name+str(i)]['sec_name']
        seg=float(synapses_dict[cell_name+str(i)]['seg_num'])
        synapses_locations.append([sec,seg])
        spine_properties[i]=get_building_spine(cell_name,i)


    morphology = ephys.morphologies.NrnFileMorphology(morphology_dirr, load_cell_function=load_cell_function,do_replace_axon=True,
                                                      extra_func=True, extra_func_run=add_morph, spine_poses=synapses_locations,
                                                      do_resize_dend=do_resize_dend,resize_dend_by=resize_dend_by,
                                                      do_shrinkage=True,shrinkage_by=shrinkage_by,
                                                      spine_properties=spine_properties)
    # morphology = ephys.morphologies.NrnFileMorphology(morphology_dirr, do_replace_axon=True,
    #                                                   extra_func=True, extra_func_run=add_morph, spine_poses=synapses_locations[cell],
    #                                                   do_resize_dend=do_resize_dend,resize_dend_by=resize_dend_by,nseg_frequency=40)  # change axon to AIS and add spine locations
    # morphology1 = ephys.morphologies.NrnFileMorphology(morphology_dirr, load_cell_function=load_cell_function,do_replace_axon=True,
    #                                                   extra_func=True, extra_func_run=add_morph,
    #                                                   spine_poses=synapses_locations,
    #                                                   do_resize_dend=True,resize_dend_by=another_morphology_resize_dend_by,
    #                                                   nseg_frequency=40)  # change axon to AIS and add spine locations
    somatic_loc = ephys.locations.NrnSeclistLocation('somatic', seclist_name='somatic')
    basal_loc = ephys.locations.NrnSeclistLocation('basal', seclist_name='basal')
    apical_loc = ephys.locations.NrnSeclistLocation('apical', seclist_name='apical')
    axonal_loc = ephys.locations.NrnSeclistLocation('axonal', seclist_name='axonal')

    location_dict = {'all': [somatic_loc, basal_loc, apical_loc, axonal_loc],
                     'global': [somatic_loc, basal_loc, apical_loc, axonal_loc],
                     'somatic': [somatic_loc],
                     'apical': [apical_loc],
                     'basal': [basal_loc],
                     'axon': [axonal_loc]}
    all = [somatic_loc, basal_loc, apical_loc, axonal_loc]

    ###################################################################################
    # mech_configs=ast.literal_eval(open(mechanism).read())
    mechanism_list = []
    # for mech in mech_configs:
    #     sec_list = []
    #     for l in mech['sectionlist']:
    #         sec_list.extend(location_dict[l])
    #     mechanism_list.append( ephys.mechanisms.NrnMODMechanism(name=mech['mech_name'],prefix=mech['mech_name'],locations=sec_list))

    sec_list = location_dict["all"]
    mechanism_list.append(
        ephys.mechanisms.NrnMODMechanism(name="pas", prefix="pas", locations=sec_list))

    ##################################################################################


    ###################################################################################
    # model parameters
    ###################################################################################
    param_names = ["cm"]
    parameters_list = []

    sec_list = location_dict["all"]

    F_FACTOR_DISTANCE = NrnSegmentSomaDistanceScaler_(name='spine_factor',
                                                      dist_thresh_apical=SPINE_START,
                                                      dist_thresh_basal=SPINE_START,
                                                      F_factor=F_factor,
                                                      shrinckage_factor=shrinkage_by)
    parameters_list.append(
        ephys.parameters.NrnSectionParameter(name="Ra", param_name="Ra", value=passive_val["RA"],
                                             bounds=[60, 350], locations=sec_list, frozen=RA_FROZEN)) #@# in the paper they said bound of 70-100 ohm*cm
    parameters_list.append(
        ephys.parameters.NrnSectionParameter(name="g_pas", param_name="g_pas", value=1.0 / passive_val["RM"],
                                             locations=sec_list, frozen=True, value_scaler=F_FACTOR_DISTANCE))
    parameters_list.append(
        ephys.parameters.NrnSectionParameter(name="cm", param_name="cm", bounds=[0.5, 4], value=CM_startValue,
                                             locations=sec_list, frozen=CM_FROZEN, value_scaler=F_FACTOR_DISTANCE)) #@# change the limit form [0.5, 1.5]

    param_names.append("e_pas")
    sec_list = location_dict["all"]

    parameters_list.append(
        ephys.parameters.NrnSectionParameter(name="e_pas", param_name="e_pas", value=E_PAS, locations=sec_list,
                                             frozen=True))

    syn_locations = []
    syn_mec = []
    tau_param_locs = []
    param_locs = []
    NMDA_param_locs = []
    syn_params = []

    ##################################################################
    #
    # useing weight and tau for every syn in opt
    #
    ##################################################################
    netstims = []
    netstims_NMDA = []
    rec = []
    somacenter_loc = ephys.locations.NrnSeclistCompLocation(
        name='somacenter',
        seclist_name='somatic',
        sec_index=0,
        comp_x=0.5)
    for i, syn in enumerate(synapses_locations):
        syn_locations.append(ephys.locations.NrnSectionCompLocation(
            name='syn' + str(i),
            sec_name="spineHead" + str(i),#@#??
            comp_x=1)) #segx (0..1) of segment inside section


        # insert AMPA
        syn_mec.append(ephys.mechanisms.NrnMODPointProcessMechanism(
            name='exp2syn_' + str(i),
            suffix='Exp2Syn',
            locations=[syn_locations[-1]]))
        tau_param_locs.append(ephys.locations.NrnPointProcessLocation(
            'expsyn_loc' + str(i),
            pprocess_mech=syn_mec[-1])) #pprocess_mech (str) – point process mechanism

        # insert NMDA
        syn_mec.append(ephys.mechanisms.NrnMODPointProcessMechanism(
            name='NMDA_' + str(i),
            suffix='NMDA',
            locations=[syn_locations[-1]]))
        NMDA_param_locs.append(ephys.locations.NrnPointProcessLocation(
            'NMDA_loc' + str(i),
            pprocess_mech=syn_mec[-1]))
#@# why I need to add AMPA and NMDA recheptors for each synaptic location instead one
        #################################diff weight to synapses###################################################
        #
        stim_start = spike_timeing + neuron_start_time
        # # this only for the first synapse in that cell
        number = 1
        interval = 1
        # for i in range(len(get_n_spine(cell_name)):
        netstims.append(ephys.stimuli.NrnNetStimStimulus(
            total_duration=T_base[-1] + neuron_start_time,
            number=number,
            interval=interval,
            start=stim_start,
            weight=5e-4,
            locations=[tau_param_locs[i]]))

        netstims_NMDA.append(ephys.stimuli.NrnNetStimStimulus(
            total_duration=T_base[-1]+neuron_start_time,
            number=number,
            interval=interval,
            start=stim_start,
            weight=5e-4,
            locations=[NMDA_param_locs[i]]))

        syn_params.append(NrnNetstimWeightParameter(
            name='weight_AMPA',
            param_name='weight[0]',
            frozen=False,
            value=0.002,
            bounds=[0.000000, 0.01],
            locations=[netstims[i]],
            reletive_strength = [reletive_strengths[i]])) #[1, 0.1,0.01]))
            # reletive_strength =   [get_parameter(cell_name,'PSD',spine_num=i)]))#[1, 0.1,0.01]))
    # this  need to add the weight to optimization

        syn_params.append(NrnNetstimWeightParameter(
            name='weight_NMDA',
            param_name='weight[0]',
            frozen=frozen_NMDA_weigth,
            value=0.0012,
            bounds=[0.000, 0.005],
            locations=[netstims_NMDA[i]],
            reletive_strength = [reletive_strengths[i]])) #[1, 0.1,0.01]))

            # reletive_strength = [get_parameter(cell_name,'PSD',spine_num=i)])) #[1, 0.1,0.01]))


    rec.append(ephys.recordings.CompRecording(
        name='soma.v',
        location=somacenter_loc,
        variable='v'))
    # for syn_loc in syn_locations:
    rec.append(ephys.recordings.CompRecording(
        name='syn0.v',
        location=syn_locations[0],
        variable='v'))

    syn_params.append(ephys.parameters.NrnPointProcessParameter(
        name='exp2syn_tau1',
        param_name='tau1',
        value=0.0012,
        frozen=AMPA_RISE_FIX,
        bounds=[0.001, 2.1],#[0.1, 0.4],
        locations=tau_param_locs))
    syn_params.append(ephys.parameters.NrnPointProcessParameter(
        name='exp2syn_tau2',
        param_name='tau2',
        value=1.8,#1.8,  # min(AMPA_FIT[cell]['tau2'],8),
        frozen=AMPA_DECAY_FIX,
        bounds=[0.01, 4],#[1, 3],
        locations=tau_param_locs))

    syn_params.append(ephys.parameters.NrnPointProcessParameter(
        name='NMDA_tau_r_NMDA',
        param_name='tau_r_NMDA',
        value=8,
        frozen=False,
        bounds=[7, 15],
        locations=NMDA_param_locs))
    syn_params.append(ephys.parameters.NrnPointProcessParameter(
        name='NMDA_tau_d_NMDA',
        param_name='tau_d_NMDA',
        value=35,
        frozen=False,
        bounds=[25, 90],
        locations=NMDA_param_locs))
    syn_params.append(ephys.parameters.NrnPointProcessParameter(
        name='NMDA_n_NMDA',
        param_name='n_NMDA',
        value=0.27,
        frozen=N_NMDA_FROZEN,
        bounds=[0.1, 0.4],
        locations=NMDA_param_locs))
    syn_params.append(ephys.parameters.NrnPointProcessParameter(
        name='NMDA_gama_NMDA',
        param_name='gama_NMDA',
        value=0.076,
        frozen=GAMMA_FROZEN,
        bounds=[0.06, 0.09],
        locations=NMDA_param_locs))

    protocol = ephys.protocols.SweepProtocol('netstim_protocol', netstims + netstims_NMDA, [rec[0]], cvode_active=False)
    protocol_spine_head = ephys.protocols.SweepProtocol('netstim_protocol', netstims+ netstims_NMDA , [rec[1]], cvode_active=False)

    ##################################################################################


    ##################################################################################
    #
    # build  the model
    #
    ##################################################################################

    model = ephys.models.CellModel('Model', morph=morphology, mechs=mechanism_list + syn_mec,
                                   params=parameters_list + syn_params,
                                   # seclist_names=['dendritic']
                                   )
    param_names = [param.name for param in model.params.values() if not param.frozen]  # parameters for oprimization

    ##################################################################################
    # print(model_description)
    print(model)
    parameters = model.params
    print(parameters.keys())

    ##################################################################################
    #
    # define simulator
    #
    ##################################################################################
    sim = ephys.simulators.NrnSimulator(dt=dt,
                                        cvode_active=False)  # this uses neuron as the simulator*
    ##################################################################################


    ##################################################################################
    #
    # difine features
    #
    ##################################################################################
    feature1 = EFeatureRDSM(T_base, V_base)
    feature2 = EFeaturePeakTime(T_base, V_base)
    feature3 = EFeaturePeak(T_base, V_base, exp_std=0.05)

    objective1 = ephys.objectives.SingletonObjective('netstim_protocol1', feature1)
    objective2 = ephys.objectives.SingletonObjective('netstim_protocol1', feature2)
    objective3 = ephys.objectives.SingletonObjective('netstim_protocol3', feature3)

    # objectives=[objective1,objective2 , objective3]
    objectives = [objective1, objective3]
    score_calc = ephys.objectivescalculators.ObjectivesCalculator(objectives)

    ##################################################################################

    def run(SweepProtocolRin2):
        return SweepProtocolRin2.run

    ##################################################################################
    #
    # difine evaluator
    #
    ##################################################################################
    if in_parallel:
        from datetime import datetime
        import ipyparallel as ipp
        rc = ipp.Client(profile=profile)
        print(rc.ids)
        # rc.wait_for_engines(n=cpu_node,timeout=180)
        print(rc[:].apply_sync(lambda: "Hello, World"))
        for g in rc.ids:
            try:
                with rc[g].sync_imports():
                    import bluepyopt

                    from extraClasses import NrnSegmentSomaDistanceScaler_, NrnSectionParameterPas, neuron_start_time, \
                        EFeatureImpadance, EFeaturePeak, EFeaturePeakTime, EFeatureRDSM, NrnNetstimWeightParameter, \
                        SweepProtocolRin2 # add_morph creat_spine
            except:
                print("closing engine number", g)
                rc.shutdown([g])
        print("that what's left: ", rc.ids)

        import logging
        logger = logging.getLogger()

        rc[:].push(dict(add_morph=add_morph, create_spine=create_spine,
                        NECK_LENGHT = [spine_properties[i]['NECK_LENGHT'] for i in range(get_n_spinese(cell_name))],
                        HEAD_DIAM = [spine_properties[i]['HEAD_DIAM'] for i in range(get_n_spinese(cell_name))],
                        passive_val = passive_val, Rneck=Rneck, cell=cell))
        print('Using ipyparallel with %d engines', len(rc),flush=True)
        print(rc[:].apply_sync(lambda: print(add_morph)))
        lview = rc.load_balanced_view()

        def mapper(func, it):
            print("func in mapper is: ", func.__name__)
            start_time = datetime.now()
            ret = lview.map_sync(func, it)

            logger.debug('Generation took %s', datetime.now() - start_time)
            return ret

        map_function = mapper
    else:
        map_function = None
    ##################################################################################



    ##################################################################################
    #
    # define evaluator
    #
    ##################################################################################
    print("params ", param_names, model.params.keys())
    cell_evaluator = ephys.evaluators.CellEvaluator(
        cell_model=model,
        param_names=param_names,
        fitness_protocols={'RDSM': protocol},  # "Rin2":protocol3
        fitness_calculator=score_calc,
        sim=sim)
    ##################################################################################

    optimisation = bpopt.optimisations.DEAPOptimisation(
        evaluator=cell_evaluator,
        offspring_size=generation_size,  #– Number of offspring individuals in each generation
        #@# offspring_size=1 feels very small
        map_function=map_function,
        seed=seed)  #– Random number generator seed

    data_bef = open(base_save_folder + 'befor_simulation.txt', 'w')
    data_bef.write('model description:\n'+model_description+'\n')
    data_bef.write('neck resistance is '+str(result_R_neck_m_ohm)+'\n')
    data_bef.write(model.__str__())
    data_bef.close()
    stim_befor=True


    if stim_befor:
        start_values = {}
        for param in model.params:
            if model.params[param].frozen:
                continue
            start_values[param] = model.params[param].value
        start_values1 = {}
        # for param in model1.params:
        #     if model1.params[param].frozen:
        #         continue
        #     start_values1[param] = model1.params[param].value
        fig=add_figure('befure fit',T_with_units.units,V_with_units.units)
        responses = protocol.run(cell_model=model, param_values=start_values, sim=sim)
        temp = np.array(responses['soma.v']['time'])
        temp2 = np.array(responses['soma.v']['voltage'])
        start = np.where(temp > neuron_start_time)[0][0]
        temp = temp - temp[start]
        temp = temp[start:]
        temp2 = temp2[start:]
        plt.plot(temp, temp2, color='yellowgreen', alpha=1, linewidth=5,label='dend*'+str(resize_dend_by))

        # plt.errorbar(T_base,V_base, yerr=V2, color = 'k', ecolor="b", alpha = 0.03)
        plt.plot(T_base, V_base, color='black',alpha=0.2,label='data',lw=5)
        plt.legend()
        plt.savefig(base_save_folder + 'before_fit_transient_RDSM.png')
        pickle.dump(fig, open(base_save_folder + 'before_fit_transient_RDSM.p', 'wb'))

        plt.close()
    final_pop, hall_of_fame, logs, hist = optimisation.run(max_ngen=num_of_genarations)

    print(cell)
    print('hall of fame:')
    print(hall_of_fame)

    print()
    print('final population')
    print(final_pop)

    best = hall_of_fame[0]
    parameters2 = param_names
    # parameters2.remove("e_pas")
    pickle.dump({
        "parameters": parameters2,
        "hist": hist,
        "logs": logs,
        # "tau": peel_epsp_first[cell] / 1000.0,#@#
        # "Rin": Rin[cell],#@#
        "model": model.__str__()
    }, open(base_save_folder + "data.p", "wb"))

    pickle.dump({
        "parameters": parameters2,
        "hall_of_fame": hall_of_fame,
        "model": model.__str__(),
        "syn_location":synapses_locations,
        "spine": spine_properties,
        "F_factor":F_factor
    }, open(base_save_folder + "hall_of_fame.p", "wb"))

    pickle.dump({
        "parameters": parameters2,
        "final_pop": final_pop,
        "model": model.__str__(),
        "syn_location": synapses_locations,
    }, open(base_save_folder + "final_pop.p", "wb"))

    data = open(base_save_folder + 'data.txt', 'w')
    data.write('model description:\n'+model_description+'\n')
    data.write('Best individual values\n')

    for key, val in zip(parameters2, best):
        v=val
        if str(key).startswith('weight'):
            v *=1000
            data.write(key + '\t\t' + str(v) + '\t [nano-Siemens]\n')
        else:
            data.write(key + '\t\t' + str(v) + '\t [mS]\n')
        if key == "g_pas": r = val
    # data.write('RM\t\t'+str(1.0/r)+'\n')
    data.write('\n')
    data.write('hall of fame ' + str(len(hall_of_fame)) + '\n')
    m = np.array(hall_of_fame).mean(axis=0)
    s = np.array(hall_of_fame).std(axis=0)
    data.write('key		     mean		     std             units\n')
    for key, val, st in zip(parameters2, m, s):
        v = val
        st2=st
        if str(key).startswith('weight'):
            v *= 1000
            st2*=1000
            data.write(key + '\t' + str(round(v, 4)) + '\t' + str(round(st2, 4)) +'\t [nano-Siemens]' +'\n')
        else:
            data.write(key + '\t' + str(round(v, 4)) + '\t' + str(round(st2, 4)) +'\t [mS]' +'\n')

    data.write('\n')
    title = '		'
    for key in parameters2:
        title += key + '	'
    title += ' RM\n'
    data.write(title)
    for ind in hall_of_fame:
        ind2 = np.array(ind).round(4)
        line = ''
        for k in ind:
            if (round(k, 4) == 0):
                line += str(k) + '	'
            else:
                line += str(round(k, 4)) + '	'
        data.write(line + str(round(1.0 / ind[0], 3)) + '\n')
        data.write('Fitness values:' + str(ind.fitness) + '\n')

    data.write('\n\nFinal population: ' + str(len(final_pop))+'\n')
    m = np.array(final_pop).mean(axis=0)
    s = np.array(final_pop).std(axis=0)
    data.write('key		      mean		      std           units\n')
    for key, val, st in zip(parameters2, m, s):
        v = val
        st2=st
        if str(key).startswith('weight'):
            v *= 1000
            st2 *= 1000
            data.write(key + '\t' + str(round(v, 4)) + '\t' + str(round(st2, 4)) + '\t [nano Siemens]\n')
        else:
            data.write(key + '\t' + str(round(v, 4)) + '\t' + str(round(st2, 4)) + '\t [mS]\n')
    # data.write('RM\t\t'+str(round(1.0/m[0],3))+'\t'+str(round(1.0/s[0],3))+'\n')

    data.close()
    pickle.dump({
        "parameters": parameters2,
        "final_pop": final_pop,
        "model": model.__str__(),
        "mean_final_pop":m,
        "std_final_pop":s
    }, open(base_save_folder + "final_pop.p", "wb"))
    print()
    best_ind = hall_of_fame[0]
    print('Best individual: ', best_ind)
    print('Fitness values: ', best_ind.fitness)

    best_ind_dict = cell_evaluator.param_dict(best_ind)
    print(cell_evaluator.evaluate_with_dicts(best_ind_dict))
    default_params = {}
    # for key, val in zip(parameters2, best_ind):
    #     default_params[key] = val
    print(default_params)
    fig=add_figure('MOO RDSM fit to transient',T_with_units.units,V_with_units.units)
    responses = protocol.run(cell_model=model, param_values=best_ind_dict, sim=sim)

    temp = np.array(responses['soma.v']['time'])
    temp2 = np.array(responses['soma.v']['voltage'])
    start = np.where(temp > neuron_start_time)[0][0]
    temp = temp - temp[start]
    temp = temp[start:]
    temp2 = temp2[start:]

    if do_resize_dend:
        plt.plot(temp, temp2, color='yellowgreen', linewidth=5,label='after fit dend*'+str(resize_dend_by))
    else:
        plt.plot(temp, temp2, color='yellowgreen', linewidth=5,label='after fit dend=1')

    # plt.errorbar(T_base,V_base, yerr=V2, color = 'k', ecolor="b", alpha = 0.03)
    plt.plot(T_base, V_base, color='black',label='data',alpha=0.2,lw=5)
    # plt.bar(T2,V2,color='b', alpha=0.2)

    plt.xlabel('time(ms)')
    plt.ylabel('V(mV)')
    plt.plot([], [], ' ', label='gmax_AMPA='+str(round(best[0]*1000,3))+' [nS] \ngmax_NMDA=' +str(round(best[1]*1000,3))+' [nS]\nrelative strenght '+str(reletive_strengths))
    plt.legend(fontsize=12)
    plt.savefig(base_save_folder + 'fit_transient_RDSM.png')
    plt.savefig(base_save_folder + 'fit_transient_RDSM.pdf')
    pickle.dump(fig, open(base_save_folder + 'fit_transient_RDSM.p', 'wb'))
    plt.close()

    print("when done h.dt = ", sim.neuron.h.dt)



# generation_size = 100
# num_of_genarations = 5000
seed = 123456
cell=cell_name


print(cell)
#  for run in cluster:
# qsub -pe pnrn 51 first_run_cm_g_pas3.sh 1RM000 100 10 0 50 Ra_250
# ssh moria.fridman@bs-cluster.elsc.huji.ac.il
# sbatch -p ss.q -c50 first_run_cm_g_pas3.sh 1000 100 10 0 50 Ra_250 human_spine 365
# start_values = NMDA_fit_grad[cell]

CM_FROZEN = True
RA_FROZEN = True

N_NMDA_FROZEN = True
GAMMA_FROZEN = True

AMPA_RISE_FIX = False
AMPA_DECAY_FIX = False

####################spine parameters######################
# NECK_LENGHT,NECK_DIAM,HEAD_DIAM=get_spine_params(spine_type)

if file_type=='hoc':
    load_cell_function=load_hoc
elif file_type=='ASC':
    load_cell_function=load_ASC
elif 'swc' in file_type:
    load_cell_function=load_swc
Rneck = passive_val["RA"]
if do_calculate_F_factor:
    temp_cell=None
    temp_cell=load_cell_function(glob(morphology_dirr[:morphology_dirr.rfind('/')]+'/*'+file_type)[0])
    # if file_type=='hoc':
    #     temp_cell=load_hoc(morphology_dirr)
    # elif file_type=='ASC':
    #     temp_cell=load_ASC(morphology_dirr)
    for sec in temp_cell.dend+temp_cell.apic:
        sec.diam=sec.diam*resize_dend_by
        sec.L=sec.L*shrinkage_by
    F_factor=calculate_F_factor(temp_cell,'mouse_spine',double_spine=double_spine_area)
else:
    F_factor = 1.9
temp_cell=None
model_description=model_description+'\nF_factor is equal to '+str(F_factor)

spine_properties={}
result_R_neck_m_ohm=[]
for i in range(get_n_spinese(cell_name)):
    spine_properties[i]=get_building_spine(cell_name,i)
    result_R_neck_m_ohm.append((spine_properties[i]['NECK_LENGHT'] * 4.0 * passive_val['RA'])/(np.pi*(spine_properties[i]['NECK_DIAM']/2)**2) *100.0 *1e-6)# 0.25 is neck_diam
spine_properties['F_factor']=F_factor

#################################33
CM_startValue = passive_val["CM"]
# result_R_neck_m_ohm = ((NECK_LENGHT * 4.0 * float(Rneck))/(np.pi*0.25**2)) / 100.0 # 0.25 is neck_diam
# result_R_neck_m_ohm = ((NECK_LENGHT * 4.0 * float(Rneck))/(np.pi*(spine_neck_diam/2)**2)) *100.0 *1e-6# 0.25 is neck_diam

in_parallel = profile != "_"
print("profile ", profile)
run(cell, seed=seed)
print('the MOO running is completed')
# need to revert protocols and check dt
