# This program displays the shear stress and bending moment diagrams of a beam supported in specific ways under specific loading conditions. Project is modified from - https://courses.degreetutors.com/building-a-shear-force-bending-moment-diagram-calculator

import sys # Program uses sys library to teach the user on what to type in the command-line
import turtle # Import built-in graphics module


def main():
    # Check if user typed in the correct input
    if len(sys.argv) == 1:
        pass
    else:
        sys.exit("usage: beam.py")

    # Ask input from user
    user_input = get_input()


# Function to get input from the user
def get_input():
    # Welcome message
    print("Welcome to beam.py! To get started please choose how you would like to input the data! :)") # Message to welcome the user and guide them on what to type next
    
    # Check if user type in the correct input, re-prompt user if wrong input is given
    while True:
        try:
            input_mode = int(input('Type "1" to input data manually\nType "2" to import existing data file\nType "3" to exit\nPlease choose a number: ')) # Asking user on the method for data input
            if input_mode == 1: # Ask user to input data
                get_beam_configuration(mode=1) # Call beam configuration and pass in number for data validation. 1 for interactive, 2 for file input
                ask_file_output() # Ask user if they want to save the file
                parse() # Call parse() function to parse the data given by the user
                sys.exit("Program ended") 

            elif input_mode == 2: # Import file
                get_beam_configuration(mode=2) # Call beam configuration and pass in number for data validation. 1 for interactive, 2 for file input
                parse() # Call parse() function to parse the data given by the user
                sys.exit("Program ended") 

            else: # Exit program if user input 3
                 exit_program()

        except ValueError:
            print("Please enter only 1, 2 or 3!") # Print out error message if user do dont give an int that is 1-3
            pass


# Function to save file output
def ask_file_output():
    while True: # Infinite loop if wrong value is given
        try:
            print("Would you like to save your input?")
            save_file = int(input('Type "1" for "Yes", Type "2" for "No": '))

            if save_file == 1: # Ask user for file name if 1
                file_name = input("Please name the file in .txt format. E.g. Testing.txt: ")

                with open(file_name, "w") as f:
                    f.write("{} {}\n{} {}\n{} {}\n{} {}\n{} {}\n{} {}\n{} {}\n{} {}\n{} {}\n".format("beam_type", beam_type, "wall_position", wall_position, "span", span, "A", A, "B", B, "point_loads", point_loads, "point_moments", point_moments, "distributed_loads", distributed_loads, "linear_loads", linear_loads))

                break
            else: # Break out of program is user does not want to save file
                break
        except ValueError:
            print("Please only enter an integer!")
    

