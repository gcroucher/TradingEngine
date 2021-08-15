from trader import Trader
trader = Trader("chengduhunters", "NK225")

#TODO 

# "HOTLOOP"
while True:
    response = trader.get_top_level()
    print(f"My active orders: {trader.order_store}")
    print(f"Top level of market is {response.json()}")

    text = input("Awaiting input in format 'BUY/SELL 5 @ 50': ")
    try:
        args = text.split()
        print(f"You want to {args[0]} {int(args[1])} {args[2]} {int(args[3])}")
    except (IndexError, ValueError) as e:
        print(f"Please enter in valid format, {e}")
        continue
    isbid = 1 if args[0] == "BUY" else 0
    volume = int(args[1])
    price = int(args[3])

    response = trader.place_order(isbid, volume, price)
    print(f"Response: {response.status_code}")
    print()