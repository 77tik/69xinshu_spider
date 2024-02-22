import requests


def do_request(url, headers, method="GET"):

    res = requests.request(method=method, url=url,headers=headers)
    if res.ok:
        return res
    else:
        raise Exception(res.text)