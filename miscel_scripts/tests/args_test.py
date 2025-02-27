import sys
import getopt


def myfunc(argv):
    arg_username = ""
    arg_clientname = ""
    arg_help = "{0} -u <username> -c <clientname> ".format(argv[0])
    
    try:
        opts, args = getopt.getopt(argv[1:], "hu:c:", ["help", "username=", "clientname="])
    except:
        print(arg_help)
        sys.exit(2)
        
        
    if not opts:
        print(arg_help)
        sys.exit(2)
    
    for opt, arg in opts:
        
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-u", "--username"):
            arg_username = arg
        elif opt in ("-c", "--clientname"):
            arg_clientname = arg

    return {'username': arg_username, 'clientname':arg_clientname}



if __name__ == "__main__":
    arg_dict = myfunc(sys.argv)
    print(arg_dict)