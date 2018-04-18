import requests


class NSO(object):

    def __init__(self, ip='localhost', username='admin', password='admin',
                 port=8080, ssl=False):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        if ssl:
            scheme = "https"
        else:
            scheme = "http"
        self.base_url = "{}://{}:{}".format(scheme, self.ip, self.port)

    @property
    def headers(self):
        headers = {
            'Content-Type': "application/vnd.yang.data+json",
            'Accept': "application/vnd.yang.collection+json,"
                      "application/vnd.yang.data+json"
            }
        return headers

    def _utf8_encode(self, obj):
        if obj is None:
            return None
        if type(obj) is unicode: # noqa
            return obj.encode('utf-8')
        if type(obj) is list:
            return [self._utf8_encode(value) for value in obj]
        if type(obj) is dict:
            obj_dest = {}
            for key, value in obj.iteritems():
                if 'EXEC' not in key:
                    obj_dest[self._utf8_encode(key)] = self._utf8_encode(value)
            return obj_dest
        return obj

    def get(self, uri):
        url = self.base_url + uri

        response = requests.get(url,
                                headers=self.headers,
                                auth=(self.username, self.password))
        if response.ok:
            return response
        else:
            response.raise_for_status()

    def post(self, uri, data=None):
        url = self.base_url + uri

        response = requests.post(url,
                                 headers=self.headers,
                                 auth=(self.username, self.password))
        if response.ok:
            return response
        else:
            response.raise_for_status()

    def sync_from(self, device=None):
        if device:
            raise NotImplementedError
        else:
            url = "/api/config/devices/_operations/sync-from"
            resp = self.post(url)
            return resp.json()

    def get_device_config(self, device):
        """
        gets device configuration from NSO
        """
        url = '/api/config/devices/device/{}/config?deep'.format(device)
        resp = self.get(url)

        return self._utf8_encode(resp.json())

    def get_device_list(self):
        """
        returns a list of device names from NSO
        """
        url = "/api/running/devices/device"
        response = self.get(url)
        device_list = list()
        for d in response.json()["collection"]["tailf-ncs:device"]:
            device_list.append(d["name"])
        return device_list
