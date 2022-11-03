from tethys_sdk.base import TethysAppBase, url_map_maker

from tethys_sdk.app_settings import CustomSetting

class EarthEngine(TethysAppBase):
    """
    Tethys app class for Earth Engine.
    """

    name = 'Water Mapping App'
    index = 'home'
    icon = 'earth_engine/images/earth-engine-logo.png'
    package = 'earth_engine'
    root_url = 'earth-engine'
    color = '#84ADEA'
    description = ''
    tags = ''
    enable_feedback = False
    feedback_emails = []
    controller_modules = [ 'controllers' ]

    # def url_maps(self):
    #     """
    #     Add controllers
    #     """
    #     UrlMap = url_map_maker(self.root_url)

    #     url_maps = (
    #         UrlMap(
    #             name='home',
    #             url='earth-engine',
    #             controller='earth_engine.controllers.home'
    #         ),
    #         UrlMap(
    #             name='get_image_collection',
    #             url='earth-engine/get-image-collection',
    #             controller='earth_engine.controllers.get_image_collection'
    #         ),
    #         UrlMap(
    #             name='get_image_layer',
    #             url='get-image-layer/',
    #             controller='earth_engine.controllers.retrieve_layer'
    #         ),
    #         UrlMap(
    #             name='get_export',
    #             url='get-export/',
    #             controller='earth_engine.controllers.export_layer'
    #         )

    #     )

    #     return url_maps
    def custom_settings(self):
        """
        Example custom_settings method.
        """
        custom_settings = (
            CustomSetting(
                name='service_account',
                type=CustomSetting.TYPE_STRING,
                description='service account mail',
                required=False
            ),
            CustomSetting(
                name='path_to_json_key',
                type=CustomSetting.TYPE_STRING,
                description='The path to json key for authetication',
                required=False
            ),
        )

        return custom_settings