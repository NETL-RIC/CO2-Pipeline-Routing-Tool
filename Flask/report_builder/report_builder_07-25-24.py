import os
from pathlib import Path
from datetime import datetime
from osgeo import ogr, osr
import pandas as pd
import numpy as np
import collections
from fpdf import FPDF

from extra_utils import resource_path


global sub_title
sub_title = list()

codecs = ['utf_8','windows-1252','utf_32','utf_32_be','utf_32_le','utf_16','utf_7','utf_8_sig','ascii','big5',
          'big5hkscs','cp037','cp273','cp424','cp437','cp500','cp720','cp737','cp775','cp850','cp852','cp855', 'cp856',
          'cp857','cp858','cp860','cp861','cp862','cp863','cp864','cp865','cp866','cp869','cp874','cp875','cp932',
          'cp949','cp950','cp1006','cp1026','cp1125','cp1140','cp1250','cp1251','cp1252','cp1253','cp1254','cp1255',
          'cp1256','cp1257','cp1258','euc_jp','euc_jis_2004','euc_jisx0213','euc_kr','gb2312','gbk','gb18030','hz',
          'iso2022_jp','iso2022_jp_1','iso2022_jp_2','iso2022_jp_2004','iso2022_jp_3','iso2022_jp_ext','iso2022_kr',
          'latin_1','iso8859_2','iso8859_3','iso8859_4','iso8859_5','iso8859_6','iso8859_7','iso8859_8','iso8859_9',
          'iso8859_10','iso8859_11','iso8859_13','iso8859_14','iso8859_15','iso8859_16','johab','koi8_r','koi8_t',
          'koi8_u','kz1048','mac_cyrillic','mac_greek','mac_iceland','mac_latin2','mac_roman','mac_turkish','ptcp154',
          'shift_jis','shift_jis_2004','shift_jisx0213', 'utf_16_be','utf_16_le']
replacers = [' ', '-', '(', ')', '%', ',', '.', '=', '>', '/']
decimal_places = 2


def GetIDsAndLengthOrArea(new_shp, grid_shp, tracts_shp):
    """
    Opens shapefiles as layers, identifies ids of vg and tracts that intersect line,
    returns lists of ids and length of line or area of polygon (reprojects geometry to NA Albers projection in meters).
     Assumes all three are in same spatial reference sytstem.
    :param new_shp: line or polygon shapefile (output of tool OR input from user)
    :param grid_shp: vector grid shapefile in inputs folder on backend
    :param tracts_shp: census tract shapefile in inputs folder on backend
    :return: list of ids where grid_shp intersects with new_shp, list of ids where tracts_shp intersects with new_shp,
            new_shp length (m) or area (m) depending on if geometry is a line or polgyon
    """
    print(f"In GetIDs... {new_shp}, {grid_shp}, {tracts_shp}")
    # Open shapefiles as layers
    driver = ogr.GetDriverByName("ESRI Shapefile")
    ds = driver.Open(new_shp, 0)
    input_lyr = ds.GetLayer()
    geometry_type = input_lyr.GetGeomType()
    vg_ds = driver.Open(grid_shp, 0)
    vg_lyr = vg_ds.GetLayer()
    tract_ds = driver.Open(tracts_shp, 0)
    tract_lyr = tract_ds.GetLayer()
    print("Shapes and layers loaded")
    # Temp output information
    mem_driver = ogr.GetDriverByName('MEMORY')
    mem_ds = mem_driver.CreateDataSource('memData')
    memLyr = mem_ds.CreateLayer("memData", geom_type=input_lyr.GetGeomType())
    outLayerDefn = memLyr.GetLayerDefn()

    # Build coordinate transformation for pulling length or area in meters
    # Transfrom input_lyr geom to calculate length in meters - using NAD 1983 Albers North America
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(4326)
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(102008)

    # create the CoordinateTransformation
    coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    # Pull list of intersecting ids
    stat = 0.0
    vg_ids = list()
    tract_ids = list()
    for l_feat in input_lyr:
        l_geom = l_feat.GetGeometryRef()
        for v_feat in vg_lyr:
            v_geom = v_feat.GetGeometryRef()
            if l_geom.Intersects(v_geom):
                vg_ids.append(v_feat.GetFID())
        for t_feat in tract_lyr:
            t_geom = t_feat.GetGeometryRef()
            if l_geom.Intersects(t_geom):
                tract_ids.append(t_feat.GetFID())

        if geometry_type in [2,3]:
            # Convert from WGS84 into meters to pull stats in meters
            l_geom.Transform(coordTrans)

            if geometry_type == 2:
                stat += l_geom.Length()
            elif geometry_type == 3:
                stat += l_geom.Area()

        else:
            # STEPHEN - here is a check for the geometry type to ensure the shapefile being evaluated is either a line or polygon
            print(f"Unable to pull statistic for geometry type ({geometry_type})") #TODO: Raise exception the input shapefile not able to be evaluated do to geometry type
        outFeature = ogr.Feature(outLayerDefn)
        outFeature.SetGeometry(l_geom)
        memLyr.CreateFeature(outFeature)
    del memLyr, mem_ds, mem_driver
    driver = None
    input_lyr, vg_lyr, tract_lyr = None, None, None
    ds, vg_ds, tract_ds = None, None, None
    # del driver
    # del input_lyr, vg_lyr, tract_lyr # Closing open layers
    # del ds, vg_ds, tract_ds # Closing open drivers
    return vg_ids, tract_ids, stat, geometry_type


