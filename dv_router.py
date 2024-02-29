"""
Your awesome Distance Vector router for CS 168

Based on skeleton code by:
  MurphyMc, zhangwen0411, lab352
"""

import sim.api as api
from cs168.dv import (
    RoutePacket,
    Table,
    TableEntry,
    DVRouterBase,
    Ports,
    FOREVER,
    INFINITY,
)


class DVRouter(DVRouterBase):

    # A route should time out after this interval
    ROUTE_TTL = 15

    # -----------------------------------------------
    # At most one of these should ever be on at once
    SPLIT_HORIZON = False
    POISON_REVERSE = False
    # -----------------------------------------------

    # Determines if you send poison for expired routes
    POISON_EXPIRED = False

    # Determines if you send updates when a link comes up
    SEND_ON_LINK_UP = False

    # Determines if you send poison when a link goes down
    POISON_ON_LINK_DOWN = False

    def __init__(self):
        """
        Called when the instance is initialized.
        DO NOT remove any existing code from this method.
        However, feel free to add to it for memory purposes in the final stage!
        """
        assert not (
            self.SPLIT_HORIZON and self.POISON_REVERSE
        ), "Split horizon and poison reverse can't both be on"

        self.start_timer()  # Starts signaling the timer at correct rate.

        # Contains all current ports and their latencies.
        # See the write-up for documentation.
        self.ports = Ports()

        # This is the table that contains all current routes
        self.table = Table()
        self.table.owner = self

    def add_static_route(self, host, port):
        """
        Adds a static route to this router's table.

        Called automatically by the framework whenever a host is connected
        to this router.

        :param host: the host.
        :param port: the port that the host is attached to.
        :returns: nothing.
        """
        # `port` should have been added to `peer_tables` by `handle_link_up`
        # when the link came up.
        assert port in self.ports.get_all_ports(), "Link should be up, but is not."
        new_te = TableEntry(
            dst=host, port=port, latency=self.ports.get_latency(port), expire_time=FOREVER
        )
        self.table.update({
            host: new_te
        })

    def handle_data_packet(self, packet, in_port):
        """
        Called when a data packet arrives at this router.

        You may want to forward the packet, drop the packet, etc. here.

        :param packet: the packet that arrived.
        :param in_port: the port from which the packet arrived.
        :return: nothing.
        """

        if packet.dst in self.table:
            # Forward to the destination
            te = self.table[packet.dst]
            out_port = te.port
            if te.latency < INFINITY:

                self.send(packet=packet, port=out_port, flood=False)
            else:
                # Drop the packet
                pass
        else:
            pass

    # use tuples array to store the history of the route ads
    ads_history = ({})
    def send_routes(self, force=False, single_port=None):
        """
        Send route advertisements for all routes in the table.

        :param force: if True, advertises ALL routes in the table;
                      otherwise, advertises only those routes that have
                      changed since the last advertisement.
               single_port: if not None, sends updates only to that port; to
                            be used in conjunction with handle_link_up.
        :return: nothing.
        """
        if force :
            if self.SPLIT_HORIZON:
                for te in self.table:
                    route = self.table.get(te)
                    if single_port:
                        if self.POISON_REVERSE:
                            if single_port != route.port:
                                self.ads_history.update({
                                    (route.dst, single_port): route.latency
                                })
                                self.send_route(port=single_port,dst=route.dst,latency=route.latency)
                            else:
                                self.ads_history.update({
                                    (route.dst, single_port): INFINITY
                                })
                                self.send_route(port=single_port,dst=route.dst,latency=INFINITY)
                        else :
                            self.ads_history.update({
                                (route.dst, single_port): route.latency
                            })
                            self.send_route(port=single_port,dst=route.dst,latency=route.latency)
                    else:
                        for port in self.ports.get_all_ports():
                            if self.POISON_REVERSE:
                                if port != route.port:
                                    self.ads_history.update({
                                        (route.dst, port): route.latency
                                    })
                                    self.send_route(port=port,dst=route.dst,latency=route.latency)
                                else:
                                    self.ads_history.update({
                                        (route.dst, port): INFINITY
                                    })
                                    self.send_route(port=port,dst=route.dst,latency=INFINITY)
                            elif port != route.port:
                                self.ads_history.update({
                                    (route.dst, port): route.latency
                                })
                                self.send_route(port=port,dst=route.dst,latency=route.latency)  
      
            else:
                for te in self.table:
                    route = self.table.get(te)
                
                    if self.POISON_REVERSE:
                        if single_port:
                            if single_port != route.port:
                                self.ads_history.update({
                                    (route.dst, single_port): route.latency
                                })
                                self.send_route(port=single_port,dst=route.dst,latency=route.latency)
                            else:
                                self.ads_history.update({
                                    (route.dst, single_port): INFINITY
                                })
                                self.send_route(port=single_port,dst=route.dst,latency=INFINITY)
                        else:
                            for port in self.ports.get_all_ports():
                                if port != route.port:
                                    self.ads_history.update({
                                        (route.dst, port): route.latency
                                    })
                                    self.send_route(port=port,dst=route.dst,latency=route.latency)
                                else:
                                    self.ads_history.update({
                                        (route.dst, port): INFINITY
                                    })
                                    self.send_route(port=port,dst=route.dst,latency=INFINITY)

                    else:
                        if single_port:
                            self.ads_history.update({
                                (route.dst, single_port): route.latency
                            })
                            self.send_route(port=single_port,dst=route.dst,latency=route.latency)
                        else:
                            for port in self.ports.get_all_ports():
                                self.ads_history.update({
                                    (route.dst, port): route.latency
                                })
                                self.send_route(port=port,dst=route.dst,latency=route.latency)
                            
        else:
            if self.SPLIT_HORIZON:
                for te in self.table:
                    route = self.table.get(te)
                    if single_port:
                        if self.POISON_REVERSE:
                            if single_port != route.port:
                                if (route.dst, single_port) in self.ads_history:
                                    if self.ads_history.get((route.dst, single_port)) != route.latency:
                                        self.ads_history.update({
                                            (route.dst, single_port): route.latency
                                        })
                                        self.send_route(port=single_port,dst=route.dst,latency=route.latency)
                                else:
                                    self.ads_history.update({
                                        (route.dst, single_port): route.latency
                                    })
                                    self.send_route(port=single_port,dst=route.dst,latency=route.latency)
                            else:
                                if (route.dst, single_port) in self.ads_history:
                                    if self.ads_history.get((route.dst, single_port)) != INFINITY:
                                        self.ads_history.update({
                                            (route.dst, single_port): INFINITY
                                        })
                                        self.send_route(port=single_port,dst=route.dst,latency=INFINITY)
                                else :
                                    self.ads_history.update({
                                        (route.dst, single_port): INFINITY
                                    })
                                    self.send_route(port=single_port,dst=route.dst,latency=INFINITY)
                        else :
                            if (route.dst, single_port) in self.ads_history:
                                if self.ads_history.get((route.dst, single_port)) != route.latency:
                                    self.ads_history.update({
                                        (route.dst, single_port): route.latency
                                    })
                                    self.send_route(port=single_port,dst=route.dst,latency=route.latency)
                            else:
                                self.ads_history.update({
                                    (route.dst, single_port): route.latency
                                })
                                self.send_route(port=single_port,dst=route.dst,latency=route.latency)
                    else:
                        for port in self.ports.get_all_ports():
                            if self.POISON_REVERSE:
                                if port != route.port:
                                    if (route.dst, port) in self.ads_history:
                                        if self.ads_history.get((route.dst, port)) != route.latency:
                                            self.ads_history.update({
                                                (route.dst, port): route.latency
                                            })
                                            self.send_route(port=port,dst=route.dst,latency=route.latency)
                                    else:
                                        self.ads_history.update({
                                            (route.dst, port): route.latency
                                        })
                                        self.send_route(port=port,dst=route.dst,latency=route.latency)
                                else:
                                    if (route.dst, port) in self.ads_history:
                                        if self.ads_history.get((route.dst, port)) != INFINITY:
                                            self.ads_history.update({
                                                (route.dst, port): INFINITY
                                            })
                                            self.send_route(port=port,dst=route.dst,latency=INFINITY)
                                    else:
                                        self.ads_history.update({
                                            (route.dst, port): INFINITY
                                        })
                                        self.send_route(port=port,dst=route.dst,latency=INFINITY)
                                    
                            else:
                                if port != route.port:
                                    if (route.dst, port) in self.ads_history:
                                        if self.ads_history.get((route.dst, port)) != route.latency:
                                            self.ads_history.update({
                                                (route.dst, port): route.latency
                                            })
                                            self.send_route(port=port,dst=route.dst,latency=route.latency)
                                    else:
                                        self.ads_history.update({
                                            (route.dst, port): route.latency
                                        })
                                        self.send_route(port=port,dst=route.dst,latency=route.latency)
                                # else:
                                    # if (route.dst, port) in self.ads_history:
                                    #     if self.ads_history.get((route.dst, port)) != INFINITY:
                                    #         self.ads_history.update({
                                    #             (route.dst, port): INFINITY
                                    #         })
                                    #         self.send_route(port=port,dst=route.dst,latency=INFINITY)
                                    # else:
                                    #     self.ads_history.update({
                                    #         (route.dst, port): INFINITY
                                    #     })
                                    #     self.send_route(port=port,dst=route.dst,latency=INFINITY)
            else:
                for te in self.table:
                    route = self.table.get(te)
                
                    if self.POISON_REVERSE:
                        if single_port:
                            if single_port != route.port:
                                if (route.dst, single_port) in self.ads_history:
                                    if self.ads_history.get((route.dst, single_port)) != route.latency:
                                        self.ads_history.update({
                                            (route.dst, single_port): route.latency
                                        })
                                        self.send_route(port=single_port,dst=route.dst,latency=route.latency)
                                else:
                                    self.ads_history.update({
                                        (route.dst, single_port): route.latency
                                    })
                                    self.send_route(port=single_port,dst=route.dst,latency=route.latency)
                            else:
                                if (route.dst, single_port) in self.ads_history:
                                    if self.ads_history.get((route.dst, single_port)) != INFINITY:
                                        self.ads_history.update({
                                            (route.dst, single_port): INFINITY
                                        })
                                        self.send_route(port=single_port,dst=route.dst,latency=INFINITY)
                                else:
                                    self.ads_history.update({
                                        (route.dst, single_port): INFINITY
                                    })
                                    self.send_route(port=single_port,dst=route.dst,latency=INFINITY)
                        else:
                            for port in self.ports.get_all_ports():
                                if port != route.port:
                                    if (route.dst, port) in self.ads_history:
                                        if self.ads_history.get((route.dst, port)) != route.latency:
                                            self.ads_history.update({
                                                (route.dst, port): route.latency
                                            })
                                            self.send_route(port=port,dst=route.dst,latency=route.latency)
                                    else:
                                        self.ads_history.update({
                                            (route.dst, port): route.latency
                                        })
                                        self.send_route(port=port,dst=route.dst,latency=route.latency)
                                else:
                                    if (route.dst, port) in self.ads_history:
                                        if self.ads_history.get((route.dst, port)) != INFINITY:
                                            self.ads_history.update({
                                                (route.dst, port): INFINITY
                                            })
                                            self.send_route(port=port,dst=route.dst,latency=INFINITY)
                                    else:
                                        self.ads_history.update({
                                            (route.dst, port): INFINITY
                                        })
                                        self.send_route(port=port,dst=route.dst,latency=INFINITY)

                    else:
                        if single_port:
                            if (route.dst, single_port) in self.ads_history:
                                if self.ads_history.get((route.dst, single_port)) != route.latency:
                                    self.ads_history.update({
                                        (route.dst, single_port): route.latency
                                    })
                                    self.send_route(port=single_port,dst=route.dst,latency=route.latency)
                            else:
                                self.ads_history.update({
                                    (route.dst, single_port): route.latency
                                })
                                self.send_route(port=single_port,dst=route.dst,latency=route.latency)
                        else:
                            for port in self.ports.get_all_ports():
                                if (route.dst, port) in self.ads_history:
                                    if self.ads_history.get((route.dst, port)) != route.latency:
                                        self.ads_history.update({
                                            (route.dst, port): route.latency
                                        })
                                        self.send_route(port=port,dst=route.dst,latency=route.latency)
                                else:
                                    self.ads_history.update({
                                        (route.dst, port): route.latency
                                    })
                                    self.send_route(port=port,dst=route.dst,latency=route.latency)
                  
        # TODO: fill this in!
    del_te = ({})
    def expire_routes(self):
        """
        Clears out expired routes from table.
        accordingly.
        """
        expire_te = []
        for te in self.table:
            route = self.table.get(te)
            if route.expire_time < api.current_time():
                if route not in expire_te:
                    expire_te.append(te) 
        
        if self.POISON_EXPIRED:
            # need advertise the corresponding route's latency to be INFINITY
            for te in expire_te:
                route = self.table.get(te)
                for port in self.ports.get_all_ports():
                    self.table.update({
                        te:TableEntry(
                            dst=route.dst,port=route.port,latency=INFINITY,expire_time=api.current_time()+self.ROUTE_TTL
                        )
                    })
                    self.del_te.update({
                        te:api.current_time() + self.ROUTE_TTL
                    })

            for te in self.del_te:
                if self.del_te.get(te) < api.current_time():
                    del self.table[te]
                    del self.del_te[te]
        else:
            for te in expire_te:
                del self.table[te]
        # TODO: fill this in!

    def handle_route_advertisement(self, route_dst, route_latency, port):
        """
        Called when the router receives a route advertisement from a neighbor.

        :param route_dst: the destination of the advertised route.
        :param route_latency: latency from the neighbor to the destination.
        :param port: the port that the advertisement arrived on.
        :return: nothing.
        """
        for port_it in self.ports.get_all_ports():
            if port_it == port:
                lat = self.ports.get_latency(port_it)
                if lat >= INFINITY:
                    return
                if route_dst in self.table:
                    te = self.table[route_dst]
                    if te.port == port:
                        # Update the latency
                        if route_latency + lat >= INFINITY:
                            new_te = TableEntry(
                                dst=route_dst, port=port, latency=INFINITY, expire_time=self.ROUTE_TTL + api.current_time()
                            )
                            self.table.update({
                                route_dst: new_te
                            })
                        else:
                            new_te = TableEntry(
                                dst=route_dst, port=port, latency=route_latency + lat, expire_time=self.ROUTE_TTL + api.current_time()
                            )
                            self.table.update({
                                route_dst: new_te
                            })
                    elif te.latency > route_latency + lat:
                        new_te = TableEntry(
                            dst=route_dst, port=port, latency=route_latency + lat, expire_time=self.ROUTE_TTL + api.current_time()
                        )
                        self.table.update({
                            route_dst: new_te
                        })
                
                    self.send_routes(force=False)
                else:
                    if route_latency + lat < INFINITY:
                        new_te = TableEntry(
                            dst=route_dst, port=port, latency=route_latency + lat, expire_time=self.ROUTE_TTL+api.current_time()
                        )
                        self.table.update({
                            route_dst: new_te
                        })
                        self.send_routes(force=False)

        # TODO: fill this in!

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this router goes up.

        :param port: the port that the link is attached to.
        :param latency: the link latency.
        :returns: nothing.
        """
        self.ports.add_port(port, latency)
        if self.SEND_ON_LINK_UP:
            self.send_routes(force=True, single_port=port)

        # TODO: fill in the rest!

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this router goes down.

        :param port: the port number used by the link.
        :returns: nothing.
        """
        
        if self.POISON_ON_LINK_DOWN:
            for te in self.table:
                route = self.table.get(te)
                if route.port == port:
                    self.table.update({
                        te:TableEntry(
                            dst=route.dst,port=route.port,latency=INFINITY,expire_time=api.current_time()+self.ROUTE_TTL
                        )
                    })
            self.send_routes(force=False)
        self.ports.remove_port(port)
        # TODO: fill this in!

    # Feel free to add any helper methods!
