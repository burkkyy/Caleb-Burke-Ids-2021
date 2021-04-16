import network

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

def printCommands(cmds):
    print("\nCOMMANDS:")
    for command in cmds.keys():
        print(f"'{command}'")

def main():
    # Start the network
    net = network.BlockchainNetwork()
    net.start()

    # Initialize user commands as callable funcs in dict commands
    commands = {
        "activeConns": lambda: printConns(net),
        "printChain": net.ledger.print_chain,
        "printChainInfo": net.ledger.printChainInfo,
        "printPendingIdentities": lambda: printPendingIdentities(net),
        "help": lambda: printCommands(commands)
    }

    print("TYPE Q OR QUIT ANYWHERE AND ENTER TO CLEAN EXIT, IGNORE ANNYOING PRINTS")
    print("TYPE HELP FOR LIST OF ALL COMMANDS")
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