def CleanDF(df, nulls, id_fld, ids):
    """
    Subset df to only where id_fld == id, remove columns where all column values are null
    #TODO: Discuss if the removal of columns is desired within the report

    :param df: pandas dataframe
    :param nulls: list of null values
    :param id_fld: id field
    :param ids: list of relavent ids to keep
    :return: cleaned df
    """

    df = df[df[id_fld].isin(ids)]

    for c in df.columns.tolist():
        for n in nulls:
            df[c].replace(n,np.nan)

    return df

    # Uncomment following to drop empty columns
    # c_drop = list()
    # for c in df.columns.tolist():
    #     if df[c].isnull().all():
    #         c_drop.append(c)
    # if c_drop:
    #     df = df.drop(columns=c_drop)
    # return df


def PrettyNumber(value):
    """
    Convert number to limit decimal places and add commas
    :param value: numeric value
    :return: pretty numeric value
    """
    if type(value) == int:
        return f'{value:,}'
    elif type(value) in [float]:
        value = round(value, decimal_places)
        return f'{value:,}'
    else:
        return value


class PDF(FPDF):
    def header(self):
        curr_date = datetime.now().strftime("%m/%d/%y %H:%M")
        # Logo
        self.image(resource_path("report_builder/images/DOE_NETL_Logos.png"), 10, 10, 60)
        #self.image(r"C:\Users\romeolf\Desktop\GitHub\SMART_CO2_TRANPORT_ROUTING_TOOL\CO2-Pipeline-Routing-Tool\Flask\report_builder\images\DOE_NETL_Logos.png", 10, 10, 60)
        # Arial bold 15
        self.set_font('Helvetica', 'B', 14)
        # Move to the right
        self.cell(115)
        # Title
        self.cell(20, 5, 'Smart CO2 Transport-Route Planning Tool (alpha)', 0, 0, 'C')
        # Line break
        self.ln(6)
        # Arial bold 15
        self.set_font('Helvetica', 'I', 12)
        # Move to the right
        self.cell(115)
        # Title
        self.cell(20, 5, f"Route Evaluation - {curr_date}", 0, 0, 'C')
        # Line break
        self.ln(10)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        ## Logo
        #self.image(r"images/disCO2ver_EDX_color_stacked_nobackground.png", -15, 10, 20)"
        # Arial italic 8
        self.set_font('Helvetica', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'R')


