import base64
import os
import requests
import json
import datetime
import subprocess
from fake_useragent import UserAgent
from capsolver_test import solve_hcaptcha
from faker import Faker

fake = Faker()

ua = UserAgent()
DIGITALOCEAN_TOKEN = "dop_v1_2bfbbd8de79e10a9cde7967e5d8d17813be02fe07f8c7742aef19fe86f569ea7"


def get_countries():
    url = "https://api2.e-konsulat.gov.pl/api/slownikiekonsulat/kraje/2"

    payload = {}
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://secure2.e-konsulat.gov.pl',
        'Referer': 'https://secure2.e-konsulat.gov.pl/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()


def check_visa():
    url = "https://api2.e-konsulat.gov.pl/api/rezerwacja-wizyt-wizowych/terminy/1105"
    token = solve_hcaptcha()
    payload = json.dumps(
        {
            "token": token["gRecaptchaResponse"],
        }
    )
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Origin": "https://secure2.e-konsulat.gov.pl",
        "Referer": "https://secure2.e-konsulat.gov.pl/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.json())
    return response.json()


def book_visa():
    visa = check_visa()
    if visa.get("reason") and visa["reason"] == "LIMIT_Z_JEDNEGO_IP_PRZEKROCZONY":
        create_droplet()
        ip_addresses = droplets[0]['networks']['v4']
        for ip in ip_addresses:
            if ip['type'] == 'public':
                build_docker_in_server(ip_address=ip['ip_address'])
        return None
    elif not visa["tabelaDni"]:
        return None
    url = "https://api2.e-konsulat.gov.pl/api/rezerwacja-wizyt-wizowych/rezerwacje"

    payload = json.dumps(
        {
            "data": visa["tabelaDni"][0],
            "id_lokalizacji": 1105,
            "id_wersji_jezykowej": 2,
            "token": visa["token"],
        }
    )
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Origin": "https://secure2.e-konsulat.gov.pl",
        "Referer": "https://secure2.e-konsulat.gov.pl/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": ua.random,
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.json())
    return response.json()


def fill_form():
    bilet = book_visa()
    if bilet:
        url = "https://api2.e-konsulat.gov.pl/api/formularze/dane-wizowy/zapisz-krajowa"

        payload = json.dumps(
            {
                "bilet": bilet["bilet"],
                "idWersjiJezykowej": 2,
                "daneFormularza": {
                    "nazwisko": fake.last_name(),
                    "nazwiskoRodowe": fake.last_name(),
                    "imiona": fake.first_name(),
                    "dataUrodzenia": fake.date(),
                    "miejsceUrodzenia": fake.city(),
                    "krajUrodzenia": "ANDORRA",
                    "krajUrodzeniaICAO": "AND",
                    "posiadaneObywatelstwo": "ANDORRA",
                    "posiadaneObywatelstwoICAO": "AND",
                    "obecneObywatelstwo": "ANGUILLA",
                    "obecneObywatelstwoICAO": "AIA",
                    "plec": "M",
                    "stanCywilny": "KP",
                    "numerDowodu": fake.passport_number(),
                    "rodzajDokumentuPodrozy": 1,
                    "numerPaszportu": fake.passport_number(),
                    "dokumentPodrozyWydanyDnia": fake.date_between(
                        start_date="-1m", end_date="-5d"
                    ).strftime("%Y-%m-%d"),
                    "dokumentPodrozyWaznyDo": fake.date_between(
                        start_date="+2d", end_date="+1m"
                    ).strftime("%Y-%m-%d"),
                    "dokumentPodrozyWydanyPrzez": fake.company_suffix(),
                    "opiekunowie": [],
                    "osoba": {
                        "osobaPanstwoICAO": "AND",
                        "osobaStanProwincja": fake.street_name(),
                        "osobaMiejscowosc": fake.city(),
                        "osobaKodPocztowy": fake.postcode(),
                        "osobaAdres": fake.building_number(),
                        "eMail": fake.email(),
                        "numerTelefonuPrefix": fake.country_calling_code(),
                        "numerTelefonuNumer": fake.msisdn(),
                    },
                    "pracodawca": {
                        "wykonywanyZawodKod": "33",
                        "panstwoICAO": "AIA",
                        "stanProwincja": fake.street_name(),
                        "miejscowosc": fake.city(),
                        "kodPocztowy": fake.postcode(),
                        "adres": fake.building_number(),
                        "prefixTelefonu": fake.country_calling_code(),
                        "numerTelefonu": fake.msisdn(),
                        "nazwa": fake.company(),
                    },
                    "celPodrozy": [1],
                    "podroz": {
                        "krajDocelowyICAO": "POL",
                        "pierwszyWjazdICAO": "AUT",
                        "iloscWjazdow": 1,
                        "okresPobytu": 91,
                        "dataPierwszegoWjazdu": fake.date_between(
                            start_date="+1m", end_date="+2m"
                        ).strftime("%Y-%m-%d"),
                        "dataWyjazdu": fake.date_between(
                            start_date="+3m", end_date="+6m"
                        ).strftime("%Y-%m-%d"),
                    },
                    "poprzednieWizy": [],
                    "czyPobieranoOdciskiPalcow": False,
                    "koszty": {
                        "sponsor": False,
                        "czySponsorujeOsobaPrzyjmujaca": False,
                        "czySponsorujeInnaOsoba": False,
                        "czyGotowka": True,
                        "czyCzeki": False,
                        "czyKarty": False,
                        "czyZakwaterowanie": False,
                        "czyTransport": False,
                        "czyPokrywaKoszty": False,
                        "czyInne": False,
                        "ubezpieczenieWazneDo": "",
                    },
                },
                "rodzajUslugi": 1,
            }
        )
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://secure2.e-konsulat.gov.pl",
            "Referer": "https://secure2.e-konsulat.gov.pl/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": ua.random,
            "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.json())
        return response.json()


