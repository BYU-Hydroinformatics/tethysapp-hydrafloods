import logging
import ee
from ee.ee_exception import EEException
import hydrafloods as hf
from . import params as gee_account
from .products import EE_PRODUCTS
from . import cloud_mask as cm

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
        from oauth2client.service_account import ServiceAccountCredentials
        credentials = ServiceAccountCredentials.from_p12_keyfile(
            service_account_email='',
            filename='',
            private_key_password='notasecret',
            scopes=ee.oauth.SCOPE + ' https://www.googleapis.com/auth/drive '
        )
        ee.Initialize(credentials)


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


def get_image_collection_asset(platform, sensor, product, date_from=None, date_to=None, reducer='median'):
    """
    Get tile url for image collection asset.
    """
    ee_product = EE_PRODUCTS[platform][sensor][product]

    collection = ee_product['collection']

    index = ee_product.get('index', None)
    vis_params = ee_product.get('vis_params', {})
    cloud_mask = ee_product.get('cloud_mask', None)

    log.debug(f'Image Collection Name: {collection}')
    log.debug(f'Band Selector: {index}')
    log.debug(f'Vis Params: {vis_params}')

    try:
        ee_collection = ee.ImageCollection(collection)

        if product == "SAR":
            ee_collection = ee_collection.filter(ee.Filter.listContains("transmitterReceiverPolarisation", index))


        if date_from and date_to:
            ee_filter_date = ee.Filter.date(date_from, date_to)
            ee_collection = ee_collection.filter(ee_filter_date)

        if index:
            ee_collection = ee_collection.select(index)

        if cloud_mask:
            cloud_mask_func = getattr(cm, cloud_mask, None)
            if cloud_mask_func:
                ee_collection = ee_collection.map(cloud_mask_func)

        if reducer:
            ee_collection = getattr(ee_collection, reducer)()

        tile_url = image_to_map_id(ee_collection, vis_params)

        return tile_url

    except EEException:
        log.exception('An error occurred while attempting to retrieve the image collection asset.')

def sentinel1(region,start_time,end_time,apply_terrain_correction=True,apply_speckle_filter=True,force_projection=True):

    region = ee.Feature(region).geometry()
    ds = hf.Sentinel1(region,start_time,end_time)

    proc = []
    if apply_terrain_correction:
        elv = ee.Image("NASA/NASADEM_HGT/001").select("elevation").unmask(0)
        buffer = 50
        proc.append([hf.slope_correction,dict(elevation=elv,buffer=buffer)])

    if apply_speckle_filter:
        proc.append(hf.gamma_map)

    proc.append([hf.edge_otsu, dict(edge_buffer=300,initial_threshold=-16,scale=120)])

    if force_projection:
        proc.append(lambda x: x.reproject(ee.Projection("EPSG:4326").atScale(30)))

    water = ds.pipe(proc)

    return {"satellite":ds.collection.mean(),"water": water.collection.mode()}

def landsat8(region,start_time,end_time):

    return


def get_tile_url(ee_image,vis_params):
    map_id_dict = ee.Image(ee_image).getMapId(vis_params)
    return map_id_dict['tile_fetcher'].url_format
