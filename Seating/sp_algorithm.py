import random

class SpMethod3:
    def __init__(self, rooms: list, classes: list, settings=None) -> None:
        self.rooms = rooms
        self.classes_all = classes
        self.classes = []

        for cls in classes:
            self.classes.append(cls["students"])
        self.settings = settings


    def total_seats(self):
        seat = 0
        for room in self.rooms:
            seat += int(room['total_seats'])

        return seat

    def total_students(self):
        students = 0
        for clas in self.classes:
            students += len(clas)

        return students

    def is_possible(self):
        seats = self.total_seats()
        students = self.total_students()

        if students <= seats:
            # print("It is possible")
            return True

        # print(f"Not Possible as Seats= {seats} And Students= {students}")
        return False

    def print_room_data(self, room_num, room):

        total_row = len(room)
        print("+", ("-" * ((25 * total_row )-2)), "+", sep="")
        print("|", f" Room : {room_num}", " " * ((25 * total_row)-12), "|", sep="")
        print("+", ("-" * ((25 * total_row )-2)), "+", sep="")

        c = 0
        for clumn in range(len(room[0])):
            # print(f"clumn==> {clumn}")
            print("|", " " * ((25 * total_row ) - 2), "|", sep="")
            print("|  ", end="")
            space = 0
            total_space = (25 * total_row ) - 2

            for clumn2 in range(len(room)):
                try:
                    desk_d = room[clumn2][c]
                except:
                    desk_d = ["                 "]
                l = 1
                for roll in desk_d:
                    print(roll, end="")
                    if l < len(desk_d):
                        print(" : ", end="")

                    l += 1
                print("      ", end="")
            print("")
            c += 1

        print("+", ("-" * ((25 * total_row )-2)), "+", sep="")

        print("\n\n")



    def planning(self):
        planned_data = {}

        for room in self.rooms: # iterating one room from all rooms
            room_data = [] # to store room planning
            room_num = room['room_no'] # store room number

            for row in room["rows"]: # iterating one rows from room for planning each row seating plan individually
                row_data = [] # to store one row seating plan

                desks = room['rows'][row]['desks'] # number of desk in a row
                capacity = room['rows'][row]['capacity'] # capacity of each desk in a row

                on_class = 0 # which class is in used for planning

                desk_data = [] # to store all seat in desk like format after filling all rows  Eg. [ 21BC0045, 22BC0043]

                for cap in range(capacity):
                    temp_data = [] # to store temp row seating plan

                    for desk in range(desks): # this will fill the data vertically in every row of a class  Eg. [ 21BC068, 21BC069]
                        try:
                            temp_data.append(self.classes[on_class].pop(0)) # removing rollnumber from classes list and adding to temp_data varialble.This means, allocating seat to a roolnumber
                        except:

                            print(f"SelfClass==> {self.classes}")

                            if self.classes != []:
                                if self.classes[on_class] == []:
                                    self.classes.pop(on_class)

                            if len(self.classes) > 0:
                                print("Next class is started.....")
                                temp_data.append(self.classes[on_class].pop(0))

                            else:
                                temp_data.append("       ")


                    desk_data.append(temp_data)# Adding one column seating plan


                for indx in range(desks):# here just changing seating data from verically to horizontly
                    d = [] #store temp one desk data
                    for rw in desk_data: # itrating every sub_row in row
                        d.append(rw[indx])# Adding one seat to one desk plan

                    row_data.append(d)# adding one desk plan to row plan


                # Adding one row seating plan to room plan
                room_data.append(row_data)

            if room['gate_side'] == "right":
                room_data = room_data[::-1]

            # Adding one room plan to  planned_data with room number
            planned_data[room_num] = [[room['gate_side'], room['room_disc']] ,room_data]

        #planing is compelete and now return planned data
        return planned_data



