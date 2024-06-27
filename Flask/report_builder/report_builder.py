import os
from pathlib import Path
from datetime import datetime

from osgeo import ogr, osr
import pandas as pd
import numpy as np
import collections
from fpdf import FPDF

from extra_utils import resource_path

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
    # Open shapefiles as layers
    driver = ogr.GetDriverByName("ESRI Shapefile")
    ds = driver.Open(new_shp, 0)
    input_lyr = ds.GetLayer()
    geometry_type = input_lyr.GetGeomType()
    vg_ds = driver.Open(grid_shp, 0)
    vg_lyr = vg_ds.GetLayer()
    tract_ds = driver.Open(tracts_shp, 0)
    tract_lyr = tract_ds.GetLayer()
    # Temp output information
    mem_driver = ogr.GetDriverByName('MEMORY')
    mem_ds = mem_driver.CreateDataSource('memData')
    memLyr = mem_ds.CreateLayer("memData", geom_type=input_lyr.GetGeomType())
    outLayerDefn = memLyr.GetLayerDefn()
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
    return vg_ids, tract_ids, stat, geometry_type

def GetIDsAndLengthOrArea_old(line, vg, tracts):
    """
    Opens shapefiles as layers, identifies ids of vg and tracts that intersect line,
    returns lists of ids and length of line or area of polygon (reprojects geometry to NA Albers projection in meters).
     Assumes all three are in same spatial reference sytstem.

    :param line: line shapefile (output of tool)
    :param vg: vector grid shapefile
    :param tracts: census tract shapefile
    :return: list of ids where vg intersects with line, list of ids where tract intersects with line, line length (m)
    """
    # Open shapefiles as layers
    driver = ogr.GetDriverByName("ESRI Shapefile")
    ds = driver.Open(line, 0)
    input_lyr = ds.GetLayer()

    geometry_type = input_lyr.GetGeomType()

    # Transfrom input_lyr geom to calculate length in meters - using NAD 1983 Albers North America
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(4326)
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(102008)

    # create the CoordinateTransformation
    coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    vg_ds = driver.Open(vg, 0)
    vg_lyr = vg_ds.GetLayer()

    tract_ds = driver.Open(tracts, 0)
    tract_lyr = tract_ds.GetLayer()

    # Temp output information
    mem_driver = ogr.GetDriverByName('MEMORY')
    mem_ds = mem_driver.CreateDataSource('memData')
    memLyr = mem_ds.CreateLayer("memData", geom_type=input_lyr.GetGeomType())
    outLayerDefn = memLyr.GetLayerDefn()

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

        l_geom.Transform(coordTrans)
        if geometry_type == 2:
            stat += l_geom.Length()
        elif geometry_type == 3:
            stat += l_geom.Area()
        else:
            print(f"Unable to pull statistic for geometry type ({geometry_type})") #TODO: Raise exception the input shapefile not able to be evaluated do to geometry type

        outFeature = ogr.Feature(outLayerDefn)
        outFeature.SetGeometry(l_geom)
        memLyr.CreateFeature(outFeature)

    del memLyr, mem_ds, mem_driver

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
        self.image(r"report_builder/images/DOE_NETL_Logos.png", 10, 10, 60)
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


