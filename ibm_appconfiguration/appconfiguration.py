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
IBM Cloud App Configuration is a centralized feature management and configuration service on IBM Cloud
for use with web and mobile applications, microservices, and distributed environments.

Instrument your applications with App Configuration Python SDK, and use the App Configuration dashboard,
CLI or API to define feature flags or properties, organized into collections and targeted to segments.
Toggle feature flag states in the cloud to activate or deactivate features in your application or environment, when required.
You can also manage the properties for distributed applications centrally.
"""
from typing import Dict, Optional
from .configurations.internal.utils.validators import Validators
from .configurations.models import Feature, Property
from .configurations.internal.utils.logger import Logger
from .configurations.internal.common import config_messages
from .configurations.configuration_handler import ConfigurationHandler


class AppConfiguration:
    """ AppConfiguration class"""
    __instance = None

    # regions
    REGION_US_SOUTH = "us-south"
    REGION_EU_GB = "eu-gb"
    REGION_AU_SYD = "au-syd"
    override_server_host = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if AppConfiguration.__instance is None:
            return AppConfiguration()
        return AppConfiguration.__instance

    @staticmethod
    def enable_debug(enable: bool):
        """Set the logger in debug mode

        Args:
            enable: A boolean value to set the logger debug mode
        """
        Logger.set_debug(enable)

    def __init__(self):
        """ Virtually private constructor. """

        if AppConfiguration.__instance is not None:
            raise Exception("AppConfiguration " + config_messages.SINGLETON_EXCEPTION)

        self.__apikey = ''
        self.__region = ''
        self.__configuration_handler_instance = None
        self.__guid = ''
        self.__is_initialized = False
        self.__is_initialized_configuration = False
        self.__is_loading = False
        AppConfiguration.__instance = self

    def init(self, region: str, guid: str, apikey: str):
        """Initialise the AppConfiguration

           Args:
               region: Region Region name where the service instance is created.
               guid : GUID of the App Configuration service.\
               Get it from the service credentials section of the dashboard
               apikey : ApiKey of the App Configuration service.\
               Get it from the service credentials section of the dashboard
        """

        if not Validators.validate_string(region):
            Logger.error(config_messages.REGION_ERROR)
            return
        if not Validators.validate_string(apikey):
            Logger.error(config_messages.APIKEY_ERROR)
            return
        if not Validators.validate_string(guid):
            Logger.error(config_messages.GUID_ERROR)
            return
        self.__apikey = apikey
        self.__region = region
        self.__guid = guid
        self.__is_initialized = True
        self.__is_loading = False
        self.__setup_configuration_handler()

    def get_region(self) -> str:
        """Get the region currently used by the service.

        Returns:
            The region string currently used by the service.
        """
        return self.__region

    def get_guid(self) -> str:
        """Get the guid currently used by the service.

        Returns:
            The guid string currently used by the service.
        """
        return self.__guid

    def get_apikey(self) -> str:
        """Get the apikey currently used by the service.

        Returns:
            The apikey string currently used by the service.
        """
        return self.__apikey

    def set_context(self, collection_id: str, environment_id: str,
                    configuration_file: Optional[str] = None,
                    live_config_update_enabled: Optional[bool] = True):

        """Set the collection and environment value of the service.
        This method accepts configuration_file and live_config_update_enabled
        for offline usage.

        Args:
            collection_id : Id of the collection created in App Configuration service instance.
            environment_id : Id of the environment created in App Configuration service instance.
            configuration_file : Path to the JSON file which contains configuration details.
            live_config_update_enabled : Set this value to false if the new configuration values \
            shouldn't be fetched from the server. Make sure to provide a proper JSON file \
             in the configuration_file path. By default, this value is enabled.
        """

        if not self.__is_initialized:
            Logger.error(config_messages.COLLECTION_INIT_ERROR)
            return

        if not Validators.validate_string(collection_id):
            Logger.error(config_messages.COLLECTION_ID_VALUE_ERROR)
            return

        if not Validators.validate_string(environment_id):
            Logger.error(config_messages.ENVIRONMENT_ID_VALUE_ERROR)
            return

        self.__is_initialized_configuration = True
        if not live_config_update_enabled and configuration_file is None:
            Logger.error(config_messages.CONFIGURATION_FILE_NOT_FOUND_ERROR)
            return

        self.__configuration_handler_instance.set_context(collection_id, environment_id,
                                                          configuration_file,
                                                          live_config_update_enabled)
        self.__load_data_now()

    def fetch_configurations(self):
        """Fetch the latest configurations"""
        if self.__is_initialized and self.__is_initialized_configuration:
            self.__load_data_now()
        else:
            Logger.error(config_messages.COLLECTION_INIT_ERROR)

    def __setup_configuration_handler(self):
        self.__configuration_handler_instance = ConfigurationHandler.get_instance()
        self.__configuration_handler_instance.init(apikey=self.__apikey,
                                                   guid=self.__guid,
                                                   region=self.__region,
                                                   override_server_host=self.override_server_host)

    def __load_data_now(self):
        if self.__is_loading:
            return
        self.__is_loading = True
        self.__configuration_handler_instance.load_data()
        self.__is_loading = False

    def register_configuration_update_listener(self, listener):
        """Register a listener for the Configuration changes.

        Args:
            listener: A method for listening to the Configuration changes
        """
        if self.__is_initialized and self.__is_initialized_configuration:
            self.__configuration_handler_instance.register_configuration_update_listener(listener)
        else:
            Logger.error(config_messages.COLLECTION_INIT_ERROR)

    def get_feature(self, feature_id: str) -> Feature:
        """Get the Feature with give Feature Id

        Args:
            feature_id: The Feature ID value.
        Returns:
            Feature object with the given feature_id. If the Feature is not available \
            then expect `None`.
        """
        if self.__is_initialized and self.__is_initialized_configuration:
            return self.__configuration_handler_instance.get_feature(feature_id)
        Logger.error(config_messages.COLLECTION_INIT_ERROR)
        return None

    def get_features(self) -> Dict[str, Feature]:
        """Get the list of Feature objects

        Returns:
            List of Feature objects
        """
        if self.__is_initialized and self.__is_initialized_configuration:
            return self.__configuration_handler_instance.get_features()
        Logger.error(config_messages.COLLECTION_INIT_ERROR)
        return None

    def get_properties(self) -> Dict[str, Property]:
        """Get the list of Property objects

        Returns:
            List of Property objects
        """
        if self.__is_initialized and self.__is_initialized_configuration:
            return self.__configuration_handler_instance.get_properties()
        Logger.error(config_messages.COLLECTION_INIT_ERROR)
        return None

    def get_property(self, property_id: str) -> Property:
        """Get the Property with give Property Id

        Args:
            property_id: The Property ID value.
        Returns:
            Property object with the given property_id. If the Property is \
            not available then expect `None`.
        """
        if self.__is_initialized and self.__is_initialized_configuration:
            return self.__configuration_handler_instance.get_property(property_id)
        Logger.error(config_messages.COLLECTION_INIT_ERROR)
        return None
