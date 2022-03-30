state = 0
x = 0
A = 2
B = 2
C = 1

while x != 1:
    scores = []

    volume = int(input("Volume of phase 0: "))
    waiting_time = int(input("Waiting time of phase 0: "))
    hunger_level = int(input("Hunger level of phase 0: "))
    scores.append(((A * volume) + (B * waiting_time / volume) + (C * hunger_level)) / 4)

    volume = int(input("Volume of phase 3: "))
    waiting_time = int(input("Waiting time of phase 3: "))
    hunger_level = int(input("Hunger level of phase 3: "))
    scores.append(((A * volume) + (B * waiting_time / volume) + (C * hunger_level)) / 2)

    if state == 0:
        if scores[0] > scores[1]:
            state = 0
            print("State: " + str(state))
            time = int(input("Additional time for phase 0: "))
            if time > 37:
                time = 37                
            print("Staying in phase " + str(state) + " for " + str(time) + " seconds")
        else:
            state = 1
            print("State: " + str(state))
            print("Staying in phase " + str(state) + " for 5 seconds")

            state = 2 
            print("State: " + str(state))
            print("Staying in phase " + str(state) + " for 3 seconds")

            state = 3
            print("State: " + str(state))

    elif state == 3:
        if scores[1] > scores[0]:
            state = 3
            print("State: " + str(state))
            time = int(input("Additional time for phase 3: "))
            if time > 37:
                time = 37                
            print("Staying in phase " + str(state) + " for " + str(time) + " seconds")
        else:
            state = 4
            print("State: " + str(state))
            print("Staying in phase " + str(state) + " for 5 seconds")

            state = 5
            print("State: " + str(state))
            print("Staying in phase " + str(state) + " for 3 seconds")
            
            state = 0
            print("State: " + str(state))
