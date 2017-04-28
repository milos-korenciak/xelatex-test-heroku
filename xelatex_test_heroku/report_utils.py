# -*- coding: utf-8 -*-
from __future__ import print_function  # Python 2 vs. 3 compatibility --> use print()
from __future__ import division  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import unicode_literals  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import absolute_import  # Python 2 vs. 3 compatibility --> absolute imports

from jinja2 import Template
import json
import os
import numpy as np
import uuid
import collections

setting_string = r'''
\documentclass[11pt,a4paper]{article}
\\usepackage[a4paper]{geometry}
\\usepackage{array}
\\usepackage{graphicx}
\\usepackage{booktabs}
\\usepackage{fontspec} % to use a custom font (e.g., Roboto). To use with lualatex instead of pdflatex
\\setmainfont{ {{font_name}} }
\\usepackage{lastpage} % to use the last page number in footer
\\usepackage{datetime} % to get months as a words, not numbers
%\\usepackage[italian,english]{babel} % to get some another languages later on (using \selectlanguage{italian})
\\usepackage{fancyhdr}
\pagestyle{fancy}  % to have header and footer
\\usepackage{grffile} % to manage fancy characters in figure file names (i.e., underscores)

% polyglossia stuff:
\\usepackage{fontspec}
\\usepackage{polyglossia}
\setmainlanguage{english}
{% if secondary_language == "arabic" %}
\setotherlanguage{arabic}
\\newfontfamily\\arabicfont[Script=Arabic,Scale=1.1]{Amiri}
{% endif %}

% the next 5 lines are to set the figure positioning. Figures in spare pages are centered to
% cover all the blank space. With these settings they are forced to align to the top of the page
\makeatletter
\setlength\@fptop{0pt}
\setlength\@fpsep{30pt plus 0fil}
\setlength\@fpbot{0pt}
\makeatother

\setlength{\\abovetopsep}{1ex} % to set up the separation distance between the caption and the table

\setlength\\topmargin{-40pt} % Top margin
\setlength\headheight{20pt} % Header height
%\setlength\\textwidth{7.0in} % Text width
\setlength\\textheight{9.5in} % Text height
%\setlength\oddsidemargin{-30pt} % Left margin
%\setlength\evensidemargin{-30pt} % Left margin (even pages) - only relevant with 'twoside' article option
\\begin{document}
'''
header_string = '''
\\fancyhf{}
\\fancyhead[R]{ {{report_type}} {% if report_title %} \\newline {{report_title}} {% endif %} }
\\fancyhead[L]{\includegraphics[width=2cm]{{ '{' }}{{logo_filepath}}}} {# needed escape {{ '{' }} due to jinja error #}
\\fancyfoot[R]{\\thepage / \pageref{LastPage}}
\\fancyfoot[L]{Chapter \\nouppercase{\leftmark} \\ {\\textcopyright} Solargis, {\monthname} \\the\year}
'''
cover_string = '''
%opening
\\title{ {{report_title}} }
\\author{Solargis\\texttrademark  s.r.o}

\maketitle
\\thispagestyle{empty}

\\newpage
\setcounter{page}{1}
'''
chapter_string = '''
\section{ {{chapter_title}} }
The Solargis\\texttrademark forecasting technology comprises various cutting-edge methodologies to predict solar radiation and other meteorological variables. Our technology provides worldwide forecasting solutions for time horizons ranging from few minutes up to 10 days ahead with sub-hourly resolution and several updates a day. From 10 minutes to 6 hours ahead, the solar radiation prediction is performed based on both time casting of near-real-time satellite-derived images and numerical weather prediction (NWP) models. For time horizons beyond 6 hours, NWP models are the only current method providing reliable estimates.
{% if secondary_language == "arabic" %}
\\begin{Arabic}
{% endif %}
{{arabic_script}}
{% if secondary_language == "arabic" %}
\end{Arabic}{% endif %}
'''
end_string = '\end{document}'

arabic_string = u'تحتوي العربية على 28 حرفًا مكتوبًا. ويرى بعض اللغويين أنه يجب إضافة حرف الهمزة إلى حروف العربية، ليصبح عدد الحروف 29. تكتب العربية من اليمين إلى اليسار - مثلها اللغة الفارسية والعبرية وعلى عكس الكثير من اللغات العالمية - ومن أعلى الصفحة إلى أسفلها.'

