# Copyright 2021 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module provides the methods to facilitate the API requests to the App Configuration service.
"""
import json as json_import
from typing import Optional, Union
from ibm_cloud_sdk_core import BaseService, DetailedResponse, ApiException
from .url_builder import URLBuilder
from .logger import Logger
from ibm_appconfiguration.version import __version__
from ..common import config_constants


class APIManager(BaseService):
    """The API Manager for the library"""

    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if APIManager.__instance is None:
            return APIManager()
        return APIManager.__instance

    def __init__(self):
        Logger.debug("Initialised _BaseRequest")

    def setup_base(self):
        """SetUp the Base class with service_url and authenticator"""
        BaseService.__init__(self,
                             service_url=URLBuilder.get_base_url(),
                             authenticator=URLBuilder.get_iam_authenticator())

    def prepare_api_request(self,
                            method: str,
                            url: str,
                            data: Optional[Union[str, dict]] = None) -> DetailedResponse:
        """ Prepare the API call request

        Args:
            method: Method for the request
            url: Url of the request
            data: data to be send.
        Returns:
            return the DetailedResponse.
        """

        headers = {}
        if data and isinstance(data, dict):
            data = self.__remove_null_values(data)
            headers['Content-Type'] = 'application/json'
            headers['User-Agent'] =  '{0}/{1}'.format(config_constants.SDK_NAME, __version__)
            data = json_import.dumps(data)

        try:
            request = self.prepare_request(method=method,
                                       url=url,
                                       headers=headers,
                                       data=data)
            response = self.send(request)
            return response
        except ApiException as api_exception:
            return DetailedResponse(response=None,
                                    headers=None,
                                    status_code=api_exception.code)
        except Exception as exception:
            Logger.debug(f'Error in service API call {str(exception)}')
            return DetailedResponse(status_code=400)

    def __remove_null_values(self, dictionary: dict) -> dict:
        """Create a new dictionary without keys mapped to null values.

        Args:
            dictionary: The dictionary potentially containing keys mapped to values of None.

        Returns:
            A dict with no keys mapped to None.
        """
        if isinstance(dictionary, dict):
            return {k: v for (k, v) in dictionary.items() if v is not None}
        return dictionary
