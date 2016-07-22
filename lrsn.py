#!/usr/bin/python
# coding: ascii
#-------------------------------------------------------------------------------
# Name:        LRSN.pl (Lab Reservation System Navigator a.k.a. Larson)
# Purpose:     To allow for quick database information aquisition
#
# Author:      Dennis Sauve
#
# Created:     06/22/2012
# Updated:     07/23/0212
# Version:     0.36
#
# Notes:       To be used with Linux only, Windows will not accept certain
#              commands. Can be used on terminal window to Linux from Windows.
#
#              Version 0.04 incorporated the ability to show all the current
#              reservations.
#              Version 0.10 saw completion of Current Reservation formatting.
#              Version 0.13 Was a stopping point on June 22nd.
#              Version 0.16 saw addition of type-search.
#              Version 0.19 I added the concept of searching by location, dev
#                           not yet started on that front.
#              Version 0.21 Starting to dev search by location.
#              Version 0.23 Saw Completion of the search by location ability,
#                           looking into making command line options.
#              Version 0.27 Command line options completed for now. Should make
#                           quick use a breeze.
#              Version 0.28 Added name command line option.
#              Version 0.29 mgmt --> Console. No Footer in Reservation results.
#                           Also added the "quiet" mode.
#              Version 0.30 No clear screen in command line argument mode.
#              Version 0.32 Searches are now case insensitive.
#-------------------------------------------------------------------------------

import os, MySQLdb, time, datetime, string, traceback
from os import system
from optparse import OptionParser

vr = 'version 0.36'

now = datetime.datetime.now()
epoch = time.mktime(now.timetuple())

descript = """This is the Lab Reservation System Navigator, a.k.a. Larson.
Use it to find whatever you need in an efficient text based format. This is a
passive program, meaning that there is no insertion to the MySQL Database. For
further information regarding this program, contact either Dennis Sauve or [Redacted].\n"""+vr

howto = """lrsn.py [options[args]] <---Which are optional. """

parser = OptionParser(description=descript, version=vr, usage=howto)
parser.add_option('-a', '--active', action='store_true', help='Displays all active devices, then exits. Can be used in conjunction with comma, and quiet.')
parser.add_option('-c', '--comma', action='store_true', help='Displays output with no spaces, being only delimited by commas. Can be used with any argument. Not recommended for use with the GUI.')
parser.add_option('-e', '--email', action='store_true', help='On outputs that include reservation owners, the respective emails will be printed alongside. Use with care.')
parser.add_option('-l', '--location', help="Looks for locations containing the argument, including partials, case-insensitive, and returns the results.")
parser.add_option('-n', '--name', help="Looks for devices where the name contains search key, partials will work.")
parser.add_option('-r', '--reservations', action='store_true', help='Displays all current reservations and exits. Can be used with comma, and quiet.')
parser.add_option('-q', '--quiet', action='store_true', help='Runs the script in quiet mode, only output the results. Limits the gui.')
parser.add_option('-u', '--user', help='Requires a search keyword, goes and tries to match to a user.')
(opts, args) = parser.parse_args()

def main():
    if opts.quiet:
        pass
    else:
        system('clear')
        print("""Lab Reservation System Navigator
    Version: %s
    Created by: Dennis Sauve""") % vr

    try:
        conn = MySQLdb.connect (host = "[Redacted]", user = "[Redacted]", passwd = "[Redacted]", db = "[Redacted]")
        cursor = conn.cursor ()
    except:
        fail("could not connect to the [Redacted] database.")

    if opts.quiet:
        pass
    else:
        print("\nConnection to [Redacted] Database Established.")

    if opts.reservations:
        current_reservations_menu(cursor)
    elif opts.active:
        active_devices_menu(cursor)
    elif opts.location:
        location_menu(cursor)
    elif opts.name:
        device_name_menu(cursor)
    elif opts.user:
        search_users(cursor)
    else:
        if opts.quiet:
            pass
        else:
            raw_input("Press Enter to Continue.")

    system('clear')
    main_menu(cursor)

