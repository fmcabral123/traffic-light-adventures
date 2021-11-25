from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options

# everything above this is just for the purposes of setting up and for the sake of not breaking everything

import csv
import pandas as pd

def algorithm():
    step = 0
    min = 47
    T = 3600
    hungerlevel = [0, 0]
    traci.trafficlight.setPhase("gneJ27", 0)

    row = ["time", "waiting time", "queue length", "departure rate", "phase"]
    rows = []
    waitingtime, queuelength, exited = 0, 0, 0

    while step <= T: 
        traci.simulationStep()
        if step % min == 0: 
            scores = algo(hungerlevel)
            if traci.trafficlight.getPhase("gneJ27") == 0: 
                if scores[1] > scores[0]:
                    traci.trafficlight.setPhase("gneJ27", 1)
                    hungerlevel[0] += 5
                    hungerlevel[1] = 0
                else:
                    traci.trafficlight.setPhase("gneJ27", 0)
                    duration = int((traci.lane.getLastStepVehicleNumber("gneE20_1")*traci.lane.getLastStepLength("gneE20_1")+traci.lane.getLastStepVehicleNumber("gneE20_2")*traci.lane.getLastStepLength("gneE20_2")+traci.lane.getLastStepVehicleNumber("gneE19_1")*traci.lane.getLastStepLength("gneE19_1")+traci.lane.getLastStepVehicleNumber("gneE19_2")*traci.lane.getLastStepLength("gneE19_2"))/(traci.lane.getLastStepMeanSpeed("gneE20_1") + traci.lane.getLastStepMeanSpeed("gneE20_2") + traci.lane.getLastStepMeanSpeed("gneE19_1") + traci.lane.getLastStepMeanSpeed("gneE19_2") + 0.01))
                    print(step, duration)
                    traci.trafficlight.setPhaseDuration("gneJ27", duration)
            elif traci.trafficlight.getPhase("gneJ27") == 3:
                if scores[0] > scores[1]:
                    traci.trafficlight.setPhase("gneJ27", 4)
                    hungerlevel[0] = 0
                    hungerlevel[1] += 5
                else:
                    traci.trafficlight.setPhase("gneJ27", 3)
                    duration = int((traci.lane.getLastStepVehicleNumber("gneE21_1")*traci.lane.getLastStepLength("gneE21_1")+traci.lane.getLastStepVehicleNumber("gneE21_2")*traci.lane.getLastStepLength("gneE21_2"))/(traci.lane.getLastStepMeanSpeed("gneE21_1") + traci.lane.getLastStepMeanSpeed("gneE21_2") + 0.01))
                    print(step, duration)
                    traci.trafficlight.setPhaseDuration("gneJ27", duration)
        waiting = traci.lane.getWaitingTime("gneE20_1") + traci.lane.getWaitingTime("gneE20_2") + traci.lane.getWaitingTime("gneE19_1") + traci.lane.getWaitingTime("gneE19_2") + traci.lane.getWaitingTime("gneE21_1") + traci.lane.getWaitingTime("gneE21_2")
        volume = traci.lane.getLastStepVehicleNumber("gneE20_1") + traci.lane.getLastStepVehicleNumber("gneE20_2") + traci.lane.getLastStepVehicleNumber("gneE19_1") + traci.lane.getLastStepVehicleNumber("gneE19_2") + traci.lane.getLastStepVehicleNumber("gneE21_1") + traci.lane.getLastStepVehicleNumber("gneE21_2")    
        exit = traci.simulation.getArrivedNumber()
        data = [step, waiting / volume, volume / 6, exit, traci.trafficlight.getPhase("gneJ27")]
        waitingtime += data[1]
        queuelength += data[2]
        exited += data[3]
        rows.append(data)
        step += 1
    
    # "gneE20_1" + "gneE20_2" + "gneE19_1" + "gneE19_2": phase 0
    # "gneE21_1" + "gneE21_2": phase 3

    f1 = "results/dataalgo.csv" # for instantaneous values
    f2 = "results/dataalgoave.csv" # for average values
  
    # writing to csv file
    with open(f1, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        csvwriter.writerow(row)
        
        csvwriter.writerows(rows)

    df1 = pd.read_csv('results/dataalgo.csv')
    df1.to_csv('results/dataalgo.csv', index=False)
    
    with open(f2, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        csvwriter.writerow(["average waiting time", "average queue length", "average departure rate"])
        csvwriter.writerow([waitingtime / T, queuelength / T, exited / T])

    df2 = pd.read_csv('results/dataalgoave.csv')
    df2.to_csv('results/dataalgoave.csv', index=False)

    traci.close()
    sys.stdout.flush()

'''
def run2(): # THIS IS THE REVISED ALGORITHM, WORK HERE! also don't forget to do run2() at the bottom
    step = 0
    min = 0
    T = 3600
    phase = -1
    ticker = 0
    hungerlevel = [0, 0]
    traci.trafficlight.setPhase("gneJ27", 0)

    row = ["time", "waiting time", "queue length", "departure rate", "phase"]
    rows = []
    waitingtime, queuelength, exited = 0, 0, 0

    while step <= T: 
        traci.simulationStep()
        if traci.trafficlight.getPhase("gneJ27") == 0:
            if traci.trafficlight.getPhase("gneJ27") != phase:
                min = int((traci.lane.getLastStepVehicleNumber("gneE20_1")*traci.lane.getLastStepLength("gneE20_1")+traci.lane.getLastStepVehicleNumber("gneE20_2")*traci.lane.getLastStepLength("gneE20_2")+traci.lane.getLastStepVehicleNumber("gneE19_1")*traci.lane.getLastStepLength("gneE19_1")+traci.lane.getLastStepVehicleNumber("gneE19_2")*traci.lane.getLastStepLength("gneE19_2"))/(traci.lane.getLastStepMeanSpeed("gneE20_1") + traci.lane.getLastStepMeanSpeed("gneE20_2") + traci.lane.getLastStepMeanSpeed("gneE19_1") + traci.lane.getLastStepMeanSpeed("gneE19_2") + 0.01))
                if min > 50:
                    min = 50
                traci.trafficlight.setPhase("gneJ27", 0)
                ticker += 1
            else:
                if ticker < min:
                    traci.trafficlight.setPhase("gneJ27", 0)
                    ticker += 1
                else:
                    scores = algo(hungerlevel)
                    ticker = 0
                    if scores[1] > scores[0]:
                        traci.trafficlight.setPhase("gneJ27", 1)
                        hungerlevel[0] += 5
                        hungerlevel[1] = 0
                    else:
                        min = int((traci.lane.getLastStepVehicleNumber("gneE20_1")*traci.lane.getLastStepLength("gneE20_1")+traci.lane.getLastStepVehicleNumber("gneE20_2")*traci.lane.getLastStepLength("gneE20_2")+traci.lane.getLastStepVehicleNumber("gneE19_1")*traci.lane.getLastStepLength("gneE19_1")+traci.lane.getLastStepVehicleNumber("gneE19_2")*traci.lane.getLastStepLength("gneE19_2"))/(traci.lane.getLastStepMeanSpeed("gneE20_1") + traci.lane.getLastStepMeanSpeed("gneE20_2") + traci.lane.getLastStepMeanSpeed("gneE19_1") + traci.lane.getLastStepMeanSpeed("gneE19_2") + 0.01))
                        if min > 50:
                            min = 50
                        traci.trafficlight.setPhase("gneJ27", 0)
                        ticker += 1

        elif traci.trafficlight.getPhase("gneJ27") == 3:
            if traci.trafficlight.getPhase("gneJ27") != phase:
                min = int((traci.lane.getLastStepVehicleNumber("gneE21_1")*traci.lane.getLastStepLength("gneE21_1")+traci.lane.getLastStepVehicleNumber("gneE21_2")*traci.lane.getLastStepLength("gneE21_2"))/(traci.lane.getLastStepMeanSpeed("gneE21_1") + traci.lane.getLastStepMeanSpeed("gneE21_2") + 0.01))
                if min > 50:
                    min = 50
                traci.trafficlight.setPhase("gneJ27", 3)
                ticker += 1
            else:
                if ticker < min:
                    traci.trafficlight.setPhase("gneJ27", 3)
                    ticker += 1
                else:
                    scores = algo(hungerlevel)
                    ticker = 0
                    if scores[0] > scores[1]:
                        traci.trafficlight.setPhase("gneJ27", 4)
                        hungerlevel[0] = 0
                        hungerlevel[1] += 5
                    else:
                        min = int((traci.lane.getLastStepVehicleNumber("gneE21_1")*traci.lane.getLastStepLength("gneE21_1")+traci.lane.getLastStepVehicleNumber("gneE21_2")*traci.lane.getLastStepLength("gneE21_2"))/(traci.lane.getLastStepMeanSpeed("gneE21_1") + traci.lane.getLastStepMeanSpeed("gneE21_2")  + 0.01))
                        if min > 50:
                            min = 50
                        traci.trafficlight.setPhase("gneJ27", 3)
                        ticker += 1

        phase = traci.trafficlight.getPhase("gneJ27")
        waiting = traci.lane.getWaitingTime("gneE20_1") + traci.lane.getWaitingTime("gneE20_2") + traci.lane.getWaitingTime("gneE19_1") + traci.lane.getWaitingTime("gneE19_2") + traci.lane.getWaitingTime("gneE21_1") + traci.lane.getWaitingTime("gneE21_2")
        volume = traci.lane.getLastStepVehicleNumber("gneE20_1") + traci.lane.getLastStepVehicleNumber("gneE20_2") + traci.lane.getLastStepVehicleNumber("gneE19_1") + traci.lane.getLastStepVehicleNumber("gneE19_2") + traci.lane.getLastStepVehicleNumber("gneE21_1") + traci.lane.getLastStepVehicleNumber("gneE21_2")    
        exit = traci.simulation.getArrivedNumber()
        data = [step, waiting / volume, volume / 6, exit, traci.trafficlight.getPhase("gneJ27")]
        waitingtime += data[1]
        queuelength += data[2]
        exited += data[3]
        rows.append(data)
        step += 1
    
    # "gneE20_1" + "gneE20_2" + "gneE19_1" + "gneE19_2": phase 0
    # "gneE21_1" + "gneE21_2": phase 3

    f1 = "results/dataalgo.csv" # for instantaneous values
    f2 = "results/dataalgoave.csv" # for average values
  
    # writing to csv file
    with open(f1, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        csvwriter.writerow(row)
        
        csvwriter.writerows(rows)

    df1 = pd.read_csv('results/dataalgo.csv')
    df1.to_csv('results/dataalgo.csv', index=False)
    
    with open(f2, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        csvwriter.writerow(["average waiting time", "average queue length", "average departure rate"])
        csvwriter.writerow([waitingtime / T, queuelength / T, exited / T])

    df2 = pd.read_csv('results/dataalgoave.csv')
    df2.to_csv('results/dataalgoave.csv', index=False)

    traci.close()
    sys.stdout.flush()
'''

def fixed(): # call for fixed-time. here, we only run this for the purposes of data collection (lmao). same datacollection process as before.
    step = 0
    T = 3600
    traci.trafficlight.setPhase("gneJ27", 0) # phase indexes run from 0 to n - 1 if we have n phases, like a list

    row = ["time", "waiting time", "queue length", "departure rate", "phase"]
    rows = []
    waitingtime, queuelength, exited = 0, 0, 0

    while step <= T: 
        traci.simulationStep()
        waiting = traci.lane.getWaitingTime("gneE20_1") + traci.lane.getWaitingTime("gneE20_2") + traci.lane.getWaitingTime("gneE19_1") + traci.lane.getWaitingTime("gneE19_2") + traci.lane.getWaitingTime("gneE21_1") + traci.lane.getWaitingTime("gneE21_2")
        volume = traci.lane.getLastStepVehicleNumber("gneE20_1") + traci.lane.getLastStepVehicleNumber("gneE20_2") + traci.lane.getLastStepVehicleNumber("gneE19_1") + traci.lane.getLastStepVehicleNumber("gneE19_2") + traci.lane.getLastStepVehicleNumber("gneE21_1") + traci.lane.getLastStepVehicleNumber("gneE21_2")    
        exit = traci.simulation.getArrivedNumber()
        data = [step, waiting / volume, volume / 6, exit, traci.trafficlight.getPhase("gneJ27")]
        waitingtime += data[1]
        queuelength += data[2]
        exited += data[3]
        rows.append(data)
        step += 1

    f1 = "results/datafixed.csv" # for instantaneous values
    f2 = "results/datafixedave.csv" # for average values
  
    # writing to csv file
    with open(f1, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        csvwriter.writerow(row)
        
        csvwriter.writerows(rows)

    df1 = pd.read_csv('results/datafixed.csv')
    df1.to_csv('results/datafixed.csv', index=False)
    
    with open(f2, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        csvwriter.writerow(["average waiting time", "average queue length", "average departure rate"])
        csvwriter.writerow([waitingtime / T, queuelength / T, exited / T])

    df2 = pd.read_csv('results/datafixedave.csv')
    df2.to_csv('results/datafixedave.csv', index=False)

    traci.close()
    sys.stdout.flush()    

def algo(hungerlevel):
    A = 1
    B = 1
    C = 1
    scores = [] 

    volume = traci.lane.getLastStepVehicleNumber("gneE20_1") + traci.lane.getLastStepVehicleNumber("gneE20_2") + traci.lane.getLastStepVehicleNumber("gneE19_1") + traci.lane.getLastStepVehicleNumber("gneE19_2")
    waitingtime = traci.lane.getWaitingTime("gneE20_1") + traci.lane.getWaitingTime("gneE20_2") + traci.lane.getWaitingTime("gneE19_1") + traci.lane.getWaitingTime("gneE19_2")
    scores.append(((A * volume / 4) + (B * waitingtime / volume) + (C * 4 * hungerlevel[0])) / 4)

    volume = traci.lane.getLastStepVehicleNumber("gneE21_1") + traci.lane.getLastStepVehicleNumber("gneE21_2")
    waitingtime = traci.lane.getWaitingTime("gneE21_1") + traci.lane.getWaitingTime("gneE21_2")
    scores.append(((A * volume / 2) + (B * waitingtime / volume) + (C * 2 * hungerlevel[1])) / 2)

    return scores

# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    # generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/T.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    algorithm()
