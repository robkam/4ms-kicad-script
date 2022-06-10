import sys

E96_base_values = [
    1.00, 1.02, 1.05,
    1.07, 1.10, 1.13,
    1.15, 1.18, 1.21,
    1.24, 1.27, 1.30,
    1.33, 1.37, 1.40,
    1.43, 1.47, 1.50,
    1.54, 1.58, 1.62,
    1.65, 1.69, 1.74,
    1.78, 1.82, 1.87,
    1.91, 1.96, 2.00,
    2.05, 2.10, 2.16,
    2.21, 2.26, 2.32,
    2.37, 2.43, 2.49,
    2.55, 2.61, 2.67,
    2.74, 2.80, 2.87,
    2.94, 3.01, 3.09,
    3.16, 3.24, 3.32,
    3.40, 3.48, 3.57,
    3.65, 3.74, 3.83,
    3.92, 4.02, 4.12,
    4.22, 4.32, 4.42,
    4.53, 4.64, 4.75,
    4.87, 4.99, 5.11,
    5.23, 5.36, 5.49,
    5.62, 5.76, 5.90,
    6.04, 6.19, 6.34,
    6.49, 6.65, 6.81,
    6.98, 7.15, 7.32,
    7.50, 7.68, 7.87,
    8.06, 8.25, 8.45,
    8.66, 8.87, 9.09,
    9.31, 9.53, 9.76,
]

#Values in E24 that aren't also in E96
extra_E24_base_values = [
    1.20, 1.60, 1.80, 
    2.20, 2.40, 2.70, 
    3.00, 3.30, 3.60, 
    3.90, 4.30, 4.70, 
    5.10, 5.60, 6.20, 
    6.80, 8.20, 9.10
]

E96_plus_E24_values = E96_base_values + extra_E24_base_values

multiplier_list = [
    1,
    10,
    100,
    1000,
    10000,
    100000,
    1000000
]

min_value = {
    "1%": {
        "0201": 1,
        "0402": 1,
        "0603": 1,
        "0805": 1,
        "1206": 1,
        "1210": 1,
        "2010": 1,
        "2512": 1,
    },
    "0.1%": {
        "0201": 9999999,
        "0402": 4.7,
        "0603": 1,
        "0805": 1,
        "1206": 1,
        "1210": 4.7,
        "2010": 4.7,
        "2512": 4.7,
    },
}

max_value = {
    "1%": {
        "0201": 10000000,
        "0402": 10000000,
        "0603": 10000000,
        "0805": 10000000,
        "1206": 10000000,
        "1210": 10000000,
        "2010": 10000000,
        "2512": 10000000,
    },
    "0.1%": {
        "0201": 0,
        "0402": 240000,
        "0603": 1000000,
        "0805": 1500000,
        "1206": 1500000,
        "1210": 1000000,
        "2010": 1000000,
        "2512": 1000000,
    },
}


package_list = ["0201", "0402", "0603", "0805", "1206", "1210", "2010", "2512"]

wattage_dict = {
    "0201": "1/20W",
    "0402": "1/16W",
    "0603": "1/10W",
    "0805": "1/8W",
    "1206": "1/4W",
    "1210": "1/2W",
    "2010": "3/4W",
    "2512": "1W",
}

tolerance_list = ["1%", "0.1%"]

template_file = "resistor_template_kicad_sym"
jlc_file = "JLCPCB-ChipResistorSMT-20220531.csv"

def get_value_with_units(value):
    if value < 1000:
        return str(value)[:4].rstrip('0').rstrip('.') + "Ω"
    elif value < 1000000:
        return str(value/1000)[:4].rstrip('0').rstrip('.') + "k"
    elif value < 1000000000:
        return str(value/1000000)[:4].rstrip('0').rstrip('.') + "M"
    else:
        return "ValueTooLarge"

def get_short_value(value):
    """
    Return Yageo value string:
    Max 4 characters, strip trailing 0's
    R = decimal place
    K = kilo
    M = mega
    """
    if value < 1000:
        return str(value).replace(".", "R")[:4].rstrip('0')
    elif value < 1000000:
        return str(value/1000).replace(".", "K")[:4].rstrip('0')
    elif value < 1000000000:
        return str(value/1000000).replace(".", "M")[:4].rstrip('0')
    else:
        return "ValueTooLarge"


def get_jlcpcb_id(jlc, value_with_units, package, tolerance):
    id = "?"
    val = " " + value_with_units.strip("R").strip("Ω").lower() + "�" #Hex code fffd appears as a separator in the source csv file
    pack = " " + package + " "
    tol = tolerance + " "
    for comp in jlc:
        if (val in comp) and (pack in comp) and (tol in comp):
            id = comp.split(",")[0].strip('"')
            break
    return id


def gen_res(jlc, value_ohms, package, tolerance, tpl_data):
    value_with_units = get_value_with_units(value_ohms)
    value_short = get_short_value(value_ohms)
    wattage = wattage_dict[package]
    # 1% Yageo ~$0.005/ea e.g. 1.02k is  RC0603FR-071K02L
    # 0.1% Yageo 25ppm/C ~$0.04/ea e.g. 1.02k is RT0603BRD071K02L
    if tolerance=="0.1%":
        partnum = "RT%PKG%BRD07%VALSHORT%L"
        opttol = "_" + tolerance
    else:
        partnum = "RC%PKG%FR-07%VALSHORT%L"
        opttol = ""
    jlc_id = get_jlcpcb_id(jlc, value_with_units, package, tolerance)

    symdata = tpl_data.replace(r'%PARTNUM%', partnum)
    symdata = symdata.replace(r'%VAL%', value_with_units)
    symdata = symdata.replace(r'%VALSHORT%', value_short)
    symdata = symdata.replace(r'%PKG%', package)
    symdata = symdata.replace(r'%OPTTOL%', opttol)
    symdata = symdata.replace(r'%TOL%', tolerance)
    symdata = symdata.replace(r'%WATTS%', wattage)
    symdata = symdata.replace(r'%JLCPCBID%', jlc_id)
    return symdata