def main_menu(cursor):
    print("""Select an initial search parameter:
        1. Device Name
        2. Device Type
        3. Active Devices
        4. Current Reservations
        5. Location (By Rack)
        6. Search Users

       -1. Exit
       -2. About""")
    choice = raw_input("Option: ")
    if choice == "1":
        device_name_menu(cursor)
    elif choice == "2":
        device_type_menu(cursor)
    elif choice == "3":
        active_devices_menu(cursor)
    elif choice == "4":
        current_reservations_menu(cursor)
    elif choice == "5":
        location_menu(cursor)
    elif choice == "6":
        search_users(cursor)
    elif choice == "-1" or choice == "exit":
        system('clear')
        exit()
    elif choice == "-2":
        about()
        main_menu(cursor)
    else:
        system('clear')
        print("You've made an invalid input.")
        main_menu(cursor)

def device_name_menu(cursor):
    if opts.name:
        name = opts.name
    else:
        system('clear')
        name = raw_input("Device Name: ")
    cmd = 'SELECT name FROM resources'
    data = execute_cmd(cursor, cmd)
    if opts.quiet:
        pass
    elif opts.comma:
        pass
    else:
        print ("%40s %8s %20s %20s %20s %15s") % ("Name", "Location", "Console", "Power 1", "Power 2", "Family")
    for line in data:
        for item in line:
            if name.lower() in item.lower():
                cmd = "SELECT name, location, console, power1, power2, family FROM resources WHERE name='%s'" % item
                device = execute_cmd(cursor, cmd)
                if opts.comma:
                    print ("%s,%s,%s,%s,%s,%s") % (device[0][0], device[0][1], device[0][2], device[0][3], device[0][4], device[0][5])
                else:
                    print ("%40s %8s %20s %20s %20s %15s") % (device[0][0], device[0][1], device[0][2], device[0][3], device[0][4], device[0][5])
    if opts.name:
        exit()
    choice = raw_input("Press Enter to continue:")
    system('clear')
    main_menu(cursor)

def device_type_menu(cursor):
    system("clear")
    final_list = []
    namel, locationl, mgmtl, p1l, p2l, familyl = 12, 12, 12, 12, 12, 12
    choice = raw_input("""Please Select one of the following types of epuiptment:

    1. Appliance
    2. Blade
    3. Chassis
    4. Thermal Chamber
    5. IXIA
    6. Lab Gear

    Choice: """)

    if choice == "1":
        data = execute_cmd(cursor, "SELECT name, location, console, power1, power2, family FROM resources WHERE type='1' AND status='a'")
    elif choice == "2":
        data = execute_cmd(cursor, "SELECT name, location, console, power1, power2, family FROM resources WHERE type='2' AND status='a'")
    elif choice == "3":
        data = execute_cmd(cursor, "SELECT name, location, console, power1, power2, family FROM resources WHERE type='3' AND status='a'")
    elif choice == "4":
        data = execute_cmd(cursor, "SELECT name, location, console, power1, power2, family FROM resources WHERE type='4' AND status='a'")
    elif choice == "5":
        data = execute_cmd(cursor, "SELECT name, location, console, power1, power2, family FROM resources WHERE type='5' AND status='a'")
    elif choice == "6":
        data = execute_cmd(cursor, "SELECT name, location, console, power1, power2, family FROM resources WHERE type='6' AND status='a'")
    else:
        print ("Invalid choice!")
        device_type_menu(cursor)

    for line in data:
        name, location, console, power1, power2, family = line[0], line[1], line[2], line[3], line[4], line[5]
        try:
            if len(name) > namel:
                namel = len(name)
        except:
            pass
        try:
            if len(location) > locationl:
                locationl = len(location)
        except:
            pass
        try:
            if len(console) > mgmtl:
                mgmtl = len(console)
        except:
            pass
        try:
            if len(power1) > p1l:
                p1l = len(power1)
        except:
            pass
        try:
            if len(power2) > p2l:
                p2l = len(power2)
        except:
            pass
        try:
            if len(family) > familyl:
                familyl = len(family)
        except:
            pass
        info = [name, location, console, power1, power2, family]
        final_list.append(info)
    final_list.sort()

    if opts.quiet:
        pass
    elif opts.comma:
        pass
    else:
        print('%'+str(namel)+'s %'+str(locationl)+'s %'+str(mgmtl)+'s %'+str(p1l)+'s %'+str(p2l)+'s %'+str(familyl)+'s') % ("Name", "Location", "Management", "Power 1", "Power 2", "Family\n")

    for line in final_list:
        if opts.comma:
            print('%s,%s,%s,%s,%s,%s') % (line[0], line[1], line[2], line[3], line[4], line[5])
        else:
            print('%'+str(namel)+'s %'+str(locationl)+'s %'+str(mgmtl)+'s %'+str(p1l)+'s %'+str(p2l)+'s %'+str(familyl)+'s') % (line[0], line[1], line[2], line[3], line[4], line[5])

    choice = raw_input("Press 1 to search list, or press Enter to Continue: ")
    if choice == "1":
        term = raw_input("Enter a Search Term: ")
        for line in final_list:
            for item in line:
                try:
                    if term in item:
                        print('%'+str(namel)+'s %'+str(locationl)+'s %'+str(mgmtl)+'s %'+str(p1l)+'s %'+str(p2l)+'s %'+str(familyl)+'s') % (line[0], line[1], line[2], line[3], line[4], line[5])
                except:
                    pass
        raw_input("Press Enter to Continue: ")
        system("clear")
        main_menu(cursor)
    else:
        system('clear')
        main_menu(cursor)

