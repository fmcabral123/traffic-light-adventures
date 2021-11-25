# traffic-light-adventures
This repository contains all of the project files used for the development of an adaptive traffic light algorithm for T-junction intersections in partial fulfillment of a high school research course.

_(Last updated on November 25, 2021)_

## Algorithm logic

```
for every 37 seconds:
    if phase == 0:
        if phase 3 score > phase 0 score:
            go to phase 3
        else:
            stay in phase 0
            calculate duration
            
    elif phase == 3:
        if phase 0 score > phase 3 score:
            go to phase 0
        else:    
            stay in phase 3
            calculate duration
```

## Score function

A weighted average was used. A score S for a given traffic phase is obtained by averaging the scores s of the lanes comprising the phase. The equation for this score s is: s = Aw + Bq + Ch, where w is the waiting time per vehicle (s/vehicle), q is the queue length per lane (vehicle/lane), and h is the hunger level (i.e. how many phases have passed since the given lane last received a green light). The constants were set to be A = 2, B = 2, and C = 1. More weight was given to waiting time and queue length.

## Green light duration

The green light duration t for a phase is determined by the equation t = l/v, where l is the average length of the vehicle queues (in m), and likewise, v is the average velocity (in m/s) of the vehicles in the lane. Note that there will inevitably be occasions where v goes to or tends to 0. A correctional term of 0.01 was thus added in the denominator, and durations that tend to infinity were avoided by the algorithm logic defined above. 

## Simulation

Here is a picture of the simulation running with the adaptive algorithm (though it is admittedly hard to tell what algorithm is being used by just one still image)! Pretty cool. The simulation was designed to run up to a time T = 3600 s.

![image](https://user-images.githubusercontent.com/75599698/143374379-6b4b1fed-1b98-47b2-ade7-2b9722e0d77a.png)

## Results

**Adaptive algorithm:**
![image](https://user-images.githubusercontent.com/75599698/143375687-bce3d8c8-e691-417c-af63-48942600a484.png)
![image](https://user-images.githubusercontent.com/75599698/143376568-7ee7fa6d-91f4-4fc2-9271-7d95303a1bd1.png)
![image](https://user-images.githubusercontent.com/75599698/143376594-1803c356-e303-4ade-84ed-76523f70aea0.png)
![image](https://user-images.githubusercontent.com/75599698/143376602-9875aaf1-426f-409c-b55f-4c9f16dc8d25.png)

**Fixed-time algorithm:**
![image](https://user-images.githubusercontent.com/75599698/143375087-89a3e810-b1bb-4fb0-a8e2-4bd407ca98f7.png)
![image](https://user-images.githubusercontent.com/75599698/143376671-5536ef9b-029a-4d9a-96b8-87a466e38688.png)
![image](https://user-images.githubusercontent.com/75599698/143376681-36342697-7d6c-4941-af20-ae3b46e46b51.png)
![image](https://user-images.githubusercontent.com/75599698/143376685-9583ce0d-943e-4f02-8567-6a64ca272a48.png)
