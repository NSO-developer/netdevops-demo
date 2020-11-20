"""
helpers/nso.py

A file that contains a couple of method to interact
via RESTCONF with a NSO instance.
"""
import requests


class NSO():
    """
    an instance of the NSO class allow to interact via RESTCONF API
    with a NSO instance for a couple of API endpoints:

    * sync_from - to sync-from all the devices or one device (the
                  second option is not Implemented)
    * get_device_config - to retrieve the config from one device
    * get_device_list - to retrieve the list of device names in the
                        NSO instance
    """

    def __init__(self, ip='localhost', username='admin', password='admin',
                 port=8080, ssl=False):
        """
        :param ip string: the IP address of the NSO instance
        :param username string: the username to use to connect to NSO
        :param password string: the password for the given username
        :param port int: the port on which RESTCONF is listening
        :param ssl bool: True for https - False for http
        """
        # Disabling too-many-argument
        # pylint: disable=R0913
        self.ip_addr = ip
        self.username = username
        self.password = password
        self.port = port
        if ssl:
            scheme = "https"
        else:
            scheme = "http"
        self.base_url = "{}://{}:{}".format(scheme, self.ip_addr, self.port)

    @property
    def headers(self):
        """
        Headers for every RESTCONF request
        """
        headers = {
            'Content-Type': "application/yang-data+json",
            'Accept': "application/yang-data+json"
            }
        return headers

    # Disabling inconsistent-return-statements as the raise_for_status
    # method hides the raise and pylint detect a warning
    def get(self, uri): # pylint: disable=R1710
        """
        Method that gets a URI, build the final URL
        and execute a GET request on the final URL.

        :param uri string: the URI to GET on the NSO instance
        :return requests.Response: the GET response
        :raises requests.HTTPError: if an error occured
        """
        url = self.base_url + uri

        response = requests.get(url,
                                headers=self.headers,
                                auth=(self.username, self.password))
        if response.ok:
            return response

        response.raise_for_status()

    # Disabling inconsistent-return-statements as the raise_for_status
    # method hides the raise and pylint detect a warning
    def post(self, uri, data=None): # pylint: disable=R1710
        """
        Method that gets a URI, build the final URL
        and execute a POST request on the final URL.

        Note: data is not used in this example

        :param uri string: the URI to POST on the NSO instance
        :param data: (optional) Dictionary, list of tuples, bytes,
                     or file-like object to send in the body of the
                     request
        :return requests.Response: the POST response
        :raises requests.HTTPError: if an error occured
        :raises NotImplementedError: if data is set this exception is
                                     raised.
        """
        if data:
            raise NotImplementedError

        url = self.base_url + uri

        response = requests.post(url,
                                 headers=self.headers,
                                 auth=(self.username, self.password))
        if response.ok:
            return response

        response.raise_for_status()

    def sync_from(self, device=None):
        """
        Run a sync-from action on either all devices in the NSO instance
        or the device passed as parameter.

        Note: the second option is not implemented

        :param device string: (optional) - the name of the device to run
                              sync-from. If not given then sync-from is
                              run on all devices on the NSO instance
        :raises NotImplementedError: if a device is given as parameter
                                     this exception is raised.
        """
        if device:
            raise NotImplementedError

        url = "/restconf/data/tailf-ncs:devices/sync-from"
        resp = self.post(url)
        return resp.json()

    def get_device_config(self, device):
        """
        Get the device configuration from NSO

        In RESTCONF need to add the query parameter content=config otherwise
        get also the operationnal data

        :param device string: the name of the device from which to retrieve
                              the configuration in NSO
        """
        url = '/restconf/data/tailf-ncs:devices/device={}/config?content=config'.format(device)
        resp = self.get(url)

        return resp.json()

    def get_device_list(self):
        """
        Get the list of device names from NSO
        """
        url = "/restconf/data/tailf-ncs:devices/device"
        response = self.get(url)
        device_list = list()
        for dev in response.json()["tailf-ncs:device"]:
            device_list.append(dev["name"])
        return device_list
