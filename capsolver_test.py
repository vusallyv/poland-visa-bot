import capsolver


capsolver.api_key = "CAP-984BC79804B845446BE80D8519078E6D"


def solve_hcaptcha():
    solution = capsolver.solve(
        {
            "type": "HCaptchaTaskProxyLess",
            "websiteURL": "https://secure2.e-konsulat.gov.pl/placowki/1105/wiza-krajowa/wizyty/weryfikacja-obrazkowa/",
            "websiteKey": "9f29f8f9-7a15-4e72-84d6-cb16261caeb4",
        }
    )
    print(solution)
    return solution
