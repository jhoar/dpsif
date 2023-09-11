import Timeline
import HMS
import math
import datetime
from astropy.time import Time
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
import numpy

def successrate(ms):
    m_limit = 0
    for m in ms:
        if m <= 75.0:
            m_limit += 1
    return m_limit / len(ms)


def writeSeries(state, mode, t0, ts, xs, ys, zs, sxs, sys, szs, ms, cs, sizes, modes, pmodes, tracks):

    mjd = Time(t0)
    mjd.format = 'mjd'
    utc = t0.astimezone(datetime.timezone.utc)
    name = '_OUT_' + utc.strftime('%Y-%m-%dT%H-%M-%SZ') + "_" + state + "_" + mode + '.txt'

    with open(name, "w") as outfile:
        outfile.write('mjd,utc,x,y,z,m,prev_mode,mode,track\n')
        n_rows = len(ts)
        for i in range(n_rows):
            mjd = Time(ts[i])
            mjd.format = 'mjd'
            utc = ts[i].astimezone(datetime.timezone.utc)

            outfile.write(str(mjd) + ',' + utc.strftime('%Y-%m-%dT%H:%M:%SZ') + ',' + str(xs[i]) + ',' + str(ys[i]) + ',' + str(zs[i]) + ',' + str(ms[i]) + ',' + str(pmodes[i]) + ',' + str(modes[i]) + ',' + str(tracks[i]) + '\n')

def plotSeries(state, mode, t0, ts, xs, ys, zs, sxs, sys, szs, ms, cs, sizes, modes, pmodes, tracks):

    mjd = Time(t0)
    mjd.format = 'mjd'
    utc = t0.astimezone(datetime.timezone.utc)
    name =  '_OUT_' + utc.strftime('%Y-%m-%dT%H-%M-%SZ') + "_" + state + "_" + mode + '.png'

    params = {
         'axes.labelsize': 'x-small',
         'figure.titlesize': 'x-small', 
         'axes.titlesize':'x-small',
         'ytick.labelsize': 'x-small',
         'xtick.labelsize': 'x-small'
         }

    success = successrate(ms)

    pylab.rcParams.update(params)
    plt.clf()

    fig, axs = plt.subplots(1, 2)
    fig.suptitle(state + "->" + mode + " " + utc.strftime('%Y-%m-%dT%H:%M:%SZ') + ' ' + str(len(xs)) + ' samples')
    axs[0].scatter(xs, ys, c=cs, s=sizes)
    axs[0].set_title('RPE Mean = ' + str(numpy.mean(ms)) + '\nσ = ' + str(numpy.std(ms)) + '\nRPE <= 75mas = ' + str(success * 100) + '%')
    axs[0].set_aspect('equal')
    axs[0].add_artist( plt.Circle( (0.0, 0.0), 75.0 , fill = False ) )

    axs[1].scatter(sxs, sys, c=cs, s=sizes)
    axs[1].set_title('History of accumulated errors')
    axs[1].set_aspect('equal')


    if success >= 0.997:
        plt.savefig('OK/' + name, format='png', dpi=300)
    else:
        plt.savefig('NOK/' + name, format='png', dpi=300)

    plt.close()

