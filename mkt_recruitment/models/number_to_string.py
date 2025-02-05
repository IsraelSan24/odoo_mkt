def number_to_string_hundred(number):
    """ Summary
        Convert numbers less than 100 to string
    """
    units = ["cero","uno","dos","tres","cuatro","cinco","seis","siete","ocho","nueve","diez","once","doce","trece","catorce","quince"]
    tens = ["","diez","veinte","treinta","cuarenta","cincuenta","sesenta","setenta","ochenta","noventa"]

    unidades = number % 10
    decenas = number // 10
    result = ""
    if number <= 15:
        result += units[number]
    else:
        if decenas == 1:
            result += "dieci"
        elif decenas == 2:
            if unidades == 0:
                result += "veinte"
            else:
                result += "veinti"
        else:
            result += tens[decenas]
            if unidades != 0:
                result += " y "
        if unidades != 0:
            result += units[unidades]
    return result


def number_to_string_thousand(number):
    """ Summary
        Convert numbers less than 1000 to string
    """
    hundreds = ["","cien","doscientos","trescientos","cuatroscientos","quinientos","seiscientos","setecientos","ochocientos","novecientos"]

    decenas = number % 100
    centenas = number // 100

    result = ""
    if centenas != 0:
        if centenas == 1:
            if decenas == 0:
                result += "cien"
            else:
                result += "ciento"
        else:
            result += hundreds[centenas]
        if decenas != 0:
            result += " "
    if centenas == 0 or decenas != 0:
        result += number_to_string_hundred(decenas)
    return result


def number_to_string_million(number):
    """ Summary
        Convert numbers less than 1000000 to string
    """
    centenas = number % 1000
    miles = number // 1000

    result = ""
    if miles >= 2:
        result += number_to_string_thousand(miles) + " "
    if miles != 0:
        result += "mil"
    if centenas != 0 or miles == 0:
        if miles != 0:
            result += " "
        result += number_to_string_thousand(centenas)
    return result


def number_to_string(number):
    """ Summary
        Convert numbers less than 1000000000000 to string
    """
    integer_part, decimal_part = str(number).split('.')
    integer_part = int(integer_part)

    miles = integer_part % 1000000
    millones = integer_part // 1000000

    result = ""
    if millones >= 2:
        result += number_to_string_million(millones) + " millones"
    if millones == 1:
        result += "Un millón"
    if miles != 0 or millones == 0:
        if millones != 0:
            result += " "
        result += number_to_string_million(miles)
    if decimal_part in ("0","00"):
        result += " 00/100"
    else:
        if len( decimal_part ) == 1:
            result += " " + str(decimal_part) + "0/100"
        else:
            result += " " + str(decimal_part) + "/100"
    return result.replace('uno mil','un mil').upper()