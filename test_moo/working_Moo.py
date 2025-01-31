#! /ems/elsc-labs/segev-i/yoni.leibner/anaconda2/bin/ipython
from __future__ import print_function
runnum='18' #change for every running
model_description='running number is'+ str(runnum)+'\n after yoni correction   '\
            '\n diameter*2 '\
            '\n small generation (100)\n'
                  #'\n the weight for the 1 synaps that groger send me is 1 for both NMDA and AMPA.\n' # write what is change in this running
do_resize_dend=True
resize_dend_by=2
generation_size = 100
num_of_genarations = 100

import bluepyopt as bpopt
import bluepyopt.ephys as ephys
import pprint

pp = pprint.PrettyPrinter(indent=2)
import numpy as np

# matplotlib.use('agg')
import matplotlib.pyplot as plt
import os, sys, pickle
# import ast
#from utiles import *
#############################################################
#
# maker: YONI LEIBNER
#
# parameter that compansate for spine area in CM or g_pas
#
#############################################################

from bluepyopt.ephys.parameters import NrnParameter, NrnRangeParameter
from bluepyopt.ephys.parameterscalers import *

import logging

logger = logging.getLogger(__name__)
#######################################
import signal
def SIGSEGV_signal_arises(signalNum, stack):
    print(f"{signalNum} : SIGSEGV arises")
    # Your code

signal.signal(signal.SIGSEGV, SIGSEGV_signal_arises)
##########################################################
#
def create_spine(sim, icell, sec, pos, number=0, neck_diam=0.25, neck_length=1.35,
                 head_diam=0.944):  # np.sqrt(2.8/(4*np.pi))
    neck = sim.neuron.h.Section(name="spineNeck" + str(number))
    head = sim.neuron.h.Section(name="spineHead" + str(number))
    icell.all.append(neck)
    icell.all.append(head)
    neck.L = neck_length
    neck.diam = neck_diam
    head.L = head.diam = head_diam
    head.connect(neck(1))
    neck.connect(sec(pos))
    sim.neuron.h("access " + str(neck.hoc_internal_name()))
    if Rneck == "normal_neck":
        icell.all.append(neck)
        if sec.name().find('dend') > -1:
            icell.basal.append(neck)
        else:
            icell.apical.append(neck)
    sim.neuron.h.pop_section()
    sim.neuron.h("access " + str(head.hoc_internal_name()))
    icell.all.append(head)
    if sec.name().find('dend') > -1:
        icell.basal.append(head)
    else:
        icell.apical.append(head)
    sim.neuron.h.pop_section()
    for sec in [neck, head]:
        sec.insert("pas")
    if not Rneck == "normal_neck":
        neck.g_pas = 1.0 / passive_val[cell]["RM"]
        neck.cm= passive_val[cell]["CM"]
        neck.Ra=int(Rneck)
    return [neck, head]


def add_morph(sim, icell, syns):
    all = []
    # sim.neuron.h.execute('create spineNeck['+str(len(syns))+']', icell)
    # sim.neuron.h.execute('create spineHead['+str(len(syns))+']', icell)

    for i, syn in enumerate(syns):
        num = syn[0]
        num = int(num[num.find("[") + 1:num.find("]")])
        if syn[0].find("dend") > -1:
            sec = icell.dend[num]
        elif syn[0].find("apic") > -1:
            sec = icell.apic[num]
        else:
            sec = icell.soma[0]
        all.append(create_spine(sim, icell, sec, syn[1], i, neck_diam=0.25, neck_length=NECK_LENGHT,
                                head_diam=HEAD_DIAM))
    # neck_length=1.35
    return all


##################################################################################################
##################################################################################################
##################################################################################################


##########################################################
#
# set this befor start
#
##########################################################

import glob

base = "../"