report_string = '''
\documentclass[11pt,a4paper]{article}
% \documentclass{book}
\\usepackage[a4paper, total={8in, 9in}]{geometry}
\\usepackage{graphicx}  % for images
\\usepackage[demo]{graphicx}  % for subfigures
\\usepackage{caption}  % for subfigures
\\usepackage{subcaption}  % for subfigures
\\usepackage{filecontents}  % for base64 images
% \graphicspath{ {./} } % for images
\DeclareGraphicsExtensions{.pdf,.png,.jpg}
\\usepackage{booktabs}
\\usepackage{fontspec} % to use a custom font (e.g., Roboto). To use with lualatex instead of pdflatex
\\setmainfont{ {{font_name}} }
\\usepackage{lastpage} % to use the last page number in footer
\\usepackage{datetime} % to get months as a words, not numbers
\\usepackage[table,xcdraw]{xcolor} % for tables
\\usepackage{multirow} % for tables
\\usepackage{array} % for tables
%\\usepackage[italian,english]{babel} % to get some another languages later on (using \selectlanguage{italian})
\\usepackage{fancyhdr}
\pagestyle{fancy}  % to have header and footer
\\usepackage{grffile} % to manage fancy characters in figure file names (i.e., underscores)

% polyglossia stuff:
\\usepackage{fontspec}
\\usepackage{polyglossia}
\setmainlanguage{english}
{% if secondary_language == "arabic" %}
\setotherlanguage{arabic}
\\newfontfamily\\arabicfont[Script=Arabic,Scale=1.1]{Amiri}
{% endif %}

% the next 5 lines are to set the figure positioning. Figures in spare pages are centered to
% cover all the blank space. With these settings they are forced to align to the top of the page
\makeatletter
\setlength\@fptop{0pt}
\setlength\@fpsep{30pt plus 0fil}
\setlength\@fpbot{0pt}
\makeatother

\setlength{\\abovetopsep}{1ex} % to set up the separation distance between the caption and the table

\setlength\\topmargin{-40pt} % Top margin
\setlength\headheight{20pt} % Header height
%\setlength\\textwidth{7.0in} % Text width
\setlength\\textheight{9.5in} % Text height
%\setlength\oddsidemargin{-30pt} % Left margin
%\setlength\evensidemargin{-30pt} % Left margin (even pages) - only relevant with 'twoside' article option
\\begin{document}

{{report_header}}
{% if has_cover %}
{{report_cover}}
{% endif %}

{{report_body}}

\end{document}
'''
chapter_title = '''
{% if secondary_language == "arabic" %}
\\begin{Arabic}
\\section{ {{chapter_title}} }
\end{Arabic}
{% else %}
\\section{ {{chapter_title}} }
{% endif %}
'''
chapter_title = '''
{% if secondary_language == "arabic" %}
\\section{\\textarabic{ {{chapter_title}} }}
% \\section{\\begin{Arabic}{{chapter_title}}\end{Arabic}}
{% else %}
\\section{ {{chapter_title}} }
{% endif %}
'''
# chapter_title = '\section{ {{chapter_title}} }'
chapter_paragraphs = '''
{% if secondary_language == "arabic" %}
\\begin{Arabic}
{% endif %}
{% for paragraph in chapter_paragraphs %}
{{paragraph}}
{% endfor %}
{% if secondary_language == "arabic" %}
\end{Arabic}{% endif %}
'''
table_string = '''
\\begin{table}[]
\centering
\caption{My caption}
\label{my-label}
\\begin{tabular}{lll}
\hline
\\rowcolor[HTML]{EFEFEF}
\\textbf{january} & \\textbf{february} & \\textbf{march} \\\\ \hline
120 & \cellcolor[HTML]{cc1616}150 & 160 \\\\ \hline
\end{tabular}
\end{table}
'''


def get_chapter_title(chapter_title, title_string=None, language='english'):
    if not title_string:
        title_string = '''{% if secondary_language == "arabic" %}
\\section{\\textarabic{ {{chapter_title}} }}
% \\section{\\begin{Arabic}{{chapter_title}}\end{Arabic}}
{% else %}
\\section{ {{chapter_title}} }
{% endif %}
'''
    return Template(title_string).render(chapter_title=chapter_title, secondary_language=language)


def get_paragraph(paragraph, paragraph_string=None, minipage_ratio=1, language='english'):
    if not paragraph_string:
        paragraph_string = '''
{% if secondary_language == "arabic" %}
\\begin{Arabic}
{% endif %}
{{paragraph}}
{% if secondary_language == "arabic" %}
\end{Arabic}{% endif %}
'''
    return Template(paragraph_string).render(paragraph=paragraph, minipage_ratio=minipage_ratio, secondary_language=language)


