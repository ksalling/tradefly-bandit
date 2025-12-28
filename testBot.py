import asyncio
import aiohttp
import logging

hrj = 1370614665649979472
fj = 1379787390155096105
squid = 1375506611195351131
tradefly = 1378750234334597191
bydfi_scalp = 1421331231282298950
bydfi_swing = 1421331173073748030
bydfi_copy = 1421331378506694797
shenanigans = 1362101608984481938
gen_chat = 1350316337909731373
flex = 1350317108927401984
pumpamentals = 1358833841959337984
squad_charts = 1350317442861105212

# Configure basic logging to see the output from the run_test function
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

fj_test_message = """ENA/USDT (long) 4h chart

Entry:  0,6364 - I'm waiting for the resistance breakout (use stop-limit/stop-market order)

TP1: 0,6577
TP2: 0,6902
TP3: 0,7271
TP4: 0,7879
TP5: 0,8712

SL: 0,5986

R:R: 6,21
@Brigade ⚔️"""

hrj_test_message = """XTZ/USDT (LONG) @Brigade ⚔️ 

Leverage: 10X 
Balance: 5% of capital

Entry: 0.676 - (limit order)

TP1: 0.746
TP2: 0.833
TP3: 0.930
TP4: 1.054

SL: 0.608

R:R: 5:5"""

false_test = "TP 2 was reached @Brigade ⚔️ "

def create_test_payload(message_content, channel_name, channel_id):
    """Creates a dictionary payload for the API request."""
    payload = {
        "channel_id": str(channel_id),
        "channel_name": channel_name,
        "message": message_content
    }
    return payload

async def run_test(payload):
    """Sends a single test payload to the API endpoint."""
    api_url = "http://127.0.0.1/api/banditMessages/"
    logger.info(f"Sending test message for channel: {payload['channel_name']}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload) as response:
                if response.status == 201:
                    logger.info(f"SUCCESS: API returned status 201 for channel '{payload['channel_name']}'.")
                else:
                    logger.error(f"FAILURE: API returned status {response.status} for channel '{payload['channel_name']}'. Response: {await response.text()}")
    except aiohttp.ClientConnectorError as e:
        logger.error(f"CONNECTION FAILED: Could not connect to the API at {api_url}. Ensure the Django server is running. Error: {e}")

async def main():
    """Main function to create and run all tests."""
    # Create payloads for each test case
    fj_payload = create_test_payload(fj_test_message, "FJ", fj)
    hrj_payload = create_test_payload(hrj_test_message, "HRJ", hrj)

    # Run the tests
    await run_test(fj_payload)
    await run_test(hrj_payload)

if __name__ == "__main__":
    asyncio.run(main())