def run(cell, seed=0):
    from extraClasses import NrnSegmentSomaDistanceScaler_, NrnSectionParameterPas, neuron_start_time, \
        EFeatureImpadance, EFeaturePeak, EFeaturePeakTime, EFeatureRDSM, NrnNetstimWeightParameter, SweepProtocolRin2
    #cell_folder = base + cell + "/"  # the folder where the data is
    # cell_folder="/ems/elsc-labs/segev-i/moria.fridman/project/data_analysis_git/data_analysis/test_moo/"
    morphology_dirr = '/ems/elsc-labs/segev-i/moria.fridman/project/data_analysis_git/data_analysis/try1.swc'
    #############################################################################################################
    from open_pickle import read_from_pickle
    RDSM_objective_file = "../data/syn_mean.p"
    #RDSM_objective_file = base + "traces_for_epsp/" + cell + "/firstSyn_mean.txt"
    #RDSM_objective_file_std = base + "traces_for_epsp/" + cell + "/firstSyn_std.txt"

    M, hz, rest, = read_from_pickle(RDSM_objective_file, rest=True,hz=True)

    T_base = M[1]
    V_base = M[0]+rest
    # M2 = np.loadtxt(RDSM_objective_file_std)
    # T2 = M2[:, 0]
    # V2 = M2[:, 1]

    dt = 1000/hz
    # spike_timeing = start_times[cell]
    spike_timeing=99
    # spike_timeing_ix = int(start_times[cell] / dt)
    spike_timeing_ix = int(99 / dt)
    # E_PAS = np.mean(V[max(0,spike_timeing_ix-2000):spike_timeing_ix])
    # E_PAS = np.mean(V_base[:max(40, spike_timeing_ix - 10)])
    E_PAS=rest
    try: os.mkdir(base2)
    except: pass
    try:  os.mkdir(base2 + 'MOO_opt_folder_same_w_peel_syn_spines_featues_cm_g_pas_first_seed_' + str(seed))
    except: pass
    try: os.mkdir(base2 + 'MOO_opt_folder_same_w_peel_syn_spines_featues_cm_g_pas_first_seed_' + str(seed) + '/' + cell)
    except: pass
    try: os.mkdir(base2 + 'MOO_opt_folder_same_w_peel_syn_spines_featues_cm_g_pas_first_seed_' + str(seed) + '/' + cell   +'/run_' + runnum)
    except: pass
    ###################################################################################
    # make morphology png fig and load morphology to opt
    ###################################################################################
    base_save_folder = base2 + 'MOO_opt_folder_same_w_peel_syn_spines_featues_cm_g_pas_first_seed_' + str(
        seed) + '/' + cell + "/"+'run_'+runnum+'/'

    # to insert syn here?
    from calculate_synaptic_loc import synaptic_loc
    syn_poses={}
    syn_poses['170830HuSHS2C1IN0toIN3'] = [np.array([198.04, 51.55, 11.31]),
                 np.array([87.81, -41.95, -13.15]),
                 np.array([-143.67, 210.14, 23.0])]
    syn_poses['05_08_A_01062017']=[(-5.56,-325.88, -451.42)]
    synapses_locations={}
    synapses_locations[cell] = synaptic_loc(cell, syn_poses[cell])
    morphology = ephys.morphologies.NrnFileMorphology(morphology_dirr, do_replace_axon=True,
                                                      extra_func=True, extra_func_run=add_morph, spine_poses=synapses_locations[cell],
                                                      do_resize_dend=do_resize_dend,resize_dend_by=resize_dend_by)  # change axon to AIS and add spine locations
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
    all_l = [somatic_loc, basal_loc, apical_loc, axonal_loc]

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
                                                      dist_thresh_apical=60,
                                                      dist_thresh_basal=60,
                                                      F_factor=F_factor)

    parameters_list.append(
        ephys.parameters.NrnSectionParameter(name="Ra", param_name="Ra", value=passive_val[cell]["RA"],
                                             bounds=[70, 300], locations=sec_list, frozen=RA_FROZEN)) #@# in the paper they said bound of 70-100 ohm*cm
    parameters_list.append(
        ephys.parameters.NrnSectionParameter(name="g_pas", param_name="g_pas", value=1.0 / passive_val[cell]["RM"],
                                             locations=sec_list, frozen=True, value_scaler=F_FACTOR_DISTANCE))
    parameters_list.append(
        ephys.parameters.NrnSectionParameter(name="cm", param_name="cm", bounds=[0.5, 3], value=CM_startValue,
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
    for i, syn in enumerate(synapses_locations[cell]):
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
        if cell == "170830HuSHS2C1IN0toIN3":
            number = 2
            interval = 10.5
        else:
            number = 1
            interval = 1
        number = 1
        interval = 1
        # for i in range(len(synapses_locations[cell])):
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
            name='weight_AMPA'+str(i),
            param_name='weight[0]',
            frozen=False,
            value=0.0015,
            bounds=[0.000000, 0.01],
            locations=[netstims[i]],
            reletive_strength = [1]))#[1, 0.1,0.01]))

    # this  need to add the weight to optimization
        syn_params.append(NrnNetstimWeightParameter(
            name='weight_NMDA'+str(i),
            param_name='weight[0]',
            frozen=False,
            value=0.0012,
            bounds=[0.000, 0.005],
            locations=[netstims_NMDA[i]],
            reletive_strength = [1]))#[1, 0.1,0.01]))

    #################################same weight to synapses###################################################
    # stim_start = spike_timeing + neuron_start_time
    #
    # # this only for the first synapse in that cell
    # if cell == "170830HuSHS2C1IN0toIN3":
    #     number = 2
    #     interval = 10.5
    # else:
    #     number = 1
    #     interval = 1
    # #@# I want to fit to my stimuluse
    # number = 1
    # interval = 1
    # # the neetstim is instantiate in the weight_AMPA function so the stimuli in the protocol is removed
    # netstims.append(ephys.stimuli.NrnNetStimStimulus(
    #     total_duration=T_base[-1] + neuron_start_time, #@#neuron_start_time is when NEURON start to run?
    #     number=number,
    #     interval=interval,
    #     start=stim_start,
    #     weight=5e-4,
    #     locations=tau_param_locs))
    #
    # netstims_NMDA.append(ephys.stimuli.NrnNetStimStimulus(
    #     total_duration=T_base[-1] + neuron_start_time,
    #     number=number,
    #     interval=interval,
    #     start=stim_start,
    #     weight=5e-4,
    #     locations=NMDA_param_locs))

    # netstims_change = []
    # netstims_NMDA_change = []
    # syn_params.append(NrnNetstimWeightParameter(
    #     name='weight_AMPA',
    #     param_name='weight[0]',
    #     value=0.0008,
    #     frozen=False,
    #     bounds=[0.00001, 0.0025],
    #     locations=netstims,
    #     reletive_strength = [1, 0.3, 0.5])) #@# what is realative_strength
    #
    # # this  need to add the weight to optimization
    # syn_params.append(NrnNetstimWeightParameter(
    #     name='weight_NMDA',
    #     param_name='weight[0]',
    #     value=0.0012,
    #     frozen=False,
    #     bounds=[0.0002, 0.003],
    #     locations=netstims_NMDA,
    #     # reletive_strength = [1, 0.3, 0.5] #@# what is this?
    # ))

    ################################################################################################

    rec.append(ephys.recordings.CompRecording(
        name='soma.v',
        location=somacenter_loc,
        variable='v'))

    syn_params.append(ephys.parameters.NrnPointProcessParameter(
        name='exp2syn_tau1',
        param_name='tau1',
        value=0.3,
        frozen=AMPA_RISE_FIX,
        bounds=[0.2, 0.4],
        locations=tau_param_locs))
    syn_params.append(ephys.parameters.NrnPointProcessParameter(
        name='exp2syn_tau2',
        param_name='tau2',
        value=1.8,  # min(AMPA_FIT[cell]['tau2'],8),
        frozen=AMPA_DECAY_FIX,
        bounds=[1, 3],
        locations=tau_param_locs))

    syn_params.append(ephys.parameters.NrnPointProcessParameter(
        name='NMDA_tau_r_NMDA',
        param_name='tau_r_NMDA',
        value=8,
        frozen=False,
        bounds=[4, 15],
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

    protocol = ephys.protocols.SweepProtocol('netstim_protocol', netstims + netstims_NMDA, rec, cvode_active=False)

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
    print(model_description)
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
    feature3 = EFeaturePeak(T_base, V_base)

    objective1 = ephys.objectives.SingletonObjective('netstim_protocol1', feature1)
    objective2 = ephys.objectives.SingletonObjective('netstim_protocol1', feature2)
    objective3 = ephys.objectives.SingletonObjective('netstim_protoco3', feature3)

    # objectives=[objective1,objective2 , objective3]
    objectives = [objective1]
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
        print(rc[:].apply_sync(lambda: "Hello, World"))
        for g in rc.ids:
            try:
                with rc[g].sync_imports():
                    import bluepyopt

                    from extraClasses import NrnSegmentSomaDistanceScaler_, NrnSectionParameterPas, neuron_start_time, \
                        EFeatureImpadance, EFeaturePeak, EFeaturePeakTime, EFeatureRDSM, NrnNetstimWeightParameter, \
                        SweepProtocolRin2
            except:
                print("closing engine number", g)
                rc.shutdown([g])
        print("that what's left: ", rc.ids)

        import logging
        logger = logging.getLogger()

        rc[:].push(dict(add_morph=add_morph, create_spine=create_spine,
                        NECK_LENGHT = NECK_LENGHT, HEAD_DIAM = HEAD_DIAM,
                        passive_val = passive_val, Rneck=Rneck, cell=cell))
        print('Using ipyparallel with %d engines', len(rc))

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
    data_bef.write(model.__str__())
    data_bef.close()
    stim_befor=True


    if stim_befor:
        start_values = {}
        for param in model.params:
            if model.params[param].frozen:
                continue
            start_values[param] = model.params[param].value
        responses = protocol.run(cell_model=model, param_values=start_values, sim=sim)

        temp = np.array(responses['soma.v']['time'])
        temp2 = np.array(responses['soma.v']['voltage'])
        start = np.where(temp > neuron_start_time)[0][0]
        temp = temp - temp[start]
        temp = temp[start:]
        temp2 = temp2[start:]
        plt.plot(temp, temp2, color='purple', alpha=0.6, linewidth=5)

        # plt.errorbar(T_base,V_base, yerr=V2, color = 'k', ecolor="b", alpha = 0.03)
        plt.plot(T_base, V_base, color='k')
        plt.savefig(base_save_folder + 'before_fit_transient_RDSM')
        plt.close()
    final_pop, hall_of_fame, logs, hist = optimisation.run(max_ngen=num_of_genarations)

    print(cell)
    print(hall_of_fame)

    print()

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
        "model": model.__str__()
    }, open(base_save_folder + "hall_of_fame.p", "wb"))

    pickle.dump({
        "parameters": parameters2,
        "final_pop": final_pop,
        "model": model.__str__()
    }, open(base_save_folder + "final_pop.p", "wb"))

    data = open(base_save_folder + 'data.txt', 'w')
    data.write('model description:\n'+model_description+'\n')
    data.write('Best individual values\n')

    for key, val in zip(parameters2, best):
        v=val
        if str(key).startswith('weight'): v *=1000
        data.write(key + '\t\t' + str(v) + '\n')
        if key == "g_pas": r = val
    # data.write('RM\t\t'+str(1.0/r)+'\n')

    data.write('hall of fame ' + str(len(hall_of_fame)) + '\n')
    m = np.array(hall_of_fame).mean(axis=0)
    s = np.array(hall_of_fame).std(axis=0)
    data.write('key		mean		std \n')
    for key, val, st in zip(parameters2, m, s):
        v = val
        st2=st
        if str(key).startswith('weight'):
            v *= 1000
            st2*=1000
        data.write(key + '\t' + str(round(v, 4)) + '\t' + str(round(st2, 4)) + '\n')

    data.write('\n')
    title = '		'
    for key in parameters2:
        title += key + '	'
    title += ' RM\n'
    data.write(title)
    for ind in hall_of_fame:
        ind2 = np.array(ind).round(3)
        line = ''
        for k in ind:
            if (round(k, 3) == 0):
                line += str(k) + '	'
            else:
                line += str(round(k, 3)) + '	'
        data.write(line + str(round(1.0 / ind[0], 3)) + '\n')
        data.write('Fitness values:' + str(ind.fitness) + '\n')

    data.write('\n\nFinal population: ' + str(len(final_pop)))
    m = np.array(final_pop).mean(axis=0)
    s = np.array(final_pop).std(axis=0)
    data.write('key		mean		std\n')
    for key, val, st in zip(parameters2, m, s):
        v = val
        st2=st
        if str(key).startswith('weight'):
            v *= 1000
            st2 *= 1000
        data.write(key + '\t' + str(round(v, 4)) + '\t' + str(round(st2, 4)) + '\n')
    # data.write('RM\t\t'+str(round(1.0/m[0],3))+'\t'+str(round(1.0/s[0],3))+'\n')

    data.close()

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
    responses = protocol.run(cell_model=model, param_values=best_ind_dict, sim=sim)

    temp = np.array(responses['soma.v']['time'])
    temp2 = np.array(responses['soma.v']['voltage'])
    start = np.where(temp > neuron_start_time)[0][0]
    temp = temp - temp[start]
    temp = temp[start:]
    temp2 = temp2[start:]
    plt.plot(temp, temp2, color='purple', alpha=0.6, linewidth=5)

    # plt.errorbar(T_base,V_base, yerr=V2, color = 'k', ecolor="b", alpha = 0.03)
    plt.plot(T_base, V_base, color='k')
    # plt.bar(T2,V2,color='b', alpha=0.2)

    plt.xlabel('time(ms)')
    plt.ylabel('V(mV)')
    plt.title('MOO RDSM fit to transient')
    plt.savefig(base_save_folder + 'fit_transient_RDSM')
    plt.savefig(base_save_folder + 'fit_transient_RDSM.pdf')
    plt.close()

    print("when done h.dt = ", sim.neuron.h.dt)


