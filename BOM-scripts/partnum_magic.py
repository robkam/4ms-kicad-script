import re
import string

def deduce_SMD_TH(package):
    smdcheck = str(package[-4:]) #  package at end
    smdcheck2 = str(package[0:7]) # package at start
    headercheck = str(package[0:4]) #TH headers
    if (   smdcheck == ("0603") 
        or smdcheck == ("0805") 
        or smdcheck == ("1206")
        or smdcheck == ("323F")
        or smdcheck == ("-123")
        or smdcheck2 == ("CP_Elec")
        ):
        smd = ("SMD")
        points = int(2)
 
    elif (smdcheck == ("C33X")
        or smdcheck == ("OT23")
        ):
        smd = ("SMD")
        points = int(3)

    elif smdcheck == ("CC-4"):
        smd = ("SMD")
        points = int(4) 

    elif smdcheck2 == ("SOT-363"):
        smd = ("SMD")
        points = int(6)

    elif smdcheck2 == ("TSSOP-8"):
        smd = ("SMD")
        points = int(8)
        
    elif smdcheck2 == ("SOIC-14"):
        smd = ("SMD")
        points = int(14)

    #TH headers
    elif headercheck == ("Pins"):
        smd = ("TH")
        points = ("")
    
    else:
        smd = ("")
        points = ("")

    return [smd, points]

def deduce_resistor_metric(value):
    """
    Returns the metric of the given human-readable resistor value
    Finds various invalid cases and returns None
    Returns None (invalid), "R", "K", or "M"
    """
    if len(value) == 0:
        return None

    if value.find('m') >= 0:
        return None  #Todo: figure out part numbers for milliOhm values

    if value[0] == '0':
        return None  #Todo: handle metric shifts: 0.12k => 120R, and 1230R => 1.23k

    value = value.upper()

    num_letters = count_letters(value)
    if (num_letters == 0):
        return "R"

    if (num_letters > 1):
        return None

    if (count_characters("[KMR]", value) != 1):
        return None

    if (value.find('K') > 0):
        return 'K'
    elif (value.find('M') > 0):
        return 'M'
    elif (value.find('R') > 0):
        return 'R'
    else:
        return None

def is_malformed(value, metric):
    """
    Returns True if given value is not a valid number
    Cases such as 1k2 and 1.2k are both considered valid
    But 1k2.3 or 1.2k3 are not
    The only valid metrics allowed are "K", "M" and "R" (not case-sensitive).
    """
    if len(value) == 0:
        return True
    elif count_characters("\.", value) > 1:
        return True
    elif metric == None:
        return True

    metric_pos = value.upper().find(metric)
    has_metric_and_decimal = (metric_pos > 0) and (value.find('.') > 0)
    value_ends_in_metric = metric_pos == (len(value)-1)

    if (has_metric_and_decimal and not value_ends_in_metric) : #e.g: 1.2k3 and 1k2.3 are invalid
        return True
    return False


def deduce_0603_resistor(value):
    """
    Deduce a resistors part number based on a given human-readable value.
    Values can be something like "1.2k" or "1k23" or "123.0M" or "45.0" or "45R"
    If it can't be deduced, empty strings are returned
    Otherwise, returns a tuple of three strings: manufacturer, part_no, designation

    As of now, only 0603 Yageo RC-series Thick Film resistors are supported
    Todo: Deduce metric shifts, such as 1230R == 1.23K, and 0.1k == 100R
    Todo: figure out part numbers for 4-sig-fig resistors, e.g. 12k34
    Todo: figure out part numbers for milliOhm resistors, e.g. 50m
    Todo: Handle ohm symbol the same as R
    Todo: Check with actual Yageo part numbers (mouser API?)
    """
    metric = deduce_resistor_metric(value)

    if is_malformed(value, metric):
        return ["", "", ""]

    manuf_value = value.upper()
    metric_pos = manuf_value.find(metric)
    decimal_pos = manuf_value.find('.')

    if (decimal_pos >= 0):
        manuf_value = manuf_value.replace(".", metric, 1)
        if (metric_pos >= 0):
            manuf_value = manuf_value[:metric_pos]
    
    elif (metric_pos < 0 ):
        manuf_value = manuf_value + metric

    manuf_value = string.rstrip(manuf_value, "0")

    if count_digits(manuf_value) > 3:
        return ["", "", ""]

    manufacturer = ("Yageo")
    part_no = ("RC0603FR-07" + str(manuf_value) + "L")
    designation = (str(value) + ", 1%, 1/10W, 0603")

    return [manufacturer, part_no, designation]