if __name__ == "__main__":
    showusage = False
    outfile = ""
    errstr = ""
    minmult = 1
    maxmult = 1000000

    if len(sys.argv) > 1:
        outfile = sys.argv[1]
    else:
        errstr = "Please specify an output file name"
        showusage = True

    package = "0603"
    if len(sys.argv) > 2:
        package = sys.argv[2]
        if package not in package_list:
            errstr = "Package parameter is not known"
            showusage = True

    tolerance = "1%"
    if len(sys.argv) > 3:
        tolerance = sys.argv[3]
        if tolerance not in tolerance_list:
            errstr = "Tolerance must be 1% or 0.1%"
            showusage = True

    if len(sys.argv) > 4:
        try:
            minmult = int(sys.argv[4])
        except:
            minmult = 1
        if minmult not in multiplier_list:
            errstr = "min_mult parameter is not a power of 10 between 1 and 1000000"
            showusage = True

    if len(sys.argv) > 5:
        try:
            maxmult = int(sys.argv[5])
        except:
            maxmult = 1000000
        if maxmult not in multiplier_list:
            errstr = "max_mult parameter is not a power of 10 between 1 and 1000000"
            showusage = True
        elif maxmult < minmult:
            errstr = "max_mult must be greater than or equal to min_mult"
            showusage = True

    try:
        with open(jlc_file) as db:
            jlc = db.readlines()
    except:
        jlc = []

    if showusage:
        if errstr:
            print("\nERROR: " + errstr)
        print("""
    Usage: python3 resistor_gen.py libfilename {package} {tolerance} {min_mult} {max_mult} 

    Generates a Kicad 6 symbol library or E96+E24 resistors for a given
    package size. Yageo RC-series resistor part numbers will be added
    to each symbol's Part Number field.

    {libfilename} is the output file name. Required. If you want Kicad to recognize the file, end it with .kicad_sym
    {package} can be 0201, 0402, 0603, 0805, or 1206 (default 0603)
    {tolerance} can be 1% or 0.1% (default 1%)
    {min_mult} is lowest power of 10 for which to generate values (default 1}
    {max_mult} is highest power of 10 for which to generate values (default 1000000}
       
    If you specify the libfilename as 'print-partnums' then instead of saving
    to a file, the part numbers only will be output to stdout.

    If you specify the libfilename as 'print-bom' then instead of saving to a
    file, then a JLCPCB compatible BOM csv will be output to stdout. 
    """)

    elif outfile=="print-partnums":
        tpl = "%PARTNUM%"
        for m in multiplier_list[multiplier_list.index(minmult):multiplier_list.index(maxmult)+1]:
            for v in E96_plus_E24_values:
                val = m * v
                if val >= min_value[tolerance][package] and val <= max_value[tolerance][package]:
                    print(gen_res(jlc, val, package, tolerance, tpl))

    elif outfile=="print-bom":
        print('"Comment", "Designator", "Footprint", "JLCPCB Part #"')
        i = 0
        for m in multiplier_list[multiplier_list.index(minmult):multiplier_list.index(maxmult)+1]:
            for v in E96_plus_E24_values:
                val = m * v
                tpl = f"\"%VAL% %PKG% %TOL%\", \"R{i}\", \"R%PKG%\",  \"%JLCPCBID%\""
                i = i + 1
                if val >= min_value[tolerance][package] and val <= max_value[tolerance][package]:
                    print(gen_res(jlc, val, package, tolerance, tpl))

    else:
        print(f"Generating values for {package} {tolerance} from {get_value_with_units(1.01 * minmult)} to {get_value_with_units(9.76 * maxmult)}")

        header = """(kicad_symbol_lib (version 20211014) (generator kicad_symbol_editor)
"""
        footer = """)
"""


        libdata = header
        with open(template_file) as tpl:
            tpl_data = tpl.read()
            for m in multiplier_list:
                if m < minmult or m > maxmult:
                    continue
                for v in E96_plus_E24_values:
                    val = m * v
                    if val >= min_value[tolerance][package] and val <= max_value[tolerance][package]:
                        libdata += gen_res(jlc, val, package, tolerance, tpl_data)

            libdata += footer
            with open(outfile, "w") as f:
                f.write(libdata)


# 0603 1% Not found:
# 2.16
# 11.2
# 11.7
# 14.2
# 19
# 21.6
# 22.5
# 26
# 33.1
# 35.6
# 40.1
# 41.2
# 57.5
# 88.6
# 112
# 114
# 204
# 216
# 225
# 231
# 254
# 401
# 463
# 844
# 886
# 952
# 2.16k
# 11.2k
# 21.6k
# 22.5k
# 40.1k
# 88.6k
# 112k
# 114k
# 204k
# 216k
# 225k
# 231k
# 254k
# 401k
# 463k
# 844k
# 886k
# 952k
# 1.13M
# 1.18M
# 1.65M
# 1.78M
# 1.82M
# 2.05M
# 2.16M
# 2.49M
# 2.61M
# 2.67M
# 3.16M
# 3.48M
# 4.12M
# 4.53M
# 4.87M
# 5.11M
# 5.23M
# 5.49M
# 5.76M
# 7.15M
# 8.06M
# 8.87M
# 9.31M
