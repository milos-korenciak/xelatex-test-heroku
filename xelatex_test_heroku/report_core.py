# coding=utf-8

from __future__ import print_function  # Python 2 vs. 3 compatibility --> use print()
from __future__ import division  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import unicode_literals  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import absolute_import  # Python 2 vs. 3 compatibility --> absolute imports
from . import report_utils
from . import data_processor
import json
from jinja2 import Template, Undefined
import os
import numpy as np
import uuid
import shutil
import subprocess
from .basic_logger import make_logger


logger = make_logger(__name__)
logger.setLevel('DEBUG')


class ReportTemplator(object):

    def __init__(self, **kwargs):
        report_json_param = 'report_json'
        mandatory_json_params = ['settings', 'chapters', 'templates']
        assert report_json_param in kwargs, "'{0}' is a mandatory parameter to initialize '{1}' object!".format(report_json_param, self.__class__.__name__)
        report_json = kwargs.get(report_json_param, None)
        report_dict = report_utils.parse_json_like(report_json, report_json_param, self.__class__.__name__)
        self.__dict__.update(report_dict)
        for param in mandatory_json_params:
            assert hasattr(self, param), "'{0}' parameter of class '{1}' must contain key '{2}'!".format(report_json_param, self.__class__.__name__, param)
        self.language = self.settings.get('language', 'english')

    def get_header(self):
        header_key = 'header'
        if hasattr(self, header_key):
            header_string = report_utils.get_string_from_template(self.templates.get(header_key, None), header_key)
            # print self.header
            return Template(header_string).render(**self.header)
        else:
            return ''

    def get_cover(self):
        cover_key = 'cover'
        if hasattr(self, cover_key):
            cover_string = report_utils.get_string_from_template(self.templates.get(cover_key, None), cover_key)
            return Template(cover_string).render(**self.cover)
        else:
            return ''

    def get_chapters(self, temp_folder='/tmp', remove_temp=True, wms_map_key='wms_map', grey_map_key='grey_map'):
        report_body = ''
        assert self.chapters.__class__ == list, "'body' value must be a list!"
        for chapter in self.chapters:
            # print chapter
            assert chapter.__class__ == list, "Every report chapter must be a list! ('body' list part '{}')".format(str(chapter))
            for chapter_part in chapter:
                assert len(chapter_part.keys()) == 1, "Each chapter part must be a dictionary with exactly one key!"
                part_key = chapter_part.keys()[0]
                implemented_keys = ['title', 'paragraph', 'table', 'image']
                assert part_key in implemented_keys, "Chapter part key in chapters list must be one of {}!".format(implemented_keys)
                if part_key.lower() == 'title':
                    title_string = report_utils.get_string_from_template(self.templates.get('title', None), 'title')
                    report_body += report_utils.get_chapter_title(chapter_part[part_key], title_string=title_string, language=self.language)
                elif part_key.lower() == 'paragraph':
                    paragraph_string = report_utils.get_string_from_template(self.templates.get('paragraph', None), 'paragraph')
                    minipage_ratio = 1  # TODO: just on testing purposes!
                    report_body += report_utils.get_paragraph(chapter_part[part_key], paragraph_string=paragraph_string,
                                                              minipage_ratio=minipage_ratio, language=self.language)
                elif part_key.lower() == 'table':
                    table_string = report_utils.get_string_from_template(self.templates.get('table', None), 'table')

                    # to get some meaningful defaults:
                    caption = chapter_part[part_key].get('caption', None)
                    header = chapter_part[part_key].get('header', None)
                    # print header
                    complex_header = chapter_part[part_key].get('complex_header', None)
                    values = chapter_part[part_key].get('values', None)
                    footer = chapter_part[part_key].get('footer', None)
                    first_column = chapter_part[part_key].get('first_column', None)
                    last_column = chapter_part[part_key].get('last_column', None)
                    apply_value_colors = chapter_part[part_key].get('apply_value_colors', False)
                    bold_first_column = chapter_part[part_key].get('bold_first_column', False)
                    bold_last_column = chapter_part[part_key].get('bold_last_column', False)
                    use_horizontal_lines = chapter_part[part_key].get('use_horizontal_lines', True)
                    column_widths = chapter_part[part_key].get('column_widths', None)
                    at_newpage = chapter_part[part_key].get('at_newpage', False)
                    minipage_ratio = chapter_part[part_key].get('minipage_ratio', 1)
                    color_header = chapter_part[part_key].get('color_header', 'EFEFEF')
                    color_footer = chapter_part[part_key].get('color_footer', 'EFEFEF')
                    value_color_ramp = chapter_part[part_key].get('value_color_ramp', ('3A52bA', '62B0C3', '77E16A', 'E9F949', 'FFD62B', 'FA8C21', 'F2413D'))
                    # print value_color_ramp

                    # # get some defaults from 'general' settings:
                    # color_header = chapter_part[part_key].get('color_header', self.settings.get('table', 'EFEFEF').get('color_header', 'EFEFEF'))
                    # # color_header = chapter_part[part_key].get('color_header', self.settings.get('table_header_color', 'EFEFEF'))
                    # # color_footer = chapter_part[part_key].get('color_footer', self.settings.get('table_footer_color', 'EFEFEF'))
                    # color_footer = chapter_part[part_key].get('color_footer', self.settings.get('table', 'EFEFEF').get('color_footer', 'EFEFEF'))
                    # # value_color_ramp = chapter_part[part_key].get('value_color_ramp', self.settings.get('table_value_colors', ('3A52bA', '62B0C3', '77E16A', 'E9F949', 'FFD62B', 'FA8C21', 'F2413D')))
                    # value_color_ramp = chapter_part[part_key].get('value_color_ramp', self.settings.get('table', ('3A52bA', '62B0C3', '77E16A', 'E9F949', 'FFD62B', 'FA8C21', 'F2413D')).get('value_color_ramp', ('3A52bA', '62B0C3', '77E16A', 'E9F949', 'FFD62B', 'FA8C21', 'F2413D')))

                    # generate the table:
                    # print values, values.__class__
                    report_body += report_utils.get_general_table(table_string=table_string, caption=caption, header=header, values=values, footer=footer,
                                                                  apply_value_colors=apply_value_colors, color_header=color_header, color_footer=color_footer,
                                                                  value_color_ramp=value_color_ramp, first_column=first_column, last_column=last_column,
                                                                  bold_first_column=bold_first_column, bold_last_column=bold_last_column, complex_header=complex_header,
                                                                  use_horizontal_lines=use_horizontal_lines, column_widths=column_widths, at_newpage=at_newpage,
                                                                  minipage_ratio=minipage_ratio)
                elif part_key.lower() == 'image':
                    image_string = report_utils.get_string_from_template(self.templates.get('image', None), 'image')
                    # assert 'path' in chapter_part[part_key], "'image' element of 'body' must contain attribute 'path'!"
                    if 'path' in chapter_part[part_key]:
                        image_path = chapter_part[part_key]['path']
                    elif 'base64' in chapter_part[part_key]:
                        pass  # TODO: continue development (save it)!
                    elif wms_map_key in chapter_part[part_key]:
                        image_path = data_processor.save_custom_image_type(custom_image_dict=chapter_part[part_key][wms_map_key], temp_folder=temp_folder,
                                                              temp_img_prefix=wms_map_key, temp_img_format='png', remove_temp=remove_temp)
                    elif grey_map_key in chapter_part[part_key]:
                        image_path = data_processor.save_custom_image_type(custom_image_dict=chapter_part[part_key][grey_map_key], temp_folder=temp_folder,
                                                              temp_img_prefix=grey_map_key, temp_img_format='png', remove_temp=remove_temp)
                        # # print chapter_part[part_key][wms_map_key]
                        # assert 'url' in chapter_part[part_key][wms_map_key].keys(), "Key 'url' is missing in WMS settings for '{}'!".format(wms_map_key)
                        # wms_url = chapter_part[part_key][wms_map_key].get('url')
                        # # print wms_url
                        # # print chapter_part[part_key][wms_map_key]
                        # if not os.path.isdir(temp_folder):
                        #     os.mkdir(temp_folder)
                        #     logger.debug("Temporary folder '{}' created!".format(temp_folder))
                        # image_path = os.path.join(temp_folder, 'wms_map_{}.png'.format(uuid.uuid4()))
                        # data_processor.save_url_file(wms_url, image_path, url_params=chapter_part[part_key][wms_map_key])
                        # if remove_temp and os.path.exists(image_path):
                        #     os.remove(image_path)
                        #     logger.debug("Temporary WMS image '{}' deleted!".format(image_path))
                    caption = chapter_part[part_key].get('caption', None)
                    textwidth_ratio = chapter_part[part_key].get('textwidth_ratio', 0.5)
                    center = chapter_part[part_key].get('center', False)
                    wrap_figure = chapter_part[part_key].get('wrap_figure', None)
                    minipage_ratio = chapter_part[part_key].get('minipage_ratio', 1)
                    report_body += report_utils.get_image(image_path, image_string=image_string, caption=caption, textwidth_ratio=textwidth_ratio,
                                                          center=center, wrap_figure=wrap_figure, minipage_ratio=minipage_ratio)

        return report_body

    def to_latex(self, temp_folder='/tmp', remove_temp=True):
        include_contents = self.settings.get('include_contents', False)  # if not stated in report JSON, no TOC will be present
        report_font = self.settings.get('font', 'Roboto')  # if 'font' missing in report JSON, 'Roboto' will be used
        main_font_path = self.settings.get('font_path', '/usr/share/fonts/truetype/roboto/')  # usual roboto path on ubuntu
        arabic_font = self.settings.get('arabic_font', 'Amiri')
        template_dict = dict(report_header=self.get_header(), report_cover=self.get_cover(), report_body=self.get_chapters(temp_folder=temp_folder, remove_temp=remove_temp),
                             language=self.language, main_font=report_font, main_font_path=main_font_path, arabic_font=arabic_font, include_contents=include_contents)
        report_string = report_utils.get_string_from_template(self.templates.get('report', None), 'report')
        latex_src = Template(report_string).render(template_dict)
        logger.debug("LaTeX string determined!")
        return latex_src

    def to_pdf(self, pdf_filepath=None, remove_temp=True, temp_folder='/tmp'):
        # temp_folder = '/tmp'
        if pdf_filepath:
            out_dir = os.path.join(temp_folder, os.path.split(pdf_filepath)[1].replace('.', '_'))
            # print out_dir
            tex_filepath = os.path.join(out_dir, os.path.split(pdf_filepath)[1].split('.')[0] + '.tex')
            # print tex_filepath
        else:
            temp_fld_name = 'temp_pdf_{}'.format(uuid.uuid4())
            out_dir = os.path.join(temp_folder, temp_fld_name)
            tex_filepath = os.path.join(out_dir, temp_fld_name + '.tex')
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
            logger.debug("Temporary folder '{}' created!".format(out_dir))
        with open(tex_filepath, 'w') as f:
            f.write(self.to_latex(temp_folder=out_dir, remove_temp=False).encode('utf8'))

        if os.getenv('PORT', None):  # if on Heroku
            os.environ["TEXMFLOCAL"] = "/app/buildpack/texmf-local"
            os.environ["TEXMFSYSCONFIG"] = "/app/buildpack/texmf-config"
            os.environ["TEXMFSYSVAR"] = "/app/buildpack/texmf-var"
            os.environ["TEXMFVAR"] = temp_folder
            BIN_PATH = os.environ.get("BIN_PATH", "/app/buildpack/bin/x86_64-linux/")  # we search for the xelatex binary
            XELATEX_PATH = os.path.join(BIN_PATH, "xelatex")
        else:  # if local / neptun etc
            XELATEX_PATH = 'xelatex'
        # os.system('lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory="%s" "%s"' % (out_dir, tex_filepath))
        # os.system('lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory="%s" "%s"' % (out_dir, tex_filepath))
        # subprocess.call(['lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory="%s" "%s"' % (out_dir, tex_filepath)], shell=True)
        # subprocess.call(['lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory="%s" "%s"' % (out_dir, tex_filepath)], shell=True)
        # subprocess.call([XELATEX_PATH + ' --shell-escape -synctex=1 -interaction=nonstopmode -output-directory="%s" "%s"' % (out_dir, tex_filepath)], shell=True)
        subprocess.call([XELATEX_PATH, '--shell-escape', '-synctex=1', '-interaction=nonstopmode', '-output-directory=%s'%out_dir,'%s'%tex_filepath])
        subprocess.call([XELATEX_PATH, '--shell-escape', '-synctex=1', '-interaction=nonstopmode', '-output-directory=%s'%out_dir,'%s'%tex_filepath])
        # subprocess.call(['lualatex', '--shell-escape', '-synctex=1', '-interaction=nonstopmode', '-output-directory="{}"'.format(out_dir), '"{}"'.format(tex_filepath)], stdout=None, stderr=subprocess.STDOUT)
        # subprocess.call('lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory="%s" "%s"' % (out_dir, tex_filepath))
        # os.system('pdflatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory="%s" "%s"' % (out_dir, tex_filepath))
        compiled_pdf_path = tex_filepath.replace('.tex', '.pdf')
        if os.path.isfile(compiled_pdf_path):
            logger.debug("PDF created!")
            if pdf_filepath:
                shutil.copyfile(compiled_pdf_path, pdf_filepath)
                logger.debug("PDF saved to '{}'!".format(pdf_filepath))
            with open(compiled_pdf_path, 'rb') as file_obj:
                binary_pdf = file_obj.read()
        else:
            logger.warning("PDF have not been created, check tex logs in folder '{}' (parameter 'remove_temp' must be False)!".format(out_dir))  # TODO: raise error here?
            binary_pdf = None
        if remove_temp:
            shutil.rmtree(out_dir)
            logger.debug("Temporary folder '{}' deleted!".format(out_dir))
        return binary_pdf


