import subprocess
import ipaddress
from concurrent.futures import ThreadPoolExecutor


def ping_host(ip: str, retries: int = 3, timeout: int = 2) -> bool:
    """Executa o comando de ping para verificar se o IP está ativo."""
    try:
        # O comando 'ping' varia conforme o sistema operacional
        # No Linux/Mac, o parâmetro '-c' envia o número de pacotes de ping
        # O parâmetro '-W' especifica o tempo máximo de espera por resposta
        command = ['ping', '-c', str(retries), '-W', str(timeout), ip]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Se o comando de ping retornar código 0, significa que o host está ativo
        return result.returncode == 0
    except subprocess.SubprocessError:
        return False


def scan_network(network: str) -> list:
    """Escaneia uma faixa de rede e retorna os IPs ativos."""
    active_ips = []
    network_address = ipaddress.ip_network(network, strict=False)

    with ThreadPoolExecutor(max_workers=20) as executor:
        # Executando os pings em paralelo
        results = executor.map(ping_host, (str(ip) for ip in network_address.hosts()))
        for ip, is_active in zip(network_address.hosts(), results):
            if is_active:
                active_ips.append(str(ip))

    return active_ips


def main():
    """Função principal para rodar o script e exibir os resultados."""
    network = input("Digite a faixa de rede (ex: 192.168.1.0/24): ")
    try:
        active_ips = scan_network(network)
        if active_ips:
            print("IPs ativos encontrados na rede:")
            for ip in active_ips:
                print(ip)
        else:
            print("Nenhum IP ativo encontrado.")
    except ValueError:
        print("Faixa de rede inválida. Certifique-se de que está no formato correto (ex: 192.168.1.0/24).")


if __name__ == "__main__":
    main()