# Function to process beam configuration
def get_beam_configuration(mode):
    global span, A, B, beam_type, wall_position
    beam_type = ""
    wall_position = None
    span = 0 # Span of the beam
    A = 0 # Distance to left support 
    B = 0 # Distance to left support

    # Initialisations
    global point_loads, point_moments, distributed_loads, linear_loads # Initalize containers (Override below)
    point_loads = [[]] # Point forces (Location, X magnitude, Y magnitude)
    point_moments = [[]] # point moments (location, magnitude)
    distributed_loads = [[]] # Distributed loads (xStart, xEnd, Mag)
    linear_loads = [[]] # Distributed loads with linearly varying intensity (xStart, xEnd, startMag, endMag)

    if mode == 1: # If user chooses to input data manually
        # Ask the user for inputs
        beam_type = validate_beam_type()
        span = validate_beam_length()
        
        # Validate beam type
        if beam_type == "Simply_supported" or beam_type == "Overhanging": # Ask for position of A and B support if beam is simply supported or overhanging
            A = validate_support_position("A")
            B = validate_support_position("B")
        else: # Ask for wall position for cantilever beam
            wall_position = validate_cantilever_support()

        # Exit program if error in A and B
        if A > span or B > span:
            sys.exit("Support cannot be longer than span! Please run the program again with the correct support!")

        # Ask for load position
        validate_load_position()

    else: # If user chooses to import data
        d = {
            "beam_type": None,
            "wall_position": None,
            "span": None,
            "A": None,
            "B": None,
            "point_loads": None,
            "point_moments": None,
            "distributed_loads": None,
            "linear_loads": None
        }

        while True: # Code read and append data into file_data list
            try:
                file_name = input('To open file, type in filename.extension. E.g. "datafile.txt": ') # Get user input

                with open("{}".format(file_name), encoding='utf-8') as f: # Open file and read data

                    choice = 0
                    if file_name == "datafile.txt": # Special validation for datafile.txt
                        
                        choice = int(input('Type "1" for Simply Supported, Type "2" for Overhanging, Type "3" for Cantilever: '))
                       
                        line_ls = [] # 1 - 9 Simply supported, 10 - 18 Overhanging, 19 - 27 Cantilever
                        for line in f:
                            line_ls.append(line.replace("\n", ""))

                        if choice == 1: # Go to simply supported line

                            for i in range(0, 5):
                                line = line_ls[i]
                                key, value = line.split(" ")
                                d[key] = value

                            for i in range(5, 9): # Special way to parse point load, poin moment, distributed loads, and linear loads
                                line = line_ls[i]
                                line = line.replace(",", "")
                                line = line.replace("]", "")
                                line = line.replace("[", "")
                                line = line.replace("[[", "")
                                line = line.replace("]]", "")
                                line = line.split(" ")

                                appending_list = [] # Used for adding total point loads
                                if line[0] == "point_loads": # Count up till 3
                                    if len(line) > 2: # List will look like this ['point_loads', '6,', '0,', '-90']

                                        count = 0 # Use to reset list if it contains 3 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 3: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if line[0] == "point_loads":
                                            if len(point_loads[0]) == 0:
                                                point_loads = appending_list
                                            else:
                                                point_loads = point_loads.append(appending_list)
                                        appending_list = [] # Reset appending_list
                                
                                elif line[0] == "linear_loads": # Count up till 2
                                    if len(line) > 2: # List will look like this ['point_loads', '6,', '0,', '-90']

                                        count = 0 # Use to reset list if it contains 3 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 4: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if line[0] == "linear_loads":
                                            if len(linear_loads[0]) == 0:
                                                linear_loads = appending_list
                                            else:
                                                linear_loads = linear_loads.append(appending_list)
                                        appending_list = [] # Reset appending_list          
                                
                                elif line[0] == "point_moments": # Count up till 2
                                    key = line[0]
                                    if len(line) > 2: # List will look like this ['point_moments', '6,', '0']

                                        count = 0 # Use to reset list if it contains 2 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 2: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if len(point_moments[0]) == 0:
                                            point_moments = appending_list
                                        else:
                                            point_moments = point_moments.append(appending_list)
                                    appending_list = [] # Reset appending_list

                                elif line[0] == "distributed_loads": # Count up till 4
                                    key = line[0]
                                    if len(line) > 2: # List will look like this ['distributed_loads', '6,', '0', '7']

                                        count = 0 # Use to reset list if it contains 4 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 3: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if len(distributed_loads[0]) == 0:
                                            distributed_loads = appending_list
                                        else:
                                            distributed_loads = distributed_loads.append(appending_list)
                                    appending_list = [] # Reset appending_list
                
                                else: # If len is not more than 2 just add the load as [[]]
                                    line[0] = [[]]
                            
                        if choice == 2: # Go to Overhanging

                            for i in range(10, 14):
                                line = line_ls[i]
                                key, value = line.split(" ")
                                d[key] = value

                            for i in range(14, 18): # Special way to parse point load, poin moment, distributed loads, and linear loads
                                line = line_ls[i]
                                line = line.replace(",", "")
                                line = line.replace("]", "")
                                line = line.replace("[", "")
                                line = line.replace("[[", "")
                                line = line.replace("]]", "")
                                line = line.split(" ")

                                appending_list = [] # Used for adding total point loads
                                if line[0] == "point_loads": # Count up till 3
                                    if len(line) > 2: # List will look like this ['point_loads', '6,', '0,', '-90']

                                        count = 0 # Use to reset list if it contains 3 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 3: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if line[0] == "point_loads":
                                            if len(point_loads[0]) == 0:
                                                point_loads = appending_list
                                            else:
                                                point_loads = point_loads.append(appending_list)
                                        appending_list = [] # Reset appending_list
                                
                                elif line[0] == "linear_loads": # Count up till 2
                                    if len(line) > 2: # List will look like this ['point_loads', '6,', '0,', '-90']

                                        count = 0 # Use to reset list if it contains 3 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 4: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if line[0] == "linear_loads":
                                            if len(linear_loads[0]) == 0:
                                                linear_loads = appending_list
                                            else:
                                                linear_loads = linear_loads.append(appending_list)
                                        appending_list = [] # Reset appending_list          
                                
                                elif line[0] == "point_moments": # Count up till 2
                                    key = line[0]
                                    if len(line) > 2: # List will look like this ['point_moments', '6,', '0']

                                        count = 0 # Use to reset list if it contains 2 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 2: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if len(point_moments[0]) == 0:
                                            point_moments = appending_list
                                        else:
                                            point_moments = point_moments.append(appending_list)
                                    appending_list = [] # Reset appending_list

                                elif line[0] == "distributed_loads": # Count up till 4
                                    key = line[0]
                                    if len(line) > 2: # List will look like this ['distributed_loads', '6,', '0', '7']

                                        count = 0 # Use to reset list if it contains 4 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 3: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if len(distributed_loads[0]) == 0:
                                            distributed_loads = appending_list
                                        else:
                                            distributed_loads = distributed_loads.append(appending_list)
                                    appending_list = [] # Reset appending_list
                
                                else: # If len is not more than 2 just add the load as [[]]
                                    line[0] = [[]]

                        if choice == 3: # Cantilever
                            for i in range(18, 23):
                                line = line_ls[i]
                                key, value = line.split(" ")
                                d[key] = value

                            for i in range(23, 27): # Special way to parse point load, poin moment, distributed loads, and linear loads
                                line = line_ls[i]
                                line = line.replace(",", "")
                                line = line.replace("]", "")
                                line = line.replace("[", "")
                                line = line.replace("[[", "")
                                line = line.replace("]]", "")
                                line = line.split(" ")

                                appending_list = [] # Used for adding total point loads
                                if line[0] == "point_loads": # Count up till 3
                                    if len(line) > 2: # List will look like this ['point_loads', '6,', '0,', '-90']

                                        count = 0 # Use to reset list if it contains 3 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 3: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if line[0] == "point_loads":
                                            if len(point_loads[0]) == 0:
                                                point_loads = appending_list
                                            else:
                                                point_loads = point_loads.append(appending_list)
                                        appending_list = [] # Reset appending_list
                                
                                elif line[0] == "linear_loads": # Count up till 2
                                    if len(line) > 2: # List will look like this ['point_loads', '6,', '0,', '-90']

                                        count = 0 # Use to reset list if it contains 3 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 4: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if line[0] == "linear_loads":
                                            if len(linear_loads[0]) == 0:
                                                linear_loads = appending_list
                                            else:
                                                linear_loads = linear_loads.append(appending_list)
                                        appending_list = [] # Reset appending_list          
                                
                                elif line[0] == "point_moments": # Count up till 2
                                    key = line[0]
                                    if len(line) > 2: # List will look like this ['point_moments', '6,', '0']

                                        count = 0 # Use to reset list if it contains 2 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 2: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if len(point_moments[0]) == 0:
                                            point_moments = appending_list
                                        else:
                                            point_moments = point_moments.append(appending_list)
                                    appending_list = [] # Reset appending_list

                                elif line[0] == "distributed_loads": # Count up till 4
                                    key = line[0]
                                    if len(line) > 2: # List will look like this ['distributed_loads', '6,', '0', '7']

                                        count = 0 # Use to reset list if it contains 4 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 3: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if len(distributed_loads[0]) == 0:
                                            distributed_loads = appending_list
                                        else:
                                            distributed_loads = distributed_loads.append(appending_list)
                                    appending_list = [] # Reset appending_list
                
                                else: # If len is not more than 2 just add the load as [[]]
                                    line[0] = [[]]

                        beam_type = d["beam_type"]
                        wall_position = d["wall_position"]
                        span = int(d["span"])
                        A = int(d["A"])
                        B = int(d["B"])

                        break

                    else:
                        line_ls = []
                        for line in f:
                            line_ls.append(line.replace("\n", ""))

                        for i in range(0, 5):
                            line = line_ls[i]
                            key, value = line.split(" ")
                            d[key] = value

                        for i in range(5, 9): # Special way to parse point load, poin moment, distributed loads, and linear loads
                                line = line_ls[i]
                                line = line.replace(",", "")
                                line = line.replace("]", "")
                                line = line.replace("[", "")
                                line = line.replace("[[", "")
                                line = line.replace("]]", "")
                                line = line.split(" ")

                                appending_list = [] # Used for adding total point loads
                                if line[0] == "point_loads": # Count up till 3
                                    if len(line) > 2: # List will look like this ['point_loads', '6,', '0,', '-90']

                                        count = 0 # Use to reset list if it contains 3 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 3: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if line[0] == "point_loads":
                                            if len(point_loads[0]) == 0:
                                                point_loads = appending_list
                                            else:
                                                point_loads = point_loads.append(appending_list)
                                        appending_list = [] # Reset appending_list
                                
                                elif line[0] == "linear_loads": # Count up till 2
                                    if len(line) > 2: # List will look like this ['point_loads', '6,', '0,', '-90']

                                        count = 0 # Use to reset list if it contains 3 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 4: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if line[0] == "linear_loads":
                                            if len(linear_loads[0]) == 0:
                                                linear_loads = appending_list
                                            else:
                                                linear_loads = linear_loads.append(appending_list)
                                        appending_list = [] # Reset appending_list          
                                
                                elif line[0] == "point_moments": # Count up till 2
                                    key = line[0]
                                    if len(line) > 2: # List will look like this ['point_moments', '6,', '0']

                                        count = 0 # Use to reset list if it contains 2 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 2: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if len(point_moments[0]) == 0:
                                            point_moments = appending_list
                                        else:
                                            point_moments = point_moments.append(appending_list)
                                    appending_list = [] # Reset appending_list

                                elif line[0] == "distributed_loads": # Count up till 4
                                    key = line[0]
                                    if len(line) > 2: # List will look like this ['distributed_loads', '6,', '0', '7']

                                        count = 0 # Use to reset list if it contains 4 variables
                                        small_list = []

                                        for i in range(1, len(line)):
                                            small_list.append(int(line[i]))
                                            count += 1

                                            if count == 3: # If reached max count
                                                count = 0
                                                appending_list.append(small_list)
                                                small_list = []
                                        
                                        if len(distributed_loads[0]) == 0:
                                            distributed_loads = appending_list
                                        else:
                                            distributed_loads = distributed_loads.append(appending_list)
                                    appending_list = [] # Reset appending_list
                
                                else: # If len is not more than 2 just add the load as [[]]
                                    line[0] = [[]]


                        beam_type = d["beam_type"]
                        wall_position = d["wall_position"]
                        span = int(d["span"])
                        A = int(d["A"])
                        B = int(d["B"])

                        break

            except FileNotFoundError:
                print("Invalid file name! Please follow the correct format!")
            
            except Exception as e:
                print(e)



    # Remove empty list if user input value. Else, ignore
    if len(point_loads) >= 2:
        point_loads = list(filter(None, point_loads))
    if len(point_moments) >= 2:
        point_moments = list(filter(None, point_moments))
    if len(distributed_loads) >= 2:
        distributed_loads = list(filter(None, distributed_loads))
    if len(linear_loads) >= 2:
        linear_loads = list(filter(None, linear_loads))


