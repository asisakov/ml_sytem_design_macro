import enum


def getStockNamesEnum(client):
    res = client.query('SELECT DISTINCT stock_name FROM stock')
    d = {}
    for row in res.result_rows:
        d[row[0]] = row[0]

    return enum.Enum('StockNames', d)