def get_paragraphs(paragraphs, paragraphs_string=None, language='english'):
    if not paragraphs_string:
        paragraphs_string = '''
{% if secondary_language == "arabic" %}
\\begin{Arabic}
{% endif %}
{% for paragraph in paragraphs %}
{{paragraph}}
{% endfor %}
{% if secondary_language == "arabic" %}
\end{Arabic}{% endif %}
'''
    return Template(paragraphs_string).render(paragraphs=paragraphs, secondary_language=language)


def get_general_table(table_string=None, caption=None, header=None, values=None, footer=None, apply_value_colors=False,
                      color_header='EFEFEF', color_footer='EFEFEF',
                      value_color_ramp=('3A52bA', '62B0C3', '77E16A', 'E9F949', 'FFD62B', 'FA8C21', 'F2413D'),
                      first_column=None, last_column=None, complex_header=None,
                      bold_first_column=False, bold_last_column=False, use_horizontal_lines=True, column_widths=None,
                      at_newpage=False, minipage_ratio=1):
    if not table_string:
        table_string = '''
\\begin{table}[h!]
% \centering
{% if caption %}
\caption{ {{caption}} }
\label{ {{label}} }
{% endif %}
\\begin{tabular} { {{columns}} }
{% if use_horizontal_lines %} \hline {% endif %}
{% if header is not none%}
\\rowcolor[HTML]{ {{color_header}} }
\\textbf{ {{header[0]}} }
{% for hd in header[1:] %}
& \\textbf{ {{hd}} }
{% endfor %} \\\\ {% if use_horizontal_lines %} \hline {% endif %}
{% endif %}
{% if values is not none %}
{% for i in range(0,values_shape[0]) %}
{% if first_column is not none %}
{% if bold_first_column %} \\textbf{ {{first_column[i]}} } & {% else %} {{first_column[i]}} & {% endif %}
{% endif %}
\cellcolor[HTML]{ {{color_values[i][0]}} } {{values[i][0]}}
{% for j in range(1,values_shape[1]) %} & \cellcolor[HTML]{ {{color_values[i][j]}} } {{values[i][j]}} {% endfor %}
{% if last_column is not none %}
{% if bold_last_column %} & \\textbf{ {{last_column[i]}} } {% else %} & {{last_column[i]}} {% endif %}
{% endif %}
\\\\ {% if use_horizontal_lines %} \hline {% endif %}
{% endfor %}
{% endif %}
{% if footer is not none%}
\\rowcolor[HTML]{ {{color_footer}} }
\\textbf{ {{footer[0]}} }
{% for ft in footer[1:] %}
& \\textbf{ {{ft}} }
{% endfor %}
\\\\ {% if use_horizontal_lines %} \hline {% endif %}
{% endif %}
\end{tabular}
\end{table}
'''
    if caption:
        label = caption.replace(' ', '-')
    else:
        label = None
    # for array_like in [header, values, footer, first_column]:
    #     if array_like == []:
    #         array_like = None
    if header == []:
        header = None
        # nr_cols = len(header)
    if header is not None:
        if header.__class__ == np.ndarray:
            header_shape = values.shape
        else:
            if type(header[0]) != list and type(header[0]) != tuple:
                header = [header]
            header_shape = (len(header), len(header[0]))
    else:
        header_shape = (0, 0)
    if first_column == []:
        first_column = None
    if last_column == []:
        last_column = None
    if values == []:
        values = None
    if footer == []:
        footer = None
        # nr_cols = len(footer)
    nr_cols = 0
    if header is not None:
        nr_cols = len(header[0])
        # print( nr_cols)
    elif footer is not None:
        nr_cols = len(footer)
        # print( nr_cols)
    elif values is not None:
        if values.__class__ == np.ndarray:
            nr_cols = values.shape[1]
        else:
            nr_cols = len(values[0])
        if first_column is not None:
            nr_cols += 1
        if last_column is not None:
            nr_cols += 1
    columns = ''
    # positions = ''
    # print( column_widths, nr_cols)
    for i in range(0, nr_cols):
        if column_widths:
            # print( nr_cols, i)
            columns += 'p{' + str(column_widths[i]) + 'cm}'
        else:
            columns += 'l'
            # positions += 't'
    if values is not None:
        if values.__class__ == np.ndarray:
            values_shape = values.shape
        else:
            if type(values[0]) != list and type(values[0]) != tuple:
                values = [values]
            values_shape = (len(values), len(values[0]))
        color_values = np.chararray(values_shape, itemsize=6)
        if apply_value_colors and value_color_ramp:
            # print( values)
            min_value = np.nanmin(values)
            max_value = np.nanmax(values)
            thresholds = np.linspace(min_value, max_value, num=len(value_color_ramp) + 1)

            # print( color_values)
            # print( values.max())
            for i in range(0, len(value_color_ramp)):
                color_values[np.greater_equal(values, thresholds[i])] = value_color_ramp[i]
        else:
            color_values[:] = 'FFFFFF'

            # print( color_values)
    else:
        color_values = None
        values_shape = (0, 0)
    table_dict = dict(caption=caption, label=label, columns=columns, header=header, values=values,
                      color_values=color_values, footer=footer, complex_header=complex_header,
                      color_header=color_header, color_footer=color_footer, values_shape=values_shape, header_shape=header_shape,
                      first_column=first_column, last_column=last_column,
                      bold_first_column=bold_first_column, bold_last_column=bold_last_column,
                      use_horizontal_lines=use_horizontal_lines, at_newpage=at_newpage, minipage_ratio=minipage_ratio)
    return Template(table_string).render(**table_dict)


