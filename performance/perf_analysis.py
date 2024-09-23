import socket
import time
import matplotlib.pyplot as plt

# Define server addresses for performance tests
CHAT_SERVER_ADDRESS = ("172.28.26.254", 55555)
CODE_SERVER_ADDRESS = ("172.28.26.254", 12345)

# Function to test latency and connection time
def measure_latency_connection_time(server_address, num_requests=10):
    latencies = []
    connection_times = []
    error_count = 0
    for _ in range(num_requests):
        start_time = time.time()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                conn_start = time.time()
                sock.connect(server_address)
                connection_time = time.time() - conn_start
                sock.send(b"ping")
                sock.recv(1024)
        except Exception as e:
            print(f"Latency/Connection Time measurement error: {e}")
            latencies.append(None)
            connection_times.append(None)
            error_count += 1
        else:
            latency = time.time() - start_time
            latencies.append(latency)
            connection_times.append(connection_time)
    error_rate = error_count / num_requests
    return latencies, connection_times, error_rate

# Function to test throughput and packet loss
def measure_throughput_packet_loss(server_address, data_size=1024, num_requests=10):
    throughputs = []
    packet_loss = 0
    error_count = 0
    data = b"x" * data_size
    for _ in range(num_requests):
        start_time = time.time()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(server_address)
                sock.send(data)
                response = sock.recv(1024)
                if not response:
                    packet_loss += 1
        except Exception as e:
            print(f"Throughput/Packet Loss error: {e}")
            throughputs.append(0)
            packet_loss += 1
            error_count += 1
        else:
            duration = time.time() - start_time
            if duration > 0:
                throughput = data_size / duration
            else:
                throughput = 0  # Set throughput to 0 if the duration is zero
            throughputs.append(throughput)
    error_rate = error_count / num_requests
    return throughputs, packet_loss, error_rate

# Function to plot individual metrics
def plot_metric(data, ylabel, title, filename):
    plt.figure()
    plt.plot(data, marker='o')
    plt.title(title)
    plt.xlabel('Request')
    plt.ylabel(ylabel)
    plt.grid()
    plt.savefig(f'performance/{filename}.png')
    plt.show()

# Run performance tests for a given server
def run_performance_tests(server_address, server_name):
    # Measure latency, connection time, and error rate
    latencies, connection_times, latency_error_rate = measure_latency_connection_time(server_address)
    
    # Measure throughput, packet loss, and error rate
    throughputs, packet_loss, throughput_error_rate = measure_throughput_packet_loss(server_address)

    # Plot individual metrics
    plot_metric(latencies, 'Time (seconds)', f'Latency for {server_name}', f'{server_name}_latency')
    plot_metric(connection_times, 'Time (seconds)', f'Connection Time for {server_name}', f'{server_name}_connection_time')
    plot_metric(throughputs, 'Throughput (bytes/s)', f'Throughput for {server_name}', f'{server_name}_throughput')
    plot_metric([packet_loss] * len(throughputs), 'Packet Loss (count)', f'Packet Loss for {server_name}', f'{server_name}_packet_loss')
    plot_metric([latency_error_rate] * len(latencies), 'Error Rate (%)', f'Error Rate for {server_name}', f'{server_name}_error_rate')

if __name__ == "__main__":
    # Test performance on the Chat Server
    print("Running performance tests on Chat Server...")
    run_performance_tests(CHAT_SERVER_ADDRESS, "Chat_Server")

    # Test performance on the Code Server
    print("Running performance tests on Code Server...")
    run_performance_tests(CODE_SERVER_ADDRESS, "Code_Server")
