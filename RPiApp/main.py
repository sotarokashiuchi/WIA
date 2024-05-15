import requests

def requestNFCToch(serialNumber):
    response = requests.post(
            "http://localhost:1234/nfc/touch",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"serialNumber": serialNumber}
    )

    return response.json()["name"]

print(requestNFCToch("1"))

