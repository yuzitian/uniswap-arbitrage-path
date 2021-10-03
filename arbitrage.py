from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

sample_transport=RequestsHTTPTransport(
    url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
)
client = Client(transport=sample_transport, fetch_schema_from_transport=True)

number = 13300963

#token0Price:每个token1能换多少token0
#first:5, orderBy:totalValueLockedUSD, orderDirection:desc
query = gql('''
{
  pools(first:5, block:{number: 13300963}, orderBy:totalValueLockedUSD, orderDirection:desc){
    token0{
      symbol
      totalValueLockedUSD
    }
    token1{
      symbol
      totalValueLockedUSD
    }
    token0Price
    token1Price
    liquidity
    feeTier
  }
}
''')

pools = client.execute(query)

pool = pools["pools"]
print(pool)
poollength = len(pool)

symbolc = {}
pricec = {}
liquidc = {}
Value = {}
fee = {}
path = []

for i in range(poollength):
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
print(symbolc)
print(pricec)
print(liquidc)
print(fee)

