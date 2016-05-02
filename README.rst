octoproxy
=========

Proxy for Sidelaunching on GitHub Events

Usage
-----

**proxy.py**::

    import octoproxy

    @octoproxy.events.register_event('pull_request', repository='*')
    def do_something_on_pull_request(event_type, event_data):
        ...

     if __name__ == "__main__":
        octoproxy.app.run()

::

    $ python proxy.py


Authors
-------

`octoproxy` was written by `M. de Verteuil <mverteuil@github.com>`_.