def p(pdf, p_type, data, header=None, level=0, font_size=None, **kwargs):
    "Inserts a paragraph or table"
    og_x = pdf.x
    og_w = pdf.w
    if level > 0:
        pdf.x = pdf.x + (5 * level)
    if font_size:
        pdf.set_font("Helvetica", size=font_size)
    if p_type == "text":
        pdf.x = pdf.x + 5
        pdf.set_margins(10,10,20)
        if not font_size:
            pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(
            w=pdf.w - (pdf.l_margin + pdf.r_margin + 20),
            h=pdf.font_size * 1.4,
            text=data,
            new_x="LEFT",
            **kwargs
        )
    elif p_type == "table":
        pdf.set_font("Helvetica", size=10)
        # Build table
        num_cols = len(header)
        if num_cols == 2:
            with pdf.table(width=pdf.w - (pdf.l_margin + pdf.r_margin + 10),
                           col_widths=((pdf.w - (pdf.l_margin + pdf.r_margin + 10)) * .15, (pdf.w - (pdf.l_margin + pdf.r_margin + 10)) * .85),
                           line_height=pdf.font_size*1.4) as table:
                row = table.row()
                for h in header:
                    row.cell(h)
                for data_row in data:
                    row = table.row()
                    for datum in data_row:
                        row.cell(datum)
    elif p_type == "header_1":
        pdf.set_font("Helvetica", size=14)
        pdf.multi_cell(
            w=pdf.w - (pdf.l_margin + pdf.r_margin + 10),
            h=pdf.font_size,
            text=data,
            new_x="LMARGIN",
            new_y="NEXT",
            **kwargs,
        )
    elif p_type == "header_2":
        pdf.set_font("Helvetica", size=12)
        pdf.multi_cell(
            w=pdf.w - (pdf.l_margin + pdf.r_margin + 10),
            h=pdf.font_size,
            text=data,
            new_x="LMARGIN",
            new_y="NEXT",
            **kwargs,
        )
    elif p_type == "header_3":
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(
            w=pdf.w - (pdf.l_margin + pdf.r_margin + 10),
            h=pdf.font_size,
            text=data,
            new_x="LMARGIN",
            new_y="NEXT",
            **kwargs,
        )
    else:
        # Internal warning
        print(f"Unable to handle {p_type}")
        pass
    pdf.x = og_x
    pdf.w = og_w



def render_toc(pdf, outline):
    pdf.x = 15 #hardcode to force correct location
    for section in outline:
        link = pdf.add_link()
        pdf.set_link(link, page=section.page_number)
        if section.name in sub_title:
            p(pdf, "text",
              f'{" " * section.level * 2} {section.name} {"." * (160 - section.level * 2 - len(section.name))} {section.page_number}',
              font_size=7,
              level=2,
              link=link)
        else:
            p(pdf,
              "text", f'{" " * section.level * 2} {section.name} {"." * (120 - section.level * 2 - len(section.name))} {section.page_number}',
              font_size=9,
              level=0,
              link=link)
        #print(f'{" " * section.level * 2} {section.name} {"." * (60 - section.level*2 - len(section.name))} {section.page_number}')


