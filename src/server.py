from os import system, name
import network

def clear():  # to clear the console screen
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

def checkNetwork(net):
    net.sendToAllNetwork(None, network.STATUS_MESSAGE)

def printConns(net):
    conns = net.get_conns()
    if conns:
        for conn in conns:
            print(conn)
    else:
        print("No Connections")

def printPendingIdentities(net):
    if net.ledger.pending_identities:
        for iden in net.ledger.pending_identities:
            print(iden.to_string())
    else:
        print("None")

def deletePendingIdentities(net):
    print("Are you sure?")
    userIn = input("[Y/n]: ")
    while not userIn in ('y', 'Y', 'n', ''):
        print(userIn)
        userIn = input("[Y/n]: ")
    if userIn != 'n':
        net.ledger.pending_identities = []
        print("Successfully deleted all pending identities, change will save on exit")
    else:
        print("Deletion canceled")

def printCommands(cmds):
    print("\nCOMMANDS:")
    for command in cmds.keys():
        print(f"'{command}'")

def main():
    # Start the network
    net = network.BlockchainNetwork()
    net.start()
    clear()

    # Initialize user commands as callable funcs in dict commands
    commands = {
        "whoIsUp": lambda: checkNetwork(net),
        "connections": lambda: printConns(net),
        "chain": net.ledger.print_chain,
        "chainInfo": net.ledger.printChainInfo,
        "pendingIdentities": lambda: printPendingIdentities(net),
        "clearOutPendingIdentities": lambda: deletePendingIdentities(net),
        "mine": net.mineBlock,
        "clear": clear,
        "cls": clear,
        "help": lambda: printCommands(commands)
    }

    print(
        "Welcome to Caleb's Facial Recognition Blockchain System", 
        "\nfor list of all commands type help, type q or Q or quit to exit out of the program",
    )
    cmd = input(">>> ")
    while not cmd.lower() in ("q", "quit", "close"):
        try:
            commands[cmd]()
        except KeyError:
            print(f"[CONSOLE] Invalid command: '{cmd}'")
        cmd = input(">>> ")    
    net.close()

if __name__ == '__main__':
    main()