cell1 = "171101HuSHS2C2IN3toIN1"  # green
cell2 = "171101HuSHS2C2IN0toIN1"  # 30 indev, 300 generations, hard one #red ################################
cell3 = "180207HuSHS4C2IN1toIN0"  # dark orange
cell4 = "170830HuSHS2C1IN0toIN3"  # grey
cell5 = "171101HuSHS2C2IN0toIN3"  # "blue"                                   ################################
cell6 = "fake_cell"
cell7 =  "05_08_A_01062017"
cells = [cell1, cell2, cell3, cell4, cell5, cell6 ,cell7]

# seed = int(sys.argv[1])
# generation_size = int(sys.argv[2])
# num_of_genarations = int(sys.argv[3])
# cell_num = int(sys.argv[4])
# cell = cells[cell_num]
# profile = sys.argv[5]
# passive_val_name = sys.argv[6]
# spine_type = sys.argv[7]
# Rneck = sys.argv[8]

# generation_size = 100
# num_of_genarations = 5000
seed = 123456
cell=cells[6]
profile=""
passive_val_name = "Ra_100"
print(cell)
#  for run in cluster:
# qsub -pe pnrn 51 first_run_cm_g_pas3.sh 1000 100 10 0 50 Ra_250
# ssh yoni.leibner@bs-cluster.elsc.huji.ac.il
# sbatch -p ss.q -c51 first_run_cm_g_pas3.sh 1000 100 10 0 50 Ra_250 human_spine 365
# start_values = NMDA_fit_grad[cell]