### Helper Functions

def count_letters(thestring):
    return sum(1 for m in re.finditer("[a-zA-Z]", thestring))

def count_characters(chars, thestring):
    return sum(1 for m in re.finditer(chars, thestring))

def count_digits(thestring):
    return sum(1 for m in re.finditer("[0-9]", thestring))

def print_check(value):
    [manufacturer, part_no, designation] = deduce_0603_resistor(value)
    print "Value: " + value + "\t==>\t" + part_no


### Test Functions

def test_res_value(value, expected_partno):
    [manufacturer, part_no, designation] = deduce_0603_resistor(value)
    if (expected_partno == part_no):
        print "\tpass: " + value + " ==> " + part_no
    else:
        print "***\tFAIL: " + value + " ==> " + part_no + " Expected " + expected_partno

def test_metric(value, expected_metric):
    if (expected_metric == None):
        expected_metric_printable = "None"
    else:
        expected_metric_printable = expected_metric

    if (deduce_resistor_metric(value) != expected_metric):
        print "****\tFAIL: " + value + " should be " + expected_metric_printable
    else:
        print "\tPass: " + value + " metric is " + expected_metric_printable

def test_smd_th(package, expected_SMD_TH, expected_points):
    [smd, points] = deduce_SMD_TH(package)
    if (smd == expected_SMD_TH and points == expected_points):
        print "\tPass: " + package + " is " + str(points) + " points " + smd
    else:
        print "****\tFAIL: " + package + " expected to be " + str(expected_points) + ", " + expected_SMD_TH + " but was " + str(points) + ", " + smd

