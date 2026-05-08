import statistics
import time


class LatencyMetrics:

    def __init__(self):

        self.latencies = []
        self.start_time = time.time()
        self.total_orders = 0

    def record(self, latency_us):

        self.latencies.append(latency_us)
        self.total_orders += 1

    def percentile(self, data, percentile):

        if not data:
            return 0

        index = int(len(data) * percentile / 100)
        index = min(index, len(data) - 1)

        return sorted(data)[index]

    def report(self):

        if not self.latencies:
            print("No metrics collected")
            return

        elapsed = time.time() - self.start_time

        throughput = self.total_orders / elapsed

        print("\n========== LATENCY REPORT ==========")
        print(f"Orders Processed : {self.total_orders}")
        print(f"Elapsed Time     : {elapsed:.2f} sec")
        print(f"Throughput       : {throughput:.2f} orders/sec")
        print(f"Average Latency  : {statistics.mean(self.latencies):.2f} us")
        print(f"Median Latency   : {statistics.median(self.latencies):.2f} us")
        print(f"P95 Latency      : {self.percentile(self.latencies, 95):.2f} us")
        print(f"P99 Latency      : {self.percentile(self.latencies, 99):.2f} us")
        print("====================================")