CM_FROZEN = True
RA_FROZEN = True

N_NMDA_FROZEN = True
GAMMA_FROZEN = True

AMPA_RISE_FIX = False
AMPA_DECAY_FIX = False

if passive_val_name == "Ra_250":
    passive_val = {'170830HuSHS2C1IN0toIN3': {'CM': 0.73, 'RA': 250, 'RM': 14254.8},
                   '171101HuSHS2C2IN0toIN1': {'CM': 0.7202456742908355, 'RA': 250, 'RM': 44010.0},
                   '171101HuSHS2C2IN0toIN3': {'CM': 0.7619930711798609, 'RA': 250, 'RM': 27863.8},
                   '171101HuSHS2C2IN3toIN1': {'CM': 0.7202456742908355, 'RA': 250, 'RM': 44010.0},
                   '180207HuSHS4C2IN1toIN0': {'CM': 0.8545180040756637, 'RA': 250, 'RM': 25020.0},
                   "fake_cell": {'CM': 0.7, 'RA': 200.0, 'RM': 30000.0}}
elif passive_val_name == "Ra_100":
    passive_val = {'170830HuSHS2C1IN0toIN3': {'CM': 0.66, 'RA': 100, 'RM': 21902.6},
                   '171101HuSHS2C2IN0toIN1': {'CM': 0.6896806453365673, 'RA': 100, 'RM': 45960.42},
                   '171101HuSHS2C2IN0toIN3': {'CM': 0.6594225877073165, 'RA': 100, 'RM': 32197.9},
                   '171101HuSHS2C2IN3toIN1': {'CM': 0.6896806453365673, 'RA': 100, 'RM': 45960.42},
                   '180207HuSHS4C2IN1toIN0': {'CM': 0.7124305385529192, 'RA': 100, 'RM': 30010.0},
                   "fake_cell": {'CM': 0.7, 'RA': 200.0, 'RM': 30000.0},
                   '05_08_A_01062017':{'CM': 1, 'RA': 100, 'RM': 5684*2}}
