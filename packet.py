class Packet:
    """
    Class to represent a simulated packet. It has the following data members

    **sent_ts**: Time at which the packet was sent

    **seq_num**: Sequence number of the packet

    **pdbox_time**: Arrival time at the propogation delay box

    **retx**: To identify if the packet is a retransmission

    """

    def __init__(self, sent_ts, seq_num):
        self.sent_ts = sent_ts
        self.seq_num = seq_num  
        self.pdbox_time = -1
        self.num_retx = 0
        self.timeout_duration = 0
        self.timeout_tick = 0

    def __repr__(self):
        return str(self.seq_num)