def get_summary_table(values, caption=None, start_year=1994, monthly_sums=True, yearly_sums=True,
                      value_color_ramp=('3A52bA', '62B0C3', '77E16A', 'E9F949', 'FFD62B', 'FA8C21', 'F2413D'),
                      header=['Year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov',
                              'Dec']):
    first_column = np.arange(start=start_year, stop=start_year + values.shape[0], step=1)
    if monthly_sums:
        footer_row = ['Sum'] + list(np.sum(values, axis=0))
    else:
        footer_row = None
    if yearly_sums:
        last_column = np.sum(row_values, axis=1)
        header = header + ['Sum']
        footer_row = list(footer_row) + [np.sum(row_values)]
    else:
        last_column = None
    if value_color_ramp:
        apply_colors = True
    else:
        apply_colors = False
    return get_general_table(caption=caption, header=header, values=values, apply_value_colors=apply_colors,
                             value_color_ramp=value_color_ramp, footer=footer_row,
                             first_column=first_column, last_column=last_column, bold_first_column=True)


def get_image(image_path, image_string=None, caption=None, textwidth_ratio=0.5, center=False, wrap_figure=None, minipage_ratio=1):
    if not image_string:
        image_string = '''
{% if wrap_figure %}
\\begin{wrapfigure}{{ '{' }}{{wrap_figure}}}{{ '{' }}{{textwidth_ratio}}\\textwidth}
{% else %}
\\begin{figure}[h]
{% endif %}
{% if center %}
\centering
{% endif %}
{% if textwidth_ratio %}
\includegraphics[width={{textwidth_ratio}}\\textwidth]{{ '{' }}{{image_path}}}
{% else %}
\includegraphics{{ '{' }}{{image_path}}}
{% endif %}
{% if caption %}
{% if textwidth_ratio %}
\caption[width={{textwidth_ratio}}\\textwidth]{{ '{' }}{{caption}}}  % THIS DOESN'T WORK WELL!
{% else %}
\caption{ {{caption}} }
{% endif %}
{% endif %}
{% if wrap_figure %}
\end{wrapfigure}
{% else %}
\end{figure}
{% endif %}'''
    image_dict = dict(image_path=image_path, caption=caption, textwidth_ratio=textwidth_ratio, center=center,
                      wrap_figure=wrap_figure, minipage_ratio=minipage_ratio)
    return Template(image_string).render(**image_dict)


def get_subfigure(image_paths, caption=None, subcaptions=None, center=False):
    """
    solution from http://tex.stackexchange.com/questions/37581/latex-figures-side-by-side
    :param image_paths:
    :param caption:
    :param subcaptions:
    :param center:
    :return:
    """
    subfigure_string = '''
\\begin{figure}[h]
{% if center %}
\centering
{% endif %}
{% for i in range(0,nr_images) %}
\\begin{subfigure}{{ '{' }}{{textwidth_ratio}}\\textwidth}
{% if center %}
\centering
{% endif %}
\includegraphics[width=1\\textwidth]{{ '{' }}{{image_paths[i]}}}
{% if subcaptions %}
\caption{ {{subcaptions[i]}} }
{% endif %}
% \label{fig:sub1}
\end{subfigure}
{% endfor %}
{% if caption %}
\caption{ {{caption}} }
{% endif %}
% \label{fig:test}
\end{figure}'''
    nr_images = len(image_paths)
    textwidth_ratio = 1. / nr_images
    image_dict = dict(image_paths=image_paths, caption=caption, subcaptions=subcaptions,
                      textwidth_ratio=textwidth_ratio,
                      nr_images=nr_images, center=center)
    return Template(subfigure_string).render(**image_dict)