else:
    raise BaseException("choose Ra from Ra_100 and Ra_250 in args")

# passive_val = values_delta_pulse # value from gradint desent on delta pulse without Rin fit
# passive_val = values_delta_pulse_Rin # value from gradint desent on delta pulse without Rin fit

spine_type="mouse_spine"
Rneck='100'
####################spine parameters######################
if spine_type == "human_spine":
    #human
    NECK_LENGHT=1.35 # np.sqrt(2.8 / (4 * np.pi))
    HEAD_DIAM=0.944
elif spine_type == "mouse_spine":
    #mouse
    NECK_LENGHT=0.73
    HEAD_DIAM=0.667
elif spine_type == "shaft_spine":
    #on_shaft
    NECK_LENGHT=0.001
    HEAD_DIAM=0.944
else:
    raise BaseException("choose spine from [human_spine, mouse_spine, shaft_spine]")


#################################33
CM_startValue = passive_val[cell]["CM"]
result_R_neck_m_ohm = ((NECK_LENGHT * 4.0 * float(Rneck))/(np.pi*0.25**2)) / 100.0 # 0.25 = neck_diam
in_parallel = profile != ""
base2 = "opt_Human_L23_synapse_" + passive_val_name + "_Rneck"+spine_type+"_"+Rneck+"_"+str(round(result_R_neck_m_ohm,2))+"/"  # folder name  _RA_free
F_factor = 1.9

print("profile ", profile)

run(cell, seed=seed)
print('the MOO running is completed')