# Function to validate load position
def validate_load_position():
    while True: # Set up an infinite loop if error
        try:
            print("Please select the type of load to input.")

            if beam_type != "Cantilever":
                value = int(input('Type "1" for Point Load\nType "2" for Point Moments\nType "3" for Distributed Loads\nType "4" for Linear Loads\nType "5" to Exit\nPlease type a number: '))

                # Validate input
                if value == 1: # Get point loads
                    print('Please type the point loads in this order. Location, X Magnitude (N), Y Magnitude (N) (- For downward force) - E.g. "6, 0, -90"')
                    user_point_loads = input("Please input the point load: ")
                    pl_location, pl_xMag, pl_yMag = user_point_loads.split(",")
                    point_loads.append([int(pl_location),int(pl_xMag),int(pl_yMag)])

                elif value == 2: # Get point moment
                    print('Please type the point moment in this order. Location (m), Magnitude of force (Nm) (- for anti-clockwise) - E.g. "17, 50"')
                    user_point_moments = input("Please input the point moment: ")
                    pm_location, pm_Mag = user_point_moments.split(",")
                    point_moments.append([int(pm_location),int(pm_Mag)])
                    
                elif value == 3: # Get distributed loads
                    print('Please type the distributed load in this order. Location start (m), Location end (m), Magnitude (kn/m) - E.g. "10, 15, -13"')
                    user_distributed_loads = input("Please input the distributed load: ")
                    dl_location_start, dl_location_end, dl_Mag = user_distributed_loads.split(",")
                    distributed_loads.append([int(dl_location_start),int(dl_location_end),int(dl_Mag)])

                elif value == 4: # Get linear loads
                    print('Please type the linear load in this order. Location start (m), Location end (m), Magnitude Start (kn/m), Magnitude End (kn/m) - E.g. "8, 17, -10, 0"')
                    user_linear_loads = input("Please input the linear load: ")
                    ll_location_start, ll_location_end, ll_start_Mag, ll_end_Mag = user_linear_loads.split(",")
                    distributed_loads.append([int(ll_location_start),int(ll_location_end),int(ll_start_Mag),int(ll_end_Mag)])

                else: # Break if user give value of 5
                    break
            else:
                print('Please type the point loads in this order. Location, X Magnitude (N), Y Magnitude (N) (- For downward force) - E.g. "6, 0, -90"')
                user_point_loads = input("Please input the point load: ")
                pl_location, pl_xMag, pl_yMag = user_point_loads.split(",")
                point_loads.append([int(pl_location),int(pl_xMag),int(pl_yMag)])
                break

        except ValueError:
            print("Please only input an integer")


# Function to validate cantilever support
def validate_cantilever_support():
    while True: # Set up an infinite loop if error
        try:
            print('Please type "1" for wall on the left and "2" for wall on the right')
            return int(input("Please input (1 or 2): "))

        except ValueError:
            print("Wall position should be an integer!")


# Function to validate input
def validate_beam_length():
    while True: # Set up an infinite loop if error
        try:
            return int(input("Please input length of beam (m): "))
        except ValueError:
            print("Beam length should be an integer!")


# Function to check beam type
def validate_beam_type():
    beam_type_ls = ["Simply supported", "Overhanging", "Cantilever"] # List to name the beam types
    while True: # Set up an infinite loop if error
        try:
            print('Please type "1" for Simply_supported, "2" for "Overhanging", or "3" for "Cantilever"')
            beam_type = int(input("Please input beam type (1, 2 or 3): "))
            if beam_type == 1:
                return beam_type_ls[0]
            elif beam_type == 2:
                return beam_type_ls[1]
            else:
                return beam_type_ls[2]
        except ValueError:
            print("Beam type should be an integer!")


# Function to check support position
def validate_support_position(support):
    while True: # Set up an infinite loop if error
        try:
            return int(input("Please input distance of {} support to left support: ".format(support)))
        except ValueError:
            print("Distance for the support must be an integer!")


