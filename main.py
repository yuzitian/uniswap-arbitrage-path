from apscheduler.schedulers.blocking import BlockingScheduler
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import math

#计时循环函数
def startCronTask(task, **config):
    # BlockingScheduler
    scheduler = BlockingScheduler()
    scheduler.add_job(task, 'interval', **config)
    scheduler.start()

#获取交易池信息
def get_pool(number):
    sample_transport = RequestsHTTPTransport(
        url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
    )
    client = Client(transport=sample_transport, fetch_schema_from_transport=True)
    # token0Price:每个token1能换多少token0;token0个数/token1个数
    query = gql('''
    {
      pools(first:100, block:{number: ''' + str(number) + '''}, orderBy:totalValueLockedUSD, orderDirection:desc){
        token0{
          symbol
        }
        token1{
          symbol
        }
        token0Price
        token1Price
        liquidity
        feeTier
      }
    }
    ''')
    pools = client.execute(query)
    pool = pools['pools']
    return pool

#解析交易池信息
def jiexi(pool):
    symbolc = {}
    pricec = {}
    liquidc = {}
    fee = {}
    for i in range(len(pool)):
        if pool[i]["token0"]["symbol"] not in symbolc.keys():
            symbolc[pool[i]["token0"]["symbol"]] = []
            symbolc[pool[i]["token0"]["symbol"]].append(pool[i]["token1"]["symbol"])
            pricec[pool[i]["token0"]["symbol"]] = []
            pricec[pool[i]["token0"]["symbol"]].append(pool[i]["token1Price"])
            liquidc[pool[i]["token0"]["symbol"]] = []
            liquidc[pool[i]["token0"]["symbol"]].append(pool[i]["liquidity"])
            fee[pool[i]["token0"]["symbol"]] = []
            fee[pool[i]["token0"]["symbol"]].append(pool[i]["feeTier"])
        else:
            if pool[i]["token1"]["symbol"] not in symbolc[pool[i]["token0"]["symbol"]]:
                symbolc[pool[i]["token0"]["symbol"]].append(pool[i]["token1"]["symbol"])
                pricec[pool[i]["token0"]["symbol"]].append(pool[i]["token1Price"])
                liquidc[pool[i]["token0"]["symbol"]].append(pool[i]["liquidity"])
                fee[pool[i]["token0"]["symbol"]].append(pool[i]["feeTier"])
        if pool[i]["token1"]["symbol"] not in symbolc.keys():
            symbolc[pool[i]["token1"]["symbol"]] = []
            symbolc[pool[i]["token1"]["symbol"]].append(pool[i]["token0"]["symbol"])
            pricec[pool[i]["token1"]["symbol"]] = []
            pricec[pool[i]["token1"]["symbol"]].append(pool[i]["token0Price"])
            liquidc[pool[i]["token1"]["symbol"]] = []
            liquidc[pool[i]["token1"]["symbol"]].append(pool[i]["liquidity"])
            fee[pool[i]["token1"]["symbol"]] = []
            fee[pool[i]["token1"]["symbol"]].append(pool[i]["feeTier"])
        else:
            if pool[i]["token0"]["symbol"] not in symbolc[pool[i]["token1"]["symbol"]]:
                symbolc[pool[i]["token1"]["symbol"]].append(pool[i]["token0"]["symbol"])
                pricec[pool[i]["token1"]["symbol"]].append(pool[i]["token0Price"])
                liquidc[pool[i]["token1"]["symbol"]].append(pool[i]["liquidity"])
                fee[pool[i]["token1"]["symbol"]].append(pool[i]["feeTier"])
    return symbolc, pricec, liquidc, fee

#构建货币的数字索引
def create_index(symbolc):
    target = dict()
    x = 0
    for i in symbolc.keys():
        target[i] = x
        x += 1
    return target

#翻转数字索引
def fanzhuan(d):
    return dict(map(lambda t:(t[1],t[0]), d.items()))

#更改币种索引
def change_symbol(symbolc, dict1, dict2):
    target = dict()
    for i in range(len(symbolc)):
        target[i] = []
        for x in symbolc[dict2[i]]:
            target[i].append(dict1[x])
    return target

#求出所有长度为三的环
def find_circle(graph):
    paths = []
    for a in graph.keys():
        for b in graph[a]:
            for c in graph[b]:
                path = []
                if a in graph[c]:
                    path.append(a)
                    path.append(b)
                    path.append(c)
                    path.append(a)
                    paths.append(path)
    return paths

#将币种索引换回币种
def recover_symbol(paths, dict2):
    circles = []
    for i in range(len(paths)):
        demo = []
        for j in paths[i]:
            demo.append(dict2[j])
        circles.append(demo)
    return circles

#计算价格
def circle_price(circle, symbolc, pricec, liquidc, fee):
    index1 = symbolc[circle[0]].index(circle[1])
    index2 = symbolc[circle[1]].index(circle[2])
    index3 = symbolc[circle[2]].index(circle[3])
    pool1token0 = float(pricec[circle[0]][index1])
    pool2token0 = float(pricec[circle[1]][index2])
    pool3token0 = float(pricec[circle[2]][index3])
    liquid1 = float(liquidc[circle[0]][index1])
    liquid2 = float(liquidc[circle[1]][index2])
    liquid3 = float(liquidc[circle[2]][index3])
    fee1 = 1 - float(fee[circle[0]][index1]) / 1000000
    fee2 = 1 - float(fee[circle[1]][index2]) / 1000000
    fee3 = 1 - float(fee[circle[2]][index3]) / 1000000
    r1 = math.sqrt(pool1token0 * liquid1)
    r0 = liquid1 / r1
    r2 = math.sqrt(pool2token0 * liquid2)
    R1 = liquid2 / r2
    r3 = math.sqrt(pool3token0 * liquid3)
    R2 = liquid3 / r3
    E1 = R2 * R1 * r0
    E2 = R2 * R1 * fee1 + R2 * fee2 * r1 * fee1 + fee3 * r2 * fee2 * r1 * fee1
    E3 = r3 * fee3 * r2 * fee2 * r1 * fee1
    deltaA = (math.sqrt(E1 * E3) - E1) / E2
    if deltaA > 0:
        delta = E3 * deltaA / (E1 + E2 * deltaA) - deltaA
    else:
        delta = 0
    return delta, deltaA

#保存成字典
def create_dict(path, price, priceA):
    final = {}
    final['path'] = path[0] + '->' + path[1] + '->' + path[2] + '->' + path[3]
    final['arbitrage'] = price
    final['cost'] = priceA
    return final

#计算套利空间
def arbitrage(number):
    finals = []
    pool = get_pool(number)
    symbolc, pricec, liquidc, fee = jiexi(pool)
    dict1 = create_index(symbolc)
    dict2 = fanzhuan(dict1)
    num = change_symbol(symbolc, dict1, dict2)
    paths = find_circle(num)
    circles = recover_symbol(paths, dict2)
    for i in circles:
        price, priceA = circle_price(i, symbolc, pricec, liquidc, fee)
        if priceA > 0:
            finals.append(create_dict(i, price, priceA))
    return finals