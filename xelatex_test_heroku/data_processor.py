# -*- coding: utf-8 -*-
from __future__ import print_function  # Python 2 vs. 3 compatibility --> use print()
from __future__ import division  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import unicode_literals  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import absolute_import  # Python 2 vs. 3 compatibility --> absolute imports

import shutil
import requests
import os
import uuid
# import grequests
from .basic_logger import make_logger


logger = make_logger(__name__)
logger.setLevel('DEBUG')


def save_url_file(url, file_path, url_params={}, timeout=60):
    logger.debug("Making GET request to URL '{0}' with parameters '{1}' and timeout {2} seconds...".format(url, url_params, timeout))
    for k, v in url_params.iteritems():
        if isinstance(v, (list, tuple)):
            url_params[k] = ",".join(map(str, v))
    response = requests.get(url, params=url_params, timeout=timeout, stream=True)
    status = response.status_code
    logger.debug("Response status is '{0}' (in {1}), full URL is '{2}'!".format(status, response.headers.get('x-runtime'), response.url))
    # print response.content
    # status = response.status_code
    if status == 200:
        with open(file_path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
            logger.debug("URL content saved to '{}'!".format(file_path))
    del response
    return status


def save_custom_image_type(custom_image_dict, temp_folder='/tmp', temp_img_prefix='map', temp_img_format='png', remove_temp=True):
    # print chapter_part[part_key][wms_map_key]
    assert 'url' in custom_image_dict.keys(), "Key 'url' is missing in WMS settings for '{}'!".format(custom_image_type_key)
    wms_url = custom_image_dict.get('url')
    # print wms_url
    # print chapter_part[part_key][wms_map_key]
    if not os.path.isdir(temp_folder):
        os.mkdir(temp_folder)
        logger.debug("Temporary folder '{}' created!".format(temp_folder))
    image_path = os.path.join(temp_folder, '{0}_{1}.{2}'.format(temp_img_prefix, uuid.uuid4(), temp_img_format))
    save_url_file(wms_url, image_path, url_params=custom_image_dict)
    if remove_temp and os.path.exists(image_path):
        os.remove(image_path)
        logger.debug("Temporary image '{}' deleted!".format(image_path))
    return image_path


def get_dwm_params(layer, bbox, size, dpi=300, time=None, discrete_colors='false', legend='per_layer', legend_style='horizontal', legend_title=None,
                   scalebar_size='default', logo_size='default', markers=None):
    if isinstance(markers, list) or isinstance(markers, tuple):
        if isinstance(markers[0], list) or isinstance(markers[0], tuple):
            markers_str = ''
            for i in range(0, len(markers)):
                if i != 0:
                    markers_str += '\n'
                markers_str += ",".join(map(str, markers[i]))
            markers = markers_str
        else:
            markers = ",".join(map(str, markers))
    url_params = {
        "service": "WMS",
        "request": "GetPrint",
        "version": "1.3.0",
        "layers": layer,
        "format": "image/png",
        "time": time,
        "legend": legend,
        "discrete": discrete_colors,
        "interpolation": "nearest",
        "width": size[0],
        "height": size[1],
        "crs": "EPSG:4326",
        "bbox": ",".join(map(str, bbox)),
        "legend_size": None,
        "exact_legend_size": "false",
        "legend_style": legend_style,
        "legend_title": legend_title,
        "background_layers": "countries,coast,oceans,waters,rivers,grid,cities",
        "background_opacity": 100,
        "watermarks": 6,
        "scalebar_size": scalebar_size,
        "logo_size": logo_size,
        "dpi": dpi,
        "positions": "legend:br,logo:tl,scalebar:bl",
        "markers": markers
    }
    return url_params


if __name__ == '__main__':

    test_processor = False
    test_service = True

    if test_processor:
        img_url = 'https://tiles3.solargis.com/ghi_yr_avg/4/0_0/z4_9x6.jpg'
        img_url = 'http://neptun/wms'
        img_filepath = 'response_test.png'
        bbox = (47.27922900257082,17.08751678466797,49.62494564650146,22.20714569091797)
        layer = 'GHI_global_yearly'
        size = (1771, 733)
        markers = (48.625647, 19.171143, 'Sliac')
        markers = ((48.625647, 19.171143, 'Sliac'), (47.625647, 19.171143, 'daco na madaroch'))
        map_params = get_dwm_params(layer, bbox, size, markers=markers)
        # print map_params
        save_url_file(img_url, img_filepath, url_params=map_params)

    if test_service:
        import report_utils
        output_pdf = 'test_service.pdf'
        service_url = 'http://127.0.0.1:8030/reports/composer'
        request_params = {'output': 'pdf'}
        json_file = 'request_examples/composer_local_wms.json'
        request_json = report_utils.parse_json_like(json_file)
        # print request_json
        response = requests.post(service_url, json=request_json, params=request_params)
        if response.headers.get('content-type') == 'application/pdf':
            with open(output_pdf, 'w') as out_file:
                # shutil.copyfileobj(response.raw, out_file)
                out_file.write(response.content)
                logger.debug("URL content saved to '{}'!".format(output_pdf))
        else:
            print(response.text)

