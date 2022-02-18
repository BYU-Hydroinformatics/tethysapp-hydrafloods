import datetime as dt
from django.shortcuts import render
from tethys_sdk.permissions import login_required
from tethys_sdk.gizmos import SelectInput, DatePicker, Button, MapView, MVView
import logging
from django.http import JsonResponse, HttpResponseNotAllowed
from .gee.methods import sentinel1, landsat8, get_tile_url
import json

log = logging.getLogger(f'tethys.apps.{__name__}')


@login_required()
def home(request):
    """
    Controller for the app home page.
    """

    initial_start_date = '2022-01-05'
    initial_end_date = '2022-01-25'
    first_product_end_date = '2022-02-08'
    first_product_start_date = '2010-01-01'

    start_date = DatePicker(
        name='start_date',
        display_text='Start Date',
        format='yyyy-mm-dd',
        start_view='decade',
        today_button=True,
        today_highlight=True,
        start_date=first_product_start_date,
        end_date=first_product_end_date,
        initial=initial_start_date,
        autoclose=True
    )

    end_date = DatePicker(
        name='end_date',
        display_text='End Date',
        format='yyyy-mm-dd',
        start_view='decade',
        today_button=True,
        today_highlight=True,
        start_date=first_product_start_date,
        end_date=first_product_end_date,
        initial=initial_end_date,
        autoclose=True
    )

    # Build reducer method control
    reducer_select = SelectInput(
        name='reducer',
        display_text='Reduction Method',
        options=(
            ('Median', 'median'),
            ('Mode', 'mode'),
            ('Mean', 'mean'),
            ('Minimum', 'min'),
            ('Maximum', 'max'),
        )
    )

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'reducer_select': reducer_select,
    }

    return render(request, 'earth_engine/home.html', context)

@login_required()
def get_image_collection(request):
    """
    Controller to handle image collection requests.
    """
    response_data = {'success': False}

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    try:
        log.debug(f'POST: {request.POST}')

        platform = request.POST.get('platform', None)
        sensor = request.POST.get('sensor', None)
        product = request.POST.get('product', None)
        start_date = request.POST.get('start_date', None)
        end_date = request.POST.get('end_date', None)
        reducer = request.POST.get('reducer', None)

        url = get_image_collection_asset(
            platform=platform,
            sensor=sensor,
            product=product,
            date_from=start_date,
            date_to=end_date,
            reducer=reducer
        )

        log.debug(f'Image Collection URL: {url}')

        response_data.update({
            'success': True,
            'url': url
        })

    except Exception as e:
        response_data['error'] = f'Error Processing Request: {e}'

    return JsonResponse(response_data)

def retrieve_layer(request):
    print("calling retrieve_layers")
    response_data = {'success': False}

    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    try:
        log.debug(f'GET: {request.GET}')

        region = request.GET.get('input_spatial', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)

        sensor = request.GET.get('dataset', None)

        if sensor == "sentinel1":
            imgs = sentinel1(json.loads(region),start_date,end_date)
            wurl = get_tile_url(imgs["water"].selfMask(), {"min":0,"max":1,"palette": "darkblue"})
            surl = get_tile_url(imgs["satellite"], {"bands":"VV","min":-25,"max":0})

        elif sensor == "landsat8":
            imgs = landsat8(json.loads(region),start_date,end_date)
            wurl = get_tile_url(imgs["water"].selfMask(), {"min":0,"max":1,"palette": "darkblue"})
            surl = get_tile_url(imgs["satellite"], {"bands":"swir2,nir,green","min":50,"max":5500})

        else:
            raise NotImplementedError(f"sensor option {sensor} is not implemented")

        response_data.update({
            'success': True,
            'water_url': wurl,
            'image_url': surl
        })

    except Exception as e:
        response_data['error'] = f'Error Processing Request: {e}'

    return JsonResponse(response_data)