def print_pdf():
    form = fill_form()
    if form and form['guid']:
        url = f"https://api2.e-konsulat.gov.pl/api/formularze/pdf-wizowe/{form['guid']}"

        payload = {}
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Origin": "https://secure2.e-konsulat.gov.pl",
            "Referer": "https://secure2.e-konsulat.gov.pl/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            # 'Cookie': 'AGAffinityCookieForSecure2=31dbc1778a2b3747dd6a591aeb16ed41; AGAffinityCookieForSecure2CORS=31dbc1778a2b3747dd6a591aeb16ed41'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.ok:
            pdf = response.json()["pdf"]
            file_name = response.json()["numerFormularza"]
            data = base64.b64decode(pdf)
            MEDIA_ROOT = "/home/vusallyv/Projects/visa-poland/media"
            if not os.path.exists(MEDIA_ROOT):
                os.mkdir(MEDIA_ROOT)
            with open(f"{MEDIA_ROOT}/{file_name}.pdf", "wb") as f:
                f.write(data)
        return response.json()
    else:
        return "Something went wrong"


def perfom_actions_in_droplet(droplet_id, payload):
    url = f"https://api.digitalocean.com/v2/droplets/{droplet_id}/actions"

    payload = payload
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DIGITALOCEAN_TOKEN}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()


def list_snapshots():
    url = "https://api.digitalocean.com/v2/snapshots?page=1&per_page=100&resource_type=droplet"

    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DIGITALOCEAN_TOKEN}',
        'Cookie': '__cf_bm=cdpIbopDS8URF3z860JeWZIMXRcJwlk9OM3cKCzpJNQ-1693940890-0-ASPz4zdcyFtNvJk1U6V9pubdUibAv+rJM01/ufpDzzLgbym+WkE8oIhmiYjJdygx9X8f8dezFfqkemjs8WkXYXu78/R3v6nvqJ7ERzqgYDac'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()


def list_droplets():
    url = "https://api.digitalocean.com/v2/droplets?page=1&per_page=100&tag_name=polandvisa"

    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DIGITALOCEAN_TOKEN}',
        'Cookie': '__cf_bm=TcCun9YTplo5BbPreXPbH2NdK4LaPVGD4osefymyU3k-1693942217-0-AXWxcxoQgEBVvVyzdgFGhXbtb11PgU/CfPKX208GsaHMLky/5qCwBMZuNpWYLLwxh33p6FkDBQHHxgunF0lHO2dEcOt7ulRYjsrC796PNvav'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    droplets = sorted(response.json()['droplets'],
                      key=lambda droplet: droplet["created_at"])
    return droplets


def create_ssh_key():
    url = "https://api.digitalocean.com/v2/account/keys"

    payload = json.dumps({
        "name": snapshot_name,
        "public_key": ssh_key
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DIGITALOCEAN_TOKEN}',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()


def create_droplet():
    snapshots = list_snapshots()
    generated_ssh_key = create_ssh_key()
    url = "https://api.digitalocean.com/v2/droplets"

    payload = json.dumps({
        "name": f"polandvisa-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}",
        "region": "fra",
        "size": "s-1vcpu-1gb",
        "image": snapshots["snapshots"][0]["id"],
        "ssh_keys": [
            generated_ssh_key["ssh_key"]["id"],
            generated_ssh_key["ssh_key"]["fingerprint"]
        ],
        "backups": False,
        "ipv6": True,
        "monitoring": True,
        "tags": [
            "polandvisa"
        ],
        "user_data": "#cloud-config\nruncmd:\n  - touch /test.txt\n",
        "vpc_uuid": "8f7bd01a-1216-4a8b-935f-881dfc752040"
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DIGITALOCEAN_TOKEN}',
        'Cookie': '__cf_bm=Z0sxIRE1ueAAqEM7TMMfsuGuvyFaW61A2flnWIZJrsc-1693938960-0-AXwXI75MYFxIpSGgBvqukJSVzTlR/6Nfr4Cd2MuaDBrtFvcsVo5W8ljuIglc3zLNNfWTNG1BZBF5jobMHiyOICjAnNP3a7mdRBvBvt3RZTcR'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()


def build_docker_in_server(ip_address):
    print(ip_address)
    subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no",
                   f"root@{ip_address}", "cd /var/www/rezneed-b2b-backend; docker-compose down; docker-compose up -d --build"])


subprocess.run(["ssh-keygen", "-q", "-t", "rsa", "-N", "''",
               "-f", "~/.ssh/id_rsa", "<<<y", ">/dev/null", "2>&1"])
path = '~/.ssh/id_rsa.pub'
cmd = 'cat ' + os.path.expanduser(path)
output = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
response = output.communicate()
ssh_key = response[0].decode("utf-8")
droplets = list_droplets()
snapshot_name = f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
perfom_actions_in_droplet(droplet_id=droplets[0]['id'], payload={
                          "type": "snapshot", "name": f"{snapshot_name}"})

while True:
    print_pdf()
