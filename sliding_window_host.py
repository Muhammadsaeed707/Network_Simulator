from packet import Packet
from timeout_calculator import TimeoutCalculator


class SlidingWindowHost:
    """
    This host follows the SlidingWindow protocol. It maintains a window size and the
    list of unacked packets. The algorithm itself is documented with the send method
    """
    def __init__(self, window_size, verbose=True, min_timeout=TimeoutCalculator.MIN_TIMEOUT, max_timeout=TimeoutCalculator.MAX_TIMEOUT):
        self.unacked = []
        self.window = window_size
        self.max_seq = -1
        self.in_order_rx_seq = -1
        self.timeout_calculator = TimeoutCalculator(verbose=verbose, min_timeout=min_timeout, max_timeout=max_timeout)
        self.verbose = verbose

    def send(self, tick):
        """
        Method to send packets on to the network. Host must first check if there are any
        unacked packets, if yes, it should retransmit those first. If the window is still
        empty, the host can send more new packets on to the network.

        Args:

            **tick**: Current simulated time

        Returns:
            A list of packets that need to be transmitted. Even in case of a single packet,
            it should be returned as part of a list (i.e. [packet])
        """
        # TODO: Create an empty list of packets that the host will send
        packets = []
        # Process retransmissions
        for i, unacked_pkt in enumerate(self.unacked):
            unacked_pkt = self.unacked[i]
            if tick >= unacked_pkt.timeout_tick:
                if self.verbose:
                    print("@ " + str(tick) + " timeout for unacked_pkt " + str(unacked_pkt.seq_num) + " timeout duration was " + str(unacked_pkt.timeout_duration))
                # TODO: Retransmit any packet that has timed out
                # New packet
                retx_pkt = Packet(tick, unacked_pkt.seq_num)
                # Incrementing num_retx 
                retx_pkt.num_retx = unacked_pkt.num_retx+1
                # Add packet to the list
                packets.append(retx_pkt)
                # Back off timer
                self.timeout_calculator.exp_backoff()
                # Update timeout_tick and timeout_duration
                retx_pkt.timeout_duration = self.timeout_calculator.timeout
                retx_pkt.timeout_tick = retx_pkt.timeout_duration+tick
                if self.verbose:
                    print( "retx packet @ " + str(tick) + " with sequence number " + str(retx_pkt.seq_num))
                if self.verbose:
                    print("@ " + str(tick) + " exp backoff for packet " + str(unacked_pkt.seq_num))
            self.unacked[i] = unacked_pkt

        assert len(self.unacked) <= self.window

        # Fill window with new packets
        while len(self.unacked) < self.window:
            # TODO: Create new packets, set their retransmission timeout, and add them to the list
            pkt = Packet(tick, self.max_seq+1)
            pkt.timeout_duration = self.timeout_calculator.timeout
            pkt.timeout_tick = pkt.timeout_duration+tick
            packets.append(pkt)
            # TODO: Remember to update self.max_seq and add the just sent packet to self.unacked
            self.max_seq += 1
            self.unacked.append(pkt)
            if self.verbose:
                print("sent packet @ " + str(tick) + " with sequence number " + str(pkt.seq_num))
        assert len(self.unacked) == self.window

        # TODO: return the list of packets that need to be transmitted on to the network
        return packets

    def recv(self, pkt, tick):
        """
        Function to get a packet from the network.

        Args:

            **pkt**: Packet received from the network

            **tick**: Simulated time
        """

        assert tick > pkt.sent_ts
        # TODO: Compute RTT sample
        rtt_sample = tick-pkt.sent_ts
        # TODO: Update timeout
        self.timeout_calculator.update_timeout(rtt_sample)
        # TODO: Remove received packet from self.unacked
        for i in range(len(self.unacked)):
            if self.unacked[i].seq_num == pkt.seq_num:
                self.unacked.pop(i)
                break
        # TODO: Update in_order_rx_seq to reflect the largest sequence number that you have received in order so far
        self.in_order_rx_seq = self.max_seq
        for i in self.unacked:
            if i.seq_num < self.in_order_rx_seq:
                self.in_order_rx_seq = i.seq_num-1
        assert len(self.unacked) <= self.window
        if self.verbose:
            print("rx packet @ " + str(tick) + " with sequence number " + str(pkt.seq_num))
