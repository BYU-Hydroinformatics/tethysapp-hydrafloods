EE_PRODUCTS = {
    'sentinel': {
        '1': {
            'SAR':{
                'display': 'SAR',
                'collection': 'COPERNICUS/S1_GRD',
                'index': 'VV',
                'vis_params': {
                    'min': -25,
                    'max': 0,
                },
                'start_date': '2014-10-03',
                'end_date': None  # to present
            }
        },
    },
    # 'landsat': {
    #     '8': {
    #         # 'surface': {
    #         #     'display': 'Surface Reflectance',
    #         #     'collection': 'LANDSAT/LC08/C01/T1_SR',
    #         #     'index': None,
    #         #     'vis_params': {
    #         #         'bands': ['B4', 'B3', 'B2'],
    #         #         'min': 0,
    #         #         'max': 3000,
    #         #         'gamma': 1.4,
    #         #     },
    #         #     'cloud_mask': 'mask_l8_sr',
    #         #     'start_date': '2013-04-01',
    #         #     'end_date': None  # to present
    #         # },
    #         # 'ndvi': {
    #         #     'display': '8-day Normalized Difference Vegetation (NDVI)',
    #         #     'collection': 'LANDSAT/LC08/C01/T1_8DAY_NDVI',
    #         #     'index': 'NDVI',
    #         #     'vis_params': {
    #         #         'min': 0.0,
    #         #         'max': 1.0,
    #         #         'palette': [
    #         #             'FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718', '74A901',
    #         #             '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01',
    #         #             '012E01', '011D01', '011301'
    #         #         ],
    #         #     },
    #         #     'start_date': '2013-04-01',
    #         #     'end_date': None  # to present
    #         # },
    #         # 'ndsi': {
    #         #     'display': '8-day Normalized Difference Snow Index (NDSI)',
    #         #     'collection': 'LANDSAT/LC08/C01/T1_8DAY_NDSI',
    #         #     'index': 'NDSI',
    #         #     'vis_params': {
    #         #         'palette': ['000088', '0000FF', '8888FF', 'FFFFFF'],
    #         #     },
    #         #     'start_date': '2013-04-01',
    #         #     'end_date': None  # to present
    #         # },
    #         'mndwi': {
    #             'display': 'Landsat',
    #             'collection': 'LANDSAT/LC08/C01/T1',
    #             'index': 'B3',
    #             'vis_params': {
    #                 'palette': ['000088', '0000FF', '8888FF', 'FFFFFF'],
    #             },
    #             'start_date': '2013-04-11',
    #             'end_date': None  # to present
    #         },
    #     }
    # }
}