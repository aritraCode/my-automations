from tradingview_ta import TA_Handler
from datetime import datetime
import requests
import json
import pytz
import os

DBPATH = "./data_base.json"
LOGPATH = "./trade_log.txt"

def log_message(message):
    """Append a timestamped message to the trade log file."""
    with open(LOGPATH, "a") as f:
        f.write(f"[{date()}] {message}\n")


def load_position(filepath=DBPATH):
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {}
        for k, v in {"price": 0, "side": 0, "pl": 0}.items():
            if k not in data:
                data[k] = v
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"price": 0, "side": 0, "pl": 0}


def save(data, filepath=DBPATH):
    with open(filepath, "w") as f:
        json.dump(data, f)


def btc_data():
    try:
        handlar = TA_Handler(symbol="BTCUSD", exchange="BITSTAMP", screener="CRYPTO", interval="4h")
        analysis = handlar.get_analysis()
        if not analysis:
            return None, None
        signal = analysis.summary.get("RECOMMENDATION", None)
        price = analysis.indicators.get("close", None)
        return signal, price
    except Exception:
        return None, None


def date():
    return datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d/%m/%Y %A %H:%M:%S")


def send_report(message, signal, price, position):
    price_str = f"{price:.2f}" if isinstance(price, (int, float)) and price is not None else str(price)
    payload = f"""
[{date()}] {message}
signal, price = {signal}, {price_str}
position = {position}
"""
    try:
        url = os.getenv("URL")
        if isinstance(url, str) and url:
            response = requests.post(url=url, data=payload)
            response.raise_for_status()
            print(payload)
        else:
            print(payload)
    except requests.RequestException as e:
        print(f"Report send error: {e}")


def buy_sell():
    position = load_position()
    signal, price = btc_data()
    action_message = "No trade action"

    if signal is not None and price is not None:
        if signal in ["BUY", "STRONG_BUY"]:
            if position["side"] == 0:
                new_position = {"price": price, "side": 1, "pl": position["pl"]}
                save(new_position)
                action_message = f"Opened new LONG position at {price:.2f}"
            elif position["side"] == -1:
                pl = position["pl"] + round(((price - position["price"]) * position["side"]), 2)
                new_position = {"price": price, "side": 1, "pl": pl}
                save(new_position)
                action_message = f"Exited SHORT and entered LONG at {price:.2f}, P/L={pl:.2f}"

        elif signal in ["SELL", "STRONG_SELL"]:
            if position["side"] == 0:
                new_position = {"price": price, "side": -1, "pl": position["pl"]}
                save(new_position)
                action_message = f"Opened new SHORT position at {price:.2f}"
            elif position["side"] == 1:
                pl = position["pl"] + round(((price - position["price"]) * position["side"]), 2)
                new_position = {"price": price, "side": -1, "pl": pl}
                save(new_position)
                action_message = f"Exited LONG and entered SHORT at {price:.2f}, P/L={pl:.2f}"

    send_report(action_message, signal, price, str(load_position()))

    # Log the trade action
    if action_message:
        log_message(action_message)
    else:
        log_message(f"No trade action. Signal={signal}, price={price}")


if __name__ == "__main__":
    buy_sell()