def get_paralel_images(image_paths, captions=None, center=True):
    nr_images = len(image_paths)
    textwidth_ratio = 1 / float(nr_images) - 0.1
    textwidth_ratio = 1. / nr_images
    image_string = '''
\\begin{figure}[h]
{% if center %}
\centering
{% endif %}
{% for i in range(0,nr_images) %}
\\begin{minipage}{{ '{' }}{{textwidth_ratio}}\\textwidth}
\includegraphics[width=\\textwidth]{{ '{' }}{{image_paths[i]}}}
{% if captions %}
\caption{ {{captions[i]}} }
% \captionof{figure}{ {{captions[i]}} }
{% endif %}
\end{minipage}
\hfill
{% endfor %}
\end{figure}'''
    image_string = '''
\\begin{figure}[hp]
{% if center %}
\centering
{% endif %}
{% for i in range(0,nr_images) %}
\includegraphics[width={{textwidth_ratio}}\\textwidth]{{ '{' }}{{image_paths[i]}}}
{% if captions %}
\caption{ {{captions[i]}} }
{% endif %}
{% endfor %}
\end{figure}'''
    image_dict = dict(image_paths=image_paths, captions=captions, nr_images=nr_images, textwidth_ratio=textwidth_ratio,
                      center=center)
    return Template(image_string).render(**image_dict)


def get_base64_image(base64_string, caption=None, textwidth_ratio=0.5, file_extension='png'):
    jobname_base64 = "\jobname-%s.base64" % uuid.uuid4()
    jobname_tmp_image = "\jobname-%s.%s" % (uuid.uuid4(), file_extension)
    image_string = '''
\\begin{filecontents*}{ {{jobname_base64}} }
{{base64_string}}
\end{filecontents*}
\immediate\write18{base64 -d {{jobname_base64}} > {{jobname_tmp_image}}}
\\fbox{\includegraphics[width={{textwidth_ratio}}\\textwidth]{ {{jobname_tmp_image}} }}'''
    image_dict = dict(base64_string=base64_string, caption=caption, jobname_base64=jobname_base64,
                      jobname_tmp_image=jobname_tmp_image,
                      textwidth_ratio=textwidth_ratio)
    return Template(image_string).render(**image_dict)


def parse_json_like(json_to_parse, json_param_name=None, class_name=None):
    """
    Parses JSON-like input
    :param json_to_parse: dictionary or string/unicode (with JSON or file path)
    :param json_param_name: string (used for error messages)
    :param class_name: string (used for error messages)
    :return: dictionary
    """
    assert type(json_to_parse) is str or type(json_to_parse) is unicode or type(
        json_to_parse) is dict, "Parameter '{0}' of class '{1}' must be string or dictionary!".format(json_param_name,
                                                                                                      class_name)
    if type(json_to_parse) is str or type(json_to_parse) is unicode:
        if os.path.isfile(json_to_parse):
            with open(json_to_parse) as file_obj:
                # print( json_to_parse)
                json_to_parse = file_obj.read()
                # print( json_to_parse, json_to_parse.__class__)
        try:
            json_dict = json.loads(json_to_parse)
        except ValueError:
            raise ValueError(
                "Parameter '{0}' of class '{1}' is not well formed JSON string or JSON file!".format(json_param_name,
                                                                                                     class_name))
    elif type(json_to_parse) is dict:
        json_dict = json_to_parse
    return json_dict


def parse_property_file(property_file, property_separator='='):
    """
    Parses property file (written in form for example 'key=value \n'), inspired by http://stackoverflow.com/questions/3997777/what-would-be-a-quick-way-to-read-a-property-file-in-python
    :param property_file: string with filepath
    :param property_separator: string to separate key and value (for example '=' or ': ')
    :return: parsed dictionary
    """
    assert os.path.isfile(property_file), "Property file '{}' does not exist!".format(property_file)
    # assert type(property_file) is str or type(property_file) is unicode, "'property_file' parameter '{}' must be string or unicode!".format(property_file)
    # if os.path.isfile(property_file):
    #     with open(property_file) as file_obj:
    #         property_file = file_obj.read()
    return dict(line.strip().split(property_separator, maxsplit=1) for line in open(property_file) if not line.startswith('#') and not line.startswith('\n'))


def sefely_update_dict(orig_dict, new_dict):
    """
    Updates orig_dict by new_dict at any depth level
    :param orig_dict: dict
    :param new_dict: dict
    :return: dict
    """
    return_dict = orig_dict.copy()
    for key, val in new_dict.items():
        if isinstance(val, collections.Mapping):
            tmp = sefely_update_dict(return_dict.get(key, {}), val)
            return_dict[key] = tmp
        # elif isinstance(val, list):  # TODO: do we want alse list appending?
        #     orig_dict[key] = (orig_dict.get(key, []) + val)
        else:
            return_dict[key] = new_dict[key]
    return return_dict