def report_builder(shapefile, start_coordinates=None, end_coordinates=None, out_path="output"):
    """

    :param shapefile: polygon or line shapefile from tool output OR user input, must be in WGS84
    :param start_coordinates: "latitude, longitude" written as decimal degrees, should be direct from tool
    :param end_coordinate: "latitude, longitude" written as decimal degrees, should be direct from tool
    :param out_path: output location to save pdf report
    :return: pdf report file
    """
    print(f"Report builder recieved: {shapefile}, {start_coordinates}, {end_coordinates}")
    curr_date = datetime.now().strftime("%m/%d/%y %H:%M")
    report_input = resource_path('report_builder\inputs')

    # Hardcoded data for evaluation
    vg_shp = os.path.join(report_input, "vg_base.shp")
    vg_id = 'OID_'
    vg_table = os.path.join(report_input, "10km_SpatialJoin_42_51_55_59_28.csv")

    tract_shp = os.path.join(report_input, "tract_base.shp")
    tract_id = 'OID_'
    state_fld = "STATE_NAME"
    county_fld = "CNTY_NAME"
    tract_fld = "TRACTCE_1"

    tract_table = os.path.join(report_input, "census_tract_boundaries_USA_AK.csv")

    def_table = os.path.join(report_input, "report_base.csv")
    category = "Category"
    orig_table = "table"
    measurement = "Report Measurement"
    query = "original field"
    title = "field_alias"
    title_2 = "field_alias_2"
    f_type = "field_type"
    orig_dataset = "Baseline FCS"
    orig_dataset_name = "Baseline FCS Nice Name"

    null_list = ['', 'None', 0, '0', 0.0, '0.0', 'nan']
    presence_vals = ["Exists", "Yes", 1.0]
    only_presence = ["Aquifers", "land_cover_v2", "National_Monuments", "National_Parks"]

    # CHECK IF PRINTED PATH IS ACTUALLY A PATH

    # shapefile = "../" + shapefile   # need to prefix ../ to go back out of report_builder directory to get .shp file
    # shapefile = Path.absolute("../" + shapefile)

    shapefile = os.path.abspath(shapefile)
    # Run intersection and pull intersecting ids and line length from shapefiles
    vg_ids, tract_ids, statistic, geometry_type = GetIDsAndLengthOrArea(shapefile, vg_shp, tract_shp)
    # Pull data by FID into dataframe for report
    vg_df = CleanDF(pd.read_csv(vg_table), null_list, vg_id, vg_ids)
    print(vg_df.shape)
    """
    else:
        print(
            f"No intersections found when comparing route to 10km multivariate grid across CONUS or AK")  # TODO: Raise as warning in tool
    """

    # Pull data by FID into dataframe for report
    if tract_ids:
        tract_df = CleanDF(pd.read_csv(tract_table), null_list, tract_id, tract_ids)
        print(tract_df.shape)
    else:
        print(
            f"No intersections found when comparing route to dataset at Census Tract-level across CONUS or AK")  # TODO: Raise as warning in tool

    # Get baseline categories and fields to search for by table
    def_dicts = list()

    w = 0
    worked = False
    while worked == False:
        try:
            def_df = pd.read_csv(def_table, encoding=codecs[w])
            worked = True
        except:
            w += 1
    for index, row in def_df.iterrows():
        if row[orig_table] != "x" and not pd.isna(row[category]) and row[category] != 'x' and row[category] != 'Header':
            title_ = row[title]
            for r in replacers:
                title_ = title_.replace(r, '_')
            def_dicts.append({category: row[category],
                              orig_table: row[orig_table],
                              orig_dataset: row[orig_dataset],
                              orig_dataset_name: row[orig_dataset_name],
                              measurement: row[measurement],
                              title: row[title],
                              'title_': title_,
                              title_2: row[title_2],
                              query: row[query],
                              f_type: row[f_type],
                              "values": [],
                              "printable_values": "",
                              "states": [],
                              "counties": [],
                              "census_tracts": []}
                             )
    del row, index, def_df

    # Get list of unique categories
    categories = list(set([dd[category] for dd in def_dicts if dd[category] != 'Header']))
    categories.sort()

    # Identify datasets where multiple items are recorded
    multiple_measurements = list()
    for c in categories:

        # Get list of datasets
        datasets_by_orig = list([cd[orig_dataset_name] for cd in [dd for dd in def_dicts if dd[category] == c]])
        count_datasets = collections.Counter(datasets_by_orig)
        for k, v in count_datasets.items():
            if v > 1:
                multiple_measurements.append(k)

    # Loop def_dicts and fill numeric or text values keys from vg_df or tract_df
    vg_cols = vg_df.columns.tolist()
    tract_cols = tract_df.columns.tolist()
    for dd in def_dicts:
        if dd[orig_table] == "grid":
            if dd["title_"] in vg_cols:
                dd["values"] = vg_df[dd["title_"]].tolist()
            else:
                print(f"{dd['title_']} missing from dataframe")  # TODO: Raise as warning in tool

        elif dd[orig_table] == "tract":
            if dd["title_"] in tract_cols:
                dd['values'] = tract_df[dd['title_']].tolist()
            else:
                print(f"{dd['title_']} missing from dataframe")  # TODO: Raise as warning in tool

        else:
            print(f"Unable to pull values from {dd[orig_table]}")  # TODO: Raise as warning in tool

        # # Pull intersecting states and counties
        dd["states"] = tract_df[state_fld].tolist()
        dd["counties"] = tract_df[county_fld].tolist()
        dd["census_tracts"] = tract_df[tract_fld].tolist()

        if dd["values"]:

            nonna_values = [vd for vd in dd["values"] if str(vd) not in null_list]
            if nonna_values:

                if dd[measurement] in ["Area", "Length"]:
                    # X out of X cells with data
                    dd["printable_values"] = dd[
                                                 "printable_values"] + f"{PrettyNumber(len(nonna_values))} out of {PrettyNumber(len(dd['values']))} 10km cells intersect ({PrettyNumber(len(nonna_values) / len(dd['values']) * 100.0)}%)\n"
                    # Total
                    dd["printable_values"] = dd[
                                                 "printable_values"] + f"Total {dd[measurement]} = {PrettyNumber(sum(nonna_values) / 1000.0)} km\n"
                    # Maximum
                    dd["printable_values"] = dd[
                                                 "printable_values"] + f"Maximum {dd[measurement]} = {PrettyNumber(max(nonna_values) / 1000.0)} km\n"
                    # Mean
                    dd["printable_values"] = dd[
                                                 "printable_values"] + f"Mean {dd[measurement]} = {PrettyNumber((sum(nonna_values) / len(nonna_values)) / 1000.0)} km\n"
                    # Min
                    dd["printable_values"] = dd[
                                                 "printable_values"] + f"Minimum {dd[measurement]} = {PrettyNumber(min(nonna_values) / 1000.0)} km\n"

                elif dd[measurement] == "Count":
                    # X out of X cells with data
                    dd["printable_values"] = dd[
                                                 "printable_values"] + f"{PrettyNumber(len(nonna_values))} out of {PrettyNumber(len(dd['values']))} " \
                                                                       f"10km cells contain values ({PrettyNumber(len(nonna_values) / len(dd['values']) * 100.0)}%)\n"
                    # Total
                    dd["printable_values"] = dd[
                                                 "printable_values"] + f"Total {dd[measurement]} = {PrettyNumber(sum(nonna_values))}\n"
                    # Maximum
                    dd["printable_values"] = dd[
                                                 "printable_values"] + f"Maximum {dd[measurement]} = {PrettyNumber(max(nonna_values))}\n"
                    # Mean
                    dd["printable_values"] = dd[
                                                 "printable_values"] + f"Mean {dd[measurement]} = {PrettyNumber(sum(nonna_values) / len(nonna_values))}\n"
                    # Min
                    dd["printable_values"] = dd[
                                                 "printable_values"] + f"Minimum {dd[measurement]} = {PrettyNumber(min(nonna_values))}\n"

                elif dd[measurement] == "Joined":
                    # X out of X tracts with data
                    dd["printable_values"] = dd["printable_values"] + f"{PrettyNumber(len(nonna_values))} out of " \
                                                                      f"{PrettyNumber(len(dd['values']))} Census Tracts intersect " \
                                                                      f"({PrettyNumber(len(nonna_values) / len(dd['values']) * 100.0)}%)\n"
                    # Total
                    dd["printable_values"] = dd["printable_values"] + f"Total = {PrettyNumber(sum(nonna_values))}\n"
                    # Maximum
                    dd["printable_values"] = dd["printable_values"] + f"Maximum = {PrettyNumber(max(nonna_values))}\n"
                    # Mean
                    dd["printable_values"] = dd[
                                                 "printable_values"] + f"Mean = {PrettyNumber(sum(nonna_values) / len(nonna_values))}\n"
                    # Min
                    dd["printable_values"] = dd["printable_values"] + f"Minimum = {PrettyNumber(min(nonna_values))}\n"

                elif dd[measurement] == "Joined-BS":  # TODO: Add handling
                    by_state = list()
                    n_i = 0
                    for n in dd["values"]:
                        if n in presence_vals and dd["states"][n_i] not in by_state:
                            by_state.append(dd["states"][n_i])

                    if by_state:
                        dd["printable_values"] = dd["printable_values"] + f"Present in {'; '.join(by_state)}\n"
                    else:
                        dd["printable_values"] = dd["printable_values"] + f"Not present in intersecting states\n"

                elif dd[measurement] == "Joined-BT":  # TODO: Add handling by state
                    presence_count = len([n for n in nonna_values if n in presence_vals])
                    # X out of X tracts with data
                    dd["printable_values"] = dd["printable_values"] + f"{presence_count} out of " \
                                                                      f"{PrettyNumber(len(dd['values']))} Census Tracts are {dd[title_2]} " \
                                                                      f"({PrettyNumber(presence_count / len(dd['values']) * 100.0)}%)\n"

                elif dd[measurement] == "Joined-BSV":  # TODO: Add handling
                    by_state = list()
                    n_i = 0
                    for n in range(len(dd["values"])):
                        by_state.append((dd["states"][n], dd["values"][n]))

                    by_state = list(set(by_state))
                    if by_state:
                        for b in by_state:
                            dd["printable_values"] = dd["printable_values"] + f"{b[0]} = {b[1]}\n"
                    else:
                        dd["printable_values"] = dd["printable_values"] + f"Not present in intersecting states\n"


                elif dd[measurement] == "List":
                    dd["printable_values"] = dd["printable_values"] + f"{PrettyNumber(len(nonna_values))} out of " \
                                                                      f"{PrettyNumber(len(dd['values']))} 10km cells intersect " \
                                                                      f"({PrettyNumber(len(nonna_values) / len(dd['values']) * 100.0)}%)\n"

                    full_unqiue_values = list()
                    for v in nonna_values:
                        if '|' in v:
                            for vv in v.split('|'):
                                if vv not in full_unqiue_values:
                                    full_unqiue_values.append(vv)
                        else:
                            if v not in full_unqiue_values:
                                full_unqiue_values.append(v)
                        # print(full_unqiue_values)
                    if full_unqiue_values:
                        dd["printable_values"] = dd["printable_values"] + f"List: {'; '.join(full_unqiue_values)}\n"
            else:
                dd["printable_values"] = dd["printable_values"] + f"No intersections found\n"

        else:
            print(f"WARNING: No values found for {dd[orig_dataset]}")

    # Loop through and clean "printable_values" where no intersections were identified based on only_presence list
    for o in only_presence:
        delete = False
        for dd in def_dicts:
            if dd[orig_dataset] == o:
                # print(dd["printable_values"])
                if "No intersections found" in dd["printable_values"]:
                    delete = True
                    dd["printable_values"] = ""
                    continue

        if delete == False:
            for dd in def_dicts:
                if dd[orig_dataset] == o:
                    if "No intersections found" not in dd["printable_values"]:
                        continue

    states = list()
    counties = list()
    for c in tract_df['CNTY_NAME'].tolist():
        if c not in counties:
            counties.append(c)
            states.append(tract_df['STATE_NAME'].tolist()[tract_df['CNTY_NAME'].tolist().index(c)])


    # Write to PDF
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_margins(10, 10, 10)

    # Table of contents placeholder
    pdf.cell(0, h=pdf.font_size, txt="", border=0, ln=1)
    p(pdf, "header_1", "Table of Contents", level=0)
    pdf.insert_toc_placeholder(render_toc)
    toc_alpha = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                 'U', 'V', 'W', 'X', 'Y', 'Z']
    toc_romnum = ['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV','XVI']
    i_abc = 0
    i_rom = 0

    # A. General Information
    text = ""
    if start_coordinates is not None:
        text = text+f"\tStart Location: {start_coordinates}\n"
    if end_coordinates is not None:
        text = text + f"\tEnd Location: {end_coordinates}\n"

    if geometry_type == 2:
        text = text + f"\tRoute Length: {PrettyNumber(statistic / 1000.0)} km\n"
    else:
        text = text + f"\tRoute Area: {PrettyNumber(statistic / 1000.0)} km\n"
    pdf.start_section(f"{toc_romnum[i_rom]}. General Route Information", level=0)

    p(pdf, "header_1", f"{toc_romnum[i_rom]}. General Route Information", level=0)
    p(pdf, "text", text)
    i_rom += 1
    pdf.cell(0, h=pdf.font_size, txt="", border=0, ln=1)

    # B. Make table of counties per state
    state_table = list()
    states = list(set(states))
    states.sort()
    c_i = 0
    for s in states:
        county_list = list()
        for c in counties:
            if s == states[c_i]:
                county_list.append(c)
        c_i += 1
        state_table.append((s, ', '.join(county_list)))
    state_table = set(state_table)

    pdf.start_section(f"{toc_romnum[i_rom]}. Counties by State", level=0)
    p(pdf, "header_1", f"{toc_romnum[i_rom]}. Counties by State", level=0)
    p(pdf, "table", state_table, header=["State", "Counties"], level=1)
    i_rom += 1
    pdf.cell(0, h=pdf.font_size, txt="", border=0, ln=1)

    pdf.start_section(f"{toc_romnum[i_rom]}. Spatially Intersecting Features by Category", level=0)
    p(pdf, "header_1", f"{toc_romnum[i_rom]}. Spatially Intersecting Features by Category", level=0)
    pdf.set_font('Helvetica', 'I', 10)
    p(pdf, 'text', f"\tNOTE: Results based on where route intersects tract or 10 km grid cell that also intersects spatial data.", level=1)
    pdf.set_font('Helvetica', '', 10)
    i_rom += 1
    pdf.cell(0, h=pdf.font_size, txt="", border=0, ln=1)

    # Loop through def_dicts to build reports
    c_index = 1
    for c in categories:
        c_index += 1

        pdf.start_section(f"{toc_alpha[i_abc]}. {c}", level=1)
        p(pdf, "header_2", f"{toc_alpha[i_abc]}. {c}", level=1)
        pdf.cell(0, h=pdf.font_size, txt="", border=0, ln=1)
        i_abc += 1

        # Pull dicts for c
        c_dicts = [dd for dd in def_dicts if dd[category] == c]

        # Get list of datasets
        datasets_by_orig = list(set([cd[orig_dataset_name] for cd in c_dicts]))
        datasets_by_orig.sort()

        toc_num = 1
        for d in datasets_by_orig:
            intersect_check = False

            for cd in c_dicts:
                if cd[orig_dataset_name] == d:
                    if cd['printable_values'] != '':

                        pdf.start_section(f"{toc_num}. {cd[title_2]}", level=2)
                        sub_title.append(f"{toc_num}. {cd[title_2]}")

                        p(pdf, "header_3", f"{toc_num}. {cd[title_2]}", level=2)
                        p(pdf, "text", cd['printable_values'], level=3)
                        toc_num += 1
                        intersect_check = True
            if intersect_check == False:

                p(pdf, "text", f"No intersections found", level=3)


    output_file_name = f"Report_{curr_date.replace('/', '').replace(' ','_').replace(':','')}.pdf"

    out_pdf = resource_path(os.path.join(out_path, output_file_name))
    pdf.output(out_pdf, 'F')
    print("PDF created.")
    return output_file_name

if __name__ == "__main__" :
    # IN-SCRIPT TESTING 
    #line_shp = r"C:\Users\romeolf\Desktop\test_files\33_report_test\input\one_hydrocarbon_pipeline_wgs84.shp"
    line_shp = "./one_aquifer_wgs84.shp"
    start_location = "33.8204468, -106.1893528" # should come from tool UI
    start_location = "38.0348321, -112.4845916"# should come from tool UI
    output_location = r"C:\Users\romeolf\Desktop\test_files\33_report_test\output"# should come from tool UI

    output_pdf = report_builder(line_shp, start_location, start_location, output_location)