def run_tests():
    print "Testing Metrics..."
    test_metric("400", "R")
    test_metric("400R", "R")
    test_metric("400r", "R")
    test_metric("400A", None)
    test_metric("400K", "K")
    test_metric("400k", "K")
    test_metric("400M", "M")
    test_metric("400m", None)
    test_metric("", None)
    test_metric("400KM", None)
    test_metric("400RM", None)
    test_metric("400RK", None)
    test_metric("400RMK", None)
    test_metric("400aRMK", None)
    test_metric("K400", None)
    test_metric("M400", None)
    test_metric("R400", None)
    test_metric("1K4", "K")
    test_metric("1M4", "M")
    test_metric("1R4", "R")

    print ""
    print "Testing value deduction..."

    test_res_value("1m", "")
    test_res_value("50m", "")
    test_res_value("50.0m", "")
    test_res_value("50m0", "")
    test_res_value("0.1", "")

    test_res_value("1", "RC0603FR-071RL")
    test_res_value("1.", "RC0603FR-071RL")
    test_res_value("1R", "RC0603FR-071RL")

    test_res_value("1R2", "RC0603FR-071R2L")
    test_res_value("1.2", "RC0603FR-071R2L")
    test_res_value("1.2R", "RC0603FR-071R2L")

    test_res_value("12", "RC0603FR-0712RL")
    test_res_value("12R", "RC0603FR-0712RL")
    test_res_value("12.", "RC0603FR-0712RL")
    test_res_value("12.R", "RC0603FR-0712RL")
    test_res_value("12.0", "RC0603FR-0712RL")
    test_res_value("12.0R", "RC0603FR-0712RL")
    test_res_value("12.00R", "RC0603FR-0712RL")
    test_res_value("12.000R", "RC0603FR-0712RL")
    test_res_value("12.01R", "")

    test_res_value("12.3", "RC0603FR-0712R3L")
    test_res_value("12.3R", "RC0603FR-0712R3L")
    test_res_value("12R3", "RC0603FR-0712R3L")
    test_res_value("12R34", "")
    test_res_value("12.34", "")
    test_res_value("12.34R", "")

    test_res_value("123", "RC0603FR-07123RL")
    test_res_value("123R", "RC0603FR-07123RL")
    test_res_value("123.0R", "RC0603FR-07123RL")
    test_res_value("123.1R", "")
    test_res_value("0.1k", "RC0603FR-07100RL") #Todo: This is failing

    test_res_value("4k", "RC0603FR-074KL")
    test_res_value("4K", "RC0603FR-074KL")
    test_res_value("4.K", "RC0603FR-074KL")
    test_res_value("4.0K", "RC0603FR-074KL")
    test_res_value("4.00K", "RC0603FR-074KL")
    test_res_value("4.000k", "RC0603FR-074KL")
    test_res_value("4k000", "RC0603FR-074KL")

    test_res_value("4.7k", "RC0603FR-074K7L")
    test_res_value("4k7", "RC0603FR-074K7L")
    test_res_value("4k70", "RC0603FR-074K7L")
    test_res_value("4k70.", "")
    test_res_value("4k72", "RC0603FR-074K72L")
    test_res_value("4k729", "")

    test_res_value("43k", "RC0603FR-0743KL")
    test_res_value("43k7", "RC0603FR-0743K7L")
    test_res_value("43.7k", "RC0603FR-0743K7L")
    test_res_value("43.7k9", "")

    test_res_value("123k", "RC0603FR-07123KL")
    test_res_value("123K", "RC0603FR-07123KL")
    test_res_value("123.0K", "RC0603FR-07123KL")
    test_res_value("123.0k", "RC0603FR-07123KL")
    test_res_value("123k4" , "")
    test_res_value("123.4k" , "")
    test_res_value("123.4k9" , "")

    test_res_value("1230" , "RC0603FR-071K23L") #Todo: This is failing
    test_res_value("1239" , "")
    test_res_value("12349" , "")
    test_res_value("12k34" , "")
    test_res_value("12k349" , "")
    test_res_value("12k345" , "")

    test_smd_th("D_SOD-123", "SMD", 2)
    test_smd_th("SOT23-3_PO132", "SMD", 3)
    test_smd_th("SOT23-3_PO123", "SMD", 3)
    test_smd_th("SOT23-3_PO213", "SMD", 3)
    test_smd_th("LED_PLCC-4", "SMD", 4)
    test_smd_th("C_0603", "SMD", 2)
    test_smd_th("C0603", "SMD", 2)
    test_smd_th("C_1206", "SMD", 2)
    test_smd_th("C1206", "SMD", 2)
    test_smd_th("C_1210", "SMD", 2)
    test_smd_th("C1210", "SMD", 2)
    test_smd_th("C_0402", "SMD", 2)
    test_smd_th("C0402", "SMD", 2)
    test_smd_th("R_0603", "SMD", 2)
    test_smd_th("R0603", "SMD", 2)
    test_smd_th("R_0402", "SMD", 2)
    test_smd_th("R0402", "SMD", 2)
    test_smd_th("LQFP-48_7x7mm_P0.5mm", "SMD", 48)
    test_smd_th("FA-238", "SMD", 4)
    test_smd_th("Button_RgbLED_SPST_TC002", "TH", 8)
    test_smd_th("Button_RgbLED_SPST_PB615303HL-7mm", "TH", 8)
    test_smd_th("TSOT-23-6", "SMD", 6)
    test_smd_th("L_Taiyo-Yuden_NR-40xx", "SMD", 2)
    test_smd_th("LED_0603_1608Metric", "SMD", 2)
    
    test_smd_th("Pins_2x08_2.54mm_TH_EuroPower", "TH", 16)
    test_smd_th("Pins_1x02_2.54mm_TH", "TH", 2)
    test_smd_th("Pins_1x06_2.54mm_TH_SWD", "TH", 6)
    test_smd_th("Pot_16mm_NoDet_RV16AF-4A", "TH", 3)
    test_smd_th("Pot_16mm_CtrDet_RV16AF-4A", "TH", 3)
    test_smd_th("Pot_16mm_21Det_RV16AF-4A", "TH", 3)
    test_smd_th("Pot_9mm_Knurl_Det", "TH", 5)
    test_smd_th("EighthInch_PJ398SM", "TH", 3)


if __name__ == "__main__":
    run_tests()