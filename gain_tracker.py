""" The gain_tracker module calculates the gain from a series of trades exported from Coinbase in CSV format

Options
-------
--filename
    The name of the CSV file placed in the same folder as gain_tracker.py
    default: trades.csv

--debug
    If true, run in debug mode
    default: False

"""
import csv
import argparse
from collections import deque

EPSILON = 1.0e-14


def main(filename, debug):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        last_trade_id = 0
        gain = 0.0
        fees = 0.0
        buys = deque()
        for row in reader:
            if debug:
                print()

            trade_id, side, size, price, fee = int(row['trade id']), row['side'], float(row['size']), float(row['price']), float(row['fee'])
            if trade_id < last_trade_id:
                print("Trades out of order. ", last_trade_id, trade_id)
            last_trade_id = trade_id

            fees += fee

            if debug:
                print("Current trade:                  ", trade_id, side, size, price)

            if side == 'BUY':
                buy_quantity = size
                buy_price = price
                buys.append((buy_quantity, buy_price))
                if debug:
                    print("Past buys for calculating gain: ", buys)
                    print("Cumulative gain:                ", gain)

            elif side == 'SELL':
                sale_quantity = size
                sale_price = price
                while sale_quantity>0.0 :
                    if sale_quantity < EPSILON:
                        if debug:
                            print("sale_quantity: ", sale_quantity)
                        break
                    if len(buys) == 0:
                        print(("There is not enough of a buy history in order to "
                              "calculate the gain from the current sale of quantity: "),
                              sale_quantity)
                        print("Gain calculation aborted.")
                        return

                    (buy_quantity, buy_price) = buys.popleft()
                    if buy_quantity >= sale_quantity:
                        gain += (sale_price - buy_price) * sale_quantity
                        buy_quantity -= sale_quantity
                        sale_quantity = 0.0
                        if buy_quantity > 0.0:
                            buys.appendleft((buy_quantity, buy_price))
                    else:
                        gain += (sale_price - buy_price) * buy_quantity
                        sale_quantity -= buy_quantity

                if debug:
                    print("Past buys for calculating gain: ", buys)
                    print("Cumulative gain:                ", gain)

            else:
                print("There's a trade in the data for which the 'side' was neither BUY nor SELL but was: ", side)
                print("Gain calculation aborted.")
                return

        print()
        print("Gain: ", round(gain, 2))
        print("Fees: ", round(fees, 2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Calculate gains from a CSV file - FIFO")
    parser.add_argument('--filename', default='trades.csv')
    parser.add_argument('--debug', type=bool, default=False)
    args = parser.parse_args()
    main(args.filename, args.debug)