# Function to parse data
def parse():
    # Defaults settings
    divs = 10000 # Divide the span up into this number of data points (Lower value means faster drawing but comes with rounding error)
    global delta
    delta = span/divs # Distance between the data points
    no_of_point_loads = len(point_loads[0]) # Test for point loads to consider
    no_of_point_moments = len(point_moments[0]) # Test for point moments to consider
    no_of_distributed_loads = len(distributed_loads[0]) # Test for uniformly distributed loads
    no_of_linearly_distributed_loads = len(linear_loads[0]) # Test for linearly distributed loads

    global X # Range of X-coordinates - Uses for loop instead of numpy.arange. Tutorial at https://pynative.com/python-range-for-float-numbers/#:~:text=The%20Python%20range()%20works,be%20interpreted%20as%20an%20integer%20. | https://www.edureka.co/community/93202/typeerror-float-object-cannot-be-interpreted-as-an-integer#:~:text=The%20“TypeError%3A%20%27float%27,does%20not%20work%20with%20floats.
    X = []

    for i in range_with_floats(0, span, delta):
        X.append(round(i, 4)) # Add the value back to the list

    reactions = [0.0, 0.0, 0.0] # Reactions (Va, Ha, Vb) - Defined as array of floats
    global shear_force, bending_moment
    shear_force = [] # Shear force at each data point
    bending_moment = [] # Bending moment at each data point
    
    # Reaction calculation - Cycle through all point loads and determine reactions
    global point_loads_record # Initialise an empty list
    point_loads_record = []
    
    if beam_type != "Cantilever": # Calculations only for simply supported and overhanging beam

        if no_of_point_loads > 0:
            for n, p in enumerate(point_loads): # n gives the position of the list e.g [0] Enumerate: https://www.programiz.com/python-programming/methods/built-in/enumerate
                Va, Ha, Vb = reactions_PL(n) # Function to calculate and return reactions
                point_loads_record.append([Va, Ha, Vb])

                # Add reactions to record
                reactions[0] = reactions[0] + Va
                reactions[1] = reactions[1] + Ha
                reactions[2] = reactions[2] + Vb

        # Shear and moment calculation - Cycle through all points and determine shear and moment
        if no_of_point_loads > 0:
            for n, p in enumerate(point_loads):
                Shear, Moment = shear_moment_point_load(n)
                shear_force.append(Shear)
                bending_moment.append(Moment)

        #  Reaction calculation - Cycle through all point moments and determine reactions
        global point_moment_records # Initialise an empty list
        point_moment_records = []

        if no_of_point_moments > 0:
            for n, m in enumerate(point_moments):
                Va, Vb = reactions_PM(n) # Function to calculate and return reactions
                point_moment_records.append([Va, Vb])

                # Add reactions to record
                reactions[0] = reactions[0] + Va
                reactions[2] = reactions[2] + Vb

        # Shear and moment calculation - Cycle through all point moments and determine shear and moment
        if no_of_point_moments > 0:
            for n, p in enumerate(point_moments):
                Shear, Moment = shear_moment_point_moment(n)
                shear_force.append(Shear)
                bending_moment.append(Moment)

        #  Reaction calculation - Cycle through all UDLs and determine reactions
        global UDL_records # Initialise an empty list
        UDL_records = []

        if no_of_distributed_loads > 0:
            for n, m in enumerate(distributed_loads):
                Va, Vb = reactions_UDL(n) # Function to calculate and return reactions
                UDL_records.append([Va, Vb])

                # Add reactions to record
                reactions[0] = reactions[0] + Va
                reactions[2] = reactions[2] + Vb

        # Shear and moment calculation - Cycle through all UDLs and determine shear and moment
        if no_of_distributed_loads > 0:
            for n, p in enumerate(distributed_loads):
                Shear, Moment = shear_moment_UDL(n)
                shear_force.append(Shear)
                bending_moment.append(Moment)

        # Reaction calculation - Cycle through all LDLs and determine reactions
        global LDL_records # Initialise and empty list
        LDL_records = []

        if no_of_linearly_distributed_loads > 0:
            for n, m in enumerate(linear_loads):
                Va, Vb = reactions_LDL(n) # Function to calculate and return reactions
                LDL_records.append([Va, Vb])

                # Add reactions to record
                reactions[0] = reactions[0] + Va
                reactions[2] = reactions[2] + Vb


        # Shear and moment calculation - Cycle through all UDLs and determine shear and moment
        if no_of_linearly_distributed_loads > 0:
            for n, p in enumerate(linear_loads):
                Shear, Moment = shear_moment_LDL(n)
                shear_force.append(Shear)
                bending_moment.append(Moment)

        print("The vertical reaction at A is {} kN".format(round(reactions[0], 2)))
        print("The vertical reaction at B is {} kN".format(round(reactions[2], 2)))
        print("The Horizontal reaction at A is {} kN".format(round(reactions[1], 2)))

    else: # Calculations for cantilever beam only
        global bm_cantilever, max_moment
        bm_cantilever = [] # Location, Magnitude
        if wall_position == "left": # Calculate if wall position is on the left
            if no_of_point_loads > 0: # No reactions due to point loads. Therefore, only calculate for shear and moment
                # Shear and moment calculation - Cycle through all points and determine shear and moment
                if no_of_point_loads > 0:
                    for n, p in enumerate(point_loads):
                        Shear, Moment = shear_moment_point_load_cantilever(n, "left")
                        shear_force.append(Shear)
                        bending_moment.append(Moment)

        else: # Calculate if wall position is on the right
            if no_of_point_loads > 0: # No reactions due to point loads. Therefore, only calculate for shear and moment
                # Shear and moment calculation - Cycle through all points and determine shear and moment
                if no_of_point_loads > 0:
                    for n, p in enumerate(point_loads):
                        Shear, Moment = shear_moment_point_load_cantilever(n, "right")
                        shear_force.append(Shear)
                        bending_moment.append(Moment)

    # Initialise new container for total shear force and total bending moment
    global total_shear_force, total_bending_moment
    total_shear_force = []
    total_bending_moment = []

    # Calculate total shear force and bending moment
    total_shear_force = column_wise_sum(shear_force)
    total_bending_moment = column_wise_sum(bending_moment)

    # Call function to draw beam, SFD, and BMD
    draw_diagrams()


# Function to calculate reactions due to point loads for cantilever
def shear_moment_point_load_cantilever(n, wall_position):
    if wall_position == "left": # For wall position on the left
        xp = point_loads[n][0] # Location of point load
        fy = point_loads[n][2] # Point load vertical component magnitude

        # Initalise new container
        Shear = []
        Moment = []

        max_shear = 0
        max_moment = 0
        for i, x in enumerate(X):
            shear = 0 # Initialise the shear force for this data point
            moment = 0 # Initialise the bending moment for this data point
            x = (round(x, 3))

            if x == 0:
                shear = -fy
                max_shear = shear

                moment = xp * fy
                max_moment = moment
                bm_cantilever.append([x, max_moment])

            if x == xp:
                shear = max_shear+fy
                max_shear = shear

                moment = -(xp * fy)
                max_moment = max_moment + moment
                bm_cantilever.append([x, max_moment])

            if x != xp:
                shear = max_shear


            # Store shear and moment for this location
            Shear.append(shear) # Add shear force at each point back to the shear_force global list
            Moment.append(moment) # Add bending moment at each point back to the bending_moment global list

        return Shear, Moment

    else: # For wall position on the right
        xp = point_loads[n][0] # Location of point load
        fy = point_loads[n][2] # Point load vertical component magnitude

        # Initalise new container
        Shear = []
        Moment = []

        max_shear = 0
        max_moment = 0
        for i, x in enumerate(X):
            shear = 0 # Initialise the shear force for this data point
            moment = 0 # Initialise the bending moment for this data point
            x = (round(x, 3))

            if x != xp:
                shear = max_shear
                if x < xp:
                    bm_cantilever.append([x, 0])

            if x == xp:
                shear = fy
                max_shear = shear

                moment = xp * fy
                max_moment = moment
                bm_cantilever.append([x, max_moment])

            if x == span:
                shear = max_shear -fy

                moment = xp * fy
                max_moment = max_moment - moment
                bm_cantilever.append([x, max_moment])

            # Store shear and moment for this location
            Shear.append(shear) # Add shear force at each point back to the shear_force global list
            Moment.append(moment) # Add bending moment at each point back to the bending_moment global list

        return Shear, Moment

