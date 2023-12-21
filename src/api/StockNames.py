import enum


def getStockNamesEnum(client):
    res = client.query('SELECT DISTINCT stock_name FROM stock')
    d = {}
    for row in res.result_rows:
        d[row[0]] = row[0]

    return enum.Enum('StockNames', d)


def getForecastStockNamesEnum(client):
    res = client.query('SELECT DISTINCT stock_name FROM forecast')
    d = {}
    for row in res.result_rows:
        d[row[0]] = row[0]

    return enum.Enum('ForecastStockNames', d)


def getForecastModelNamesEnum(client):
    res = client.query('SELECT DISTINCT model_name FROM forecast')
    d = {}
    for row in res.result_rows:
        d[row[0]] = row[0]

    return enum.Enum('ForecastModelNames', d)