def active_devices_menu(cursor):
    if opts.active:
        pass
    else:
        system('clear')
    final_list = []
    namel, locationl, mgmtl, p1l, p2l, familyl = 12, 12, 12, 12, 12, 12
    devices = execute_cmd(cursor, "SELECT name, location, console, power1, power2, family FROM resources WHERE status='a'")
    for line in devices:
        name, location, console, power1, power2, family = line[0], line[1], line[2], line[3], line[4], line[5]
        try:
            if len(name) > namel:
                namel = len(name)
        except:
            pass
        try:
            if len(location) > locationl:
                locationl = len(location)
        except:
            pass
        try:
            if len(console) > mgmtl:
                mgmtl = len(console)
        except:
            pass
        try:
            if len(power1) > p1l:
                p1l = len(power1)
        except:
            pass
        try:
            if len(power2) > p2l:
                p2l = len(power2)
        except:
            pass
        try:
            if len(family) > familyl:
                familyl = len(family)
        except:
            pass
        info = [name, location, console, power1, power2, family]
        final_list.append(info)
    final_list.sort()

    if opts.quiet:
        pass
    elif opts.comma:
        pass
    else:
        print('%'+str(namel)+'s %'+str(locationl)+'s %'+str(mgmtl)+'s %'+str(p1l)+'s %'+str(p2l)+'s %'+str(familyl)+'s') % ("Name", "Location", "Console", "Power 1", "Power 2", "Family\n")

    for line in final_list:
        if opts.comma:
            print('%s,%s,%s,%s,%s,%s') % (line[0], line[1], line[2], line[3], line[4], line[5])
        else:
            print('%'+str(namel)+'s %'+str(locationl)+'s %'+str(mgmtl)+'s %'+str(p1l)+'s %'+str(p2l)+'s %'+str(familyl)+'s') % (line[0], line[1], line[2], line[3], line[4], line[5])
    if opts.active:
        exit()
    choice = raw_input("Press 1 to search list, or press Enter to Continue: ")
    if choice == "1":
        term = raw_input("Enter a Search Term: ")
        for line in final_list:
            for item in line:
                try:
                    if term in item:
                        print('%'+str(namel)+'s %'+str(locationl)+'s %'+str(mgmtl)+'s %'+str(p1l)+'s %'+str(p2l)+'s %'+str(familyl)+'s') % (line[0], line[1], line[2], line[3], line[4], line[5])
                except:
                    pass
        raw_input("Press Enter to Continue: ")
        system("clear")
        main_menu(cursor)
    else:
        system('clear')
        main_menu(cursor)