# Function to calculate reactions due to point loads
def reactions_PL(n):
    xp = point_loads[n][0] # Location of point load
    fx = point_loads[n][1] # Point load horizontal component magnitude
    fy = point_loads[n][2] # Point load vertical component magnitude
    
    la_p = A - xp # Lever arm of point load about point A
    mp = fy * la_p # Moment generated by point load about A (Clockwise moments are positive)
    la_Vb = B - A # Lever arm of verticle reaction at B about point A

    Vb = mp / la_Vb # Verticle reaction at B
    Va = -fy-Vb # Verticle reaction at A
    Ha = -fx # Horizontal reaction at A

    return Va, Ha, Vb


# Function to calculate shear forces and bending moments due to point load
def shear_moment_point_load(n):
    xp = point_loads[n][0] # Location of point load
    fy = point_loads[n][2] # Point load vertical component magnitude
    Va = point_loads_record[n][0] # Verticle reaction at A for this point load
    Vb = point_loads_record[n][2] # Horizontal reaction at B for this point load

    # Initalise new container
    Shear = []
    Moment = []

    for i, x in enumerate(X):
        shear = 0 # Initialise the shear force for this data point
        moment = 0 # Initialise the bending moment for this data point

        if x > A:  # Calculate shear and moment due to reaction at A 
            shear = shear + Va
            moment = moment - Va*(x-A)
        
        if x > B: # Calculate shear and moment due to reaction at B
            shear = shear + Vb
            moment = moment - Vb*(x-B)

        if x > xp: # Calculate shear and moment due to point load
            shear = shear + fy
            moment = moment - fy*(x-xp)

        # Store shear and moment for this location
        Shear.append(shear) # Add shear force at each point back to the shear_force global list
        Moment.append(moment) # Add bending moment at each point back to the bending_moment global list

    return Shear, Moment


# Function to calculate reactions due to point moments
def reactions_PM(n):
    xm = point_moments[n][0] # Location of point moment
    m = point_moments[n][1] # Point moment magnitude
    la_vb = B - A # Lever arm of vertical reaction at B about point A

    Vb = m/la_vb # Vertical reaction at B
    Va = -Vb # Vertical reaction at A

    return Va, Vb


# Function to calculate shear forces and bending moments due to point moments
def shear_moment_point_moment(n):
    xm = point_moments[n][0] # Location of point moment
    m = point_moments[n][1] # Point moment magnitude
    Va = point_moment_records[n][0] # Verticle reaction at A for this point moment
    Vb = point_moment_records[n][1] # Horizontal reaction at B for this point moment
    
    # Initalise new container
    Shear = []
    Moment = []

    for i, x in enumerate(X):
        shear = 0 # Initialise the shear force for this data point
        moment = 0 # Initialise the bending moment for this data point

        if x > A:  # Calculate shear and moment due to reaction at A 
            shear = shear + Va
            moment = moment - Va*(x-A)
        
        if x > B: # Calculate shear and moment due to reaction at B
            shear = shear + Vb
            moment = moment - Vb*(x-B)

        if x > xm: # Calculate moment influence of point moment (No effect on shear)
            moment = moment - m

        # Store shear and moment for this location
        Shear.append(shear) # Add shear force at each point back to the shear_force global list
        Moment.append(moment) # Add bending moment at each point back to the bending_moment global list

    return Shear, Moment


# Function tot calculate reactions due to UDLs
def reactions_UDL(n):
    xStart = distributed_loads[n][0]
    xEnd = distributed_loads[n][1]
    fy = distributed_loads[n][2]

    fy_Res = fy*(xEnd - xStart)
    x_Res = xStart + 0.5 * (xEnd-xStart)

    la_p = A - x_Res # Lever arm of resultant point load about point A
    mp = fy_Res * la_p # Moment generated by resultant point load about A (Clockwise moments are positive)
    la_Vb = B - A # Lever arm of verticle reaction at B about point A

    Vb = mp / la_Vb # Verticle reaction at B
    Va = -fy_Res-Vb # Verticle reaction at A

    return Va, Vb


# Function to calculate shear forces and bending moments due to UDLs
def shear_moment_UDL(n):
    xStart = distributed_loads[n][0]
    xEnd = distributed_loads[n][1]
    fy = distributed_loads[n][2]
    Va = UDL_records[n][0]
    Vb = UDL_records[n][1]

    # Initalise new container
    Shear = []
    Moment = []

    for i, x in enumerate(X):
        shear = 0 # Initialise the shear force for this data point
        moment = 0 # Initialise the bending moment for this data point

        if x > A:  # Calculate shear and moment due to reaction at A 
            shear = shear + Va
            moment = moment - Va*(x-A)
        
        if x > B: # Calculate shear and moment due to reaction at B
            shear = shear + Vb
            moment = moment - Vb*(x-B)

        if x > xStart and x <= xEnd:
            shear = shear + fy*(x-xStart)
            moment = moment - fy*(x-xStart)*0.5*(x-xStart)
        elif x > xEnd:
            shear = shear + fy*(xEnd-xStart)
            moment = moment - fy*(xEnd-xStart)*(x-xStart-0.5*(xEnd-xStart))

        # Store shear and moment for this location
        Shear.append(shear) # Add shear force at each point back to the shear_force global list
        Moment.append(moment) # Add bending moment at each point back to the bending_moment global list

    return Shear, Moment


# Function to calculate reactions due to linearly varying distributed load
def reactions_LDL(n):
    xStart = linear_loads[n][0]
    xEnd = linear_loads[n][1]
    fy_start = linear_loads[n][2]
    fy_end = linear_loads[n][3]

    # Determine location and magnitude of force resultant
    if abs(fy_start) > 0:
        fy_Res = 0.5 * fy_start * (xEnd-xStart)
        x_Res = xStart + (1/3) * (xEnd-xStart)
    else:
        fy_Res = 0.5 * fy_end * (xEnd-xStart)
        x_Res = xStart + (2/3) * (xEnd-xStart)
    
    la_p = A - x_Res # Lever arm of resultant point load about point A
    mp = fy_Res * la_p # Moment generated by resultant point load about A (Clockwise moments are positive)
    la_Vb = B - A # Lever arm of verticle reaction at B about point A

    Vb = mp / la_Vb # Verticle reaction at B
    Va = -fy_Res-Vb # Verticle reaction at A

    return Va, Vb