def update_custom_image_type(configuration_dict, chapters_dict, settings_key, image_key, type_key, image_types_key, custom_type_key):
    map_types = configuration_dict.get(image_types_key, {})
    wms_settings = configuration_dict.get(settings_key, {}).get(custom_type_key, {})
    for k, v in map_types.items():
        map_types[k] = sefely_update_dict(wms_settings, map_types[k])
    for i in range(0, len(chapters_dict)):
        for j in range(0, len(chapters_dict[i])):
            if image_key == chapters_dict[i][j].keys()[0]:  # to check if the chapter item is an image
                if custom_type_key in chapters_dict[i][j][image_key].keys():
                    map_type = chapters_dict[i][j][image_key][custom_type_key].get(type_key, None)
                    if map_type and map_type in map_types.keys():
                        # print( chapters_dict[i][j][image_key][map_key])
                        chapters_dict[i][j][image_key][custom_type_key] = sefely_update_dict(map_types[map_type], chapters_dict[i][j][image_key][custom_type_key])
                        # print( chapters_dict[i][j][image_key][map_key])
    return chapters_dict


def listify_dict_values(dict_like):
    """
    Changes values of dictionary  at any depth level from string/unicode to list if start/end with [/]
    :param dict_like: dict (in later iterations it can be anything)
    :return: adjusted dictionary
    """
    if type(dict_like) == dict:
        for key, val in dict_like.items():
            dict_like[key] = listify_dict_values(dict_like.get(key, {}))
    elif type(dict_like) == list:
        for i in range(0, len(dict_like)):
            # if type(dict_like[i]) != list:
            dict_like[i] = listify_dict_values(dict_like[i])
    elif (type(dict_like) == str or type(dict_like) == unicode) and dict_like.startswith('[') \
            and dict_like.endswith(']'):
        # print( dict_like)
        try:
            dict_like = eval(dict_like)
        except:
            pass
    return dict_like


def print_pretty_json(json_dict, indent=2):
    """
    Pretty prints JSON dict
    :param json_dict: dict with valid JSON
    :param indent: int with number of spaces to indent
    :return: unicode
    """
    try:
        json_string = json.dumps(json_dict, sort_keys=True, indent=indent, separators=(',', ': '), ensure_ascii=False)
    except:
        json_string = None
    return json_string


def get_string_from_template(file_path=None, template_key=None):
    """
    asserts and read template text file
    :param file_path: string with file path
    :param template_key: string with template key (used in error messages)
    :return:
    """
    assert file_path, "Key '{}' must be defined in 'templates' key of report JSON!".format(template_key)
    assert os.path.isfile(
        file_path), "File '{0}' from key '{1}' in 'templates' key of report JSON does not exist!".format(file_path,
                                                                                                         template_key)
    with open(file_path, 'r') as fileobj:
        return fileobj.read()


def make_error_response(status_code, user_message, exception_obj):
    # print( type(exception_obj), str(exception_obj))
    return json.dumps({"status_code": status_code,
                       "message": user_message,
                       "detailed_message": "%s: %s" % (type(exception_obj).__name__, exception_obj)})


