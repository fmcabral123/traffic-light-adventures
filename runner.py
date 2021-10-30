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

import csv

def run():
    step = 0
    min = 37
    T = 3600
    hungerlevel = [0, 0]
    traci.trafficlight.setPhase("gneJ27", 0)

    row = ["Time", "Phase 1 [0] Score", "Phase 4 [1] Score", "Waiting Time", "Queue Lengths", "Number of Vehicles Exited the Intersection"]
    rows = []
    vehicles = 0
    waitingtime = 0
    queuelength = 0

    while step <= T:
        traci.simulationStep()
        if step % min == 0:
            scores = algo(hungerlevel)
            if traci.trafficlight.getPhase("gneJ27") == 0:
                if scores[1] > scores[0]:
                    traci.trafficlight.setPhase("gneJ27", 1)
            elif traci.trafficlight.getPhase("gneJ27") == 3:
                if scores[0] > scores[1]:
                    traci.trafficlight.setPhase("gneJ27", 4)
            elif traci.trafficlight.getPhase("gneJ27") == 2:
                if scores[1] > scores[0]:
                    traci.trafficlight.setPhase("gneJ27", 3)
                    hungerlevel[0] += 1
                    hungerlevel[1] = 0
            elif traci.trafficlight.getPhase("gneJ27") == 5:
                if scores[0] > scores[1]:
                    traci.trafficlight.setPhase("gneJ27", 1)
                    hungerlevel[0] = 0
                    hungerlevel[1] += 1
            elif traci.trafficlight.getPhase("gneJ27") == 1:
                if scores[1] > scores[0]:
                    traci.trafficlight.setPhase("gneJ27", 2)
            elif traci.trafficlight.getPhase("gneJ27") == 4:
                if scores[0] > scores[1]:
                    traci.trafficlight.setPhase("gneJ27", 5)
        vehicles += traci.simulation.getArrivedNumber()
        data = [step, algo(hungerlevel)[0], algo(hungerlevel)[1], traci.lane.getWaitingTime("gneE20_1") + traci.lane.getWaitingTime("gneE20_2") + traci.lane.getWaitingTime("gneE19_1") + traci.lane.getWaitingTime("gneE19_2") + traci.lane.getWaitingTime("gneE21_1") + traci.lane.getWaitingTime("gneE21_2"), traci.lane.getLastStepVehicleNumber("gneE20_1") + traci.lane.getLastStepVehicleNumber("gneE20_2") + traci.lane.getLastStepVehicleNumber("gneE19_1") + traci.lane.getLastStepVehicleNumber("gneE19_2") + traci.lane.getLastStepVehicleNumber("gneE21_1") + traci.lane.getLastStepVehicleNumber("gneE21_2"), vehicles]
        waitingtime += data[3]
        queuelength += data[4]
        rows.append(data)
        step += 1

    f1 = "results/dataalgo.csv"
    f2 = "results/dataalgocomp.csv"
  
    # writing to csv file
    with open(f1, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        
        # writing the fields
        csvwriter.writerow(row)
        
        # writing the data rows
        csvwriter.writerows(rows)
    
    with open(f2, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        
        # writing the fields
        csvwriter.writerow(["Average Waiting Time: ", waitingtime / T])
        csvwriter.writerow(["Average Queue Length: ", queuelength / T])
        csvwriter.writerow(["Average Number of Vehicles Exited per Unit Time: ", vehicles / T])
    
    traci.close()
    sys.stdout.flush()

def runfixed():
    step = 0
    min = 37
    T = 3600
    hungerlevel = [0, 0]
    traci.trafficlight.setPhase("gneJ27", 0)

    row = ["Time", "Phase 1 [0] Score", "Phase 4 [1] Score", "Waiting Time", "Queue Lengths", "Number of Vehicles Exited the Intersection"]
    rows = []
    vehicles = 0
    waitingtime = 0
    queuelength = 0

    while step <= T:
        traci.simulationStep()
        vehicles += traci.simulation.getArrivedNumber()
        data = [step, algo(hungerlevel)[0], algo(hungerlevel)[1], traci.lane.getWaitingTime("gneE20_1") + traci.lane.getWaitingTime("gneE20_2") + traci.lane.getWaitingTime("gneE19_1") + traci.lane.getWaitingTime("gneE19_2") + traci.lane.getWaitingTime("gneE21_1") + traci.lane.getWaitingTime("gneE21_2"), traci.lane.getLastStepVehicleNumber("gneE20_1") + traci.lane.getLastStepVehicleNumber("gneE20_2") + traci.lane.getLastStepVehicleNumber("gneE19_1") + traci.lane.getLastStepVehicleNumber("gneE19_2") + traci.lane.getLastStepVehicleNumber("gneE21_1") + traci.lane.getLastStepVehicleNumber("gneE21_2"), vehicles]
        waitingtime += data[3]
        queuelength += data[4]
        rows.append(data)
        step += 1

    f1 = "results/datafixed.csv"
    f2 = "results/datafixedcomp.csv"
  
    # writing to csv file
    with open(f1, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        
        # writing the fields
        csvwriter.writerow(row)
        
        # writing the data rows
        csvwriter.writerows(rows)
    
    with open(f2, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        
        # writing the fields
        csvwriter.writerow(["Average Waiting Time: ", waitingtime / T])
        csvwriter.writerow(["Average Queue Length: ", queuelength / T])
        csvwriter.writerow(["Average Number of Vehicles Exited per Unit Time: ", vehicles / T])
    
    traci.close()
    sys.stdout.flush()

def algo(hungerlevel):
    A = 2
    B = 2
    C = 1
    scores = [] 

    volume = traci.lane.getLastStepVehicleNumber("gneE20_1") + traci.lane.getLastStepVehicleNumber("gneE20_2") + traci.lane.getLastStepVehicleNumber("gneE19_1") + traci.lane.getLastStepVehicleNumber("gneE19_2")
    waitingtime = traci.lane.getWaitingTime("gneE20_1") + traci.lane.getWaitingTime("gneE20_2") + traci.lane.getWaitingTime("gneE19_1") + traci.lane.getWaitingTime("gneE19_2")
    scores.append((A * volume + B * waitingtime + C * 4 * hungerlevel[0]) / 4)

    volume = traci.lane.getLastStepVehicleNumber("gneE21_1") + traci.lane.getLastStepVehicleNumber("gneE21_2")
    waitingtime = traci.lane.getWaitingTime("gneE21_1") + traci.lane.getWaitingTime("gneE21_2")
    scores.append((A * volume + B * waitingtime + C * 2 * hungerlevel[1]) / 2)

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
    run()
