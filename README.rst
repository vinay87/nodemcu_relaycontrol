===============================
Vial - A Micropython Webserver
===============================

``Vial`` is a tiny web server to help hobbyists and developers who are using micropython to develop their own projects.
The project is so named as a nod to ``Flask``.

.. admonition:: Scope
    :class: tip
    
    The current status of this project is **alpha**. It is currently designed to target the ``nodemcu`` chip, and only the
    core micropython project. However, this will encompass other libraries that can use ``micropython``, and thereby, ``circuitpython``.

---------------
Example usage
---------------

* To make pin 2 output and switch it on, send get request to ``http://*ip-address-of-nodemcu*/write/2/on``
* To read from pin 2 with PULL_UP, send get request to ``http://*ip-address-of-nodemcu*/read/2?pull=up``
* To measure from a sensor, ``http://*ip-address-of-nodemcu*/measure/2?type=dht`` (Returns two number separated by a comma)

--------------------------------------
Instructions
--------------------------------------

- Connect to nodemcu using ``picocom`` or ``micropython webrepl`` command line tool.
- After nodemcu boots up, it will run boot.py followed by main.py
- You can send files to nodemcu as well using webrepl
- I have a raspberry pi zero which runs a single page webpage which sends ajax calls to this nodemcu
- since the pi zero runs pihole as well, i've set it up such that it runs on port 5000
- the webserver will start as soon as the pi zero is started (crontab @reboot)

##################
Querying Sensors
##################

.. code:: json
    :linenos:
    :caption: A sample query to retrieve the temperature for all onewire ds18b20 sensors connected to pin 4.
    
    GET /measure/4?type=ds18b20

    Response: 
    {
        'temperatures': [
            [
                {
                    'id': '0xc30316b1c398ff28',
                    'temperature': 28.6875
                },
                {
                    'id': '0xf70024984322ef28',
                    'temperature': 27.9375
                },
                {
                    'id': '0x65000e98431b8f28',
                    'temperature': 28.875
                },
                {
                    'id': '0x8000219843054328',
                    'temperature': 28.1875
                },
                {
                    'id': '0x2f00219843053228',
                    'temperature': 27.25
                }]
            ],
        'unit': 'celsius'
    }

.. todo::
    
    * [ ] Rewrite the library so it is pip-installable.
    * [ ] Write tests.
    * [ ] Write sphinx docs.
    * [ ] Connect to TravisCI.
    * [ ] Move ownership to the `vial-microserver <https://github.com/orgs/vial-microserver/>`_ team.


--------------
Contributors
--------------

* `Vinay Keerthi <https://github.com/vinay87>`_
* `Najeem Muhammed <https://github.com/idling-mind>`_