class ReportComposer(object):

    def __init__(self, **kwargs):
        request_param = 'request_json'
        # config_param = 'config_json'
        # mandatory_params = [request_param, config_param]
        report_type_key = 'report_type'
        reqest_lang_key = 'language'
        config_key = 'config'
        data_key = 'data'
        mandatory_request_keys = [report_type_key, reqest_lang_key, config_key, data_key]
        lang_dir_key = 'lang_dir'
        configs_key = 'report_cfg'
        templates_key = 'templates'
        mandatory_config_keys = [lang_dir_key, configs_key]

        # for param in mandatory_params:
        #     assert param in kwargs, "'{0}' is a mandatory parameter to initialize '{1}' class!".format(param, self.__class__.__name__)
        assert request_param in kwargs, "'{0}' is a mandatory parameter to initialize '{1}' class!".format(request_param, self.__class__.__name__)
        request_json = kwargs.get(request_param, None)
        request_dict = report_utils.parse_json_like(request_json, request_param, self.__class__.__name__)
        for key in mandatory_request_keys:
            assert key in request_dict, "Key '{0}' is a mandatory for '{1}' parameter of '{2}' class!".format(key, request_param, self.__class__.__name__)
        self.report_type = request_dict[report_type_key]
        # print self.report_type
        self.report_data = request_dict[data_key]

        # config_json = kwargs.get(config_param, None)
        # config_dict = report_utils.parse_json_like(config_json, config_param, self.__class__.__name__)
        config_dict = report_utils.parse_json_like(request_dict[config_key], config_key, self.__class__.__name__)
        for key in mandatory_config_keys:
            # assert key in config_dict, "Key '{0}' is a mandatory for '{1}' parameter of '{2}' class!".format(key, config_param, self.__class__.__name__)
            assert key in config_dict, "Key '{0}' is a mandatory in '{1}' key of '{2}' parameter of '{3}' class!".format(key, config_key, request_param, self.__class__.__name__)
        # print config_dict
        self.configuration = {}
        assert type(config_dict[configs_key]) == list or type(config_dict[configs_key]) == dict or type(config_dict[configs_key]) == str or type(config_dict[configs_key]) == unicode, \
            "Value of parameter '{0}[{1}][{2}]' of class '{3}' must be either list of JSON filepaths, JSON filepath or a valid JSON (dictionary)!"\
                .format(request_param, config_key, configs_key, self.__class__.__name__)
        if type(config_dict[configs_key]) == list:
            for cfg_file in config_dict[configs_key]:
                # print cfg_file, cfg_file.__class__
                cfg_dict = report_utils.parse_json_like(cfg_file)
                self.configuration = report_utils.sefely_update_dict(self.configuration, cfg_dict)
        else:
            cfg_dict = report_utils.parse_json_like(config_dict[configs_key])
            self.configuration = report_utils.sefely_update_dict(self.configuration, cfg_dict)
        # print report_utils.print_pretty_json(self.configuration)
        self.templates = config_dict.get(templates_key, {})
        self.lang_dict = None
        lang_dir = config_dict[lang_dir_key]
        assert os.path.isdir(lang_dir), "Directory '{2}' speciefied in '{0}' of '{1}' request key does not exist!".format(lang_dir_key, config_key, lang_dir)
        request_lang = request_dict.get(reqest_lang_key, 'english')  # if not found, use english!
        valid_langs = []
        for lang_file in os.listdir(lang_dir):
            valid_langs.append(str(lang_file.split('.')[0]))
            if lang_file.split('.')[0].lower() == request_lang.lower():
                lang_filepath = os.path.join(lang_dir, lang_file)
                # print lang_filepath
                self.lang_dict = report_utils.parse_json_like(lang_filepath)
        assert self.lang_dict, "Language '{0}' is not supported! Valid options are: {1}".format(request_lang, valid_langs)
        # print self.lang_dict

        # if 'latex_lang' in config_dict.keys():  # TODO: this will be probably changed!
        #     if request_lang.lower() in config_dict['latex_lang']:
        #         self.latex_language = config_dict['latex_lang'][request_lang.lower()]
        self.latex_language = request_lang.lower()

        self.report_json = self.to_json()  # if not defined as attribute, configuration is changed with multiple calls for unknown reason (no idea where to use dict.copy())!

    def configuration_to_unicode(self):
        return report_utils.print_pretty_json(self.configuration)

    def to_json(self, templates_key='templates', types_key='types', settings_key='settings', cover_key='cover', header_key='header',
                chapters_key='chapters', include_cover_key='include_cover', table_key='table', table_types_key='tables', type_key='type',
                image_key='image', wms_map_key='wms_map', wms_map_types_key='wms_maps', grey_map_key='grey_map', grey_map_types_key='grey_maps'):
        logger.debug("Determining report JSON based on the configuration...")
        report_json = dict()

        # get basic stuff from 'settings' shared among all report types
        report_json[templates_key] = self.templates
        report_json[settings_key] = self.configuration.get(settings_key, {})
        report_json[settings_key]['language'] = self.latex_language  # TODO: this will be probably changed!
        report_json[cover_key] = report_json[settings_key].get(cover_key, {})
        report_json[header_key] = report_json[settings_key].get(header_key, {})
        for key in [cover_key, header_key]:
            if key in report_json[settings_key].keys():
                report_json[settings_key].pop(key, None)

        # get other stuff from type-specific configuration
        # print self.configuration[tables_key].keys()
        for key in self.configuration[types_key].keys():
            # print key
            if self.report_type.lower() == key.lower():
                # print key
                # print self.configuration[types_key][key][chapters_key]
                for key1 in [settings_key, cover_key, header_key]:  # update settings, header and cover by type-specific values
                    if key1 in self.configuration[types_key][key].keys():
                        report_json[key1] = report_utils.sefely_update_dict(report_json[key1], self.configuration[types_key][key][key1])
                if not report_json[settings_key].get(include_cover_key, False):  # get rid of cover if not needed to prevent confusion
                    report_json.pop(cover_key, None)
                assert chapters_key in self.configuration[types_key][key].keys(), "Configuration for report type '{0}' does not contain '{1}' key!".format(key, chapters_key)
                chapters = self.configuration[types_key][key][chapters_key]
                # print chapters
                # print self.configuration[types_key][key][chapters_key]
                for i in range(0, len(chapters)):
                    assert chapters_key in self.configuration, "Report configuration must contain key '{}'!".format(chapters_key)
                    # if chapters[i].lower() in [x.lower() for x in self.configuration[chapters_key].keys()]:  # TODO: make it case-independent?
                    if chapters[i] in self.configuration[chapters_key].keys():
                        chapters[i] = self.configuration[chapters_key][chapters[i]]
                        # print chapters[i][1].get('table', {}).get('values', {}), chapters[i].__class__
                for chapter in chapters:
                    if not type(chapter) == list:
                        logger.warning("Chapter '{}' have not been found in the configuration or is not configured as a list, therefore it will be skipped!".format(chapter))  # TODO: raise error here?
                        chapters.pop(chapters.index(chapter))
                report_json[chapters_key] = chapters
        assert chapters_key in report_json.keys(), "Report type '{}' has not been found in the configuration!".format(self.report_type)

        logger.debug("Applying table types configuration...")
        table_types = self.configuration.get(table_types_key, {})
        table_settings = self.configuration.get(settings_key, {}).get(table_key, {})
        for k, v in table_types.iteritems():
            table_types[k] = report_utils.sefely_update_dict(table_settings, table_types[k])
        for i in range(0, len(report_json[chapters_key])):
            for j in range(0, len(report_json[chapters_key][i])):
                if table_key == report_json[chapters_key][i][j].keys()[0]:  # to check if the chapter item is a table
                    table_type = report_json[chapters_key][i][j][table_key].get(type_key, None)
                    if table_type and table_type in table_types.keys():
                        # print report_json[chapters_key][i][j][table_key]
                        report_json[chapters_key][i][j][table_key] = report_utils.sefely_update_dict(table_types[table_type], report_json[chapters_key][i][j][table_key])
                        # print report_json[chapters_key][i][j][table_key]

        logger.debug("Applying custom image types configuration...")
        report_json[chapters_key] = report_utils.update_custom_image_type(configuration_dict=self.configuration,
                                                                          chapters_dict=report_json[chapters_key],
                                                                          settings_key=settings_key,
                                                                          image_key=image_key,
                                                                          type_key=type_key,
                                                                          image_types_key=wms_map_types_key,
                                                                          custom_type_key=wms_map_key)
        report_json[chapters_key] = report_utils.update_custom_image_type(configuration_dict=self.configuration,
                                                                          chapters_dict=report_json[chapters_key],
                                                                          settings_key=settings_key,
                                                                          image_key=image_key,
                                                                          type_key=type_key,
                                                                          image_types_key=grey_map_types_key,
                                                                          custom_type_key=grey_map_key)

        # map_types = self.configuration.get(map_types_key, {})
        # wms_settings = self.configuration.get(settings_key, {}).get(wms_map_key, {})
        # for k, v in map_types.iteritems():
        #     map_types[k] = report_utils.sefely_update_dict(wms_settings, map_types[k])
        # for i in range(0, len(report_json[chapters_key])):
        #     for j in range(0, len(report_json[chapters_key][i])):
        #         if image_key == report_json[chapters_key][i][j].keys()[0]:  # to check if the chapter item is an image
        #             if wms_map_key in report_json[chapters_key][i][j][image_key].keys():
        #                 map_type = report_json[chapters_key][i][j][image_key][wms_map_key].get(type_key, None)
        #                 if map_type and map_type in map_types.keys():
        #                     # print report_json[chapters_key][i][j][image_key][map_key]
        #                     report_json[chapters_key][i][j][image_key][wms_map_key] = report_utils.sefely_update_dict(map_types[map_type], report_json[chapters_key][i][j][image_key][wms_map_key])
        #                     # print report_json[chapters_key][i][j][image_key][map_key]

        logger.debug("Applying language and request data...")
        report_json_uni = json.dumps(report_json, ensure_ascii=False)
        # print report_json_uni
        # print self.report_data['ghi']['values']
        # print self.report_data
        # # print self.lang_dict
        templated_uni = Template(report_json_uni, undefined=jinjaUndefined).render(data=self.report_data, lang=self.lang_dict)
        # print templated_uni
        report_json = json.loads(templated_uni)
        report_json = report_utils.listify_dict_values(report_json)  # looks silly, but needed
        # print report_utils.print_pretty_json(report_json)

        logger.debug("Report JSON determined!")
        return report_json

    def to_json_unicode(self):
        # return report_utils.print_pretty_json(self.to_json(), indent=2)
        return report_utils.print_pretty_json(self.report_json, indent=2)

    def to_json_file(self, json_filepath):
        with open(json_filepath, 'w') as fileobj:
            fileobj.write(self.to_json_unicode().encode('utf-8'))
        logger.debug("JSON file saved to '{}'!".format(json_filepath))

    def to_latex(self, temp_folder='/tmp', remove_temp=True):
        # return ReportTemplator(report_json=self.to_json()).to_latex()
        return ReportTemplator(report_json=self.report_json).to_latex(temp_folder=temp_folder, remove_temp=remove_temp)

    def to_pdf(self, pdf_filepath=None, temp_folder='/tmp', remove_temp=True):
        # return ReportTemplator(report_json=self.to_json()).to_pdf(pdf_filepath, remove_temp, temp_folder)
        return ReportTemplator(report_json=self.report_json).to_pdf(pdf_filepath, remove_temp=remove_temp, temp_folder=temp_folder)


