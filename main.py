import subprocess
import ipaddress
import netifaces
from concurrent.futures import ThreadPoolExecutor


def get_local_network() -> str:
    """Obtém o endereço IP da máquina e a máscara de sub-rede para calcular a rede."""
    # Obter a interface de rede padrão (geralmente a interface 'eth0' ou 'wlan0')
    interface = 'enx0c3796b32844'  # Alterar se necessário, dependendo da sua configuração
    try:
        # Obtém o endereço IP da interface
        ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
        # Obtém a máscara de sub-rede da interface
        netmask = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['netmask']
        # Cria a rede usando o IP e a máscara
        network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
        return str(network)
    except ValueError:
        raise Exception("Não foi possível obter o endereço IP ou máscara da interface, verifique se a interface está correta nas configurações.")
    except KeyError:
        raise Exception(f"Não foi possível encontrar informações para a interface: {interface}")


def ping_host(ip: str, retries: int = 3, timeout: int = 2) -> bool:
    """Executa o comando de ping para verificar se o IP está ativo."""
    try:
        command = ['ping', '-c', str(retries), '-W', str(timeout), ip]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except subprocess.SubprocessError:
        return False


def scan_network(network: str) -> list:
    """Escaneia uma faixa de rede e retorna os IPs ativos."""
    active_ips = []
    network_address = ipaddress.ip_network(network, strict=False)

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(ping_host, (str(ip) for ip in network_address.hosts()))
        for ip, is_active in zip(network_address.hosts(), results):
            if is_active:
                active_ips.append(str(ip))

    return active_ips


def get_network_from_user() -> str:
    """Obtém a rede diretamente do usuário."""
    network_input = input("Digite o endereço da rede (ex: 192.168.1.0/24): ")
    return network_input


def main():
    """Função principal para rodar o script e exibir os resultados."""
    try:
        print("Escolha uma opção:")
        print("1. Inserir manualmente o endereço da rede")
        print("2. Detectar automaticamente a rede")

        choice = input("Digite 1 ou 2: ")

        if choice == '1':
            # O usuário insere manualmente o endereço da rede
            network = get_network_from_user()
        elif choice == '2':
            # O programa detecta automaticamente a rede
            network = get_local_network()
            print(f"Rede detectada automaticamente: {network}")
        else:
            print("Opção inválida. Encerrando...")
            return

        # Escaneia a rede e encontra os IPs ativos
        print(f"Escaneando a rede: {network}")
        active_ips = scan_network(network)

        if active_ips:
            print("IPs ativos encontrados na rede:")
            for ip in active_ips:
                print(ip)
        else:
            print("Nenhum IP ativo encontrado.")
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    main()

