if __name__ == '__main__':
    # template_file = 'test_template.tex'
    output_latex_file = 'test_jinja.tex'

    # partial_templates = ['jinja_settings', 'jinja_header_footer', 'jinja_title', 'jinja_chapter']
    partial_templates = [setting_string, header_string, cover_string, chapter_string, end_string]

    include_title_page = True
    report_language = 'arabic'
    logo_path = 'Solargis-noR-RGB.png'
    font = 'RobotoCondensed'
    report_title = 'Some Solargis Report'
    chapter1_title = 'Forecasting methodology and assessment details'
    chapter1_title = u'ة - ومن أعلى الصفحة إلى أسفلها'
    # chapter_title = 'Dobrý deň pán Cief'
    chapter_paragraph1 = 'The Solargis\\texttrademark forecasting technology comprises various cutting-edge methodologies to predict solar radiation and other meteorological variables. Our technology provides worldwide forecasting solutions for time horizons ranging from few minutes up to 10 days ahead with sub-hourly resolution and several updates a day.'
    chapter_paragraph2 = u'تحتوي العربية على 28 حرفًا مكتوبًا. ويرى بعض اللغويين أنه يجب إضافة حرف الهمزة إلى حروف العربية، ليصبح عدد الحروف 29. تكتب العربية من اليمين إلى اليسار - مثلها اللغة الفارسية والعبرية وعلى عكس الكثير من اللغات العالمية - ومن أعلى الصفحة إلى أسفلها.'
    chapter_paragraph3 = '''The Solargis\\texttrademark forecasting\\newline
    technology comprises various cutting-edge methodologies to\\newline
    predict solar radiation and other meteorol'''
    base64_img = '''
JVBERi0xLjUKJbXtrvsKMyAwIG9iago8PCAvTGVuZ3RoIDQgMCBSCiAgIC9GaWx0ZXIgL0ZsYXRl
RGVjb2RlCj4+CnN0cmVhbQp4nJWTO1LEMAyG+5xCNYXQy69j7BFoWIpsAdx/Bjlksx4nZE0VWSP/
3y9Z+ZwIY46SAjRBThRyhq8rvL4RXL8nAlFDTQw3jxTZvAxmkCKohSEKclzOaCF5SV6KZ/iY3l8c
IZSyKTSBFmGvdASBkqFZce0H50BrTdTqsNBW8cKapNpeA66qXfFts6rEGKP9w7zfKJGhCaJokNKb
vw9GyStcaD5kHvfgQ3HzsAW/PXSCz2bfw1btIMH9Pb7JCsmA+YbVvsvZ1DmonzMYJeRUx86p+F4Z
GGfMXHXvGRXBEkPNrLdUGP0zwzSwNuxGPTK/k6nu5ZpQUTSRI9ne3dAL7zkVoGCaUIo2DTUt/gU6
+9U6/xtIJSzkocmdrVNnfAyw6+3ZUg3Ma4ftX25hXKYfzwLt9wplbmRzdHJlYW0KZW5kb2JqCjQg
MCBvYmoKICAgMzA1CmVuZG9iagoyIDAgb2JqCjw8CiAgIC9FeHRHU3RhdGUgPDwKICAgICAgL2Ew
IDw8IC9DQSAxIC9jYSAxID4+CiAgID4+Cj4+CmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9QYWdl
CiAgIC9QYXJlbnQgMSAwIFIKICAgL01lZGlhQm94IFsgMCAwIDI5Mi4zODk5MjMgNDM3LjI5MzI0
MyBdCiAgIC9Db250ZW50cyAzIDAgUgogICAvR3JvdXAgPDwKICAgICAgL1R5cGUgL0dyb3VwCiAg
ICAgIC9TIC9UcmFuc3BhcmVuY3kKICAgICAgL0NTIC9EZXZpY2VSR0IKICAgPj4KICAgL1Jlc291
cmNlcyAyIDAgUgo+PgplbmRvYmoKMSAwIG9iago8PCAvVHlwZSAvUGFnZXMKICAgL0tpZHMgWyA1
IDAgUiBdCiAgIC9Db3VudCAxCj4+CmVuZG9iago2IDAgb2JqCjw8IC9DcmVhdG9yIChjYWlybyAx
LjExLjIgKGh0dHA6Ly9jYWlyb2dyYXBoaWNzLm9yZykpCiAgIC9Qcm9kdWNlciAoY2Fpcm8gMS4x
MS4yIChodHRwOi8vY2Fpcm9ncmFwaGljcy5vcmcpKQo+PgplbmRvYmoKNyAwIG9iago8PCAvVHlw
ZSAvQ2F0YWxvZwogICAvUGFnZXMgMSAwIFIKPj4KZW5kb2JqCnhyZWYKMCA4CjAwMDAwMDAwMDAg
NjU1MzUgZiAKMDAwMDAwMDcwNSAwMDAwMCBuIAowMDAwMDAwNDE5IDAwMDAwIG4gCjAwMDAwMDAw
MTUgMDAwMDAgbiAKMDAwMDAwMDM5NyAwMDAwMCBuIAowMDAwMDAwNDkxIDAwMDAwIG4gCjAwMDAw
MDA3NzAgMDAwMDAgbiAKMDAwMDAwMDg5NyAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDgKICAg
L1Jvb3QgNyAwIFIKICAgL0luZm8gNiAwIFIKPj4Kc3RhcnR4cmVmCjk0OQolJUVPRgo='''

    # json create / parse
    json_string = json.dumps(
        {'logo_filepath': logo_path, 'font_name': font, 'report_title': report_title, 'chapter_title': chapter_title,
         'arabic_script': arabic_string, 'secondary_language': report_language})
    print( json_string)
    insets = json.loads(json_string)
    print( insets)
    print( '* * *')

    out_dir = os.path.dirname(os.path.abspath(output_latex_file))
    # insets = dict(logo_filepath=logo_path, font_name=font, report_title=report_title, chapter_title=chapter_title)
    # latex_src = ''
    #
    # # for latex_templ_file in partial_templates:
    # #     with open(latex_templ_file, 'r') as f:
    # #         latex_templ = f.read()
    # #     # print( latex_templ)
    # for latex_templ in partial_templates:
    #     latex_template = Template(latex_templ)
    #     latex_src += latex_template.render(**insets) + '\n'
    # # latex_src += '\end{document}'
    # print( latex_src)
    table_caption = 'Sample table'
    table_header = ['January', 'February', 'March', 'April', 'May']
    row_values = np.random.randint(1000, 2000, (13, 5))
    print( row_values)
    # print( row_values[0])
    footer_row = np.sum(row_values, axis=0)
    first_column = np.arange(start=1994, stop=1994 + row_values.shape[0], step=1)
    # first_column = None
    last_column = np.sum(row_values, axis=1)
    # last_column = None
    print( first_column)
    if first_column is not None:
        table_header = ['Year'] + table_header
        footer_row = ['Sum'] + list(footer_row)
    if last_column is not None:
        table_header = table_header + ['Sum']
        footer_row = list(footer_row) + [np.sum(row_values)]
    # footer_row = None
    # table_header = None
    table_dict = dict(caption='Sample table', header=['Year', 'January', 'February', 'March', 'April', 'May'],
                      values=row_values, footer=footer_row)
    header_dict = {'logo_filepath': logo_path}
    cover_dict = {'report_title': report_title}
    body_dict = dict(secondary_language=report_language, chapter_title=chapter1_title,
                     chapter_paragraphs=(chapter_paragraph1, chapter_paragraph2, chapter_paragraph3))
    report_header = Template(header_string).render(**header_dict)
    report_cover = Template(cover_string).render(**cover_dict)
    report_body = ''
    report_body += Template(chapter_title).render(**body_dict)
    report_body += Template(chapter_paragraphs).render(**body_dict)
    # report_body += Template(table_string).render(**body_dict)
    report_body += get_chapter_title('Tables')
    report_body += get_general_table(caption=table_caption, header=table_header, values=row_values,
                                     apply_value_colors=True,
                                     footer=footer_row, first_column=first_column, last_column=last_column,
                                     bold_first_column=False)
    report_body += get_general_table(
        values=[['Type of data', '15-minute time series'], ['Period', 'daco'], ['Period', 'daco']])
    report_body += get_general_table(first_column=['Type of data', 'Period'],
                                     values=[['15-minute time series'], ['daco']], bold_first_column=True,
                                     use_horizontal_lines=False, column_widths=(3, 3))
    monthly_values = np.random.randint(50, 300, (10, 12))
    color_ramp = ('3A52bA', '62B0C3', '77E16A', 'E9F949', 'FFD62B', 'FA8C21', 'F2413D')
    report_body += get_summary_table(monthly_values, caption=table_caption, start_year=1999,
                                     value_color_ramp=color_ramp,
                                     monthly_sums=True, yearly_sums=True)
    report_body += get_chapter_title('Images')
    report_body += get_image('regions_WB.jpg', caption='daco', textwidth_ratio=0.5, center=True, wrap_figure=None)
    report_body += get_image(logo_path, caption='daco insuo', textwidth_ratio=0.5, center=False, wrap_figure=None)
    report_body += get_subfigure([logo_path, logo_path], caption='subfigure', subcaptions=['fig1', 'fig2'],
                                 center=False)
    report_body += get_paralel_images([logo_path, logo_path], captions=['fig1', 'fig2'], center=False)
    report_body += get_base64_image(base64_img, caption='base64 exemple')
    captions = ['onuo', 'onuo insuo']
    # report_body += get_paralel_images(['regions_WB.jpg', logo_path, logo_path, logo_path], captions=None, center=True)

    report_dict = dict(report_header=report_header, report_cover=report_cover, report_body=report_body,
                       has_cover=include_title_page, secondary_language=report_language, font_name=font)
    # report_dict.update(insets)
    latex_src = Template(report_string).render(**report_dict)
    print( '* * *')
    print( latex_src)
    print( '* * *')

    with open(output_latex_file, 'w') as f:
        f.write(latex_src.encode('utf8'))

    # lualatex is required if we want to use a custom font, such as, Roboto.
    os.system('lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory="%s" "%s"' % (
    out_dir, output_latex_file))
    # os.system('lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory="%s" "%s"' % (out_dir, output_latex_file))
    # os.system('pdflatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory="%s" "%s"' % (out_dir, output_latex_file))
    # lualatex - synctex = 1 - interaction = nonstopmode %.tex