class jinjaUndefined(Undefined):

    # def __init__(self, *args, **kwargs):
    #     # Undefined.__init__(self, *args, **kwargs)
    #     self.data_dict = kwargs.pop('data', {})
    #     self.lang_dict = kwargs.pop('lang', {})
    #     Undefined.__init__(self, *args, **kwargs)
    #     # super(jinjaUndefined, self).__init__(*args, **kwargs)

    def _fail_with_undefined_error(self, *args, **kwargs):
        # print self._undefined_hint
        # print self._undefined_obj.keys()
        # print self._undefined_name
        # print self._undefined_exception
        # print self.data_dict
        existing_keys, missing_key = '', ''
        if self._undefined_obj:
            existing_keys = self._undefined_obj.keys()
        if self._undefined_name:
            missing_key = self._undefined_name
        raise self._undefined_exception("Missing key '{0}' from 'data' or 'lang' dictionary. Provided keys are {1}".format(missing_key, existing_keys))

if __name__ == '__main__':

    test_templator = False
    # test_templator = True
    test_composer = True
    # test_processor = False

    output_pdf_file = 'test_complex_header.pdf'
    output_pdf_file = 'test_maps.pdf'

    if test_templator:
        output_latex_file = 'test_classes.tex'

        logo_path = 'Solargis-noR-RGB.png'
        report_title = 'Some Solargis Report'
        chapter1_title = 'Some chapter'
        chapter_paragraph1 = 'The Solargis\\texttrademark forecasting technology comprises various cutting-edge methodologies to predict solar radiation and other meteorological variables. Our technology provides worldwide forecasting solutions for time horizons ranging from few minutes up to 10 days ahead with sub-hourly resolution and several updates a day.'
        row_values = np.random.randint(1000, 2000, (13, 5))
        footer_row = np.sum(row_values, axis=0)
        table_header = ['January', 'February', 'March', 'April', 'May']
        first_column = list(np.arange(start=1994, stop=1994 + row_values.shape[0], step=1))
        if first_column is not None:
            table_header = ['Year'] + table_header
            footer_row = ['Sum'] + list(footer_row)
        row_values_list = list()
        for row in list(row_values):
            row_values_list.append(list(row))

        init_dict = {'settings': {'report_type': 'pvspot', 'language': 'english', 'font': 'Roboto', 'table_header_color': 'EFEFEF',
                                 'include_contents': True},
                     'header': {'logo_filepath': logo_path, 'report_type': 'iMaps', 'report_title': None},
                     'cover': {'report_title': report_title},
                     'chapters': [
                         [{'title': chapter1_title}, {'paragraph': chapter_paragraph1}, {'image': {'path': logo_path, 'caption': 'Sample image'}}],
                         [{'title': 'Tables'}, {'table': {'first_column': ['Site name:', 'Elevation a.s.l.:'], 'values':[[u'Sliač'], ['398 m']],
                                                         'bold_first_column': True, 'use_horizontal_lines': False, 'column_widths': (3, 5)}},
                          {'table': dict(caption='Sample table', first_column=first_column, header=table_header, values=row_values_list, footer=list(footer_row))}
                          ]
                        ],
                     "templates": {
                         "report": "templates/report.tex",
                         "header": "templates/header.tex",
                         "cover": "templates/cover.tex",
                         "title": "templates/chapter_title.tex",
                         "paragraph": "templates/paragraph.tex",
                         "table": "templates/table.tex",
                         "image": "templates/image.tex"
                        }
                     }

        init_json = json.dumps(init_dict)
        # init_json = init_dict
        # init_json = 'config/test_report.json'
        print(init_json)
        #print init_json, init_json.__class__
        # r = ReportOld(report_json=init_json)
        r = ReportTemplator(report_json=init_json)
        # print r.get_chapters()
        #print r.general
        # print r.to_latex()
        # print r.get_subclasses()
        # print r.__class__
        # print r.body
        # print r.header
        # print r.get_body()
        # print r.get_cover()
        # print r.to_latex()
        print(r.to_latex())
        # r.to_pdf(output_latex_file)
        # r.to_pdf(output_pdf_file)

        # bianry_pdf = r.to_pdf()
        # with open('test_binary.pdf', 'wb') as fileobj:
        #     fileobj.write(bianry_pdf)
        # print Report.get_subclasses()

    if test_composer:
        tbl_values = np.random.randint(60, 250, (5, 12))
        footer_row = np.mean(tbl_values, axis=0, dtype=np.int)
        last_year = 2017
        first_column = np.arange(start=last_year - tbl_values.shape[0], stop=last_year, step=1)
        # first_column = None
        last_column = np.sum(tbl_values, axis=1)
        footer_row = np.append(footer_row, np.mean(last_column, dtype=np.int))
        # print tbl_values.tolist()
        ghi_dict = {'data': {'ghi': {'years': first_column.tolist(), 'records': tbl_values.tolist(), 'avg': footer_row.tolist(), 'sums': last_column.tolist()}}}

        config_file = 'config/config_paths.json'
        # config_file = report_utils.parse_json_like(config_file)
        request_dict = {'report_type': 'test', 'language': 'english', 'config': config_file,
                        'data': {'site_info': {'name': 'Souissi', 'lat': 33.951904, 'lon': -6.804657, 'map': 'overview_map.jpg'}}}
        request_dict = {'report_type': 'test', 'language': 'english', 'config': config_file,
                        'data': {'site_info': {'name': 'Souissi', 'lat': 33.951904, 'lon': -6.804657, 'bbox': [21.09375,-18.046417236328125,36.9140625,-0.028839111328125]}}}
        request_dict = {'report_type': 'test', 'language': 'english', 'config': config_file,
                        'data': {'site_info': {'name': 'Souissi', 'lat': 33.951904, 'lon': -6.804657,
                                               'bbox': [21.09375, -18.046417236328125, 36.9140625, -0.028839111328125], 'cntry_code': 'MA'}}}
        report_utils.sefely_update_dict(request_dict, ghi_dict)
        # print request_dict
        request_json = json.dumps(request_dict)
        # print report_utils.print_pretty_json(request_dict, indent=2)
        # print request_json
        # request_json = 'request_examples/composer_local.json'
        r = ReportComposer(request_json=request_json)
        # print report_utils.print_pretty_json(r.configuration)
        # print r.to_json_unicode()
        # print r.to_json_unicode()
        # r.to_latex()
        # print r.to_latex(remove_temp=False)
        # print r.to_json_file("test.json")
        r.to_pdf(output_pdf_file, remove_temp=False)
        # print r.to_latex()

