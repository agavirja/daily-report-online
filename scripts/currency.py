def currencyoptions():
    return ['COP','USD','UF']
    
def getcurrency(currency):
    if   currency=='COP': return 1
    elif currency=='USD': return 4800
    elif currency=='UF': return 4800*43.43
    else: return 1
    
    # 1 UF -> 43.43 USD
    # 4800 COP - 1 USD