class SpMethod4:
    def __init__(self, rooms: list, classes: list, settings=None) -> None:
        self.rooms = rooms
        self.classes_all = classes
        self.classes = []

        for cls in classes:
            self.classes.append(cls["students"])
        self.settings = settings


    def total_seats(self):
        seat = 0
        for room in self.rooms:
            seat += int(room['total_seats'])

        return seat

    def total_students(self):
        students = 0
        for clas in self.classes:
            students += len(clas)

        return students

    def is_possible(self):
        seats = self.total_seats()
        students = self.total_students()

        if students <= seats:
            print("It is possible")
            return True

        print(f"Not Possible as Seats= {seats} And Students= {students}")
        return False

    def print_room_data(self, room_num, room):

        total_row = len(room)
        print("+", ("-" * ((25 * total_row )-2)), "+", sep="")
        print("|", f" Room : {room_num}", " " * ((25 * total_row)-12), "|", sep="")
        print("+", ("-" * ((25 * total_row )-2)), "+", sep="")

        c = 0
        for clumn in range(len(room[0])):
            # print(f"clumn==> {clumn}")
            print("|", " " * ((25 * total_row ) - 2), "|", sep="")
            print("|  ", end="")
            space = 0
            total_space = (25 * total_row ) - 2

            for clumn2 in range(len(room)):
                try:
                    desk_d = room[clumn2][c]
                except:
                    desk_d = ["                 "]
                l = 1
                for roll in desk_d:
                    print(roll, end="")
                    if l < len(desk_d):
                        print(" : ", end="")

                    l += 1
                print("      ", end="")
            print("")
            c += 1

        print("+", ("-" * ((25 * total_row )-2)), "+", sep="")

        print("\n\n")



    def planning(self):
        planned_data = {}

        for room in self.rooms: # iterating one room from all rooms
            room_data = [] # to store room planning
            room_num = room['room_no'] # store room number

            for row in room["rows"]: # iterating one rows from room for planning each row seating plan individually
                row_data = [] # to store one row seating plan

                desks = room['rows'][row]['desks'] # number of desk in a row
                capacity = room['rows'][row]['capacity'] # capacity of each desk in a row

                on_class = 0 # which class is in used for planning

                desk_data = [] # to store all seat in desk like format after filling all rows  Eg. [ 21BC0045, 22BC0043]

                for cap in range(capacity):
                    temp_data = [] # to store temp row seating plan

                    for desk in range(desks): # this will fill the data vertically in every row of a class  Eg. [ 21BC068, 21BC068]

                        if on_class  <= len(self.classes)-1: # class wich is use shoud be less than class lenght. If it is greater, this means no class is left [on_class] value to fill data and this will raise Index not found error

                            if self.classes == []:
                                print("class is empty")

                            if self.classes[on_class] != []: # to check if class wich is in use should't emplty

                                temp_data.append(self.classes[on_class].pop(0)) # removing rollnumber from classes list and adding to temp_data varialble.This means, allocating seat to a roolnumber

                            else:
                                # if the class wich is in use is empty

                                if self.classes != []: # to check Classes is not empty other classes are present in Classes List
                                    self.classes.pop(on_class) # so, only class wich is in use is empty, so remove it from Classes list


                                    # As we itrate one seat from row, So, it need to be allocate to a roll number, So we use next class rollnumber
                                    if len(self.classes) > 0: # cheking if there is another class in thelist to move on
                                        temp_data.append(self.classes[on_class].pop(0))# from here a new class begin, starting point of a class

                                    else:# no class is present in classes list, class list is empty, so all remainging seats left empty
                                        temp_data.append("       ")
                                else:
                                    print("Class is empty")
                        else:
                            if capacity > len(self.classes): # if capacity is greater than of lenght of class, so we can allocate two seats in one banch having one student midlle from another class
                                if (on_class -2 ) >= 0: # here the class wich is in use is subtacted from 2 and if it is > 0, this means there is more than 2 different classes is present in the classes list eg. [class1, class2, class3]
                                    on_class = on_class - 2 # here we are moving to two class back, so we can add one row of same class.  Exaxple: Suppose In [class1, class2, class3] we are using <class3> and moving to two class back makes <class1> the current using class

                                    try:
                                        temp_data.append(self.classes[on_class].pop(0))# adding the rollnumber from current uing class
                                    except:
                                        temp_data.append("       ")
                                else:
                                    temp_data.append("       ")# if only one class is left in the class list, so we can't allocate two seat on same desk to same class. Ex: [ class1, class2] -both class are same
                            else:
                                temp_data.append("       ") # capacity is less than lenght of class, so we can't allocate two seat on same desk to same class. Ex: [ class1, class2] -both class are same



                    on_class += 1 # increasing the current using class value, so that in next column it uses the other class rollnumber
                    desk_data.append(temp_data)# Adding one column seating plan

                for indx in range(desks):# here just changing seating data from verically to horizontly
                    d = [] #store temp one desk data
                    for rw in desk_data: # itrating every sub_row in row
                        d.append(rw[indx])# Adding one seat to one desk plan

                    row_data.append(d)# adding one desk plan to row plan


                # Adding one row seating plan to room plan
                room_data.append(row_data)

            if room['gate_side'] == "right":
                room_data = room_data[::-1]
            # Adding one room plan to  planned_data with room number
            planned_data[room_num] = [[room['gate_side'], room['room_disc']] ,room_data]

        #planing is compelete and now return planned data
        return planned_data




# if __name__ == "__main__":
#     rooms = [Rooms.room_35, Rooms.room_33, Rooms.room_32, Rooms.room_34]

#     classes = [Class.bca_1, Class.bca_3, Class.bca_5, Class.bca_fail]

#     classes_roll_list = []
#     for clas in classes:
#         classes_roll_list.append( list(clas.keys()) )


#     # Method 2
#     method = Method2(rooms=rooms, classes= classes_roll_list)

#     #check total desk
#     total_seat = method.total_seats()
#     print(f"Total_Seats==> {total_seat}")

#     #check total students
#     total_students = method.total_students()
#     print(f"Total_Students==> {total_students}")

#     #check possibility
#     pos = method.is_possible()
#     print(f"Posibility==> {pos}")


#     print("\n\n")

#     seating_plan_data = method.planning()

#     for room in seating_plan_data:
#         method.print_room_data(room, seating_plan_data[room])
