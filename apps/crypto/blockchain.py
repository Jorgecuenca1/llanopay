import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class BlockchainService:
    """Servicio para verificar transacciones en blockchain."""

    def __init__(self):
        self.eth_node_url = getattr(settings, 'ETH_NODE_URL', 'https://polygon-rpc.com')
        self.eth_master_address = getattr(settings, 'ETH_MASTER_ADDRESS', '')
        self.btc_master_address = getattr(settings, 'BTC_MASTER_ADDRESS', '')

    def verify_eth_transaction(self, tx_hash: str) -> dict | None:
        """
        Verifica una transaccion en una red EVM (Ethereum, Polygon, BSC)
        usando web3.py.

        Returns:
            dict con datos de la transaccion o None si no se encuentra.
        """
        try:
            from web3 import Web3

            w3 = Web3(Web3.HTTPProvider(self.eth_node_url))
            tx = w3.eth.get_transaction(tx_hash)
            receipt = w3.eth.get_transaction_receipt(tx_hash)

            if tx is None:
                logger.warning(f"Transaccion ETH no encontrada: {tx_hash}")
                return None

            current_block = w3.eth.block_number
            confirmations = current_block - receipt['blockNumber'] if receipt else 0

            return {
                'hash': tx_hash,
                'from': tx['from'],
                'to': tx['to'],
                'value': str(w3.from_wei(tx['value'], 'ether')),
                'block_number': receipt['blockNumber'] if receipt else None,
                'confirmations': confirmations,
                'status': receipt['status'] if receipt else None,
                'gas_used': receipt['gasUsed'] if receipt else None,
            }
        except ImportError:
            logger.error("web3 no esta instalado. Ejecutar: pip install web3")
            return None
        except Exception as e:
            logger.error(f"Error verificando transaccion ETH {tx_hash}: {e}")
            return None

    def verify_btc_transaction(self, tx_hash: str) -> dict | None:
        """
        Verifica una transaccion Bitcoin usando la API de Blockstream.

        Returns:
            dict con datos de la transaccion o None si no se encuentra.
        """
        try:
            url = f"https://blockstream.info/api/tx/{tx_hash}"
            response = requests.get(url, timeout=30)

            if response.status_code != 200:
                logger.warning(
                    f"Transaccion BTC no encontrada: {tx_hash} "
                    f"(status {response.status_code})"
                )
                return None

            data = response.json()

            # Obtener confirmaciones
            confirmations = 0
            if data.get('status', {}).get('confirmed'):
                tip_url = "https://blockstream.info/api/blocks/tip/height"
                tip_response = requests.get(tip_url, timeout=10)
                if tip_response.status_code == 200:
                    tip_height = int(tip_response.text)
                    block_height = data['status']['block_height']
                    confirmations = tip_height - block_height + 1

            # Extraer outputs
            outputs = []
            for vout in data.get('vout', []):
                outputs.append({
                    'address': vout.get('scriptpubkey_address', ''),
                    'value_btc': vout.get('value', 0) / 1e8,
                })

            return {
                'hash': tx_hash,
                'confirmed': data.get('status', {}).get('confirmed', False),
                'block_height': data.get('status', {}).get('block_height'),
                'confirmations': confirmations,
                'outputs': outputs,
                'fee': data.get('fee', 0),
            }
        except requests.RequestException as e:
            logger.error(f"Error de red verificando transaccion BTC {tx_hash}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verificando transaccion BTC {tx_hash}: {e}")
            return None

    def get_transaction_confirmations(self, tx_hash: str, network: str) -> int:
        """
        Obtiene el numero de confirmaciones de una transaccion
        en la red especificada.
        """
        try:
            if network == 'BITCOIN':
                tx_data = self.verify_btc_transaction(tx_hash)
            else:
                tx_data = self.verify_eth_transaction(tx_hash)

            if tx_data is None:
                return 0

            return tx_data.get('confirmations', 0)
        except Exception as e:
            logger.error(
                f"Error obteniendo confirmaciones para {tx_hash} "
                f"en {network}: {e}"
            )
            return 0

    def is_transaction_to_master(self, tx_hash: str, network: str) -> bool:
        """
        Verifica que la transaccion tiene como destino la wallet maestra
        de LlanoPay.
        """
        try:
            if network == 'BITCOIN':
                tx_data = self.verify_btc_transaction(tx_hash)
                if tx_data is None:
                    return False
                master = self.btc_master_address.lower()
                for output in tx_data.get('outputs', []):
                    if output.get('address', '').lower() == master:
                        return True
                return False
            else:
                tx_data = self.verify_eth_transaction(tx_hash)
                if tx_data is None:
                    return False
                master = self.eth_master_address.lower()
                return tx_data.get('to', '').lower() == master
        except Exception as e:
            logger.error(
                f"Error verificando destino de {tx_hash} en {network}: {e}"
            )
            return False
