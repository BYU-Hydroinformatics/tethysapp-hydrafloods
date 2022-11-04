import logging
import datetime
import ee
from ee.ee_exception import EEException
import hydrafloods as hf
from . import params as gee_account
# from . import cloud_mask as cm

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
}

log = logging.getLogger(f'tethys.apps.{__name__}')

if gee_account.service_account:
    try:
        credentials = ee.ServiceAccountCredentials(gee_account.service_account, gee_account.private_key)
        ee.Initialize(credentials)
    except EEException as e:
        print(str(e))
else:
    try:
        ee.Initialize()
    except EEException as e:
        print(e)
        # from oauth2client.service_account import ServiceAccountCredentials
        # credentials = ServiceAccountCredentials.from_p12_keyfile(
        #     service_account_email='',
        #     filename='',
        #     private_key_password='notasecret',
        #     # scopes=ee.oauth.SCOPE + ' https://www.googleapis.com/auth/drive '
        # )
        # ee.Initialize(credentials)


def image_to_map_id(image_name, vis_params={}):
    """
    Get map_id parameters
    """
    try:
        ee_image = ee.Image(image_name)
        map_id = ee_image.getMapId(vis_params)
        tile_url = map_id['tile_fetcher'].url_format
        return tile_url

    except EEException:
        log.exception('An error occurred while attempting to retrieve the map id.')


# def get_image_collection_asset(platform, sensor, product, date_from=None, date_to=None, reducer='median'):
#     """
#     Get tile url for image collection asset.
#     """
#     ee_product = EE_PRODUCTS[platform][sensor][product]

#     collection = ee_product['collection']

#     # index = ee_product.get('index', None)
#     # vis_params = ee_product.get('vis_params', {})
#     # cloud_mask = ee_product.get('cloud_mask', None)

#     log.debug(f'Image Collection Name: {collection}')
#     log.debug(f'Band Selector: {index}')
#     log.debug(f'Vis Params: {vis_params}')

#     try:
#         ee_collection = ee.ImageCollection(collection)

#         if product == "SAR":
#             ee_collection = ee_collection.filter(ee.Filter.listContains("transmitterReceiverPolarisation", index))


#         if date_from and date_to:
#             ee_filter_date = ee.Filter.date(date_from, date_to)
#             ee_collection = ee_collection.filter(ee_filter_date)

#         if index:
#             ee_collection = ee_collection.select(index)

#         # if cloud_mask:
#         #     cloud_mask_func = getattr(cm, cloud_mask, None)
#         #     if cloud_mask_func:
#         #         ee_collection = ee_collection.map(cloud_mask_func)

#         if reducer:
#             ee_collection = getattr(ee_collection, reducer)()

#         tile_url = image_to_map_id(ee_collection, vis_params)

#         return tile_url

#     except EEException:
#         log.exception('An error occurred while attempting to retrieve the image collection asset.')

def sentinel1(region,start_time,end_time,apply_terrain_correction=True,apply_speckle_filter=True,force_projection=True,floods=False,fmethod="yearly",fthresh=75):

    region = ee.Feature(region).geometry()
    ds = hf.Sentinel1(region,start_time,end_time)

    hand = ee.Image("MERIT/Hydro/v1_0_1").select("hnd").unmask(0)

    img_check(ds)

    proc = []
    if apply_terrain_correction:
        elv = ee.Image("NASA/NASADEM_HGT/001").select("elevation").unmask(0)
        buffer = 100
        proc.append([hf.slope_correction,dict(elevation=elv,buffer=buffer)])

    if apply_speckle_filter:
        proc.append(hf.gamma_map)

    proc.append([hf.edge_otsu, dict(band="VH",edge_buffer=300,initial_threshold=-20,scale=120,thresh_no_data=-18)])
    proc.append(lambda x: x.And(hand.lt(15)).focal_mode())
    proc.append(max_water_mask)

    if force_projection:
        proc.append(lambda x: x.reproject(ee.Projection("EPSG:4326").atScale(30)))

    water = ds.pipe(proc)

    if floods:
        flood_img = apply_flood_map(water,fmethod,fthresh)
    else: 
        flood_img = ee.Image()

    return dict(satellite = ds.collection.mean(), water = water.collection.mode(), flood = flood_img)

def landsat8(region,start_time,end_time,cloudmask=True,floods=False,fmethod="yearly",fthresh=75):

    region = ee.Feature(region).geometry()
    ds = hf.Landsat8(region,start_time,end_time,use_qa=cloudmask)

    hand = ee.Image("MERIT/Hydro/v1_0_1").select("hnd").unmask(0)

    img_check(ds)

    proc = (
        # (hf.illumination_correction, dict(elevation=elv,scale=120)),
        hf.mndwi,
        (hf.edge_otsu, dict(edge_buffer=300,initial_threshold=0.05,scale=120,invert=True,thresh_no_data=0)),
		lambda x: x.And(hand.lt(15).focal_mode()),
        max_water_mask
    )

    water = ds.pipe(proc)

    if floods:
        flood_img = apply_flood_map(water,fmethod,fthresh)
    else: 
        flood_img = ee.Image()

    return dict(satellite = ds.collection.median(), water = water.collection.mode(), flood = flood_img)

def apply_flood_map(ds,fmethod,fthresh):
    if fmethod == "1":
        flood_method = 'yearly'
    elif fmethod == "2":
        flood_method = 'seasonal' 
    elif fmethod == "3":
        flood_method = 'occurrence'

    flood_ds = ds.apply_func(hf.extract_flood, reference=flood_method, permanent_threshold=int(fthresh))
    flood_img = flood_ds.collection.mode()
    return flood_img

def get_tile_url(ee_image,vis_params):
    map_id_dict = ee.Image(ee_image).getMapId(vis_params)
    return map_id_dict['tile_fetcher'].url_format

def get_download_url(img, region):

	region = ee.Feature(region).geometry()

	now = datetime.datetime.now()
	now_str = now.strftime("%Y%m%d%H%M%S")

	name = f"hydrafloods.export.{now_str}"

	url = img.getDownloadURL({
		'name':name,
		'scale': 30,
		'crs': 'EPSG:4326',
		'region': region
	})

	return url

def img_check(ds):

    n_imgs = ds.n_images

    if n_imgs == 0 :
        raise ValueError("no images found for the space-time domain specified")

    return

def max_water_mask(img):
    JRC_MASK = ee.Image("JRC/GSW1_3/GlobalSurfaceWater").select("occurrence").mask().gt(0)
    return img.And(JRC_MASK)