def current_reservations_menu(cursor):
    if opts.reservations:
        pass
    else:
        system('clear')
    namel, locationl, mgmtl, unamel, sdatel, edatel = 0, 0, 0, 0, 0, 0
    final_list = []
    cmd = "SELECT resid, machid, start_date, end_date, starttime, endtime FROM reservations WHERE start_date<'%s' and end_date>'%s'" % (epoch, epoch)
    reservations = execute_cmd(cursor, cmd)
    for line in reservations:
        resid, machid, startdate, enddate = line[0], line[1], line[2] + line[4], line[3] + line[5]
        cmd = "SELECT name, location, console FROM resources WHERE machid='%s' AND status='a'" % machid
        resources = execute_cmd(cursor, cmd)
        cmd = "SELECT memberid FROM reservation_users WHERE resid='%s'" % resid
        memid = execute_cmd(cursor, cmd)
        memberid = memid[0][0]
        cmd = "SELECT fname, lname, email FROM login WHERE memberid='%s'" % memberid
        login = execute_cmd(cursor, cmd)
        try:
            name, location, console, uname = resources[0][0], resources[0][1], resources[0][2], login[0][0]+" "+login[0][1]
        except:
            name, location, console, uname = "UH-OH", "ERROR - INVALID USER", "WHOEVER IS USING THIS", "SHOULD NOT BE!"
        try:
            email = login[0][2]
        except:
            email = "void"
        try:
            if len(name) > namel:
                namel = len(name)
        except:
            pass
        try:
            if len(location) > locationl:
                locationl = len(location)
        except:
            pass
        try:
            if len(console) > mgmtl:
                mgmtl = len(console)
        except:
            pass
        try:
            if len(uname) > unamel:
                unamel = len(uname)
        except:
            pass
        startdate = datetime.datetime.fromtimestamp(startdate)
        enddate = datetime.datetime.fromtimestamp(enddate)
        info = [name, location, console, uname, startdate, enddate, email]
        final_list.append(info)
    final_list.sort()
    if opts.quiet:
        pass
    elif opts.comma:
        pass
    elif opts.email:
        print('%'+str(namel)+'s %'+str(locationl)+'s %'+str(mgmtl)+'s %'+str(unamel)+'s %20s %20s %20s') % ("Name", "Location", "Console", "User's Name", "Start Time", "End Time", "E-Mail\n")
    else:
        print('%'+str(namel)+'s %'+str(locationl)+'s %'+str(mgmtl)+'s %'+str(unamel)+'s %20s %20s') % ("Name", "Location", "Console", "User's Name", "Start Time", "End Time\n")
    for line in final_list:
        if opts.comma and opts.email:
            print('%s,%s,%s,%s,%s,%s,%s') % (line[0], line[1], line[2], line[3], line[4], line[5], line[6])
        elif opts.comma:
            print('%s,%s,%s,%s,%s,%s') % (line[0], line[1], line[2], line[3], line[4], line[5])
        elif opts.email:
            print('%'+str(namel)+'s %'+str(locationl)+'s %'+str(mgmtl)+'s %'+str(unamel)+'s %20s %20s %20s') % (line[0], line[1], line[2], line[3], line[4], line[5], line[6])
        else:
            print('%'+str(namel)+'s %'+str(locationl)+'s %'+str(mgmtl)+'s %'+str(unamel)+'s %20s %20s') % (line[0], line[1], line[2], line[3], line[4], line[5])
    if opts.reservations:
        exit()
    else:
        choice = "1"
    while choice == "1":
        choice = raw_input("Press 1 to search list, or press Enter to Continue: ")
        if choice == "1":
            term = raw_input("Enter a Search Term: ")
            for line in final_list:
                for item in line:
                    try:
                        if term in item:
                            print('%'+str(namel)+'s %'+str(locationl)+'s %'+str(mgmtl)+'s %'+str(unamel)+'s %20s %20s') % (line[0], line[1], line[2], line[3], line[4], line[5])
                    except:
                        pass
    system('clear')
    main_menu(cursor)