def generateReportFullTimeline(master, timerange):

    prev_mode = ""
    t = 0
    x = 0
    y = 0
    z = 0
    sx = 0
    sy = 0
    sz = 0
    px = 0
    py = 0
    pz = 0

    ts = []
    xs = []
    ys = []
    zs = []
    sxs = []
    sys = []
    szs = []
    ms = []
    cs = []
    sizes = []
    modes = []
    pmodes = []
    tracks = []
    t0 = 0

    for timeStamp in master:
        row = master[timeStamp]
        Xrpe = row['APPT1088_DB_AOCS_AHK_C_AX_ER_A_SP'] * 206264806.71915
        Yrpe = row['APPT1089_DB_AOCS_AHK_C_AY_ER_A_SP'] * 206264806.71915
        Zrpe = row['APPT1090_DB_AOCS_AHK_C_AZ_ER_A_SP'] * 206264806.71915
        track = row['FGS_OPMODE_FAAT2010']
        mode = row['DB_AOCS_AHK_SUBSTATE_APPT0838']

        dt = datetime.datetime.fromtimestamp(timeStamp)

        if mode == "SCM_SO": 
            if prev_mode != "SCM_SO":
                print("Start @ ", str(dt))
                t = dt
                x = 0
                y = 0
                z = 0
                sx = 0
                sy = 0
                sz = 0
                m = 0
                t0 = dt
            else:
                t = dt
                x = Xrpe
                y = Yrpe
                z = Zrpe
                sx += px
                sy += py
                sz += pz
                m = math.sqrt(x * x + y * y)

            ts.append(t)
            xs.append(x)
            ys.append(y)
            zs.append(y)
            sxs.append(sx)
            sys.append(sy)
            szs.append(sy)
            ms.append(m)
            modes.append(mode)
            pmodes.append(prev_mode)
            tracks.append(track)

            size = 2 + (0.003 * abs(z))
            sizes.append(size)

            if track == 'ATM_TP':
                cs.append('tab:blue')
            elif track == 'ATM_AP_CM':
                cs.append('tab:orange')
            elif track == 'RTM_AP':
                cs.append('tab:green')
            elif track == 'RTM_TP':
                cs.append('tab:red')
            elif track == 'ATM_IC':
                cs.append('tab:purple')
            elif track == 'SBM':
                cs.append('tab:brown')
            elif track == 'RTM_IC':
                cs.append('tab:pink')
            elif track == 'ATM_AP_FM':
                cs.append( 'tab:cyan')
            else:
                cs.append('tab:olive')
                 
        px = x
        py = y
        pz = z

        state = ""
        exit = False        

        if mode == "SCM_MC" and prev_mode == "SCM_SO":
            state = "FAIL"
            exit = True

        if mode == "SCM_FA" and prev_mode == "SCM_SO":
            state = "FAIL"
            exit = True


        if (mode == "SCM_DF" or mode == "SCM_LS") and prev_mode == "SCM_SO":
            state = "OK"
            exit = True

        if exit:    
            print("End @ ", str(dt), mode)
            writeSeries(state, mode, t0, ts, xs, ys, zs, sxs, sys, szs, ms, cs, sizes, modes, pmodes, tracks)
            plotSeries(state, mode, t0, ts, xs, ys, zs, sxs, sys, szs, ms, cs, sizes, modes, pmodes, tracks)
            ts.clear()
            xs.clear()
            ys.clear()
            zs.clear()
            sxs.clear()
            sys.clear()
            szs.clear()
            cs.clear()
            ms.clear()
            sizes.clear()
            modes.clear()
            pmodes.clear()
            tracks.clear()
            

        prev_mode = mode




ares_ids = [
    (8308, 'FGS_OPMODE_FAAT2010', True), 
    (4158, 'DB_AOCS_AHK_SUBSTATE_APPT0838', True), 
    (15924, 'APPT1090_DB_AOCS_AHK_C_AZ_ER_A_SP', False), 
    (15923, 'APPT1089_DB_AOCS_AHK_C_AY_ER_A_SP', False), 
    (15922, 'APPT1088_DB_AOCS_AHK_C_AX_ER_A_SP', False),
] 

pv_001 = {
    'startyear': 2023,
    'endyear': 2023,
    'startdoy': 215,
    'enddoy': 224,
    'ossFile': 'pv\OSS_COMMISSIONING_20230803T040000-20230816T231915_005.xml'
}

pv = {
    'startyear': 2023,
    'endyear': 2023,
    'startdoy': 224,
    'enddoy': 240,
    'ossFile': 'pv\OSS_PV_20230812T000000-20230819T104213_006.xml'
}

pvrestart = {
    'startyear': 2023,
    'endyear': 2023,
    'startdoy': 243,
    'enddoy': 249,
    'ossFile': 'pv\OSS_PV_20230812T000000-20230819T104213_006.xml'
}


timerange = pvrestart

Timeline.generateHmsFiles(timerange, ares_ids)
master = Timeline.generateHmsTimeline(timerange, ares_ids)

generateReportFullTimeline(master, timerange)
