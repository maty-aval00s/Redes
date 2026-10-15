class CongestionControl:

    def __init__(self, MSS:int):
        self.current_state = "SLOW_START"
        self.MSS = MSS
        self.cwnd = MSS
        self.ssthresh = None
        self.acks_recibidos = 0

    def get_cwnd(self) -> int:
        return self.cwnd

    def get_MSS_in_cwnd(self)-> int:
        cant_mss = self.get_cwnd()//self.MSS
        return cant_mss

    def event_ack_received(self):
        if self.current_state == "SLOW_START":
            self.cwnd += self.MSS
            if self.ssthresh is not None and self.cwnd >= self.ssthresh:
                self.current_state = "CONGESTION_AVOIDANCE"
                self.acks_recibidos = 0
        elif self.current_state == "CONGESTION_AVOIDANCE":
            self.acks_recibidos += 1
            if self.acks_recibidos == self.get_MSS_in_cwnd():
                self.acks_recibidos = 0
                self.cwnd += self.MSS

    def event_timeout(self):
        if self.current_state == "SLOW_START":
            self.ssthresh = self.cwnd//2
            self.cwnd = self.MSS

        elif self.current_state == "CONGESTION_AVOIDANCE":
            self.current_state = "SLOW_START"
            self.ssthresh = self.cwnd//2 
            self.cwnd = self.MSS
    def is_state_slow_start(self):
        return self.current_state == "SLOW_START"
    
    def is_state_congestion_avoidance(self):
        return self.current_state == "CONGESTION_AVOIDANCE"

    def get_ssthresh(self):
        return self.ssthresh

    
    