def location_menu(cursor):
    if opts.location:
        pass
    else:
        system('clear')
    devices, final_list = [], []
    namel, locationl, mgmtl, p1l, p2l, familyl = 12, 12, 12, 12, 12, 12
    if opts.location:
        location = opts.location
    else:
        location = raw_input("Please Enter a Location: ")
    location_list = execute_cmd(cursor, "SELECT location FROM resources WHERE status='a'")
    ll_final = []
    for item in location_list:
        if item in ll_final:
            pass
        else:
            ll_final.append(item)
    for item in ll_final:
        lcase = str(item[0]).lower()
        if location.lower() in lcase:
            try:
                cmd = """SELECT name, location, console, power1, power2, family, machid FROM resources WHERE location="%s" AND status='a' """ % item
                datainfo = execute_cmd(cursor, cmd)
                for line in datainfo:
                    line = list(line)
                    cmd = "SELECT resid, start_date, end_date, endtime FROM reservations WHERE machid='%s'" % (line[6])
                    data = execute_cmd(cursor, cmd)
                    xyz = 0
                    for stub in data:
                        if (int(stub[1]) < epoch) and ((int(stub[2]) + (int(stub[3])*60)) > epoch):
                            cmd = "SELECT memberid FROM reservation_users WHERE resid='%s'" % stub[0]
                            memid = execute_cmd(cursor, cmd)
                            cmd = "SELECT fname, lname, email FROM login WHERE memberid='%s'" % memid[0][0]
                            login = execute_cmd(cursor, cmd)
                            holder = login[0][0] + " " + login[0][1]
                            email = login[0][2]
                            line.append(holder)
                            line.append(email)
                            devices.append(line)
                            xyz = 1
                    if xyz != 1:
                        line.append("No Current Reservation")
                        devices.append(line)
            except:
                pass



    for line in devices:
        name, location, console, power1, power2, family, holder = line[0], line[1], line[2], line[3], line[4], line[5], line[7]
        try:
            if len(name) > namel:
                namel = len(name)
        except:
            pass
        try:
            if len(location) > locationl:
                locationl = len(location)
        except:
            pass
        try:
            if len(console) > mgmtl:
                mgmtl = len(console)
        except:
            pass
        try:
            if len(power1) > p1l:
                p1l = len(power1)
        except:
            pass
        try:
            if len(power2) > p2l:
                p2l = len(power2)
        except:
            pass
        try:
            if len(family) > familyl:
                familyl = len(family)
        except:
            pass
        info = [name, location, console, power1, power2, family, holder]
        final_list.append(info)
    final_list.sort()

    final_final_list = []

    for item in final_list:
        if item in final_final_list:
            pass
        else:
            final_final_list.append(item)

    if opts.quiet:
        pass
    if opts.comma:
        pass
    else:
        print('%'+str(namel)+'s %'+str(locationl)+'s %'+str(mgmtl)+'s %'+str(p1l)+'s %'+str(p2l)+'s %'+str(familyl)+'s %s') % ("Name", "Location", "Console", "Power 1", "Power 2", "Family", "Reservation\n")

    for line in final_final_list:
        if opts.comma:
            print('%s,%s,%s,%s,%s,%s,%s') % (line[0], line[1], line[2], line[3], line[4], line[5], line[6])
        else:
            print('%'+str(namel)+'s %'+str(locationl)+'s %'+str(mgmtl)+'s %'+str(p1l)+'s %'+str(p2l)+'s %'+str(familyl)+'s %s') % (line[0], line[1], line[2], line[3], line[4], line[5], line[6])
    if opts.location:
        exit()
    choice = raw_input("Press 1 to search list, or press Enter to Continue: ")
    if choice == "1":
        term = raw_input("Enter a Search Term: ")
        for line in final_final_list:
            for item in line:
                try:
                    if term in item:
                        print('%'+str(namel)+'s %'+str(locationl)+'s %'+str(mgmtl)+'s %'+str(p1l)+'s %'+str(p2l)+'s %'+str(familyl)+'s %s') % (line[0], line[1], line[2], line[3], line[4], line[5], line[6])
                except:
                    pass
        raw_input("Press Enter to Continue: ")
        system("clear")
        main_menu(cursor)
    else:
        system('clear')
        main_menu(cursor)

def search_users(cursor):
    if opts.user:
        pass
    else:
        system('clear')
    data = execute_cmd(cursor, "SELECT email, fname, lname, phone, position, logon_name, is_admin FROM login")
    if opts.user:
        key = opts.user
    else:
        key = raw_input("Please enter your keyword: ")
    results = []
    for line in data:
        x = 0
        for item in line:
            if x == 0:
                if key.lower() in str(item).lower():
                    results.append(line)
                    x = 1
    print("%25s %12s %15s %16s %30s %16s %10s") % ("e-mail", "First Name", "Last Name", "Phone Number", "Position", "Logon Name", "Status\n")
    for line in results:
        if line[6] == 1:
            status = "admin"
        else:
            status = "user"
        print("%25s %12s %15s %16s %30s %16s %10s") % (line[0], line[1], line[2], line[3], line[4], line[5], status)
    if opts.user:
        exit()
    else:
        raw_input("Press Enter to continue:")
        system('clear')
        main_menu(cursor)

def execute_cmd(cursor, cmd):
    cursor.execute(cmd)
    data = cursor.fetchall()
    return data

def fail(reason):
    print ("Larson has failed because he " + reason)
    exit()

def about():
    system('clear')
    raw_input("""Originally created as a small yet handy tool, I developed it further,
adding in command line functionality, tweaks and improvements,
until it eventually became the program you're using now. I can't
promise that it will hold forever. Code versions change, databases
become corrupted, and time goes on, but I hope this program has in
some way been of use to you.

Thank you for using,

-Dennis Sauve, 2012


Press Enter to Return to the Main Menu...
""")
    system('clear')

main()