def report_builder(shapefile, start_coordinates=None, end_coordinates=None, out_path="output"):
    """

    :param shapefile: polygon or line shapefile from tool output OR user input, must be in WGS84
    :param start_coordinates: "latitude, longitude" written as decimal degrees, should be direct from tool
    :param end_coordinate: "latitude, longitude" written as decimal degrees, should be direct from tool
    :param out_path: output location to save pdf report
    :return: pdf report file
    """
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
   # if vg_ids:
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
    pdf.set_font('Helvetica', '', 11)
    # for i in range(1, 41):
    #     pdf.cell(0, 10, 'Printing line number ' + str(i), 0, 1)
    # Write basic stats information
    if start_coordinates is not None:
        pdf.cell(0, 5, f"Start Location: {start_coordinates}", 0, 1)
    if end_coordinates is not None:
        pdf.cell(0, 5, f"End Location: {end_coordinates}", 0, 1)
    if geometry_type == 2:
        pdf.cell(0, 5, f"Route Length: {PrettyNumber(statistic / 1000.0)} km", 0, 1)
    else:
        pdf.cell(0, 5, f"Route Area: {PrettyNumber(statistic / 1000.0)} km", 0, 1)
    pdf.cell(0, 5, f"", 0, 1)
    pdf.cell(0, 5, f"Counties Intersected by State:", 0, 1)

    for s in list(set(states)):
        pdf.cell(0, 5, f"{s}:", 0, 1)
        # Convert list of relevant counties by index into joined list by ';'
        county_list = list()
        c_i = 0
        for c in counties:
            if s == states[c_i]:
                county_list.append(c)
            c_i += 1
        pdf.cell(10)
        pdf.multi_cell(0, 5, f"{'; '.join(county_list)}", 0, 1)


    pdf.cell(0, 5, f"", 0, 1)
    pdf.cell(0, 5, f"Spatially Intersecting Features by Category:", 0, 1)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.cell(0, 5,
             f"NOTE: Results based on where route intersects tract or 10 km grid cell that also intersects spatial data.",
             0, 1)
    pdf.set_font('Helvetica', '', 11)

    # Loop through def_dicts to build reports
    for c in categories:
        pdf.cell(0, 5, f"", 0, 1)
        pdf.cell(10)
        pdf.cell(0, 5, f"{c}", 0, 1)

        # Pull dicts for c
        c_dicts = [dd for dd in def_dicts if dd[category] == c]

        # Get list of datasets
        datasets_by_orig = list(set([cd[orig_dataset_name] for cd in c_dicts]))
        datasets_by_orig.sort()

        for d in datasets_by_orig:
            intersect_check = False
            pdf.cell(0, 5, f"", 0, 1)
            pdf.cell(20)
            pdf.cell(0, 5, f"{d}", 0, 1)

            for cd in c_dicts:
                if cd[orig_dataset_name] == d:
                    if cd['printable_values'] != '':
                        if cd[orig_dataset_name] in multiple_measurements:
                            pdf.cell(30)
                            pdf.cell(0, 5, f"{cd[title_2]}", 0, 1)
                        pdf.cell(40)
                        pdf.multi_cell(0, 5, f"{cd['printable_values']}", 0, 1)
                        pdf.cell(0, 5, f"", 0, 1)
                        intersect_check = True
            if intersect_check == False:
                pdf.cell(30)
                pdf.cell(0, 5, f"No intersections found", 0, 1)
            pdf.cell(0, 5, f"", 0, 1)
    output_file_name = f"Report_{curr_date.replace('/', '').replace(' ','_').replace(':','')}.pdf"
    out_pdf = os.path.join(out_path, output_file_name)
    # out_pdf = os.path.join(out_path, "report.pdf")          #TEMPORARY SOLUTION TO GET DOWNLOADS WORKING
    pdf.output(out_pdf, 'F')
    print("PDF created.")
    return output_file_name

if __name__ == "__main__" :
    # IN-SCRIPT TESTING 
    line_shp = r"C:\Users\leveckis\Documents\code\ey24\CO2-Pipeline-Routing-Tool\Flask\one_aquifer_wgs84.shp"
    line_shp = "C:\\Users\\leveckis\\Documents\\code\\ey24\\CO2-Pipeline-Routing-Tool\\Flask\\one_aquifer_wgs84.shp"

    line_shp = "./one_aquifer_wgs84.shp"
    #line_shp = r"C:\Users\romeolf\Desktop\test_shps_for_MCG\test_shps_for_MCG\one_aquifer_wgs84.shp"# should come from tool UI
    start_location = "33.8204468, -106.1893528" # should come from tool UI
    start_location = "38.0348321, -112.4845916"# should come from tool UI
    output_location = ""# should come from tool UI

    output_pdf = report_builder(line_shp, start_location, start_location, output_location)
