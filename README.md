# Zenoh Python API

Zenoh is an extremely efficient and fault-tolerant [Named Data Networking](http://named-data.net) (NDN) protocol 
that is able to scale down to extremely constrainded devices and networks. 

The Python API is for pure clients, in other terms does not support peer-to-peer communication and can be easily
tested with our demo instace available at **demo.zenoh.io**.

## Installing the API
To install the API you can do:

    $ python3 setup.py install

Notice that on some platforms, such as Linux, you will need to do this as *sudo*.

## Running the Examples
To run the bundled examples without installing any additional software you can the **zenoh** demo instance 
available at **demo.zenoh.io**. To do so, simply run as follows:

    $ cd zenoh-python/example
    $ python3 sub.py -z demo.zenoh.io

From another terminal:

    $ cd zenoh-python/example
    $ python3 sub.py -z demo.zenoh.io