# Function to calculate shear forces and bending moments due to LDLs
def shear_moment_LDL(n):
    xStart = linear_loads[n][0]
    xEnd = linear_loads[n][1]
    fy_start = linear_loads[n][2]
    fy_end = linear_loads[n][3]
    Va = LDL_records[n][0]
    Vb = LDL_records[n][1]

    # Initalise new container
    Shear = []
    Moment = []

    for i, x in enumerate(X):
        shear = 0 # Initialise the shear force for this data point
        moment = 0 # Initialise the bending moment for this data point

        if x > A:  # Calculate shear and moment due to reaction at A 
            shear = shear + Va
            moment = moment - Va*(x-A)
        
        if x > B: # Calculate shear and moment due to reaction at B
            shear = shear + Vb
            moment = moment - Vb*(x-B)

        if x > xStart and x <= xEnd:
            if abs(fy_start) > 0:
                x_base = x - xStart
                f_cut = fy_start - x_base * (fy_start/(xEnd-xStart))
                R1 = 0.5 * x_base * (fy_start-f_cut)
                R2 = x_base * f_cut
                shear = shear + R1 + R2
                moment = moment - R1 * (2/3) * x_base - R2 * (x_base/2)
            else:
                x_base - x - xStart
                f_cut = fy_end * (x_base/(xEnd-xStart))
                R = 0.5 * x_base * f_cut
                shear = shear + R
                moment = moment - R * (x_base/3)
        elif x > xEnd:
            if abs(fy_start) > 0:
                R = 0.5 * fy_start * (xEnd-xStart)
                xr = xStart + (1/3) * (xEnd-xStart)
                shear = shear + R
                moment = moment - R * (x-xr)
            else:
                R = 0.5 * fy_end * (xEnd-xStart)
                xr = xStart + (2/3) * (xEnd-xStart)
                shear = shear + R
                moment = moment - R * (x-xr)

        # Store shear and moment for this location
        Shear.append(shear) # Add shear force at each point back to the shear_force global list
        Moment.append(moment) # Add bending moment at each point back to the bending_moment global list

    return Shear, Moment


# ! TILL HERE -=====================================================

# Function to draw shear force diagram and bending moment diagram
def draw_diagrams():
    # Set variables linked to heading direction (Use in turtle.setheading())
    look_up, look_right, look_down, look_left = 90, 0, 270, 180

    # Define span of full beam
    full_beam = span

    # Default drawing settings
    t = turtle.Turtle() # Set calling of class method to t
    t.speed(0) # Set the drawing speed to max
    turtle.bgcolor("#E0E8F4") # Set background color to light blue
    turtle.tracer(100) # Turn turtle animation off

    # Calculations to determine world coordinates
    shear_force_pos = [] # Initialise an empty list
    for i in range(len(X)): # Loop to convert all negative values in the list to positive (Use to determine max shear force)
        shear_force_pos.append(abs(total_shear_force[i]))
    max_shear_force = max(shear_force_pos)

    bending_moment_pos = [] # Initialise an empty list
    for i in range(len(X)): # Loop to convert all negative values in the list to positive (Use to determine max bending moment)
        bending_moment_pos.append(abs(total_bending_moment[i]))
    max_bending_moment = max(bending_moment_pos)

    # Find the total y distance above (0,0) needed to draw whole graph (Padding of 20% is added)
    y_distance_pos = max_bending_moment*1.7 + (max_shear_force*3.4) * 2 # (max_shear_force*2.4) * 2 - Add more padding to the top

    # Find the total y distance needed below (0,0) to draw the graph
    y_distance_neg = -max_bending_moment*1.7

    turtle.setup(1200, 1000)

    # Set the world coordinates with border at left and right sides
    turtle.setworldcoordinates(-span*0.3, y_distance_neg, span*1.075, y_distance_pos)

    # Set home coordinates for beam and SFD
    ycor_beam = max_bending_moment*1.7 + max_shear_force*4.5
    ycor_SFD = max_bending_moment*1.5 + max_shear_force*1.2

    # Write title
    write_title(t, ycor_beam, ycor_SFD, full_beam) # Call write_title() to write title of diagrams on the left

    # Draw beam
    t.penup() # Stop drawing
    t.goto(0, ycor_beam) # Set position to home of beam
    t.pendown() # Start drawing
    draw_beam(t, full_beam, look_up, look_right, look_down, look_left) # Call function to draw beam

    # Draw forces
    draw_forces(t, full_beam, ycor_beam, look_down)

    # Draw SFD
    t.penup() # Stop drawing
    t.goto(0, ycor_SFD) # Set position to home of SFD
    t.pendown() # Start drawing
    draw_x_line(t, look_right, look_left, full_beam) # Draw a dark line with the given span in the X axis
    draw_SFD(t, ycor_SFD) # Call draw_SFD() to draw SFD

    # Draw BMD
    t.penup() # Stop drawing
    t.goto(0, 0) # Set position to home of BMD
    t.pendown() # Start drawing
    draw_x_line(t, look_right, look_left, full_beam) # Draw a dark line with the given span in the X axis
    draw_BMD(t) # Call draw_BMD() function to draw BMD

    # Draw SFD Y-axis
    draw_SFD_Y_axis(t, max_shear_force, ycor_SFD, look_up)

    # Draw BMD Y-axis
    draw_BMD_Y_axis(t, max_bending_moment, look_up)

    # Draw X-axis
    draw_X_axis(t, max_bending_moment, look_right)

    # Default drawing settings
    t.penup() # Stop drawing
    t.goto(-span*0.3, y_distance_neg) # Go to bottom left corner
    turtle.update() # Perform a TurtleScreen update. To be used when tracer is turned off
    turtle.done() # End turtle drawing


