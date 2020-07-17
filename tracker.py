""" The tracker module calculates the gain from a series of trades exported from Coinbase in CSV format

Options
-------
--filename
    The name of the CSV file placed in the same folder as tracker.py
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
    with open(filename, newline='') as csv_file:

        reader = csv.DictReader(csv_file)
        last_trade_id = 0
        gain = 0.0
        fees = 0.0
        buys = deque()
        for row in reader:
            if debug:
                print()

            try:
                trade_id, side, quantity, price, fee = int(row['trade id']), row['side'], float(row['size']), float(row['price']), float(row['fee'])

                if debug:
                    print()
                    print("Current trade:                  ", trade_id, side, quantity, price)

                if trade_id < last_trade_id:
                    raise TradesOutOfOrderError
                last_trade_id = trade_id

                fees += fee

                gain = handle_trade(buys, gain, side, quantity, price)

                if debug:
                    print("Past buys for calculating gain: ", buys)
                    print("Cumulative gain:                ", gain)

            except InsufficientDataError as e:
                print(("There is not enough of a buy history in order to "
                       "calculate the gain from the current sale of quantity: "),
                      quantity)
                print("Gain calculation aborted.")
                return
            except TradesOutOfOrderError as e:
                print("Trades out of order. ", last_trade_id, trade_id)
                return
            except UnknownSideError as e:
                print("There's a trade in the data for which the 'side' was neither BUY nor SELL but was: ", side)
                print("Gain calculation aborted.")
                return
            except Exception as e:
                print("Exception: ", e)
                return

        print()
        print("Gain: ", round(gain, 2))
        print("Fees: ", round(fees, 2))


def handle_trade(buys, gain, side, quantity, price):
    if side == 'BUY':
        handle_buy(buys, quantity, price)

    elif side == 'SELL':
        gain = handle_sale(buys, gain, quantity, price)

    else:
        raise UnknownSideError

    return gain


def handle_sale(buys, gain, sale_quantity, sale_price):
    while sale_quantity > EPSILON:
        if len(buys) == 0:
            raise InsufficientDataError

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

    return gain


def handle_buy(buys, buy_quantity, buy_price):
    buys.append((buy_quantity, buy_price))


class InsufficientDataError(Exception):
    pass


class TradesOutOfOrderError(Exception):
    pass


class UnknownSideError(Exception):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Calculate gains from a CSV file - FIFO")
    parser.add_argument('--filename', default='trades.csv')
    parser.add_argument('--debug', type=bool, default=False)
    args = parser.parse_args()
    main(args.filename, args.debug)