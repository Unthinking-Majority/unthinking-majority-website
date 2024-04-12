def gp_display(val):
    """
    Format val into osrs gp display value.
    0 - 99,999 => return value
    100,000 - 9,999,999 => return value in thousands (100k, 9999k)
    10,000,000 and up =>  return value in millions (10m)
    """
    val = int(val)
    if val <= 99999:
        return val
    elif 100000 <= val <= 9999999:
        return f"{val // 1000}k"
    elif 10000000 <= val:
        return f"{val // 1000000}M"