# Function to draw forces
def draw_forces(t, full_beam, ycor_beam, look_down):
    # Let width of the beam scale with length of the beam 
    width = full_beam * 0.5

    # Check if cantilever beam (to draw walls)
    if beam_type == "Cantilever":

        if wall_position == "left":
            t.penup()
            t.goto(-0.25, ycor_beam - width*4)
            t.write("⤹", False, align="center", font=("Arial", 24, "bold"))
            t.goto(-0.7, ycor_beam - width*3)
            t.write("Ma", False, align="center", font=("Arial", 10, "bold"))
            t.goto(-0.25, ycor_beam - width*10)
            t.write("↑", False, align="center", font=("Arial", 20, "bold"))
            t.goto(-0.25, ycor_beam - width*13)
            t.write("Ry", False, align="center", font=("Arial", 10, "bold"))
            t.goto(0, ycor_beam - width*4)
            t.pendown()
            t.goto(0, ycor_beam - width*4)
            t.goto(0, ycor_beam + width*4)
        else:
            t.penup()
            t.goto(span+0.25, ycor_beam - width*4)
            t.write("⤸", False, align="center", font=("Arial", 24, "bold"))
            t.goto(span+0.7, ycor_beam - width*3)
            t.write("Ma", False, align="center", font=("Arial", 10, "bold"))
            t.goto(span+0.25, ycor_beam - width*10)
            t.write("↑", False, align="center", font=("Arial", 20, "bold"))
            t.goto(span+0.25, ycor_beam - width*13)
            t.write("Ry", False, align="center", font=("Arial", 10, "bold"))
            t.goto(span, ycor_beam - width*4)
            t.pendown()
            t.goto(span, ycor_beam - width*4)
            t.goto(span, ycor_beam + width*4)

    else: # If beam is Simply supported or overhanging

        # Draw Support
        t.penup()
        t.goto(A, ycor_beam-width*5)
        t.write("↑", False, align="center", font=("Arial", 18, "bold"))
        t.goto(A, ycor_beam-width*8)
        t.write("A", False, align="center", font=("Arial", 10, "bold"))

        t.goto(B, ycor_beam-width*5)
        t.write("↑", False, align="center", font=("Arial", 18, "bold"))
        t.goto(B, ycor_beam-width*8)
        t.write("B", False, align="center", font=("Arial", 10, "bold"))

    # Draw point loads
    if len(point_loads[0]) > 0: # Loop over point_load to determine forces
        for i, x in enumerate(point_loads):
            location, xMag, YMag = x
            if YMag < 0:
                neg_PL(t, width, ycor_beam, location, YMag)
            else:
                pos_PL(t, ycor_beam, location, YMag)

    # Draw point moments
    if len(point_moments[0]) > 0: # Loop over point_load to determine forces
        for i, x in enumerate(point_moments):
            location, Mag = x
            if Mag < 0: # CCW moment
                neg_PM(t, width, ycor_beam, location, Mag)
            else:
                pos_PM(t, width, ycor_beam, location, Mag)

    # Draw linear loads
    if len(linear_loads[0]) > 0: # Loop over point_load to determine forces
        for i, x in enumerate(linear_loads):
            xStart, xEnd, startMag, endMag = x
            neg_LL(t, width, ycor_beam, xStart, xEnd, startMag, endMag)

    # Draw distributed loads
    if len(distributed_loads[0]) > 0: # Loop over point_load to determine forces
            for i, x in enumerate(distributed_loads):
                xStart, xEnd, Mag = x
                neg_DL(t, width, ycor_beam, xStart, xEnd, Mag)


# Function to draw distributed loads
def neg_DL(t, width, ycor_beam, xStart, xEnd, Mag):
    t.penup()
    difference = xEnd - xStart
    count = 0
    for i in range(difference):
        t.goto(xStart+count, ycor_beam)
        t.write("⥥", False, align="center", font=("Arial", 20, "bold"))
        count += 1

    t.goto(xStart+difference/2, ycor_beam+width*5)
    t.write("{}kN/m".format(abs(Mag)), False, align="center", font=("Arial", 18, "bold"))


# Function to draw linear loads
def neg_LL(t, width, ycor_beam, xStart, xEnd, startMag, endMag):
    t.penup()
    difference = xEnd - xStart
    count = 0
    for i in range(difference):
        t.goto(xStart+count, ycor_beam)
        t.write("⥥", False, align="center", font=("Arial", 20, "bold"))
        count += 1

    t.goto(xStart, ycor_beam+width*5)
    t.write("{}kN/m".format(abs(startMag)), False, align="center", font=("Arial", 18, "bold"))
    t.goto(xEnd, ycor_beam+width*5)
    t.write("{}kN/m".format(abs(endMag)), False, align="center", font=("Arial", 18, "bold"))


# Function to draw CCW moment
def neg_PM(t, width, ycor_beam, location, Mag):
    t.penup()
    t.goto(location, ycor_beam-width*5)
    t.write("⤹", False, align="center", font=("Arial", 24, "bold"))
    t.goto(location, ycor_beam+width)
    t.write("{}Nm".format(abs(Mag)), False, align="center", font=("Arial", 18, "bold"))


# Function to draw CCW moment
def pos_PM(t, width, ycor_beam, location, Mag):
    t.penup()
    t.goto(location, ycor_beam-width)
    t.write("⤸", False, align="center", font=("Arial", 24, "bold"))
    t.goto(location, ycor_beam+width*5)
    t.write("{}Nm".format(abs(Mag)), False, align="center", font=("Arial", 18, "bold"))


# Function to draw downwards arrow
def neg_PL(t, width, ycor_beam, location, YMag):
    t.penup()
    t.goto(location, ycor_beam + width)
    t.write("↓", False, align="center", font=("Arial", 18, "bold"))
    t.goto(location, ycor_beam + width*5)
    t.write("{}kN".format(abs(YMag)), False, align="center", font=("Arial", 18, "bold"))


# Function to draw upward arrow
def pos_PL(t, width, ycor_beam, location, YMag):
    t.penup()
    t.goto(location, ycor_beam - width*5)
    t.write("↑", False, align="center", font=("Arial", 18, "bold"))
    t.goto(location, ycor_beam - width*10)
    t.write("{}kN".format(abs(YMag)), False, align="center", font=("Arial", 18, "bold"))


# Function to label the X-axis
def draw_X_axis(t, max_bending_moment, look_right):
    t.pensize(1) # Set pensize to 1
    t.penup() # Stop drawing
    t.goto(-span*0.05, -max_bending_moment*1.2) # Go below BMD with a bit of padding before drawing the x-axis
    t.setheading(look_right) # Point cursor to face right
    t.pendown() # Start drawing
    t.forward(span*1.1)
    t.penup() # Stop drawing
    
    divs = 10 # Set 10 different sections to mark the X-axis
    x_axis_delta = span / divs # Set the step
    t.goto(0, -max_bending_moment*1.2) # Reset positon before marking the divs
    for _ in range_with_floats(0, span, x_axis_delta):
        t.dot() # Draw the dot
        t.forward(x_axis_delta) # Move forward the delta
        t.dot() # Draw the dot


    t.goto(0, -max_bending_moment*1.35) # Reset postion before writing below the divs
    distance = 0
    # t.write("{}".format(round(distance,1)), False, align="center", font=("Arial", 8, "bold")) # Write distance
    for _ in range_with_floats(0, span, x_axis_delta):
        t.write("{}".format(round(distance,1)), False, align="center", font=("Arial", 8, "bold")) # Write distance
        t.forward(x_axis_delta) # Move forward the delta
        distance += x_axis_delta # Add delta to total distance count

    if distance == span:
        t.write("{}".format(round(distance,1)), False, align="center", font=("Arial", 8, "bold")) # Write distance

    t.goto(0, -max_bending_moment*1.6) # Reset postion before writing distance
    t.forward(span/2) # Move the distance half of span
    t.write("Distance (m)", False, align="center", font=("Arial", 14, "")) # Write distance for final point


# Function to draw SFD Y-axis
def draw_SFD_Y_axis(t, max_shear_force, ycor_SFD, look_up):
# Draw on left side of the graph
    t.penup() # Stop drawing
    t.goto(-span*0.03,ycor_SFD + -max_shear_force*1.25) # Start line at bottom of SFD
    t.setheading(look_up) # Point cursor up
    t.pensize(1) # Set pensize to smallest
    t.pendown() # Start drawing
    t.forward(max_shear_force*2.75) # Move forward
    t.penup() # Stop drawing
    t.forward(max_shear_force*0.03) # Move forward
    t.write("Shear Force (kN)", False, align="center", font=("Arial", 14, "")) # Write distance for final point
    t.goto(-span*0.03, ycor_SFD) # Go to 0 of graph
    t.dot() # Place a dot to mark 0 position
    t.goto(-span*0.06, ycor_SFD)
    t.write("{}".format(0), False, align="center", font=("Arial", 8, "bold")) # Write distance for final point

    # Calculations to draw points
    shear_force_max = max(total_shear_force)
    shear_force_min = min(total_shear_force)
    if shear_force_min < 0:
        t.goto(-span*0.03, ycor_SFD+shear_force_min) # Go to 0 of graph
        t.dot() # Place a dot to mark 0 position
        t.goto(-span*0.06, ycor_SFD+shear_force_min)  # Go to 0 of graph
        t.write("{}".format(round(shear_force_min,2)), False, align="center", font=("Arial", 8, "bold")) # Write distance for final point
    if shear_force_max > 0:
        t.goto(-span*0.03, ycor_SFD+shear_force_max) # Go to 0 of graph
        t.dot() # Place a dot to mark 0 position
        t.goto(-span*0.06, ycor_SFD+shear_force_max)  # Go to 0 of graph
        t.write("{}".format(round(shear_force_max,2)), False, align="center", font=("Arial", 8, "bold")) # Write distance for final point


# Function to draw BMD Y-axis
def draw_BMD_Y_axis(t, max_bending_moment, look_up):
    # Draw on left side of the graph
    t.penup() # Stop drawing
    t.goto(-span*0.03,-max_bending_moment*1.28) # Start line at bottom of BMD
    t.setheading(look_up) # Point cursor up
    t.pensize(1) # Set pensize to smallest
    t.pendown() # Start drawing
    t.forward(max_bending_moment*2.45) # Move forward
    t.penup() # Stop drawing
    t.forward(max_bending_moment*0.025) # Move forward
    t.write("Bending Moment (kNm)", False, align="center", font=("Arial", 14, "")) # Write distance for final point
    t.goto(-span*0.03, 0) # Go to 0 of graph
    t.dot() # Place a dot to mark 0 position
    t.goto(-span*0.06, 0)
    t.write("{}".format(0), False, align="center", font=("Arial", 8, "bold")) # Write distance for final point

    # Calculation to determine max bending moment
    bending_moment_max = max(total_bending_moment)
    bending_moment_min = min(total_bending_moment)
    if bending_moment_min < 0:
        t.goto(-span*0.03, bending_moment_min) # Go to 0 of graph
        t.dot() # Place a dot to mark 0 position
        t.goto(-span*0.06, bending_moment_min)  # Go to 0 of graph
        t.write("{}".format(round(bending_moment_min,2)), False, align="center", font=("Arial", 8, "bold")) # Write distance for final point
    if bending_moment_max > 0:
        t.goto(-span*0.03, bending_moment_max) # Go to 0 of graph
        t.dot() # Place a dot to mark 0 position
        t.goto(-span*0.06, bending_moment_max)  # Go to 0 of graph
        t.write("{}".format(round(bending_moment_max,2)), False, align="center", font=("Arial", 8, "bold")) # Write distance for final point


# Function to write Beam Diagram, Shear Force Diagram, and Bending Moment Diagram to the left of the drawings
def write_title(t, ycor_beam, ycor_SFD, full_beam):
    # Write title of Beam Diagram
    t.penup() # Stop drawing
    t.goto(-full_beam*0.28, ycor_beam)
    t.write("Beam Diagram", False, align="left", font=("Arial", 10, "bold"))

    # Write title of Shear Force Diagram
    t.goto(-full_beam*0.28, ycor_SFD)
    t.write("SFD", False, align="left", font=("Arial", 10, "bold"))

    # Write title of Bending Moment Diagram
    t.goto(-full_beam*0.28, 0)
    t.write("BMD", False, align="left", font=("Arial", 10, "bold"))


# Function to draw a darker X line and return to original position 
def draw_x_line(t, look_right, look_left, full_beam):
    t.pensize(3) # Draw a thicker line
    t.forward(full_beam) # Draw a line the length of span
    t.pensize(2) # Reset pen size
    t.setheading(look_left)
    t.penup() # Stop drawing
    t.forward(full_beam) # Travese back to original position
    t.setheading(look_right) # Point to east
    t.pendown() # Start drawing
    

# Function to draw beam
def draw_beam(t, full_beam, look_up, look_right, look_down, look_left):
    # Let width of the beam scale with length of the beam 
    width = full_beam * 0.5

    t.forward(full_beam) # Move forward the length of the beam
    t.setheading(look_down) # Let cursor point down
    t.forward(width) # Move forward the width of the beam
    t.setheading(look_left) # Let cursor point left
    t.forward(full_beam) # Move forward the length of the beam
    t.setheading(look_up) # Let cursor point left
    t.forward(width) # Move forward the width of the beam
    t.setheading(look_right) # Reset the cursor back to pointing right


# Function to draw SFD - Graph tutorial from: https://www.geeksforgeeks.org/python-program-to-draw-a-bar-chart-using-turtle/
def draw_SFD(t, ycor_SFD):
    for i in range(len(X)):
        t.forward(delta)
        t.sety(total_shear_force[i] + ycor_SFD)


# Function to draw BMD
def draw_BMD(t):
    if beam_type != "Cantilever":
        for i in range(len(X)):
            t.forward(delta)
            t.sety(total_bending_moment[i])
    else: # Use bm_cantilever list
        if wall_position == "left":
            for i, x in enumerate(bm_cantilever):
                location, Mag = x
                t.goto(location, Mag)
        else:
            for i, x in enumerate(bm_cantilever):
                location, Mag = x
                t.goto(location, Mag)


# Function to generate X-coordinates
def range_with_floats(start, stop, step):
    while stop > start:
        yield start
        start += step


# Function for column wise sum
def column_wise_sum(list):
    return [sum(i) for i in zip(*list)]


# Function to exit program
def exit_program():
    sys.exit('Exited program! To start program again please type "python beam.py" in the command-prompt') # Exit the program completely and tell what the user should do in case they want to re-run the program


# Function to strip line from readlines
def nonblank_lines(f):
    for l in f:
        line = l.rstrip()
        if line:
            yield line


if __name__ == "__main__":
    main()